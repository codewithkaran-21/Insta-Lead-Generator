"""Stage 6 — Persistence (spec §3.6, §4).

Upserts the final VERIFIED / GOLD leads into the Supabase ``leads`` table using the
``service_role`` key (backend-only). Idempotent: re-running a discovery must not create
duplicates — upsert on the natural key (handle) and update mutable metrics.

Only VERIFIED / GOLD rows are written. Rejected candidates are never persisted as leads (their
reasons live in logs / telemetry). See docs/architecture/data-flow.md (idempotency) and
docs/security.md (service_role handling).

Input: classified VerifiedLead objects. Output: rows in ``leads``. Gate: status ∈ {VERIFIED,
GOLD}. Supabase paused/unreachable → retry then dead-letter (docs/edge-cases.md).

TODO(M6): implement upsert via supabase-py; enforce status filter; emit persisted count.
"""

from __future__ import annotations


def persist(leads, client):
    """Upsert VERIFIED/GOLD leads to Supabase; skip anything else."""
    raise NotImplementedError("TODO(M6): Supabase upsert (idempotent on handle)")
