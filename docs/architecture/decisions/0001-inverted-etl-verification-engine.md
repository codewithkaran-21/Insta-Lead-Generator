# ADR-0001: Inverted-ETL verification engine (verify, don't bulk-store)

- **Status:** Accepted
- **Date:** 2026-08-21
- **Deciders:** Project owner (via RFC-2026-08)
- **Related:** [project-context.md](../../project-context.md), [system-overview.md](../system-overview.md), spec §1.2

## Context

Traditional creator-discovery platforms crawl and store massive unverified datasets, then filter
at query time. This yields stale data, high storage/compute cost, and low precision (the four
failures in [project-context.md](../../project-context.md) §1). We need outreach-grade precision
on a small budget, not breadth.

## Decision

We invert the ETL: **ingest cheap candidate streams, verify each candidate on the fly with
deterministic math + a single LLM classification, and persist only verified, outreach-grade
records.** The datastore is a curated ledger, not a crawl dump. The extraction layer is stateless
and hot-swappable.

## Alternatives considered

- **Bulk crawl + store + filter later** — high cost, stale data, and the mean-ER/geo problems
  persist because filtering happens on old aggregates. Rejected.
- **Buy an enterprise vendor feed** — $8k–18k/yr upfront, still suffers mean-ER/geo distortions,
  and no control over verification logic. Rejected (it's the problem we're solving).

## Consequences

- **Positive:** small, high-precision, current dataset; low storage; full control over quality
  gates; cost scales with verified output, not crawl size.
- **Negative:** re-verification is needed to keep data fresh (a refresh/decay job — see
  [roadmap.md](../../roadmap.md)); throughput is bounded by extraction cost, so pre-filtering
  discipline (ADR-adjacent, Stage 2) is essential.
- **Follow-ups:** the deterministic verification engine (ADR-0003) becomes the system's core and
  must be rigorously tested.
