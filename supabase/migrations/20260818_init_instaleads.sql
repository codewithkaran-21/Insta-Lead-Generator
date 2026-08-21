-- supabase/migrations/20260818_init_instaleads.sql
-- Initial schema for the InstaLeads Verification Engine (spec §4).
-- Contract: this is the authoritative shape of the `leads` table. The backend Pydantic
-- VerifiedLead model (backend/models/domain.py) and the frontend query layer must stay in sync
-- with it. See docs/architecture/data-model.md.
--
-- Migrations are immutable once applied — to change the schema, add a NEW timestamped file.

-- Enable cryptographic extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Clean existing types if rebuilding
DROP TYPE IF EXISTS lead_status CASCADE;
DROP TYPE IF EXISTS location_tier CASCADE;
DROP TYPE IF EXISTS contact_type_enum CASCADE;

-- 1. Create Enums
CREATE TYPE lead_status AS ENUM (
    'CANDIDATE',
    'ENRICHED',
    'QUALIFIED',
    'VERIFIED',
    'GOLD',
    'REJECTED'
);

CREATE TYPE location_tier AS ENUM (
    'VERIFIED_US',
    'PROBABLE_US',
    'UNKNOWN'
);

CREATE TYPE contact_type_enum AS ENUM (
    'email',
    'phone',
    'website',
    'linktree'
);

-- 2. Create Master Leads Table
CREATE TABLE leads (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username                TEXT UNIQUE NOT NULL,
    full_name               TEXT,
    profile_url             TEXT GENERATED ALWAYS AS ('https://instagram.com/' || username) STORED,

    -- Finite State Machine
    status                  lead_status NOT NULL DEFAULT 'CANDIDATE',
    rejected_reason         TEXT,
    status_updated_at       TIMESTAMPTZ DEFAULT NOW(),

    -- Audience Volume
    followers               INTEGER,
    following               INTEGER,
    post_count              INTEGER,

    -- Engagement Metrics (Deterministic In-House Math)
    mean_er                 NUMERIC(5,2),
    median_er               NUMERIC(5,2),
    min_er                  NUMERIC(5,2),
    max_er                  NUMERIC(5,2),
    er_std_dev              NUMERIC(5,2),
    posts_analyzed          SMALLINT,
    er_computed_at          TIMESTAMPTZ,

    -- Cadence & Activity Metrics
    last_post_at            TIMESTAMPTZ,
    last_post_days_ago      INTEGER,
    posts_last_30d          SMALLINT,

    -- Platform Profile Metadata
    is_business             BOOLEAN DEFAULT FALSE,
    ig_category             TEXT,
    ig_verified_badge       BOOLEAN DEFAULT FALSE,

    -- AI Classification Metadata
    niche_category          TEXT,
    content_type            TEXT,
    educational_score       NUMERIC(3,2),
    fitness_affinity        BOOLEAN,
    has_supplement_mentions BOOLEAN DEFAULT FALSE,

    -- Split Contact Record
    contact_type            contact_type_enum,
    contact_value           TEXT,
    contact_source          TEXT,
    contact_domain_mx       BOOLEAN DEFAULT FALSE,
    contact_confidence      NUMERIC(3,2),

    -- Geographic Confidence Matrix
    country_target          VARCHAR(3) DEFAULT 'USA',
    country_confidence      SMALLINT CHECK (country_confidence >= 0 AND country_confidence <= 100),
    country_tier            location_tier,
    location_signals        JSONB DEFAULT '{}'::jsonb,

    -- Data Quality Markers
    comment_like_ratio      NUMERIC(5,4),
    comment_diversity_ok    BOOLEAN DEFAULT TRUE,
    has_outlier_posts       BOOLEAN DEFAULT FALSE,

    -- Raw Data Audit Trail
    bio_text                TEXT,
    external_url            TEXT,
    discovered_via          TEXT NOT NULL,
    enriched_via            TEXT DEFAULT 'apify_profile',

    -- System Timestamps
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    enriched_at             TIMESTAMPTZ,
    verified_at             TIMESTAMPTZ,
    last_refreshed_at       TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Composite & Filtering Indexes
CREATE INDEX idx_leads_status ON leads (status);
CREATE INDEX idx_leads_median_er ON leads (median_er DESC NULLS LAST);
CREATE INDEX idx_leads_followers ON leads (followers);
CREATE INDEX idx_leads_country_conf ON leads (country_confidence DESC NULLS LAST);
CREATE INDEX idx_leads_contact_conf ON leads (contact_confidence DESC NULLS LAST);
CREATE INDEX idx_leads_fitness_affinity ON leads (fitness_affinity) WHERE fitness_affinity = TRUE;
CREATE INDEX idx_leads_gold_search ON leads (status, median_er DESC) WHERE status = 'GOLD';

-- 4. Enable Row Level Security (RLS)
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow Public Anonymous Read"
ON leads FOR SELECT
TO anon
USING (true);

CREATE POLICY "Allow Service Role Full Mutation"
ON leads FOR ALL
TO service_role
USING (true)
WITH CHECK (true);
