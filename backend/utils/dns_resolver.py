"""DNS MX-record deliverability check (spec §3.4 contact gate).

Given a contact email's domain, resolve its MX records to decide whether the address is
plausibly deliverable. Used by Stage 4 to mark ``email_deliverable`` on a lead — a lead with a
non-deliverable contact is worth less (may fail the GOLD bar).

Rules:
- Hard timeout of 3.0s per lookup (dnspython) — a hanging resolver must never stall the pipeline.
- Timeout / NXDOMAIN / no-MX are treated as "not deliverable", not as fatal errors.
See docs/edge-cases.md (DNS timeout handling).

TODO(M4): implement with dnspython resolver; cache per-domain results within a run.
"""

from __future__ import annotations

DNS_TIMEOUT_SECONDS = 3.0


def has_mx_record(domain: str) -> bool:
    """Return True if ``domain`` has at least one resolvable MX record within the timeout."""
    raise NotImplementedError("TODO(M4): MX lookup with 3.0s timeout")
