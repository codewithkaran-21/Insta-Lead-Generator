"""Stage 2 — Pre-filter (spec §3.2).

The first, cheapest gate. Drops obvious non-fits *before* paying for profile extraction:
follower band (MIN_FOLLOWERS ≤ followers ≤ MAX_FOLLOWERS), obvious spam/brand/bulk signals, and
any handle-level heuristics available without a full scrape.

Input: CandidateLead stream. Output: QUALIFIED subset. Cost: cheap. Gate: hard follower band +
heuristics. Rejections carry a ``rejected_reason`` and are logged, not stored.

TODO(M2): implement follower-band + heuristic filters; emit survivors count.
"""

from __future__ import annotations


def prefilter(candidates, settings):
    """Yield candidates that pass the cheap gate; log the rest with a reason."""
    raise NotImplementedError("TODO(M2): follower band + heuristic pre-filter")
