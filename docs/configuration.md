# Configuration Reference

> Every knob that controls the pipeline. Values are loaded by `backend/config.py` into typed
> settings from environment variables. The template is [`../.env.example`](../.env.example);
> copy it to `.env` (git-ignored) and fill in real values. Secret handling: [security.md](security.md).

## Secrets (never commit)

| Env var | Used by | Scope | Notes |
|---|---|---|---|
| `APIFY_API_TOKEN` | Stages 1 & 3 | backend | Apify search/hashtag/profile actors |
| `SERPER_API_KEY` | Stage 1 | backend | Serper.dev dorking (free 2,500 pool) |
| `GROQ_API_KEY` | Stage 5 | backend | Groq Llama classification |
| `SUPABASE_URL` | Stage 6 | backend | Project REST URL |
| `SUPABASE_ANON_KEY` | frontend read | **public** | RLS-guarded read-only |
| `SUPABASE_SERVICE_ROLE_KEY` | Stage 6 write | **backend only** | Full mutation — never ship to frontend |
| `NEXT_PUBLIC_SUPABASE_URL` | frontend | public | Next.js needs `NEXT_PUBLIC_` prefix |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | frontend | public | " |
| `SLACK_WEBHOOK_URL` | alerts | backend | Optional failure notifications |

## Run parameters (`SearchConfiguration`)

| Env var | Default | Meaning |
|---|---|---|
| `TARGET_NICHE` | `fitness` | Creator niche to target |
| `TARGET_COUNTRY` | `USA` | Country target (geo matrix is US-tuned) |
| `MIN_MEDIAN_ER` | `5.0` | Minimum median engagement rate (%) to qualify |
| `MIN_FOLLOWERS` | `10000` | Lower audience band |
| `MAX_FOLLOWERS` | `100000` | Upper audience band |
| `LOG_LEVEL` | `INFO` | `DEBUG\|INFO\|WARNING\|ERROR` |

## Verification thresholds (code constants)

These live in the Stage 4 code, not env, because they encode the product's quality contract.
Change them deliberately and re-validate against the Stage 0 control cohort.

| Constant | Value | Source |
|---|---|---|
| Follower band | `[10_000, 100_000]` | spec §3.5 |
| Recency | last post ≤ 10 days; ≥ 4 posts / 30 days | spec §3.5 |
| Median ER threshold | `5.0%` | spec §3.5 |
| Variance guard | `σ_ER < 0.80 · μ_ER` | spec §3.5 |
| Min posts | `N ≥ 8` | spec §3.5 |
| CLR band | `[0.01, 0.15]` | spec §3.5B |
| Outlier flag | `max_ER ≥ 5 × median_ER` | spec §3.5B |
| Geo confidence | pass ≥ 65; `VERIFIED_US` ≥ 80 | spec §3.5C |
| DNS MX timeout | `3.0s` | spec §3.5D |

## Precedence

`.env` (local) → GitHub Actions secrets (CI/prod). No secret is ever hard-coded. Missing required
vars should fail fast at startup with a clear error (implement in `config.py`).
