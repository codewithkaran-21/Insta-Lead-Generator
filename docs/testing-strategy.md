# Testing Strategy

> The verification engine is the product's value, so **deterministic math tests are the highest
> priority**. External services are always mocked in tests.

## Test pyramid

```
        ┌───────────────────────────┐
        │  E2E (few, manual/dispatch)│  full pipeline against a test Supabase project
        ├───────────────────────────┤
        │ Integration (mocked I/O)   │  stage wiring, normalizers, persistence upserts
        ├───────────────────────────┤
        │      Unit (many)           │  ER math, CLR, geo matrix, contact/DNS, pre-filter heap
        └───────────────────────────┘
```

Tooling: `pytest` (backend), fixtures for canned `RawProfile`/`RawPost` payloads. Frontend:
component/hook tests as the dashboard grows.

## 1. Unit tests (Stage 4 first)

Pure functions with hand-built fixtures — **no network**. Cover:

- **Median ER:** odd vs. even `N`; `N = 8` (pass boundary) and `N = 7` (reject).
- **Variance guard:** account with one viral post → `σ_ER ≥ 0.80·μ_ER` → reject; steady account → pass.
- **CLR:** `CLR < 0.01` (fake likes), `CLR > 0.15` (pod), in-band pass; `L_total = 0` guard.
- **Geo matrix:** each signal in isolation and summed; tier thresholds (65 / 80); non-US → low.
- **Contact/DNS:** business field vs. bio regex vs. external URL precedence; role-prefix penalty;
  MX timeout → `mx=False`, confidence 0.20 (mock `dns.resolver`).
- **Pre-filter:** dedup (DB + in-batch), priority scoring, max-heap ordering.

## 2. Integration tests (mocked external I/O)

- Apify normalizer: real-shaped JSON → valid `RawProfile`; malformed → dead-letter + `REJECTED`.
- Groq classifier: mocked JSON response → `NicheClassification`; 429 → backoff; parse fail → fallback.
- Persistence: upsert + FSM transitions; only `GOLD`/`VERIFIED` are query-visible.

## 3. Control-cohort validation (Stage 0)

Run the engine against the hand-verified seed accounts (spec §3.1). **Known-good positives must
not be rejected.** This is the regression guard against threshold drift when IG's algorithm
shifts — a failure here means recalibrate, not loosen (see [edge-cases.md](edge-cases.md)).

## 4. E2E (sparingly)

A `workflow_dispatch` run against a **test** Supabase project with a tiny query, asserting rows
land with correct statuses and appear on the dashboard. Not run on every PR (costs credits).

## Conventions

- Deterministic: no reliance on wall-clock/live data in unit tests; inject timestamps.
- Name tests by behavior: `test_variance_guard_rejects_single_viral_post`.
- Every bug fix adds a regression test.
- Aim for high coverage on `pipeline/` and `providers/`; the frontend is lighter.
