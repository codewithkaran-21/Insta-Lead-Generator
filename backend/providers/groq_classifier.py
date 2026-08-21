"""Groq Llama classification provider (spec §3.5, ADR-0005).

Wraps Groq ``llama-3.1-8b-instant`` in JSON mode to assign semantic labels to a verified
finalist: niche, content type, educational score, supplement mentions, extracted geo hints, and
de-obfuscated contact email. Implements ``ClassificationProvider``.

Hard rule: this NEVER decides verification pass/fail — that is deterministic (ADR-0003). It only
annotates leads that already passed Stage 4.

Gotchas: Groq 429 rate limits → tenacity backoff + batching; JSON-mode parse failures → regex
fallback. Low temperature (0.1), strict schema validated via Pydantic. See docs/edge-cases.md.

TODO(M5): implement classify(); enforce output schema; fallback path on parse failure.
"""

from __future__ import annotations

from .base import ClassificationProvider


class GroqClassifier(ClassificationProvider):
    def classify(self, profile):
        raise NotImplementedError("TODO(M5): Groq JSON-mode classification → ClassificationResult")
