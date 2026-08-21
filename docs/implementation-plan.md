# Implementation Plan (Phased Build)

> The **execution order** for building InstaLeads. This is the "how we get there" companion to
> the authoritative technical blueprint
> [`../implementation_plan(insta leads).md`](../implementation_plan%28insta%20leads%29.md), which
> holds the exhaustive detail (code, math, DDL) for each component referenced below.

Each milestone lists **scope**, **deliverables**, **exit criteria**, and the governing spec
section. Build in order — later milestones depend on earlier ones. Track live progress in
[project-status.md](project-status.md).

---

## Guiding principles

- **Vertical slices first:** get one candidate all the way through the pipeline early, then
  broaden — rather than perfecting one stage in isolation.
- **Everything behind an ABC** (spec §2) — no direct provider calls from pipeline code.
- **Test the math deterministically** (Stage 4) with fixtures; don't rely on live scrapes.
- **Only merge with tests + docs updated** (see [sdlc.md](sdlc.md)).

---

## M0 — Bootstrap & database

- **Scope:** provision Supabase; apply the schema; wire config/secrets.
- **Deliverables:** live Supabase project; `supabase/migrations/20260818_init_instaleads.sql`
  applied; `backend/config.py` loading typed settings from `.env`; `structlog` configured.
- **Exit criteria:** `leads` table + enums + indexes + RLS exist; a trivial `run_pipeline.py`
  can read/write a test row via `service_role`.
- **Spec:** §4, §2.1, §6.

## M1 — Domain models & provider interfaces

- **Scope:** implement all Pydantic models and the provider ABCs.
- **Deliverables:** `models/domain.py` (enums + `CandidateHandle`, `RawPost`, `RawProfile`,
  `NicheClassification`, `VerifiedLead`); `providers/base.py` (`DiscoveryProvider`,
  `ExtractionProvider`, `ClassificationProvider`).
- **Exit criteria:** models validate example payloads; ABCs importable; unit tests green.
- **Spec:** §2, §2.1.

## M2 — Discovery + pre-filter

- **Scope:** Stage 1 channels + Stage 2 in-memory pruning.
- **Deliverables:** `apify_search.py`, `apify_hashtag.py`, `serper_discovery.py`,
  `stage1_discovery.py`, `stage2_prefilter.py` (dedup + regex + max-heap priority).
- **Exit criteria:** a keyword/hashtag/dork query returns deduped, priority-sorted
  `CandidateHandle`s; ~60–70% of a raw pool is pruned before extraction.
- **Spec:** §3.2, §3.3.

## M3 — Extraction

- **Scope:** Stage 3 batch hydration behind `ExtractionProvider`.
- **Deliverables:** `apify_profile.py` (raw JSON → `RawProfile`/`RawPost` normalizer),
  `stage3_enrichment.py`; dead-letter handling for schema drift.
- **Exit criteria:** a batch of usernames returns validated `RawProfile`s; malformed items go to
  `logs/dead_letter.jsonl` and are marked `REJECTED(schema_parse_error)`.
- **Spec:** §3.4, §5.

## M4 — Verification engine (core value)

- **Scope:** Stage 4 deterministic gates.
- **Deliverables:** `stage4_verification.py` (follower band, activity, median ER + variance
  guard, CLR anti-bot, geo Bayesian matrix, split-contact), `utils/dns_resolver.py` (MX with
  3.0s timeout).
- **Exit criteria:** each gate has unit tests including boundary + adversarial cases (viral
  spike, engagement pod, fake likes, non-US, dead domain); Stage 0 controls pass.
- **Spec:** §3.5 (all sub-modules), §5.

## M5 — Classification

- **Scope:** Stage 5 Groq semantic classification.
- **Deliverables:** `groq_classifier.py` (JSON mode, strict schema), `stage5_classification.py`;
  `tenacity` backoff on 429; regex fallback.
- **Exit criteria:** finalists get a valid `NicheClassification`; rate-limit + parse-failure
  paths tested with mocks.
- **Spec:** §3.6, §5.

## M6 — Persistence & dashboard

- **Scope:** Stage 6 writer + FSM; Next.js dashboard.
- **Deliverables:** `stage6_persistence.py` (upsert + status transitions); frontend
  `useLeads.ts`, `LeadsTable`, `FilterSidebar`, `LeadDetailDrawer`, `StatusBadge`,
  `ExportCsvButton`, `lib/supabase.ts`.
- **Exit criteria:** verified leads persist with correct status; dashboard reads `GOLD`/`VERIFIED`
  via PostgREST under RLS; CSV export works.
- **Spec:** §3.7, §6.

## M7 — CI / automation & first full run

- **Scope:** wire GitHub Actions to real secrets; end-to-end run.
- **Deliverables:** `run_pipeline.yml` executes on dispatch; `heartbeat.yml` keeps Supabase warm;
  Slack failure alerts.
- **Exit criteria:** a dispatched run produces `GOLD` leads visible on the deployed dashboard;
  telemetry/funnel metrics logged (see [observability.md](observability.md)).
- **Spec:** §7, §6.

---

## Dependency graph

```
M0 ──► M1 ──► M2 ──► M3 ──► M4 ──► M5 ──► M6 ──► M7
                 │                        ▲
                 └──── frontend can start ┘ (against seed data after M0/M6 schema)
```
