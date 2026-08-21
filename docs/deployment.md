# Deployment

> Where each piece runs and how it ships. Configuration lives in [configuration.md](configuration.md);
> process/CI in [sdlc.md](sdlc.md).

## Topology

```
GitHub Actions ──run_pipeline.yml──► Backend pipeline ──► Supabase (Postgres + PostgREST)
      │                                                          ▲
      └──heartbeat.yml (cron)──► keepalive ping                  │ PostgREST (anon, RLS)
                                                                 │
Vercel ──► Next.js dashboard ───────────────────────────────────┘
```

## 1. Database (Supabase)

1. Create a Supabase project; note the project URL + `anon` and `service_role` keys.
2. Apply the schema: `supabase/migrations/20260818_init_instaleads.sql`
   - via Supabase CLI: `supabase db push`, **or**
   - paste into the SQL editor.
3. Confirm RLS is enabled and both policies exist (anon read, service_role all).
4. Put keys into GitHub Actions secrets and local `.env`.

Migrations are timestamped and immutable once applied — add a new file for changes.

## 2. Backend pipeline (GitHub Actions)

- Runs on **manual `workflow_dispatch`** via `.github/workflows/run_pipeline.yml` with inputs
  `target_niche`, `target_country`, `min_median_er`.
- Steps: checkout → set up Python 3.11 (pip cache) → `pip install -r backend/requirements.txt`
  → `python backend/run_pipeline.py` with secrets injected as env.
- Required secrets: `APIFY_API_TOKEN`, `SERPER_API_KEY`, `GROQ_API_KEY`, `SUPABASE_URL`,
  `SUPABASE_SERVICE_ROLE_KEY` (+ optional `SLACK_WEBHOOK_URL`).

## 3. Keepalive (GitHub Actions)

- `.github/workflows/heartbeat.yml` runs on a cron (every 3 days) + manual dispatch; issues a
  tiny authenticated `GET` against PostgREST to prevent free-tier pausing.
- Secrets: `SUPABASE_URL`, `SUPABASE_ANON_KEY`.

## 4. Frontend (Vercel)

1. Import the repo into Vercel; set root to `frontend/`.
2. Env vars: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`.
3. Build: `npm run build`; Vercel auto-deploys on push to `main`.
4. The dashboard reads only `GOLD`/`VERIFIED` rows via the RLS-guarded anon key.

## Rollback

- Frontend: redeploy the previous Vercel build.
- Backend: revert the commit and re-dispatch; pipeline runs are idempotent upserts by `username`.
- DB: forward-fix with a new migration (never mutate an applied one).
