"""Apify Instagram *search* discovery provider (spec §3.1).

Wraps the Apify search actor to surface candidate handles for a niche/country query.
Implements ``DiscoveryProvider``. Normalizes actor output → ``CandidateLead``.

Gotcha: Apify actor field names must be confirmed against a real run before trusting the
normalizer (see docs/session-logs open questions). Handle Apify 402 (out of credit) per
docs/edge-cases.md.

TODO(M2): implement discover(); apply tenacity retry on transient actor errors.
"""

from __future__ import annotations

from .base import DiscoveryProvider


class ApifySearchProvider(DiscoveryProvider):
    def discover(self, niche: str, country: str):
        raise NotImplementedError("TODO(M2): Apify search actor → CandidateLead")
