# ADR-0005: Groq Llama-3.1-8B for semantic classification

- **Status:** Accepted
- **Date:** 2026-08-21
- **Deciders:** Project owner (via RFC-2026-08)
- **Related:** [workflow.md](../../workflow.md) (Stage 5), [api-integrations.md](../../api-integrations.md), spec §3.6

## Context

After deterministic verification, finalists need semantic labels that math can't provide: niche
category, fitness affinity, content type (educational vs. promo), educational score, supplement
mentions, extracted geo hints, and de-obfuscation of emails like `john [at] gmail [dot] com`.
This is a bounded, single-pass NLP task over a short bio + a few captions, run on a few hundred
finalists per pipeline run — latency and cost matter.

## Decision

Use **Groq `llama-3.1-8b-instant`** in **JSON mode** with a strict schema and low temperature
(0.1) for a single classification call per finalist. Groq's high throughput (~800 tok/s, low
TTFT) makes ~300 finalists complete in minutes within rate limits.

## Alternatives considered

- **A larger frontier model** — higher quality but slower/pricier and unnecessary for this
  bounded classification. Rejected for the hot path (kept as a possible fallback).
- **Pure regex/keyword heuristics** — cheap and deterministic but can't judge content type or
  de-obfuscate reliably. Kept only as a **fallback** when Groq is rate-limited/unavailable.
- **Local/self-hosted model** — infra overhead not justified for V1 volume. Rejected.

## Consequences

- **Positive:** fast, cheap, structured output; confined to classification so it never affects
  deterministic pass/fail (see ADR-0003); schema-validated via Pydantic.
- **Negative:** external dependency + rate limits (~30 RPM / 30k TPM) → batching + `tenacity`
  backoff; JSON-mode parse failures must be handled → regex fallback; behind
  `ClassificationProvider` (ADR-0002) so it's swappable.
- **Follow-ups:** `OpenAIFallback` provider on the roadmap for resilience
  ([roadmap.md](../../roadmap.md)).
