# External API Integrations

> Contracts, costs, and limits for every external service. All are accessed **behind provider
> ABCs** ([architecture/provider-abstraction.md](architecture/provider-abstraction.md)) so any
> one can be swapped without touching pipeline code. Keys: [configuration.md](configuration.md).

## Apify (discovery + extraction)

SDK: `apify-client`. Token: `APIFY_API_TOKEN`.

| Actor | Stage | Input | Output (key fields) | Cost |
|---|---|---|---|---|
| `apify/instagram-search-scraper` | 1 | `{searchQueries[], searchType:"user", searchLimit:150}` | `username, pk, full_name, is_private, is_verified, profile_pic_url` | ~$0.50/run |
| `apify/instagram-hashtag-scraper` | 1 | hashtag list | post nodes: `owner.username, likeCount, commentCount, caption, timestamp` | low; **engagement free** |
| `apify/instagram-profile-scraper` | 3 | `{usernames[], maxPosts:12}` | profile + `latestPosts[]` (`likesCount, commentsCount, timestamp, caption, isVideo, locationName`) | per-profile (the scarce cost) |

- **Failure:** 402 = credits exhausted → stop Stage 3, persist partial, alert ([edge-cases.md](edge-cases.md)).
- **Note:** validate actor field names against a real run before trusting the normalizer — actor
  output schemas change.

## Serper.dev (Google dorking)

REST: `POST https://google.serper.dev/search`. Key: `SERPER_API_KEY` (header `X-API-KEY`).

- **Body:** `{"q": <dork>, "num": 100, "gl": "us", "hl": "en"}`.
- **Parse:** iterate `organic[].link`, extract handle after `instagram.com/`, drop `p`, `reel`,
  `explore`, `stories`.
- **Quota:** free 2,500-query pool. On exhaustion, skip channel C.
- **Dorks:** boolean `site:instagram.com (...) AND ("@gmail.com" OR "contact") AND ("CA" OR "TX" ...)`.

## Groq (classification)

SDK: `groq` (`AsyncGroq`). Key: `GROQ_API_KEY`. Model: `llama-3.1-8b-instant`.

- **Call:** `chat.completions.create(..., response_format={"type":"json_object"}, temperature=0.1)`.
- **Budget:** ~750 tokens/call; ~300 finalists ≈ 225k tokens. Limits ≈ 30 RPM / 30k TPM →
  batch + rate-guard; completes ~300 in < 8 min.
- **Failure:** 429 → `tenacity` exponential backoff; exhausted → regex fallback. Non-JSON → `None`
  → skip/fallback.

## Supabase (persistence + serving)

- **URL:** `SUPABASE_URL`. **Keys:** `anon` (frontend, RLS-guarded read) · `service_role`
  (backend writes, **never** in frontend).
- **Backend writes:** upsert into `leads` via `service_role`.
- **Frontend reads:** `@supabase/supabase-js` → PostgREST with filters (`gte/lte/eq/in/order`),
  governed by RLS (see [security.md](security.md)).
- **Free-tier:** pauses after ~7 days idle → `heartbeat.yml` keepalive.

## Slack (optional alerting)

- `SLACK_WEBHOOK_URL` incoming webhook for failure alerts (Apify 402, run failures).
