# ADR-0004: Supabase + PostgREST + RLS as store and API

- **Status:** Accepted
- **Date:** 2026-08-21
- **Deciders:** Project owner (via RFC-2026-08)
- **Related:** [data-model.md](../data-model.md), [security.md](../../security.md), [deployment.md](../../deployment.md), spec §4, §6

## Context

We need a relational store (the lead ledger is inherently tabular and query-heavy), a filterable
read API for the dashboard, access control (public read, restricted write), and low cost. We
don't want to build and host a bespoke API server for V1.

## Decision

Use **Supabase (managed PostgreSQL)** as the system of record. Serve the frontend directly via
**PostgREST** (Supabase's auto-generated REST API) using the **anon** key, with **Row Level
Security** enforcing: anon = read-only `SELECT`, `service_role` = full mutation (backend only).
The backend pipeline writes with the `service_role` key from GitHub Actions.

## Alternatives considered

- **Custom FastAPI + self-hosted Postgres** — full control but more infra, auth, and hosting to
  build/operate; unnecessary for a read-mostly dashboard. Rejected for V1.
- **Firebase/Firestore (NoSQL)** — poor fit for the heavily relational, range-filtered lead
  queries (ER/follower/geo/contact sorts and composite indexes). Rejected.
- **Airtable/Sheets as a DB** — quick but weak on indexes, RLS, and scale. Rejected.

## Consequences

- **Positive:** no API server to build; strong relational querying + indexes for dashboard
  filters; RLS gives a clean public-read/restricted-write boundary; generous free tier.
- **Negative:** free tier **pauses after ~7 days idle** → mitigated by the `heartbeat.yml`
  keepalive cron; care required to never expose `service_role` to the client; RLS policies must
  be reviewed whenever columns are added ([security.md](../../security.md)).
- **Follow-ups:** migrations are immutable once applied (add new files); a `pipeline_runs`
  telemetry table is a likely future addition.
