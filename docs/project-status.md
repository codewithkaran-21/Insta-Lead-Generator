# Project Status (Current State)

> **Living document.** Update this after every meaningful change. It is the fastest way for a
> human or agent to learn what actually exists right now vs. what is only specified.

- **Last updated:** 2026-08-21
- **Current phase:** Scaffolding (docs + skeleton) — **M0 not yet started for logic**
- **Overall:** 🚧 Documentation complete · Source skeleton in place · **No pipeline logic implemented**

---

## What works right now

- Full documentation set under `docs/`.
- Agent entrypoints: `AGENTS.md`, `CLAUDE.md`.
- Inert source **skeleton**: every module from the spec exists as a stub (`raise NotImplementedError`).
- Full **declarative contracts** are real (not stubs): the Supabase migration, both GitHub
  workflows, `.env.example`, `.gitignore`, starter `requirements.txt`.

**Nothing executes end-to-end yet.** Running `python backend/run_pipeline.py` will raise
`NotImplementedError`.

---

## Component status

Legend: ✅ done · 🟡 partial · ⬜ not started

| Component | Docs | Skeleton | Logic | Tests | Notes |
|---|:---:|:---:|:---:|:---:|---|
| Domain models (`models/domain.py`) | ✅ | ✅ | ⬜ | ⬜ | Signatures per spec §2.1 |
| Provider ABCs (`providers/base.py`) | ✅ | ✅ | ⬜ | ⬜ | Discovery/Extraction/Classification |
| Apify search/hashtag providers | ✅ | ✅ | ⬜ | ⬜ | |
| Serper discovery provider | ✅ | ✅ | ⬜ | ⬜ | |
| Apify profile provider | ✅ | ✅ | ⬜ | ⬜ | |
| Groq classifier provider | ✅ | ✅ | ⬜ | ⬜ | JSON mode |
| Stage 0 seeds | ✅ | ✅ | ⬜ | ⬜ | Control cohort calibration |
| Stage 1 discovery | ✅ | ✅ | ⬜ | ⬜ | |
| Stage 2 pre-filter | ✅ | ✅ | ⬜ | ⬜ | Dedup + max-heap |
| Stage 3 enrichment | ✅ | ✅ | ⬜ | ⬜ | Apify batch hydration |
| Stage 4 verification | ✅ | ✅ | ⬜ | ⬜ | Median ER, CLR, geo, MX |
| Stage 5 classification | ✅ | ✅ | ⬜ | ⬜ | |
| Stage 6 persistence | ✅ | ✅ | ⬜ | ⬜ | Supabase writer + FSM |
| `config.py` / `run_pipeline.py` | ✅ | ✅ | ⬜ | ⬜ | |
| Supabase migration | ✅ | ✅ (full) | ✅ | n/a | DDL + RLS complete (spec §4) |
| GitHub workflows | ✅ | ✅ (full) | ✅ | n/a | heartbeat + run_pipeline |
| Frontend dashboard | ✅ | ✅ | ⬜ | ⬜ | Next.js stubs |

---

## Milestone tracker

See [implementation-plan.md](implementation-plan.md) for milestone detail.

- [ ] **M0** — Repo bootstrap + DB migration applied to a live Supabase project
- [ ] **M1** — Domain models + provider ABCs implemented & unit-tested
- [ ] **M2** — Discovery (Stage 1) + pre-filter (Stage 2)
- [ ] **M3** — Extraction (Stage 3)
- [ ] **M4** — Verification engine (Stage 4) — the core value
- [ ] **M5** — Classification (Stage 5)
- [ ] **M6** — Persistence (Stage 6) + frontend dashboard
- [ ] **M7** — CI/automation wired to real secrets; first full run

---

## Known blockers / open questions

- No live Supabase project / API keys provisioned yet.
- Apify actor output field names should be validated against a real run (spec assumes
  `latestPosts`, `likesCount`, etc.) — confirm before trusting the normalizer.
- Geo-confidence signal weights are initial estimates; need calibration against the Stage 0
  control cohort (see [edge-cases.md](edge-cases.md)).

## Next actions

1. Provision Supabase + API keys; apply `supabase/migrations/20260818_init_instaleads.sql`.
2. Implement `models/domain.py` (M1) — everything depends on it.
3. Implement provider ABCs + one discovery provider end-to-end as a vertical slice.

---

## Changelog

| Date | Change |
|---|---|
| 2026-08-21 | Repo scaffolded: full docs set + source skeleton + declarative contracts. See [session log](session-logs/2026-08-21-docs-scaffolding.md). |
