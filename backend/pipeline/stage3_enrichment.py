"""Stage 3 — Enrichment / extraction (spec §3.3).

Runs the ``ExtractionProvider`` (Apify profile-scraper) on each qualified candidate to fetch the
full profile and the most recent N posts. This is the most expensive discovery-side call, so it
only runs on Stage 2 survivors.

Input: QUALIFIED candidates. Output: EnrichedProfile objects. Cost: high (per-profile scrape).
Gate: drop private/empty profiles and those with < 8 recent posts (insufficient data for a
stable median ER). IG schema drift → dead-letter (docs/edge-cases.md).

TODO(M3): implement extraction loop; enforce N ≥ 8; route failures to dead-letter.
"""

from __future__ import annotations


def enrich(candidates, extractor):
    """Extract full profiles + recent posts; drop insufficient/private profiles."""
    raise NotImplementedError("TODO(M3): profile extraction + insufficiency gate")
