"""Serper.dev Google-dorking discovery provider (spec §3.1).

Uses Serper's Google Search API to run dork queries (e.g. site:instagram.com "fitness coach"
"@gmail.com" USA) that surface handles with public contact intent. Implements
``DiscoveryProvider``; parses SERP results → ``CandidateLead``.

Gotcha: respect Serper quota; handle empty result pages gracefully. See docs/edge-cases.md.

TODO(M2): implement discover(); construct dork templates per niche/country.
"""

from __future__ import annotations

from .base import DiscoveryProvider


class SerperDiscoveryProvider(DiscoveryProvider):
    def discover(self, niche: str, country: str):
        raise NotImplementedError("TODO(M2): Serper dork queries → CandidateLead")
