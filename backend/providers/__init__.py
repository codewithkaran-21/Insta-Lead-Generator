"""Providers package — vendor integrations behind abstract interfaces.

Concrete providers (Apify, Serper, Groq) implement the ABCs in ``base.py``. Pipeline stages
depend only on those ABCs, so a vendor can be swapped without touching stage code.
See docs/architecture/provider-abstraction.md and ADR-0002.
"""

# from .base import DiscoveryProvider, ExtractionProvider, ClassificationProvider

__all__: list[str] = []  # TODO(M1): export ABCs + concrete providers
