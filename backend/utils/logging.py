"""structlog configuration (spec §6, docs/observability.md).

Central setup for structured JSON logging so every stage emits machine-parseable events with a
consistent schema (run_id, stage, event, counts). One-time ``configure_logging()`` call at
startup; modules then use ``structlog.get_logger()``.

Key event families to standardize (see docs/observability.md):
  - stage.start / stage.end with candidates_in / survivors_out (the funnel)
  - lead.rejected with rejected_reason
  - provider.error / provider.retry
  - dead_letter with payload reference

TODO(M0): implement configure_logging(); JSON renderer in prod, console renderer in dev; bind
run_id globally.
"""

from __future__ import annotations


def configure_logging(level: str = "INFO", *, json_output: bool = True) -> None:
    """Configure structlog processors + stdlib logging once at process start."""
    raise NotImplementedError("TODO(M0): configure structlog")


def get_logger(name: str | None = None):
    """Return a bound structlog logger."""
    raise NotImplementedError("TODO(M0): return structlog.get_logger()")
