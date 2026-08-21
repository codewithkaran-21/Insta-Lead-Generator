# Documentation Index

Welcome to the InstaLeads Verification Engine documentation. This `docs/` tree is the
**navigable layer** over the authoritative technical blueprint
[`implementation_plan(insta leads).md`](../implementation_plan%28insta%20leads%29.md) (RFC-2026-08).

If you are an AI coding agent, read [`../AGENTS.md`](../AGENTS.md) first.

---

## Start here

| Doc | Purpose |
|---|---|
| [project-context.md](project-context.md) | **Why** this exists — domain problem, users, goals, non-goals, constraints |
| [project-status.md](project-status.md) | **Current state** — living progress tracker (what's built vs. not) |
| [glossary.md](glossary.md) | Domain & technical terms (ER, CLR, MX, GOLD, …) |

## Architecture

| Doc | Purpose |
|---|---|
| [architecture/README.md](architecture/README.md) | Architecture overview & index |
| [architecture/system-overview.md](architecture/system-overview.md) | High-level system + global data pipeline |
| [architecture/provider-abstraction.md](architecture/provider-abstraction.md) | The swappable provider ABC layer |
| [architecture/data-model.md](architecture/data-model.md) | Pydantic models ↔ Postgres schema |
| [architecture/data-flow.md](architecture/data-flow.md) | Stage-by-stage flow + lead lifecycle FSM |
| [architecture/decisions/README.md](architecture/decisions/README.md) | Architecture Decision Records (ADRs) |

## Build & operate

| Doc | Purpose |
|---|---|
| [workflow.md](workflow.md) | The runtime pipeline (Stage 0→6) end-to-end |
| [implementation-plan.md](implementation-plan.md) | Phased milestone build plan |
| [sdlc.md](sdlc.md) | Dev lifecycle: branching, commits, PRs, CI/CD, DoD |
| [testing-strategy.md](testing-strategy.md) | Test pyramid & deterministic-math testing |
| [api-integrations.md](api-integrations.md) | External service contracts (Apify, Serper, Groq, Supabase) |
| [configuration.md](configuration.md) | Env vars & settings reference |
| [deployment.md](deployment.md) | Vercel, GitHub Actions, Supabase setup |
| [observability.md](observability.md) | Structured logging & funnel metrics |
| [security.md](security.md) | RLS, secrets, PII/ToS, rate-limit etiquette |
| [edge-cases.md](edge-cases.md) | Failure modes, self-healing & incident playbooks |
| [roadmap.md](roadmap.md) | Future providers & expansion |

## Process

| Doc | Purpose |
|---|---|
| [session-logs/README.md](session-logs/README.md) | Session-log convention (agents append per work session) |

---

## Documentation conventions

- **The spec is authoritative.** When a doc and `implementation_plan(insta leads).md` conflict,
  the spec wins — then fix the doc.
- **Keep docs scannable.** Prefer tables, diagrams, and cross-links over long prose.
- **`project-status.md` and `session-logs/` are living** — update them as work happens.
- **Decisions get ADRs.** Don't bury rationale in commit messages.
- Absolute dates only (e.g. "2026-08-21"), never "yesterday" / "last week".
