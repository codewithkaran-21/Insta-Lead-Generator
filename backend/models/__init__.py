"""Domain models package.

Import the canonical Pydantic models and enums from ``domain`` so callers can do
``from models import VerifiedLead, LeadStatus``.
"""

from .domain import (
    CandidateHandle,
    ContactType,
    LeadStatus,
    LocationTier,
    NicheClassification,
    RawPost,
    RawProfile,
    VerifiedLead,
)

__all__ = [
    "LeadStatus",
    "LocationTier",
    "ContactType",
    "CandidateHandle",
    "RawPost",
    "RawProfile",
    "NicheClassification",
    "VerifiedLead",
]
