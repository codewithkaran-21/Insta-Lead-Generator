# Architecture

Overview and index for InstaLeads' system design. This complements the authoritative blueprint
[`../../implementation_plan(insta leads).md`](../../implementation_plan%28insta%20leads%29.md)
(spec §2) with navigable, focused documents.

## The one-paragraph version

InstaLeads is a **staged pipeline** where every external subsystem (discovery, extraction,
classification, persistence) sits behind an **Abstract Base Class**, so vendors are hot-swappable.
Candidates flow Discovery → Pre-filter → Extraction → **deterministic Verification** →
LLM Classification → Persistence. The verification engine — pure in-house math (median ER +
variance guard, CLR anti-bot, Bayesian geo matrix, DNS MX) — is the architectural centerpiece and
the only place pass/fail is decided. Verified records land in Supabase Postgres and are served to
a Next.js dashboard via PostgREST under Row Level Security.

## Documents

| Doc | Focus |
|---|---|
| [system-overview.md](system-overview.md) | Global data pipeline, layers, and component responsibilities |
| [provider-abstraction.md](provider-abstraction.md) | The ABC layer and how to add/swap a provider |
| [data-model.md](data-model.md) | Pydantic domain models mapped to the Postgres schema |
| [data-flow.md](data-flow.md) | Stage-by-stage data movement + lead lifecycle state machine |
| [decisions/README.md](decisions/README.md) | Architecture Decision Records (ADRs) |

## Key architectural properties

- **Layered & decoupled:** discovery / extraction / verification / classification / persistence /
  presentation are independent; only the pipeline orchestrator knows the order.
- **Zero vendor lock-in:** swapping a provider touches exactly one implementation file.
- **Deterministic core:** verification math is reproducible and testable without network access;
  the LLM is confined to classification.
- **Cost-shaped:** cheap/free discovery and in-memory pre-filtering precede the one paid step
  (extraction).
- **Auditable:** every lead carries provenance, metrics, geo signals, and (if rejected) a reason.
- **Stateless extraction, stateful ledger:** the pipeline is re-runnable; the DB is the system of
  record (idempotent upserts by `username`).

## Component boundaries

```
providers/  ── external adapters (I/O, vendor SDKs)          ← swap here
pipeline/   ── stage logic & orchestration (pure-ish)        ← business rules
models/     ── typed contracts crossing every boundary       ← shared language
utils/      ── cross-cutting (DNS, logging)
frontend/   ── read-only presentation over PostgREST
supabase/   ── schema + access policy (system of record)
```
