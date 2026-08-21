# InstaLeads Verification Engine

> An **inverted-ETL lead verification engine** that discovers outreach-grade Instagram creators
> in the US fitness / performance / sports-nutrition verticals — by running rigorous
> **deterministic math** and a **single-pass LLM classifier** over cheap candidate streams,
> and committing only verified records to an auditable Postgres ledger.

[![Status](https://img.shields.io/badge/status-scaffolding-blue)](docs/project-status.md)
[![Docs](https://img.shields.io/badge/docs-AGENTS.md-informational)](AGENTS.md)

---

## Why

Commercial influencer platforms distort engagement rates with arithmetic means (one viral reel
skews everything), hallucinate geography from language ("English = US"), serve stale/zombie
contacts, and charge $8k–18k/yr upfront. InstaLeads fixes each of these with **outlier-resistant
median ER + variance guards**, a **multi-signal Bayesian geo-confidence matrix**, **live DNS MX
contact validation**, and low-cost hot-swappable discovery. Full rationale:
[`docs/project-context.md`](docs/project-context.md).

## How it works

```
Discovery → Pre-filter → Extraction → Verification → Classification → Persistence → Dashboard
 Apify/       in-memory   Apify        deterministic   Groq Llama      Supabase       Next.js
 Serper       dedup+heap   profiles     math + geo+MX   (JSON mode)     (RLS)          on Vercel
```

See the end-to-end [`docs/workflow.md`](docs/workflow.md) and
[`docs/architecture/`](docs/architecture/README.md).

## Project status

🚧 **Scaffolding phase.** This repository currently contains complete **documentation** and an
**inert source skeleton** (stub files). No pipeline logic is implemented yet. Track progress in
[`docs/project-status.md`](docs/project-status.md).

## Quickstart (once implemented)

```bash
# Backend
cd backend && pip install -r requirements.txt
cp ../.env.example ../.env    # fill in secrets
python run_pipeline.py

# Frontend
cd frontend && npm install && npm run dev
```

## Documentation

| Doc | What it covers |
|---|---|
| [AGENTS.md](AGENTS.md) | Canonical guide for AI coding agents (start here) |
| [docs/README.md](docs/README.md) | Full documentation index |
| [docs/project-context.md](docs/project-context.md) | Domain, users, goals, constraints |
| [docs/architecture/](docs/architecture/README.md) | System design, data model, decisions |
| [docs/workflow.md](docs/workflow.md) | The runtime pipeline (Stage 0→6) |
| [docs/implementation-plan.md](docs/implementation-plan.md) | Phased build plan |
| [docs/edge-cases.md](docs/edge-cases.md) | Failure modes & self-healing |
| [`implementation_plan(insta leads).md`](implementation_plan%28insta%20leads%29.md) | Authoritative technical blueprint (RFC-2026-08) |

## License

See [LICENSE](LICENSE).
