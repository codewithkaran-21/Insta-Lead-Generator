"""Domain models & enums — the data contract for the whole pipeline (spec §2.1).

These Pydantic v2 models are the single source of truth for the shape of data as it flows
through the stages. A lead is progressively enriched:

    CandidateHandle      # Stage 1 discovery — bare handle + source signal
      → RawProfile       # Stage 3 extraction — full profile + recent posts
        → VerifiedLead   # Stage 4/5 — metrics computed, geo scored, classified

``NicheClassification`` is the Stage 5 LLM output that is folded into ``VerifiedLead``.

``VerifiedLead`` maps 1:1 to the ``leads`` table (see docs/architecture/data-model.md and
supabase/migrations/20260818_init_instaleads.sql).

Design rules:
- Every field that reaches Postgres is typed and validated here first.
- Enums below MUST stay in sync with the Postgres enum types in the migration.
- Verification metrics (median ER, variance, CLR, geo score) are computed in Stage 4 and stored
  on ``VerifiedLead`` — never recomputed by the frontend.

Fidelity note: this file follows spec §2.1 verbatim, with two deliberate, safer deviations:
  1. It drops the spec's unused ``HttpUrl``/``EmailStr`` imports (every URL/email field is a
     plain ``str``; ``EmailStr`` would also pull in ``email-validator`` for nothing).
  2. ``default_factory`` timestamps use a timezone-aware ``_utcnow`` instead of the deprecated,
     naive ``datetime.utcnow`` — the Postgres columns are ``TIMESTAMPTZ``.
The spec's stub-only ``NicheCategory``/``ContentType`` enums are intentionally omitted: spec §2.1
models ``niche_category``/``content_type`` as free ``str`` (stored as ``TEXT``).
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


def _utcnow() -> datetime:
    """Timezone-aware UTC now. Used for ``default_factory`` timestamps.

    Preferred over ``datetime.utcnow`` (deprecated in 3.12 and naive); the ``leads`` table
    stores these as ``TIMESTAMPTZ``, which wants aware datetimes.
    """
    return datetime.now(timezone.utc)


class LeadStatus(str, Enum):
    """Lifecycle state of a lead. See docs/architecture/data-flow.md (FSM).

    Values MUST match the Postgres ``lead_status`` enum in the migration.
    """

    CANDIDATE = "CANDIDATE"      # discovered, not yet enriched
    ENRICHED = "ENRICHED"        # profile + posts extracted
    QUALIFIED = "QUALIFIED"      # passed cheap pre-filters
    VERIFIED = "VERIFIED"        # passed deterministic verification
    GOLD = "GOLD"                # top tier (e.g. VERIFIED_US + contactable)
    REJECTED = "REJECTED"        # failed a gate; carries rejected_reason


class LocationTier(str, Enum):
    """Bucketed geo-confidence outcome (Stage 4). Score is 0–100; ≥65 passes, ≥80 = VERIFIED_US.

    Values MUST match the Postgres ``location_tier`` enum in the migration.
    """

    VERIFIED_US = "VERIFIED_US"
    PROBABLE_US = "PROBABLE_US"
    UNKNOWN = "UNKNOWN"


class ContactType(str, Enum):
    """Contact channel. Values MUST match the Postgres ``contact_type_enum`` in the migration."""

    EMAIL = "email"
    PHONE = "phone"
    WEBSITE = "website"
    LINKTREE = "linktree"


class CandidateHandle(BaseModel):
    """Stage 1 output: a discovered handle plus the signal that surfaced it.

    Minimal — no verified metrics yet. ``seed_*_hint`` fields carry the free engagement numbers
    some discovery channels return (e.g. Apify hashtag posts) so Stage 2 can prioritize before
    paying for extraction. ``priority_score`` is assigned by the Stage 2 pre-filter heap.
    """

    username: str = Field(..., min_length=1, max_length=30)
    discovered_via: str
    raw_snippet: Optional[str] = None
    seed_likes_hint: Optional[int] = Field(default=None, ge=0)
    seed_comments_hint: Optional[int] = Field(default=None, ge=0)
    has_email_signal: bool = False
    has_us_geo_signal: bool = False
    priority_score: float = 0.0

    @field_validator("username")
    @classmethod
    def clean_username(cls, v: str) -> str:
        return v.lower().strip().lstrip("@")


class RawPost(BaseModel):
    """One recent post as normalized from the extraction provider (Stage 3).

    The raw material for Stage 4's engagement math. ``likes_count``/``comments_count`` feed ER
    and CLR; ``timestamp`` feeds the activity/cadence guard; ``location_name`` is a geo signal.
    """

    id: str
    shortcode: str
    caption: Optional[str] = ""
    likes_count: int = Field(default=0, ge=0)
    comments_count: int = Field(default=0, ge=0)
    timestamp: datetime
    is_video: bool = False
    location_name: Optional[str] = None


class RawProfile(BaseModel):
    """Stage 3 output: full profile plus the last N posts needed for verification.

    Normalized from vendor JSON by the extraction provider (spec §3.3). Consumed by Stage 4
    (deterministic verification) which turns it into a ``VerifiedLead``.
    """

    username: str
    full_name: Optional[str] = None
    followers_count: int = Field(default=0, ge=0)
    following_count: int = Field(default=0, ge=0)
    posts_count: int = Field(default=0, ge=0)
    biography: str = ""
    is_business: bool = False
    category: Optional[str] = None
    external_url: Optional[str] = None
    public_email: Optional[str] = None
    public_phone: Optional[str] = None
    latest_posts: List[RawPost] = Field(default_factory=list)


class NicheClassification(BaseModel):
    """Stage 5 output: semantic labels only — never a pass/fail gate decision.

    Produced by the LLM classifier (Groq JSON mode) and folded into ``VerifiedLead``.
    ``educational_score`` is bounded [0, 1]; ``deobfuscated_email`` un-mangles bio emails like
    ``john [at] gmail [dot] com`` that the Stage 2 regex cannot catch.
    """

    niche_category: str
    fitness_affinity: bool
    content_type: str
    educational_score: float = Field(..., ge=0.0, le=1.0)
    deobfuscated_email: Optional[str] = None
    extracted_geo_signals: List[str] = Field(default_factory=list)
    has_supplement_mentions: bool = False


class VerifiedLead(BaseModel):
    """Terminal record persisted to the ``leads`` table.

    Carries every computed verification metric (engagement stats, CLR, geo confidence, contact
    validity) plus classification labels and a full audit trail. See
    docs/architecture/data-model.md for the field-by-field mapping to Postgres. Only ``VERIFIED``
    / ``GOLD`` rows are surfaced on the dashboard.
    """

    id: Optional[str] = None
    username: str
    full_name: Optional[str] = None
    profile_url: str
    status: LeadStatus
    rejected_reason: Optional[str] = None
    status_updated_at: datetime = Field(default_factory=_utcnow)

    # Follower metrics
    followers: int
    following: int
    post_count: int

    # Verified Engagement Statistics
    mean_er: float
    median_er: float
    min_er: float
    max_er: float
    er_std_dev: float
    posts_analyzed: int
    er_computed_at: datetime = Field(default_factory=_utcnow)

    # Activity Metrics
    last_post_at: Optional[datetime] = None
    last_post_days_ago: Optional[int] = None
    posts_last_30d: int

    # Instagram Profile Info
    is_business: bool
    ig_category: Optional[str] = None
    ig_verified_badge: bool = False

    # AI Classification
    niche_category: Optional[str] = None
    content_type: Optional[str] = None
    educational_score: Optional[float] = None
    fitness_affinity: Optional[bool] = None
    has_supplement_mentions: bool = False

    # Split Contact Model
    contact_type: Optional[ContactType] = None
    contact_value: Optional[str] = None
    contact_source: Optional[str] = None
    contact_domain_mx: bool = False
    contact_confidence: float = 0.0

    # Geographic Confidence Matrix
    country_target: str = "USA"
    country_confidence: int = Field(..., ge=0, le=100)
    country_tier: LocationTier
    location_signals: Dict[str, Any] = Field(default_factory=dict)

    # Bot & Anomaly Detection
    comment_like_ratio: float
    comment_diversity_ok: bool = True
    has_outlier_posts: bool = False

    # Audit & Provenance
    bio_text: str
    external_url: Optional[str] = None
    discovered_via: str
    enriched_via: str = "apify_profile"
    created_at: datetime = Field(default_factory=_utcnow)
    enriched_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    last_refreshed_at: datetime = Field(default_factory=_utcnow)
