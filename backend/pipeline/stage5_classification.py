"""Stage 5 — Classification (spec §3.5).

Runs the ``ClassificationProvider`` (Groq Llama, JSON mode) over the verified finalists to add
semantic labels: niche, content type, educational score, supplement mentions, extracted geo
hints, and a de-obfuscated contact email (e.g. "john [at] gmail [dot] com" → "john@gmail.com").

This annotates only accounts that already PASSED Stage 4. It never changes pass/fail (ADR-0003,
ADR-0005). Groq 429 → backoff/batching; JSON parse failure → regex fallback.

Input: VerifiedLead (VERIFIED). Output: VerifiedLead enriched with ClassificationResult; may
promote to GOLD per business rules. Cost: low (fast LLM, few hundred rows).

TODO(M5): implement classification pass; merge labels onto the lead; apply GOLD promotion rule.
"""

from __future__ import annotations


def classify(leads, classifier):
    """Attach semantic labels to verified leads; promote to GOLD where criteria are met."""
    raise NotImplementedError("TODO(M5): LLM classification + GOLD promotion")
