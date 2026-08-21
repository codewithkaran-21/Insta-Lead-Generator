# Data Flow & Lead Lifecycle

> How a record moves through the pipeline and between statuses. Runtime narrative:
> [../workflow.md](../workflow.md). Field contracts: [data-model.md](data-model.md).

## End-to-end data movement

```
Serper/Apify search+hashtag
        │  raw handles (+ engagement/geo hints)
        ▼
CandidateHandle[]                                   status: (none yet — in memory)
        │  Stage 2: dedup + regex + priority heap
        ▼
CandidateHandle[] (pruned, sorted)                  ~30–40% of raw survives
        │  Stage 3: batch extraction (top ~1–1.5k)
        ▼
RawProfile[] (+ RawPost[])                           status: CANDIDATE → ENRICHED
        │  Stage 4: deterministic gates
        ├─ fail any gate ─────────────► REJECTED (+ rejected_reason)   [persisted, audited]
        ▼
VerifiedLead (metrics/geo/contact set)               status: ENRICHED → QUALIFIED → VERIFIED
        │  Stage 5: LLM classification
        ▼
VerifiedLead (+ NicheClassification)                 niche/affinity/content set
        │  Stage 6: upsert + final gate
        ▼
leads row                                            status: VERIFIED → GOLD (if niche matches)
        │
        ▼  PostgREST (anon, RLS) — only GOLD/VERIFIED
Next.js dashboard
```

## Lead lifecycle state machine

```
                 ┌───────────┐
   discovered →  │ CANDIDATE │  handle known; not yet extracted
                 └─────┬─────┘
   Stage 3 extract ok  │
                 ┌─────▼─────┐
                 │ ENRICHED  │  RawProfile hydrated
                 └─────┬─────┘
   Stage 4 core gates  │  (followers, activity, ER+variance, CLR)
     pass              │            fail → ┌──────────┐
                 ┌─────▼─────┐             │ REJECTED │ + rejected_reason
                 │ QUALIFIED │             └──────────┘
                 └─────┬─────┘             (terminal; audited, not surfaced)
   geo ≥ 65 & contact  │
     verified          │
                 ┌─────▼─────┐
                 │ VERIFIED  │  contactable + located
                 └─────┬─────┘
   Stage 5 niche match │  fitness affinity + confidence
                 ┌─────▼─────┐
                 │   GOLD    │  surfaced on dashboard
                 └───────────┘
```

## Transition rules

| From | To | Condition |
|---|---|---|
| — | `CANDIDATE` | discovered + survives pre-filter |
| `CANDIDATE` | `ENRICHED` | extraction returns a valid `RawProfile` |
| `CANDIDATE`/any | `REJECTED` | extraction schema parse fail (`schema_parse_error`), private/empty |
| `ENRICHED` | `QUALIFIED` | passes follower band, activity, median-ER + variance, CLR gates |
| `ENRICHED` | `REJECTED` | any core gate fails (reason recorded) |
| `QUALIFIED` | `VERIFIED` | geo confidence ≥ 65 **and** contact resolved (MX-aware) |
| `QUALIFIED` | `REJECTED` | `location_confidence_low` (or no usable contact) |
| `VERIFIED` | `GOLD` | Stage 5 confirms niche/fitness affinity + confidence |
| `VERIFIED` | `VERIFIED` | stays (surfaced) if classification is inconclusive but gates passed |

`REJECTED` is terminal for a run; re-discovery on a later run can re-enter via upsert.

## Rejection reasons (canonical)

`followers_out_of_bounds`, `inactive_profile`, `insufficient_posts`,
`median_er_below_threshold`, `sigma_er_variance_exceeded`, `fake_likes`,
`engagement_pod_detected`, `location_confidence_low`, `schema_parse_error`,
`private_or_empty`. See [../edge-cases.md](../edge-cases.md) for detection + handling.

## Idempotency

Persistence upserts by `username` (unique). Re-running the pipeline refreshes metrics and
timestamps rather than duplicating leads; `last_refreshed_at` tracks the latest pass.
