# AGENTS.md

> **This is the canonical guide for AI coding agents working in this repository.**
> It follows the open [AGENTS.md](https://agents.md) standard and is read by Codex, Cursor,
> Zed, GitHub Copilot, Windsurf, Gemini CLI, and others. `CLAUDE.md` imports this file, so
> there is one source of truth. Human contributors: start with [`README.md`](README.md).

---

## 1. Project overview

**InstaLeads Verification Engine** is an **inverted-ETL lead verification pipeline** for
discovering outreach-grade Instagram creators in the US fitness / performance / sports-nutrition
verticals. Instead of storing massive unverified crawls, it ingests cheap candidate streams,
runs **rigorous deterministic math + statistics locally**, applies a **single-pass LLM
classification**, and commits **only verified, outreach-grade records** to an auditable
Postgres ledger surfaced through a Next.js dashboard.

The pipeline is a linear, staged flow:

```
Discovery → Pre-filter → Extraction → Verification (deterministic) → Classification (LLM) → Persistence → Dashboard
 Stage 1     Stage 2       Stage 3        Stage 4                       Stage 5              Stage 6      (frontend)
```

The full technical blueprint is [`implementation_plan(insta leads).md`](implementation_plan%28insta%20leads%29.md) ("RFC-2026-08").
It is the **authoritative** detailed spec. The `docs/` tree is the navigable, machine-readable
layer on top of it.

## 2. Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Pydantic v2, `httpx`, `apify-client`, `groq`, `dnspython`, `langdetect`, `structlog`, `tenacity` |
| Datastore | Supabase (PostgreSQL + PostgREST + Row Level Security) |
| Discovery | Apify actors (search, hashtag), Serper.dev (Google dorking) |
| Extraction | Apify `instagram-profile-scraper` (behind a swappable ABC) |
| Classification | Groq `llama-3.1-8b-instant` (JSON mode) |
| Frontend | Next.js (App Router), TypeScript, `@supabase/supabase-js` |
| CI / automation | GitHub Actions (pipeline runner + Supabase keepalive) |
| Deploy | Vercel (frontend), GitHub Actions (backend runs) |

## 3. Repository map

| Path | Purpose |
|---|---|
| `backend/models/` | Pydantic domain models & enums (spec §2.1) |
| `backend/providers/` | Swappable external-service adapters behind ABCs (`base.py`) |
| `backend/pipeline/` | The 7 pipeline stages (`stage0`–`stage6`) |
| `backend/utils/` | DNS MX resolver, structlog config |
| `backend/config.py` | Typed settings / env loader |
| `backend/run_pipeline.py` | CLI orchestrator entrypoint |
| `frontend/src/` | Next.js dashboard (components, hooks, Supabase client) |
| `supabase/migrations/` | PostgreSQL DDL + RLS policies (spec §4) |
| `.github/workflows/` | CI: `run_pipeline.yml`, `heartbeat.yml` |
| `docs/` | All documentation — **read [`docs/README.md`](docs/README.md) first** |

## 4. Setup, build, test, run

```bash
# Backend
cd backend
python -m venv .venv && source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
cp ../.env.example ../.env                                # then fill in secrets
python run_pipeline.py                                    # run the full pipeline (CLI)
pytest                                                    # run backend tests (once added)
```

```bash
# Frontend
cd frontend
npm install
npm run dev            # local dev server
npm run build          # production build
```

```bash
# Database (Supabase CLI, or paste the migration into the SQL editor)
supabase db push       # applies supabase/migrations/*.sql
```

> ⚠️ These commands assume the implementation is filled in. Today the source files are
> **stubs** (`raise NotImplementedError`). See [`docs/project-status.md`](docs/project-status.md)
> for what actually works right now.

## 5. Code style & conventions

- **Python:** full type hints, Pydantic v2 models for every boundary payload, `snake_case`,
  small pure functions for math, `structlog` for all logging (never `print`). No bare `except:`.
- **TypeScript:** Next.js App Router, functional components, typed props, colocated hooks.
- **Formatting:** keep to the existing style of the file you're editing.
- **Commits:** Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`).
- **No secrets in code or git.** Everything sensitive is an env var (see [`docs/configuration.md`](docs/configuration.md)).

## 6. Architectural rules (non-negotiable)

1. **Never bypass the provider ABCs.** All external calls go through
   `backend/providers/base.py` interfaces. Swapping Apify → HikerAPI must touch exactly one
   implementation file. See [`docs/architecture/provider-abstraction.md`](docs/architecture/provider-abstraction.md).
2. **Verification math is deterministic and in-house.** No LLM decides pass/fail on
   engagement, geo, or contact validity. The LLM only *classifies* niche/content.
3. **Only `GOLD` / `VERIFIED` leads reach the dashboard.** Everything else is `REJECTED`
   with a `rejected_reason`. Never surface unverified rows.
4. **Cost discipline:** pre-filter in memory (Stage 2) *before* spending Apify extraction
   credits (Stage 3). Never extract the full candidate pool.
5. **Every rejection is auditable** — persist the reason, don't silently drop.

## 7. Verification-engine gotchas (read before touching Stage 4)

- **Median, not mean, ER.** A single viral reel inflates the mean; use the outlier-resistant
  median. See [ADR-0003](docs/architecture/decisions/0003-median-er-variance-guard.md).
- **Variance guard:** reject if `σ_ER ≥ 0.80 × mean_ER` (single-viral-post accounts).
- **Minimum sample:** require `N ≥ 8` posts or the ER stats are untrustworthy.
- **CLR bounds:** comment/like ratio must be in `[0.01, 0.15]` (fake-likes vs. engagement pods).
- **Geo is Bayesian, multi-signal** (0–100), never binary "English = US". Threshold ≥ 65.
- **DNS MX lookups must have a timeout** (`lifetime=3.0`) or the pipeline hangs.
- **Groq must be called in JSON mode** with a strict schema; parse failures → regex fallback.

Full failure catalogue: [`docs/edge-cases.md`](docs/edge-cases.md).

## 8. Security

- Secrets via env only; `service_role` key is server-side (GitHub Actions) — **never** shipped
  to the frontend. Frontend uses the `anon` key governed by RLS.
- RLS: anon = read-only `SELECT`; `service_role` = full mutation. See [`docs/security.md`](docs/security.md).
- Respect provider rate limits and ToS; the pipeline is a verification tool, not a mass scraper.

## 9. Where to look

| I need to understand… | Read |
|---|---|
| Why this project exists / the domain | [`docs/project-context.md`](docs/project-context.md) |
| The end-to-end runtime pipeline | [`docs/workflow.md`](docs/workflow.md) |
| System architecture & components | [`docs/architecture/`](docs/architecture/README.md) |
| Data models & DB schema | [`docs/architecture/data-model.md`](docs/architecture/data-model.md) |
| What's built vs. not (current state) | [`docs/project-status.md`](docs/project-status.md) |
| The phased build plan | [`docs/implementation-plan.md`](docs/implementation-plan.md) |
| Failure modes & edge cases | [`docs/edge-cases.md`](docs/edge-cases.md) |
| Dev process (git, PRs, CI, DoD) | [`docs/sdlc.md`](docs/sdlc.md) |
| External API contracts | [`docs/api-integrations.md`](docs/api-integrations.md) |
| Decisions & their rationale | [`docs/architecture/decisions/`](docs/architecture/decisions/README.md) |

## 10. Working agreements for agents

After any **meaningful** change:
1. Update [`docs/project-status.md`](docs/project-status.md) (the living state tracker).
2. Add a session entry under [`docs/session-logs/`](docs/session-logs/README.md) using the template.
3. If you made a load-bearing decision, add an ADR under `docs/architecture/decisions/`.
4. Keep this file and the docs in sync when you change structure or conventions.
