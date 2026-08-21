"""Apify Instagram *hashtag* discovery provider (spec §3.1).

Wraps the Apify hashtag actor to surface candidates posting under niche-relevant hashtags.
Implements ``DiscoveryProvider``. Normalizes actor output → ``CandidateLead``.

TODO(M2): implement discover(); dedupe handles against other discovery providers upstream.
"""

from __future__ import annotations

from .base import DiscoveryProvider


class ApifyHashtagProvider(DiscoveryProvider):
    def discover(self, niche: str, country: str):
        raise NotImplementedError("TODO(M2): Apify hashtag actor → CandidateLead")
