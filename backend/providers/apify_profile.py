"""Apify Instagram *profile-scraper* extraction provider (spec §3.3).

Wraps the Apify profile-scraper actor to fetch a full profile plus the most recent N posts for
a candidate handle. Implements ``ExtractionProvider``. Normalizes actor output →
``EnrichedProfile`` (followers, bio, external URL, business category, and per-post
likes/comments/caption/timestamp/location).

This is the most expensive discovery-side call — it runs only on candidates that survived the
cheap pre-filter (Stage 2). Handle private/empty profiles and IG schema drift → dead-letter,
per docs/edge-cases.md.

TODO(M3): implement extract(); ensure N ≥ 8 posts returned or flag insufficient-data.
"""

from __future__ import annotations

from .base import ExtractionProvider


class ApifyProfileProvider(ExtractionProvider):
    def extract(self, handle: str):
        raise NotImplementedError("TODO(M3): Apify profile actor → EnrichedProfile")
