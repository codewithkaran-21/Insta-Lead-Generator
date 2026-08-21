"""Provider abstract base classes — the vendor-neutral seam (spec §2, ADR-0002).

Three capability interfaces the pipeline depends on. Concrete implementations live alongside
this module. Swapping a vendor (e.g. Apify → HikerAPI) means adding a new subclass here and
changing one line of wiring in ``run_pipeline.py`` — never editing a pipeline stage.

Contract rules:
- Providers return **domain models** (see models/domain.py), never raw vendor JSON. Each
  provider owns the normalization from its vendor's schema to our types.
- Providers raise typed, retryable errors on transient failure; retry/backoff policy
  (tenacity) is applied here, not in stages. See docs/edge-cases.md.

TODO(M1): finalize method signatures against the concrete providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

# from typing import Iterable
# from models.domain import CandidateLead, EnrichedProfile, ClassificationResult


class DiscoveryProvider(ABC):
    """Surface candidate handles from a niche/country signal (search, hashtag, dork)."""

    @abstractmethod
    def discover(self, niche: str, country: str):  # -> Iterable[CandidateLead]
        """Yield ``CandidateLead`` objects. See spec §3.1."""
        raise NotImplementedError


class ExtractionProvider(ABC):
    """Fetch a full profile + recent posts for a candidate handle."""

    @abstractmethod
    def extract(self, handle: str):  # -> EnrichedProfile
        """Return an ``EnrichedProfile``. See spec §3.3."""
        raise NotImplementedError


class ClassificationProvider(ABC):
    """Assign semantic labels to a verified finalist (LLM). Never decides pass/fail."""

    @abstractmethod
    def classify(self, profile):  # (EnrichedProfile) -> ClassificationResult
        """Return a ``ClassificationResult``. See spec §3.5."""
        raise NotImplementedError
