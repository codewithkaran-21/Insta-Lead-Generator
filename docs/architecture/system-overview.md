# System Overview

High-level view of the InstaLeads Verification Engine. Detailed math and payloads live in the
spec (§2–§6); this doc explains the shape and the responsibilities.

## Global data pipeline

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                 GLOBAL DATA PIPELINE                                    │
└──────────────────────────────────────────────────────────────────────────────────────┘

 DISCOVERY                 PRE-FILTER                EXTRACTION
 ┌───────────────────┐    ┌─────────────────────┐   ┌─────────────────────┐
 │ • Apify Search    │    │ • Set/DB Dedup      │   │ • ExtractionProvider│
 │ • Apify Hashtag   │──► │ • Regex Email Scan  │──►│ • ApifyProfile (V1) │
 │ • Serper Dorking  │    │ • Priority Max-Heap │   │ • Hydrates 12 posts │
 └───────────────────┘    └─────────────────────┘   └──────────┬──────────┘
                                                                │
        ┌───────────────────────────────────────────────────────┘
        ▼  VERIFICATION ENGINE (DETERMINISTIC IN-HOUSE MATH)
 ┌───────────────────────────────────────────────────────────────────────────┐
 │ • Median ER + variance guard   • CLR anti-bot   • Recency/activity guard   │
 │ • Bayesian geo confidence (0–100)              • DNS MX contact validation │
 └───────────────────────────────┬───────────────────────────────────────────┘
                                  ▼
 SEMANTIC CLASSIFICATION          PERSISTENCE & PRESENTATION
 ┌──────────────────────────┐    ┌───────────────────────────────────────────┐
 │ • Groq Llama-3.1-8B      │    │ • Supabase Postgres (PostgREST + RLS)     │
 │ • Strict JSON schema     │──► │ • Lead lifecycle FSM (CANDIDATE → GOLD)   │
 │ • Niche & content gate   │    │ • Next.js dashboard on Vercel             │
 └──────────────────────────┘    └───────────────────────────────────────────┘
```

## Layers & responsibilities

| Layer | Responsibility | Code |
|---|---|---|
| **Discovery** | High-recall harvest of candidate handles from cheap channels | `providers/apify_search.py`, `apify_hashtag.py`, `serper_discovery.py`; `pipeline/stage1_discovery.py` |
| **Pre-filter** | Zero-cost dedup + signal scan + priority ordering | `pipeline/stage2_prefilter.py` |
| **Extraction** | Turn handles into normalized profiles + recent posts | `providers/apify_profile.py`; `pipeline/stage3_enrichment.py` |
| **Verification** | Deterministic pass/fail on engagement, activity, bot, geo, contact | `pipeline/stage4_verification.py`; `utils/dns_resolver.py` |
| **Classification** | LLM niche/content/affinity labeling + email de-obfuscation | `providers/groq_classifier.py`; `pipeline/stage5_classification.py` |
| **Persistence** | Upsert + lifecycle FSM into Postgres | `pipeline/stage6_persistence.py` |
| **Presentation** | Read-only filterable dashboard | `frontend/src/*` |
| **Orchestration** | Wire stages, config, logging | `run_pipeline.py`, `config.py`, `utils/logging.py` |

## Data-shape handoffs

```
CandidateHandle[]  →(prefilter)→  CandidateHandle[] (sorted)  →(extract)→  RawProfile[]
      →(verify)→  VerifiedLead (partial, gated)  →(classify)→  + NicheClassification
      →(persist)→  leads row (status ∈ {GOLD, VERIFIED, REJECTED})
```

See [data-model.md](data-model.md) for the field-level contracts and [data-flow.md](data-flow.md)
for the transitions and gate logic.

## Non-functional characteristics

- **Reproducible:** verification is deterministic; same input → same verdict.
- **Resilient:** per-record failures don't abort the batch; see [../edge-cases.md](../edge-cases.md).
- **Observable:** structured funnel logs at each stage; see [../observability.md](../observability.md).
- **Cheap:** paid extraction runs on a pruned, prioritized subset only.
