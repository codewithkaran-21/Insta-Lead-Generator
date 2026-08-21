# ADR-0003: Median ER + variance guard over arithmetic mean

- **Status:** Accepted
- **Date:** 2026-08-21
- **Deciders:** Project owner (via RFC-2026-08)
- **Related:** [workflow.md](../../workflow.md) (Stage 4), [edge-cases.md](../../edge-cases.md), spec §3.5A

## Context

Engagement rate is the primary quality signal, but it is heavily skewed by outliers. A single
viral reel (e.g. 500k views / 40k likes on a 20k-follower account) produces a ~200% post-ER that
drags the arithmetic mean far above the creator's true baseline (which may be < 1%). Naive
mean-based filters therefore promote spike-driven accounts that won't perform for outreach.

## Decision

Qualify creators on the **median** per-post ER, not the mean, and add a **variance guard**:
reject when `σ_ER ≥ 0.80 × μ_ER` (engagement dominated by a single post). Require **N ≥ 8** posts
for the statistics to be trustworthy, and flag `has_outlier_posts` when `max ER ≥ 5 × median`.

## Alternatives considered

- **Arithmetic mean ER** — the industry default; distorted by outliers. Rejected (it's the
  problem).
- **Trimmed mean / winsorization** — reduces outlier impact but needs a cutoff parameter and is
  less intuitive to explain/audit than the median. Rejected for V1 (median is simpler and robust).
- **Mean with a hard cap per post** — arbitrary cap; median achieves robustness without one.

## Consequences

- **Positive:** robust to viral spikes; rewards consistent engagement; explainable and auditable;
  cheap to compute deterministically.
- **Negative:** requires ≥ 8 recent posts (very new accounts can't qualify — acceptable);
  thresholds (5.0%, 0.80, N≥8) are calibration points that can drift with IG's algorithm →
  validated against the Stage 0 control cohort.
- **Follow-ups:** consider threshold auto-calibration from controls ([roadmap.md](../../roadmap.md)).
