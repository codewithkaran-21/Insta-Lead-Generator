# Roadmap

> Directional, not committed. V1 scope is defined by [implementation-plan.md](implementation-plan.md);
> this captures what's deliberately deferred and where the design already leaves seams.

## Near-term (post-V1)

- **Alternate extraction providers** behind the existing `ExtractionProvider` ABC:
  `HikerAPIProvider`, `CurlCffiProvider` (self-hosted residential proxy pool), `Scrapfly`.
  Goal: reduce per-profile cost / remove single-vendor dependency. See
  [architecture/provider-abstraction.md](architecture/provider-abstraction.md).
- **Classification fallback provider** (`OpenAIFallback`) behind `ClassificationProvider` for
  when Groq is rate-limited/unavailable — beyond the current regex fallback.
- **Persisted run telemetry:** a `pipeline_runs` table + funnel dashboard fed by the structured
  logs in [observability.md](observability.md).
- **Threshold auto-calibration** from the Stage 0 control cohort instead of static constants.

## Mid-term

- **Multi-country geo matrices** (UK/CA/AU) — generalize the US-tuned matrix into pluggable
  country profiles; `country_target` already exists in the schema.
- **Additional verticals** beyond fitness/supplements (the niche is parameterized).
- **Contact enrichment:** website crawl for contact pages when bio email is absent/role-based.
- **Scheduled discovery runs** (cron) with incremental dedup against the growing ledger.

## Long-term / exploratory

- **Refresh & decay:** periodically re-verify existing leads; expire stale `GOLD` rows.
- **Outreach status tracking** columns (contacted / replied / converted) — careful to keep this a
  lead engine, not a full CRM (a stated non-goal — revisit intentionally).
- **Audience-quality signals** if a cost-effective demographics source appears.

## Explicitly out of scope (see [project-context.md](project-context.md) §6)

- Becoming a bulk creator database or general scraper.
- Sending outreach / email delivery.
- Paid audience-demographics APIs in V1.

## Design seams already in place

The V1 architecture anticipates most of the above: provider ABCs (swap vendors), a
`country_target` column (multi-country), a parameterized `SearchConfiguration` (new niches), and
structured logging (telemetry dashboards). Extending rarely requires touching the verification
core.
