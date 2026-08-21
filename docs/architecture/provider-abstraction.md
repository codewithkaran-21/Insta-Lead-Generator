# Provider Abstraction Layer

> The core decoupling mechanism (spec §2). Every external subsystem is reached through an
> **Abstract Base Class**. Swapping a vendor (e.g. Apify → HikerAPI) means writing one new
> implementation file — **no pipeline or verification code changes.**

## The interfaces

Defined in `backend/providers/base.py`:

```
SearchConfiguration            # target_niche, target_country, min/max_followers, min_median_er
        │
        ▼
<<interface>> DiscoveryProvider
  + discover(query, limit) -> List[CandidateHandle]
        implementations: ApifySearch · ApifyHashtag · SerperDork

<<interface>> ExtractionProvider
  + get_profile(username) -> RawProfile
  + get_profile_batch(usernames) -> List[RawProfile]
        implementations: ApifyProfileProvider (V1)   [future: HikerAPI, CurlCffi]

<<interface>> ClassificationProvider
  + classify(bio, captions) -> NicheClassification
        implementations: GroqLlamaProvider           [future: OpenAIFallback]
```

Persistence is likewise isolated in `stage6_persistence.py` (Supabase client), so the store can be
swapped without touching stage logic.

## Why

- **Zero vendor lock-in** — pricing/availability/ToS shifts don't force a rewrite.
- **Testability** — pipeline stages take an interface; tests inject fakes, no network.
- **Parallel evolution** — discovery channels can be added without touching verification.
- **Cost experiments** — try a cheaper extraction backend behind the same contract.

## Rules

1. **Pipeline code depends only on the ABCs**, never on a concrete vendor SDK.
2. **Normalization happens in the provider** — implementations return domain models
   (`CandidateHandle`, `RawProfile`, `NicheClassification`), not raw vendor JSON.
3. **Vendor quirks stay in the implementation** — retries, pagination, field renames, auth.
4. **Failures map to domain outcomes** — e.g. extraction schema drift → dead-letter +
   `REJECTED(schema_parse_error)`, not a raw exception bubbling into a stage.

## Adding a new provider (worked example: `HikerAPIProvider`)

1. Create `backend/providers/hiker_profile.py` implementing `ExtractionProvider`.
2. Map the vendor's response into `RawProfile` / `RawPost` (mirror `apify_profile.py`).
3. Handle vendor-specific errors; enforce timeouts.
4. Select it via config/factory in `run_pipeline.py` (or `config.py`) — no change to
   `stage3_enrichment.py` or Stage 4+.
5. Add unit tests with a canned vendor payload; update [../api-integrations.md](../api-integrations.md)
   and [../project-status.md](../project-status.md).

See [decisions/0002-provider-abstraction-abc.md](decisions/0002-provider-abstraction-abc.md) for
the rationale, and [../roadmap.md](../roadmap.md) for planned providers.
