# Runtime Workflow — The Verification Pipeline

> How the system runs end-to-end at execution time. For the *development* workflow (git, PRs,
> CI), see [sdlc.md](sdlc.md). For the phased build order, see [implementation-plan.md](implementation-plan.md).

The pipeline is a linear, staged flow orchestrated by `backend/run_pipeline.py`. Each stage has
a well-defined input, output, and (where applicable) a hard gate. Cost discipline is the guiding
principle: **filter cheaply before spending extraction credits.**

```
STAGE 0        STAGE 1          STAGE 2         STAGE 3        STAGE 4            STAGE 5          STAGE 6
Seed/Calib. →  Discovery    →   Pre-filter  →   Extraction →  Verification   →   Classification → Persistence → Dashboard
(control)      (high recall)    (0-cost)        (paid)        (deterministic)     (LLM)            (Supabase)     (Next.js)
```

---

## Stage 0 — Seed anchors & calibration

- **Input:** a static cohort of 10–15 hand-verified domain profiles (e.g. `athleanx`,
  `dr.mike.israetel`, `biolayne`).
- **Purpose:** establish baseline engagement distributions for the current IG algorithm, extract
  baseline keyword co-occurrence, and validate the verification engine against known-good
  positives to prevent false-negative threshold drift.
- **Output:** calibration baselines; a passing self-test of Stage 4 against controls.
- **Code:** `backend/pipeline/stage0_seeds.py`.

## Stage 1 — High-recall multi-channel discovery

Three concurrent vectors harvest a broad pool (**~2,500–5,000 raw handles**) at minimal cost.

| Channel | Actor / API | Cost | Yield | Notes |
|---|---|---|---|---|
| A. Search | `apify/instagram-search-scraper` | ~$0.50/run | 500–1,000 | keyword query chunks |
| B. Hashtag | `apify/instagram-hashtag-scraper` | low | 1,500–2,500 | **returns likes/comments/caption free** → engagement hint before paying for extraction |
| C. Dorking | Serper.dev `/search` | free pool (2,500) | 500–1,500 | boolean `site:instagram.com` dorks; extract handles from links |

- **Output:** `List[CandidateHandle]` (username + provenance + optional engagement/geo hints).
- **Code:** `backend/pipeline/stage1_discovery.py`, `backend/providers/{apify_search,apify_hashtag,serper_discovery}.py`.

## Stage 2 — Zero-cost pre-filter & priority heap

Runs entirely in memory. Prunes **60–70%** of noise before any paid extraction.

1. **Dedup** against existing DB usernames + within-batch set.
2. **Fast regex** for email signal; **coarse keyword** scan for US-geo signal.
3. **Priority score** = email (40) + geo (30) + engagement hint (≤30) → **max-heap sort**.

- **Output:** deduped, priority-sorted `List[CandidateHandle]`.
- **Code:** `backend/pipeline/stage2_prefilter.py`.

## Stage 3 — Extraction & data hydration

Batch the **top ~1,000–1,500** prioritized candidates through the extraction ABC.

- **Provider (V1):** `apify/instagram-profile-scraper`, `maxPosts: 12`.
- **Normalization:** raw actor JSON → `RawProfile` + `RawPost` (Pydantic). Parse failures →
  dead-letter + `REJECTED(schema_parse_error)`.
- **Output:** `List[RawProfile]` with up to 12 recent posts each.
- **Code:** `backend/pipeline/stage3_enrichment.py`, `backend/providers/apify_profile.py`.

## Stage 4 — Deterministic verification engine (the core)

Sequential hard gates. First failure → `REJECTED` with reason. All math is in-house; **no LLM.**

```
Raw Profile
  ├─ Follower band     → followers ∈ [10k, 100k]        else "followers_out_of_bounds"
  ├─ Activity guard    → last post ≤ 10d, posts/30d ≥ 4 else "inactive_profile"
  ├─ Median ER         → median ER ≥ 5.0%, N ≥ 8         else "median_er_below_threshold"
  │                      σ_ER < 0.80·μ_ER                else "sigma_er_variance_exceeded"
  ├─ Anti-bot (CLR)    → CLR ∈ [0.01, 0.15]              else "fake_likes"/"engagement_pod"
  ├─ Geo matrix        → confidence ≥ 65                 else "location_confidence_low"
  └─ DNS MX            → email domain resolves MX         → PASS → Stage 5
```

- **Sub-modules:** ER math + outlier rejection · CLR anti-bot · Bayesian geo matrix (0–100) ·
  split-contact extraction + DNS MX validation.
- **Output:** verified metrics + geo tier + contact record attached to the lead.
- **Code:** `backend/pipeline/stage4_verification.py`, `backend/utils/dns_resolver.py`.
- **Gotchas:** see [`../AGENTS.md`](../AGENTS.md) §7 and [edge-cases.md](edge-cases.md).

## Stage 5 — Semantic AI classification

Single-pass Groq `llama-3.1-8b-instant` call per finalist (~750 tokens/call, ~300 finalists).

- **Output:** `NicheClassification` — niche, fitness affinity, content type, educational score,
  de-obfuscated email, geo signals, supplement mentions.
- **Resilience:** JSON mode + strict schema; 429 → exponential backoff (`tenacity`); exhausted →
  regex heuristic fallback.
- **Code:** `backend/pipeline/stage5_classification.py`, `backend/providers/groq_classifier.py`.

## Stage 6 — Persistence & serving

- Upsert into Supabase `leads` via `service_role`; advance the lead lifecycle FSM
  (`CANDIDATE → ENRICHED → QUALIFIED → VERIFIED → GOLD`, or `REJECTED`).
- **Serving:** Next.js frontend reads via PostgREST with the `anon` key under RLS; only
  `GOLD`/`VERIFIED` are surfaced.
- **Code:** `backend/pipeline/stage6_persistence.py`, `frontend/src/hooks/useLeads.ts`.

---

## Lead lifecycle state machine

```
                 ┌───────────┐
   discovered →  │ CANDIDATE │
                 └─────┬─────┘
        Stage 3 extract│
                 ┌─────▼─────┐
                 │ ENRICHED  │
                 └─────┬─────┘
     Stage 4 gates pass│                 any gate fails
                 ┌─────▼─────┐            ┌──────────┐
                 │ QUALIFIED │ ─────────► │ REJECTED │ (+ rejected_reason)
                 └─────┬─────┘            └──────────┘
       geo+MX verified │
                 ┌─────▼─────┐
                 │ VERIFIED  │
                 └─────┬─────┘
    Stage 5 niche match│ + high confidence
                 ┌─────▼─────┐
                 │   GOLD    │  ← surfaced on dashboard
                 └───────────┘
```

See [architecture/data-flow.md](architecture/data-flow.md) for the detailed transition rules.
