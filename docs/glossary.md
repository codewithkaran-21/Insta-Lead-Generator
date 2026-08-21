# Glossary

Domain and technical terms used across InstaLeads. Definitions reflect how the terms are used in
this project specifically.

| Term | Definition |
|---|---|
| **ER (Engagement Rate)** | `((likes + comments) / followers) × 100` for a post. Reported per-post and aggregated. |
| **Median ER** | The middle ER across a creator's recent posts. Outlier-resistant — the primary qualification metric (vs. mean, which a viral post distorts). |
| **Mean ER (μ_ER)** | Arithmetic average ER. Recorded for context but **not** the gate; used with σ in the variance guard. |
| **σ_ER (ER std. dev.)** | Standard deviation of per-post ER. Feeds the variance guard. |
| **Variance guard** | Rejection rule `σ_ER < 0.80 × μ_ER` — filters accounts whose engagement is driven by a single viral post. |
| **CLR (Comment/Like Ratio)** | `total_comments / total_likes` across analyzed posts. Must sit in `[0.01, 0.15]`: below = fake likes; above = engagement pod. |
| **Engagement pod** | A ring of accounts that reciprocally comment to fake engagement — flagged by abnormally high CLR. |
| **Outlier post** | A post with `ER ≥ 5 × median ER`; sets `has_outlier_posts = True`. |
| **Geo-confidence matrix** | Multi-signal Bayesian score (0–100) estimating US location from bio geo terms, post location tags, language, posting-time timezone, currency symbols, and URL TLD. |
| **Location tier** | `VERIFIED_US` (≥80), `PROBABLE_US` (≥65), `UNKNOWN` (<65). Qualification requires ≥ 65. |
| **DNS MX record** | Mail-exchange DNS record. A contact email's domain must resolve MX to be considered deliverable. |
| **Split-contact model** | Contact stored as a typed triple (type/value/source) with confidence, rather than a single ambiguous field. |
| **Role inbox** | Generic addresses (`info@`, `contact@`, …) — valid but lower-confidence than a personal address. |
| **Lead lifecycle / FSM** | `CANDIDATE → ENRICHED → QUALIFIED → VERIFIED → GOLD`, or `REJECTED`. See [architecture/data-flow.md](architecture/data-flow.md). |
| **GOLD** | Fully verified, classified, contactable lead — the only tier (with VERIFIED) surfaced on the dashboard. |
| **Inverted ETL** | This project's thesis: verify candidate streams on the fly and store only verified records, rather than storing bulk crawls and filtering later. |
| **Provider ABC** | Abstract Base Class defining a swappable interface (Discovery/Extraction/Classification) so vendors can be replaced without touching pipeline code. |
| **Pre-filter** | Stage 2 in-memory pruning (dedup + regex + priority heap) that removes ~60–70% of noise before paid extraction. |
| **Priority heap** | Max-heap ordering candidates by `email(40) + geo(30) + engagement(≤30)` so extraction credits go to the best prospects first. |
| **Dead-letter** | `logs/dead_letter.jsonl` — raw payloads that failed schema parsing, retained for inspection/replay. |
| **Seed / control cohort** | Hand-verified known-good accounts used to calibrate thresholds and guard against false-negative drift (Stage 0). |
| **PostgREST** | Supabase's auto-generated REST API over Postgres that the frontend queries directly. |
| **RLS (Row Level Security)** | Postgres access control; here, anon = read-only, service_role = full mutation. |
| **RawProfile / RawPost** | Pydantic models for normalized extraction output before verification. |
| **VerifiedLead** | The full persisted lead record (metrics + geo + contact + classification + audit). |
| **TTFT** | Time to first token — Groq latency metric (~120ms) relevant to classification throughput. |
