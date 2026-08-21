# Data Model

> The typed contracts that cross every boundary, and how they map to the Postgres schema.
> Pydantic models: spec §2.1 / `backend/models/domain.py`. DDL: spec §4 /
> `supabase/migrations/20260818_init_instaleads.sql`.

## Enums

| Enum | Values |
|---|---|
| `LeadStatus` | `CANDIDATE`, `ENRICHED`, `QUALIFIED`, `VERIFIED`, `GOLD`, `REJECTED` |
| `LocationTier` | `VERIFIED_US`, `PROBABLE_US`, `UNKNOWN` |
| `ContactType` | `email`, `phone`, `website`, `linktree` |

These exist both as Python enums and as Postgres `ENUM` types (`lead_status`, `location_tier`,
`contact_type_enum`).

## Model progression through the pipeline

```
CandidateHandle ──► RawProfile (+ RawPost[]) ──► VerifiedLead ◄── NicheClassification
   (discovery)          (extraction)              (verification + persistence)   (classification)
```

| Model | Created in | Purpose |
|---|---|---|
| `CandidateHandle` | Stage 1–2 | A discovered username + provenance + cheap hints + priority score |
| `RawPost` | Stage 3 | One normalized recent post (likes/comments/timestamp/caption/location) |
| `RawProfile` | Stage 3 | Normalized profile + up to 12 `RawPost` |
| `NicheClassification` | Stage 5 | LLM labels: niche, affinity, content type, educational score, de-obfuscated email, geo signals |
| `VerifiedLead` | Stage 4–6 | The full persisted record; maps 1:1 to a `leads` row |

## `VerifiedLead` ↔ `leads` table (grouped)

| Group | Fields |
|---|---|
| **Identity** | `username` (unique), `full_name`, `profile_url` (generated), `id` (uuid) |
| **State machine** | `status`, `rejected_reason`, `status_updated_at` |
| **Audience** | `followers`, `following`, `post_count` |
| **Engagement (in-house math)** | `mean_er`, `median_er`, `min_er`, `max_er`, `er_std_dev`, `posts_analyzed`, `er_computed_at` |
| **Activity** | `last_post_at`, `last_post_days_ago`, `posts_last_30d` |
| **Platform metadata** | `is_business`, `ig_category`, `ig_verified_badge` |
| **AI classification** | `niche_category`, `content_type`, `educational_score`, `fitness_affinity`, `has_supplement_mentions` |
| **Split contact** | `contact_type`, `contact_value`, `contact_source`, `contact_domain_mx`, `contact_confidence` |
| **Geo matrix** | `country_target`, `country_confidence` (0–100), `country_tier`, `location_signals` (JSONB) |
| **Anomaly** | `comment_like_ratio`, `comment_diversity_ok`, `has_outlier_posts` |
| **Audit / provenance** | `bio_text`, `external_url`, `discovered_via`, `enriched_via`, timestamps (`created_at`, `enriched_at`, `verified_at`, `last_refreshed_at`) |

## Notable schema details

- `profile_url` is a **generated stored column**: `'https://instagram.com/' || username`.
- `country_confidence` has a `CHECK (0..100)`.
- `location_signals` is **JSONB** — the per-signal breakdown from the geo matrix (auditable).
- Numeric precisions: ER fields `NUMERIC(5,2)`; `comment_like_ratio` `NUMERIC(5,4)`; scores
  `NUMERIC(3,2)`.
- Indexes optimize the dashboard's filters: `status`, `median_er DESC`, `followers`,
  `country_confidence`, `contact_confidence`, partial indexes on `fitness_affinity = TRUE` and
  `status = 'GOLD'`.

## Validation notes

- `CandidateHandle.username` is normalized (lowercased, `@`/whitespace stripped) via a Pydantic
  validator — do the same anywhere usernames enter the system to keep dedup correct.
- Follower/like/comment counts are `ge=0` constrained.
- `educational_score` ∈ `[0.0, 1.0]`.

See [data-flow.md](data-flow.md) for how a record moves between statuses.
