"""Stage 0 — Seeds & calibration (spec §3.0).

Builds the query seeds (niche/country → hashtags, dork templates, seed accounts) that feed
discovery, and assembles a small **control cohort** of known-good and known-bad accounts used to
validate that the verification thresholds behave (see docs/testing-strategy.md, Stage 0
control-cohort validation).

This stage produces configuration/inputs, not leads.

TODO(M2): implement seed generation; load/define the calibration cohort.
"""

from __future__ import annotations


def build_seeds(niche: str, country: str):
    """Return the discovery seeds (hashtags, dork queries, seed handles) for the run."""
    raise NotImplementedError("TODO(M2): generate seeds per spec §3.0")
