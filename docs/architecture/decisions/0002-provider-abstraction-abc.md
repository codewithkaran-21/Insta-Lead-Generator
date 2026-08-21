# ADR-0002: Provider abstraction via ABCs (zero vendor lock-in)

- **Status:** Accepted
- **Date:** 2026-08-21
- **Deciders:** Project owner (via RFC-2026-08)
- **Related:** [provider-abstraction.md](../provider-abstraction.md), spec §2

## Context

Discovery, extraction, and classification all depend on third-party services (Apify, Serper,
Groq) whose pricing, availability, and ToS can change. Coupling pipeline logic directly to a
vendor SDK would make switching providers a costly rewrite and would make the pipeline hard to
test without live network calls.

## Decision

Every external subsystem is accessed through an **Abstract Base Class**: `DiscoveryProvider`,
`ExtractionProvider`, `ClassificationProvider` (in `providers/base.py`). Concrete implementations
normalize vendor output into shared domain models. Pipeline code depends only on the interfaces.
Swapping a vendor means adding one implementation file and a config selection — nothing
downstream changes.

## Alternatives considered

- **Direct SDK calls in pipeline stages** — simplest to write first, but couples business logic
  to vendors, blocks easy testing, and makes cost experiments painful. Rejected.
- **A single generic HTTP client with per-vendor config** — under-abstracts; response shapes
  differ too much to normalize via config alone. Rejected.

## Consequences

- **Positive:** zero vendor lock-in; pipeline stages are unit-testable with fakes (no network);
  new discovery channels/extractors added independently; cost/quality experiments are cheap.
- **Negative:** an extra layer of indirection and the discipline to keep vendor quirks inside
  implementations; a factory/selection mechanism is needed in `config.py`/`run_pipeline.py`.
- **Follow-ups:** planned providers (`HikerAPIProvider`, `CurlCffiProvider`, `OpenAIFallback`) —
  see [roadmap.md](../../roadmap.md).
