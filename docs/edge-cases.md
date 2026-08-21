# Edge Cases, Failure Modes & Incident Playbooks

> Reproduces and expands spec §5. Covers **infrastructure failures** (with self-healing) and
> **data-quality traps** (the reason the verification engine exists). When implementing a stage,
> handle its rows here explicitly and log the outcome ([observability.md](observability.md)).

## 1. Infrastructure failure modes & self-healing

| Component | Failure signature | Detection | Self-healing action |
|---|---|---|---|
| **Apify extraction** | credits exhausted (HTTP 402) | `ApifyClientError` / 402 | Catch; gracefully stop Stage 3; **persist the already-enriched batch**; Slack alert. |
| **Groq classification** | 429 Too Many Requests | HTTP 429 | Exponential backoff w/ jitter via `tenacity` (2→4→8→16s). If exhausted, **fall back to regex heuristic** classification. |
| **DNS resolution** | timeout / unreachable NS | `dns.resolver.Timeout` | Wrap in **3.0s** timeout; set `contact_domain_mx=False`; downgrade `contact_confidence` to 0.20 (don't hang or crash). |
| **Supabase** | free-tier pause after ~7d idle (503 / refused) | PostgREST connection refused | Preventative **keepalive** cron (`heartbeat.yml`, every 3 days). On hit, retry with backoff. |
| **Instagram schema** | `latestPosts` key/shape changes | Pydantic `ValidationError` in normalizer | Log raw JSON to `logs/dead_letter.jsonl`; mark record `REJECTED(schema_parse_error)`; continue batch. |
| **Serper** | quota exhausted / 4xx | non-200 response | Skip channel C for the run; proceed with Apify channels; log. |
| **Empty / private / deleted profile** | missing fields, `is_private=true`, 0 posts | normalizer sees no posts | Skip verification; `REJECTED(private_or_empty)`. |

## 2. Data-quality traps (what the engine is designed to catch)

| Trap | Symptom | Guard | Reject reason |
|---|---|---|---|
| **Viral spike** | one reel dominates ER; mean looks great | median ER + `σ_ER < 0.80·μ_ER`; flag `has_outlier_posts` if `max ER ≥ 5×median` | `sigma_er_variance_exceeded` |
| **Fake likes / bought engagement** | many likes, near-zero comments | `CLR ≥ 0.01` | `fake_likes` |
| **Engagement pod** | unnaturally high comment ratio | `CLR ≤ 0.15` | `engagement_pod_detected` |
| **Insufficient sample** | `N < 8` posts | require `N ≥ 8` | `insufficient_posts` |
| **Geo hallucination** | English but UK/CA/AU/EU | multi-signal Bayesian matrix, threshold ≥ 65 | `location_confidence_low` |
| **Zombie contact** | bio email with dead domain | DNS MX must resolve | (contact downgraded; may still pass with lower confidence) |
| **Role/agency inbox** | `info@`, `contact@`, etc. | role-prefix detection lowers confidence | (flagged, not auto-rejected) |
| **Inactive creator** | last post > 10d, < 4 posts/30d | activity guard | `inactive_profile` |
| **Out-of-band audience** | followers <10k or >100k | follower band | `followers_out_of_bounds` |

## 3. Boundary conditions to test

- ER with `N = 8` exactly (odd/even median branches) and `N = 7` (must reject).
- `mean_er = 0` (avoid division by zero in the variance-guard ratio).
- `L_total = 0` in CLR (avoid divide-by-zero; treat as fail).
- Empty biography / no captions for language detection (`langdetect` raises → skip signal).
- Timestamps at the UTC daytime-window edges (hour == 4, hour == 12).
- Email regex catching trailing punctuation / multiple emails in a bio.
- De-obfuscated emails (`john [at] gmail [dot] com`) — handled in Stage 5, not the regex.

## 4. Incident playbooks

**Pipeline run produces 0 GOLD leads**
1. Check funnel logs (`prefilter_pruned`, `verification_rejected`) for where drop-off spikes.
2. Run Stage 0 controls — if known-good accounts are being rejected, thresholds drifted
   (likely an IG algorithm shift) → recalibrate, don't loosen blindly.
3. Confirm extraction returned real posts (not a schema-drift dead-letter storm).

**Costs higher than expected**
1. Verify Stage 2 pruned ~60–70% before Stage 3.
2. Confirm extraction batch size is capped (~1,000–1,500), not the full pool.

**Dashboard empty but DB has rows**
1. Check RLS anon `SELECT` policy exists and is enabled.
2. Confirm the frontend filters to `GOLD`/`VERIFIED` and env keys point at the right project.

## 5. Principles

- **Fail a single record, not the batch.** One bad profile must never abort a run.
- **Every rejection is persisted with a reason** — no silent drops.
- **Never loosen a gate to hit a lead count.** Recalibrate against controls instead.
- **Timeouts on every network call.** Unbounded waits are the #1 pipeline-hang cause.
