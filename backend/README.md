# Backend — InstaLeads Verification Engine

Python 3.11 pipeline that discovers, verifies, and classifies Instagram creator leads, then
persists only **VERIFIED / GOLD** records to Supabase. This is the inverted-ETL core: candidates
stream through six stages and are dropped the moment they fail a gate — we store conclusions,
not crawls.

> **Status:** skeleton only. Every module here is a stub (`raise NotImplementedError`) with a
> docstring pointing at the governing spec section. See [../docs/project-status.md](../docs/project-status.md).

## Layout

| Path | Purpose | Spec |
|---|---|---|
| `config.py` | Typed settings / env loader | §2 |
| `run_pipeline.py` | CLI orchestrator entrypoint (Stage 0→6) | §3 |
| `models/domain.py` | Pydantic v2 models + enums (the data contract) | §2.1 |
| `providers/base.py` | Abstract base classes (Discovery/Extraction/Classification) | §2 |
| `providers/*` | Concrete providers (Apify, Serper, Groq) behind the ABCs | §3 |
| `pipeline/stage*.py` | One module per pipeline stage | §3.0–§3.6 |
| `utils/dns_resolver.py` | MX-record deliverability check | §3.4 |
| `utils/logging.py` | structlog configuration | §6 |

## Architectural rules (do not violate)

1. **Never bypass the provider ABCs.** Pipeline stages depend on `providers/base.py`, never on a
   concrete vendor. See [ADR-0002](../docs/architecture/decisions/0002-provider-abstraction-abc.md).
2. **Verification math is deterministic and in-house** (median ER, variance guard, CLR, geo
   score). An LLM never decides pass/fail. See [ADR-0003](../docs/architecture/decisions/0003-median-er-variance-guard.md).
3. **Only GOLD / VERIFIED are persisted and surfaced.** Rejections are logged with a reason, not
   stored as leads.
4. **Cost discipline.** Fail candidates as early and cheaply as possible; the expensive stages
   (profile extraction, LLM) run last, on the fewest rows.

## Setup

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env    # then fill in real keys (never commit .env)
```

## Run

```bash
python run_pipeline.py --niche fitness --country USA
```

(Not yet functional — stubs raise `NotImplementedError`.) See
[../docs/workflow.md](../docs/workflow.md) for what each stage will do and
[../docs/implementation-plan.md](../docs/implementation-plan.md) for build order.
