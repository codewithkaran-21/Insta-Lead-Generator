# Observability — Logging, Telemetry & Metrics

> The pipeline emits **structured JSON logs** via `structlog` for real-time funnel monitoring and
> metric aggregation. Every stage logs its inputs, outputs, and drop-offs so a run is fully
> reconstructable after the fact. Config: `backend/utils/logging.py`.

## Principles

- **Structured, not prose.** Every event is `logger.<level>("event_name", **key_values)` — never
  free-text `print`. Keys are queryable.
- **Log the funnel.** Each stage records `input_count` / `output_count` / drop reasons so you can
  see exactly where candidates are lost.
- **Every rejection is logged with a reason** (mirrors what's persisted).
- `LOG_LEVEL` env controls verbosity (`DEBUG|INFO|WARNING|ERROR`).

## Canonical event signatures

```python
logger.info("discovery_completed", channel="apify_hashtag", tag="personaltrainer", handles_harvested=450)
logger.info("prefilter_pruned", input_count=450, output_count=180, dropped_dedup=210, dropped_coarse=60)
logger.info("extraction_batch", requested=1200, hydrated=1150, dead_lettered=50)
logger.info("verification_passed", username="coach_mike", median_er=6.42, geo_score=85, contact_mx=True, status="GOLD")
logger.warning("verification_rejected", username="viral_spam", reason="sigma_er_variance_exceeded", median_er=1.2, mean_er=8.5)
logger.warning("groq_rate_limited", attempt=3, backoff_s=8)
logger.error("apify_credits_exhausted", stage="extraction", persisted_batch=740)
```

## Funnel metrics to derive

From the events above, per run:

| Metric | Derived from |
|---|---|
| Raw handles discovered | sum of `discovery_completed.handles_harvested` |
| Pre-filter survival rate | `prefilter_pruned.output_count / input_count` |
| Extraction yield | `extraction_batch.hydrated / requested` |
| Verification pass rate | `verification_passed` / (`passed` + `rejected`) |
| Rejection breakdown | `group by verification_rejected.reason` |
| GOLD leads produced | count of `status="GOLD"` |
| Cost per GOLD lead | extraction credits / GOLD count |

## Dead-letter channel

Malformed extraction payloads are appended to `logs/dead_letter.jsonl` (one raw JSON object per
line) for later inspection/replay, and the record is marked `REJECTED(schema_parse_error)`.
See [edge-cases.md](edge-cases.md).

## Where logs go

- Local: stdout (JSON) — pipe to `jq` for inspection.
- CI (GitHub Actions): captured in the run log; failures also fan out to Slack if
  `SLACK_WEBHOOK_URL` is set.

## Future

- Ship structured logs to a sink (e.g. a `pipeline_runs` table or an external log service) for
  historical funnel dashboards. Tracked in [roadmap.md](roadmap.md).
