"""Stage 4 — Deterministic verification (spec §3.4). THE CORE. No LLM here.

Computes the verification metrics in-house and applies the hard gates. An account passes only if
it clears every gate. All math is deterministic and auditable (ADR-0003).

Metrics & gates (see docs/architecture/data-flow.md, docs/glossary.md):
  - median_er: median engagement rate over the last N posts (median, NOT mean — resists viral
    spikes). Gate: median_er ≥ MIN_MEDIAN_ER.
  - variance guard: σ_ER < 0.80 · μ_ER — rejects erratic/spike-driven engagement.
  - N ≥ 8 posts (else insufficient data).
  - CLR (comment/like ratio) ∈ [0.01, 0.15] — outside this band flags pods/bots/fake likes.
  - outlier flag: max ER ≥ 5 × median → flag for review.
  - geo_confidence_score (0–100): Bayesian multi-signal (bio geo, post location tags, language,
    posting timezone, currency, TLD). Gate: ≥ 65 to pass; ≥ 80 = VERIFIED_US.
  - contact deliverability: DNS MX check on the contact email (utils/dns_resolver, 3.0s timeout).

Input: EnrichedProfile. Output: VerifiedLead (status VERIFIED/GOLD) or REJECTED + reason.
Cost: ~free (pure computation). Gate: the union of the above.

TODO(M4): implement each metric + gate exactly per spec §3.4; unit-test the math first.
"""

from __future__ import annotations


def verify(profile, settings):
    """Compute metrics + apply all gates. Return a VerifiedLead or a rejection with reason."""
    raise NotImplementedError("TODO(M4): deterministic verification math + gates")
