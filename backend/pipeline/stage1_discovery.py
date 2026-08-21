"""Stage 1 — Discovery (spec §3.1).

Fans out across the configured ``DiscoveryProvider`` implementations (Apify search, Apify
hashtag, Serper dorks), merges and de-duplicates their output into a single stream of
``CandidateLead`` objects.

Input: seeds (Stage 0). Output: deduped CandidateLead stream. Cost: moderate (discovery API
calls). Gate: none yet — just collection + dedupe.

TODO(M2): implement fan-out + dedupe; emit funnel metric (candidates discovered).
"""

from __future__ import annotations


def discover(seeds, providers):
    """Merge candidates from all discovery providers; dedupe by handle."""
    raise NotImplementedError("TODO(M2): multi-provider discovery + dedupe")
