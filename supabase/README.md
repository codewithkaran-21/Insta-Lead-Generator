# Supabase

Supabase (managed PostgreSQL) is the system of record for verified leads and the read API for
the dashboard (via PostgREST). See [ADR-0004](../docs/architecture/decisions/0004-supabase-postgrest-rls.md),
[../docs/architecture/data-model.md](../docs/architecture/data-model.md), and
[../docs/deployment.md](../docs/deployment.md).

## Migrations

| File | Purpose |
|---|---|
| [`migrations/20260818_init_instaleads.sql`](migrations/20260818_init_instaleads.sql) | Initial schema: enums, `leads` table, indexes, RLS policies (spec §4) |

**Migrations are immutable once applied.** To change the schema, add a *new* timestamped file —
never edit an applied one.

## Applying the initial migration

Either paste the SQL into the Supabase **SQL Editor**, or use the Supabase CLI:

```bash
supabase db push
```

## Access model (RLS)

Row Level Security is **enabled** on `leads`:

- `anon` → `SELECT` only (the dashboard's browser client).
- `service_role` → full mutation (the backend pipeline, from GitHub Actions).

The `service_role` key is backend-only and must never reach the frontend. See
[../docs/security.md](../docs/security.md).

## Keepalive

The free tier pauses after ~7 days idle. [`.github/workflows/heartbeat.yml`](../.github/workflows/heartbeat.yml)
pings PostgREST every 3 days to keep the project awake.
