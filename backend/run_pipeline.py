"""CLI orchestrator — the pipeline entrypoint.

Wires the six stages together (Stage 0 seeds → Stage 6 persistence), injecting the configured
providers, and drives a single end-to-end run. Emits funnel telemetry at each stage boundary
(candidates in → survivors out) per docs/observability.md.

Usage (target state):
    python run_pipeline.py --niche fitness --country USA [--limit N] [--dry-run]

See docs/workflow.md for the runtime flow and spec §3 for stage details.

TODO(M6): assemble stages, add argparse CLI, structured run summary, non-zero exit on fatal
infra failure (so GitHub Actions surfaces it).
"""

from __future__ import annotations


def main() -> int:
    """Parse CLI args, build the pipeline, run it, return a process exit code."""
    raise NotImplementedError("TODO(M6): orchestrate Stage 0 → Stage 6")


if __name__ == "__main__":
    raise SystemExit(main())
