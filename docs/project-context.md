# Project Context (Context Awareness)

> The **why** behind InstaLeads. Read this before making design decisions — it captures intent,
> domain knowledge, and constraints that are not derivable from the code.

## 1. The domain problem

Influencer acquisition for **consumer health, performance fitness, and dietary-supplement**
verticals is bottlenecked by the low signal-to-noise ratio of public social data. Existing
platforms (Modash, HypeAuditor, Upfluence, Grin) exhibit four structural failures:

1. **Arithmetic-mean ER distortion** — one viral reel (e.g. 40k likes on a 20k-follower account)
   creates an artificial ~200% ER spike that skews the historical mean, so naive filters flag
   spike-driven accounts as high-performing even when baseline engagement is < 1%.
2. **Geographic hallucination** — Instagram exposes no canonical `country_code`; aggregators use
   binary "English text = US" heuristics, bleeding in UK/CA/AU/EU creators as false positives.
3. **Stale / zombie contacts** — static databases re-index every 30–90 days; bio emails are
   often abandoned, agency-managed, or lack active DNS MX routing.
4. **Predatory unit economics** — $8k–18k/yr contracts force high upfront CapEx before any
   campaign-conversion validation.

## 2. The solution thesis

Invert the ETL. **Don't store crawls — verify candidates.** Ingest cheap candidate streams,
run **deterministic in-house math + statistics** locally, apply a **targeted single-pass LLM
classification**, and commit **only outreach-grade records** to an auditable relational ledger.

Each of the four failures above is addressed directly:

| Failure | InstaLeads countermeasure |
|---|---|
| Mean ER distortion | Outlier-resistant **median ER** + **variance guard** (`σ_ER < 0.80·μ_ER`), `N ≥ 8` |
| Geo hallucination | **Multi-signal Bayesian geo-confidence matrix** (0–100), threshold ≥ 65 |
| Stale contacts | **Live DNS MX validation** on every discovered email domain |
| Unit economics | Zero-cost pre-filter before paid extraction; free/cheap discovery channels |

## 3. Target users & personas

- **Primary:** a lean supplement/fitness brand's growth or partnerships lead running
  cold-outreach campaigns to micro/mid creators (10k–100k followers) and needing *verified,
  contactable, genuinely-engaged US* creators — not a 50k-row unfiltered export.
- **Secondary:** the operator/engineer maintaining the pipeline, tuning thresholds, and reading
  the dashboard.

## 4. Target segment (initial)

- **Verticals:** fitness coaching, personal training, strength & conditioning, sports nutrition,
  supplements, hypertrophy/bodybuilding.
- **Geography:** United States (the geo matrix is US-tuned; other countries are roadmap).
- **Audience band:** 10,000–100,000 followers (micro/mid tier).
- **Quality bar:** median ER ≥ 5.0%, healthy CLR, recent activity, verified contact.

## 5. Goals

- Output **outreach-grade leads only** — every row is contactable and genuinely engaged.
- **Auditable**: every accept/reject carries machine-readable provenance and a reason.
- **Cheap to run** relative to enterprise vendors; pay per verified lead, not upfront.
- **Zero vendor lock-in** — any external provider is swappable behind an ABC.

## 6. Non-goals

- Not a general-purpose scraper or a bulk creator database.
- Not a CRM or an outreach/send tool (it produces leads; sending happens elsewhere).
- No paid-audience-demographics APIs in V1.
- No non-US geo tuning in V1.
- The LLM never makes pass/fail gate decisions — only niche/content classification.

## 7. Constraints & assumptions

- **Budget-first:** discovery must stay cheap (Apify hashtag posts include engagement for free;
  Serper has a free query pool). Extraction credits are the scarce resource — spend them last.
- **Free-tier realities:** Supabase free tier pauses after ~7 days idle → keepalive heartbeat.
  Groq rate limits (~30 RPM / 30k TPM) → batching + backoff.
- **No canonical geo/contact data** from Instagram → everything is inferred with confidence.
- **Public data only.**

## 8. Key domain concepts

See [glossary.md](glossary.md) for definitions of Engagement Rate (ER), median ER, variance
guard, Comment/Like Ratio (CLR), geo-confidence matrix, DNS MX, lead lifecycle statuses
(`CANDIDATE → … → GOLD`), and location tiers.

## 9. Sources of truth

- **Authoritative spec:** [`../implementation_plan(insta leads).md`](../implementation_plan%28insta%20leads%29.md)
- **Decisions & rationale:** [architecture/decisions/](architecture/decisions/README.md)
- **Current state:** [project-status.md](project-status.md)
