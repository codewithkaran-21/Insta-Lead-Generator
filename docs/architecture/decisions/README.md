# Architecture Decision Records (ADRs)

ADRs capture **load-bearing decisions** and *why* they were made, so future contributors (human
or agent) don't re-litigate settled choices or accidentally undo them. Rationale lives here — not
buried in commit messages.

## Process

1. Copy [`_TEMPLATE.md`](_TEMPLATE.md) to `NNNN-short-title.md` (next number).
2. Fill it in; set status `Proposed`.
3. On acceptance, set status `Accepted` and date it.
4. Superseding a decision: add a new ADR, link it, and mark the old one `Superseded by NNNN`.
5. Reference the ADR from relevant docs/code.

Statuses: `Proposed` · `Accepted` · `Superseded by NNNN` · `Deprecated`.

## Index

| # | Title | Status |
|---|---|---|
| [0001](0001-inverted-etl-verification-engine.md) | Inverted-ETL verification engine (verify, don't bulk-store) | Accepted |
| [0002](0002-provider-abstraction-abc.md) | Provider abstraction via ABCs (zero vendor lock-in) | Accepted |
| [0003](0003-median-er-variance-guard.md) | Median ER + variance guard over arithmetic mean | Accepted |
| [0004](0004-supabase-postgrest-rls.md) | Supabase + PostgREST + RLS as store & API | Accepted |
| [0005](0005-groq-llama-classification.md) | Groq Llama-3.1-8B for semantic classification | Accepted |

> These five are **reverse-engineered from the approved spec** (RFC-2026-08) to document the
> decisions already embedded in it. Future decisions get new ADRs as they arise.
