# InstaLeads Verification Engine
## Exhaustive Technical Specification & Implementation Blueprint



## 1. Executive Summary & Problem Formulation

### 1.1 The Domain Problem: Signal Degradation in Creator Discovery
Influencer acquisition for targeted consumer health, performance fitness, and dietary supplement verticals is bottlenecked by the low signal-to-noise ratio of public social data. Existing commercial platforms (Modash, HypeAuditor, Upfluence, Grin) exhibit four structural engineering failures:
1. **Arithmetic Mean Distortion on Engagement Rates (ER)**: Standard platforms calculate $\text{ER} = \frac{\sum (\text{Likes} + \text{Comments})}{N \cdot \text{Followers}}$. A single viral reel (e.g., 500k views / 40k likes on a 20k follower account) creates an artificial $200\%$ ER spike that skews the historical mean. Naive filters flag these accounts as high-performing, despite their baseline engagement sitting below $1.0\%$.
2. **Geographic Hallucination via Heuristic Leakage**: Instagram does not expose a canonical `country_code` field on public profiles. Standard aggregators use binary language classification (e.g., English text = US Creator), causing massive false-positive bleed from the UK, Canada, Australia, and English-speaking European creators.
3. **Data Stale-State & Zombie Contacts**: Static creator databases index profiles intermittently (30–90 day cycles). Bio emails are frequently abandoned, managed by defunct agency domains, or lack active DNS MX routing.
4. **Predatory Unit Economics**: Enterprise vendor contracts ($8,000–$18,000/year) force high upfront CapEx before campaign conversion validation.

### 1.2 The Architectural Solution: Inverted ETL Verification Engine
**InstaLeads** inverts traditional scraping by functioning as a **deterministic lead verification engine** with a stateless, hot-swappable extraction layer. Instead of storing massive unverified crawls, InstaLeads ingests candidate streams from low-cost discovery channels, executes rigorous mathematical and statistical verification locally, runs targeted single-pass semantic classification via low-latency LLMs, and commits only outreach-grade records to an auditable relational ledger.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     GLOBAL DATA PIPELINE                                         │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
   DISCOVERY STAGE               PRE-FILTER STAGE               EXTRACTION STAGE
 ┌───────────────────┐        ┌─────────────────────┐        ┌─────────────────────┐
 │ • Apify Search    │        │ • Bloom/Set Dedup   │        │ • ExtractionProvider│
 │ • Apify Hashtag   │ ─────► │ • Regex Email Scan  │ ─────► │ • ApifyProfile (V1) │
 │ • Serper Dorking  │        │ • Priority Max-Heap │        │ • Hydrates 12 Posts │
 └───────────────────┘        └─────────────────────┘        └──────────┬──────────┘
                                                                        │
 ┌──────────────────────────────────────────────────────────────────────┘
 │
 ▼ VERIFICATION ENGINE (DETERMINISTIC IN-HOUSE MATH)
 ┌─────────────────────────────────────────────────────────────────────────────────┐
 │ • Median ER Calculation: Outlier-resistant median across N recent posts         │
 │ • Variance Guard: Penalize sigma_ER >= 0.80 * mean_ER (anti-spike filter)       │
 │ • Anti-Bot Comment/Like Ratio (CLR): Enforce 0.01 <= CLR <= 0.15                │
 │ • Recency Guard: Last post <= 10 days, >= 4 posts / 30 days                     │
 │ • Geographic Confidence Matrix (0-100): Multi-signal Bayesian weight sum        │
 │ • Split-Contact Engine: DNS MX resolution on all discovered email domains       │
 └────────────────────────────────┬────────────────────────────────────────────────┘
                                  │
                                  ▼
   SEMANTIC CLASSIFICATION        PERSISTENCE & PRESENTATION
 ┌──────────────────────────┐  ┌───────────────────────────────────────────────────┐
 │ • Groq Llama-3.1-8B      │  │ • Supabase PostgreSQL (PostgREST API + RLS)       │
 │ • Strict Pydantic Schema │─►│ • Lead Lifecycle State Machine (CANDIDATE -> GOLD)│
 │ • Niche & Content Gate   │  │ • Next.js Filterable Dashboard on Vercel          │
 └──────────────────────────┘  └───────────────────────────────────────────────────┘
```

---

## 2. Global Architecture & Provider Abstraction Layer

To ensure zero vendor lock-in, every peripheral subsystem (Discovery, Extraction, Classification, Persistence) is decoupled through strict Abstract Base Classes (ABCs). Switching extraction from Apify to a self-hosted residential proxy pool (`curl_cffi`) or an alternate provider (`HikerAPI`, `Scrapfly`) requires modifying exactly one implementation file without touching downstream verification or presentation layers.

```
                               ┌──────────────────────────────┐
                               │     SearchConfiguration      │
                               │  - target_niche: str         │
                               │  - target_country: str       │
                               │  - min_followers: int        │
                               │  - max_followers: int        │
                               │  - min_median_er: float      │
                               └──────────────┬───────────────┘
                                              │
                                              ▼
                        ┌─────────────────────────────────────────────┐
                        │        <<interface>> DiscoveryProvider      │
                        │ + discover(query, limit) -> List[Candidate] │
                        └──────┬──────────────┬──────────────┬────────┘
                               ▲              ▲              ▲
                               │              │              │
                    ┌──────────┴───┐   ┌──────┴───────┐   ┌──┴───────────┐
                    │ ApifySearch  │   │ ApifyHashtag │   │  SerperDork  │
                    └──────────────┘   └──────────────┘   └──────────────┘

                                              │
                                              ▼
                        ┌─────────────────────────────────────────────┐
                        │       <<interface>> ExtractionProvider      │
                        │ + get_profile(username) -> RawProfile       │
                        │ + get_profile_batch(users) -> List[RawProf] │
                        └─────────────────────┬───────────────────────┘
                                              ▲
                                              │
                               ┌──────────────┴──────────────┐
                               │  ApifyProfileProvider (V1)  │
                               │  [Future: HikerAPIProvider] │
                               │  [Future: CurlCffiProvider] │
                               └─────────────────────────────┘

                                              │
                                              ▼
                        ┌─────────────────────────────────────────────┐
                        │     <<interface>> ClassificationProvider    │
                        │ + classify(bio, captions) -> NicheResult    │
                        └─────────────────────┬───────────────────────┘
                                              ▲
                                              │
                               ┌──────────────┴──────────────┐
                               │     GroqLlamaProvider       │
                               │  [Future: OpenAIFallback]   │
                               └─────────────────────────────┘
```

### 2.1 Complete Pydantic Domain Model Specifications

```python
# backend/models/domain.py
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, EmailStr, field_validator

class LeadStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    ENRICHED = "ENRICHED"
    QUALIFIED = "QUALIFIED"
    VERIFIED = "VERIFIED"
    GOLD = "GOLD"
    REJECTED = "REJECTED"

class LocationTier(str, Enum):
    VERIFIED_US = "VERIFIED_US"
    PROBABLE_US = "PROBABLE_US"
    UNKNOWN = "UNKNOWN"

class ContactType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    WEBSITE = "website"
    LINKTREE = "linktree"

class CandidateHandle(BaseModel):
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
    id: str
    shortcode: str
    caption: Optional[str] = ""
    likes_count: int = Field(default=0, ge=0)
    comments_count: int = Field(default=0, ge=0)
    timestamp: datetime
    is_video: bool = False
    location_name: Optional[str] = None

class RawProfile(BaseModel):
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
    niche_category: str
    fitness_affinity: bool
    content_type: str
    educational_score: float = Field(..., ge=0.0, le=1.0)
    deobfuscated_email: Optional[str] = None
    extracted_geo_signals: List[str] = Field(default_factory=list)
    has_supplement_mentions: bool = False

class VerifiedLead(BaseModel):
    id: Optional[str] = None
    username: str
    full_name: Optional[str] = None
    profile_url: str
    status: LeadStatus
    rejected_reason: Optional[str] = None
    status_updated_at: datetime = Field(default_factory=datetime.utcnow)

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
    er_computed_at: datetime = Field(default_factory=datetime.utcnow)

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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    enriched_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    last_refreshed_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## 3. Exhaustive Stage-by-Stage Technical Blueprint

```
========================================================================================================
STAGE 0: SEED ANCHORS & DOMAIN CALIBRATION
========================================================================================================
```

### 3.1.1 Purpose & Calibration Vectors
Stage 0 injects a static control cohort of 10–15 hand-verified domain profiles (e.g., certified CSCS coaches, collegiate strength athletes, verified sports nutritionists). 
* **Control Objectives**:
  * Establish baseline engagement distributions ($\mu_{\text{control}}, \text{Median}_{\text{control}}$) for the current Instagram algorithm update.
  * Extract baseline keyword co-occurrence frequencies in bios and post captions.
  * Execute validation runs of the verification engine against positive controls to prevent false-negative threshold drift.

```python
# backend/pipeline/stage0_seed_anchors.py
SEED_CONTROL_ACCOUNTS = [
    {"username": "athleanx", "expected_niche": "fitness_trainer", "min_expected_er": 1.5},
    {"username": "dr.mike.israetel", "expected_niche": "fitness_trainer", "min_expected_er": 3.0},
    {"username": "biolayne", "expected_niche": "nutritionist", "min_expected_er": 2.0},
]
```

```
========================================================================================================
STAGE 1: HIGH-RECALL MULTI-CHANNEL DISCOVERY
========================================================================================================
```

### 3.2.1 Channel Architectures & Protocols
Stage 1 executes three concurrent discovery vectors to harvest a broad candidate pool ($2,500–5,000$ raw handles) at minimal cost.

```
                                  DISCOVERY LAYER CHANNELS
                                             │
      ┌──────────────────────────────────────┼──────────────────────────────────────┐
      │                                      │                                      │
      ▼                                      ▼                                      ▼
1. Apify Search Actor                  2. Apify Hashtag Actor                 3. Serper.dev SERP Engine
- Keyword Query Chunks                 - Ingests Recent Tag Posts             - Boolean Search Operators
- Cost: ~$0.50 per run                 - Post Likes/Comments Included FREE    - 2,500 Queries Free Pool
- Yield: 500-1000 Handles              - Yield: 1500-2500 Handles             - Yield: 500-1500 Handles
```

#### Channel A: Apify Instagram Search Actor (`apify/instagram-search-scraper`)
* **Execution Parameters**:
  ```json
  {
    "searchQueries": [
      "fitness coach", "personal trainer", "strength conditioning",
      "sports nutritionist", "online fitness coach", "functional fitness",
      "bodybuilding prep coach", "corrective exercise specialist"
    ],
    "searchType": "user",
    "searchLimit": 150
  }
  ```
* **Extracted Schema**: Array of objects containing `{ "username", "pk", "full_name", "is_private", "is_verified", "profile_pic_url" }`.

#### Channel B: Apify Instagram Hashtag Actor (`apify/instagram-hashtag-scraper`)
* **Execution Strategy**: High-intent niche tags yield active creators whose recent posts contain engagement indicators.
* **Hashtag Matrix**:
  `#personaltrainer`, `#onlinefitnesscoach`, `#cscscoach`, `#sportsnutritionist`, `#supplementstack`, `#powerliftingcoach`, `#hypertrophy`, `#gluteworkout`, `#fitnesstrainer`
* **Crucial Cost Optimization**: Post nodes return `{ "owner": { "username" }, "likeCount", "commentCount", "caption", "timestamp" }`. This allows the pre-filter stage to calculate an initial engagement hint *before* paying for full profile extraction.

#### Channel C: Serper.dev Google Dorking Engine
* **Protocol**: Direct REST calls against `https://google.serper.dev/search` executing boolean search dorks.
* **Query Templates**:
  ```
  site:instagram.com ("fitness coach" OR "personal trainer") AND ("@gmail.com" OR "@yahoo.com" OR "contact") AND ("CA" OR "TX" OR "FL" OR "NY") -site:instagram.com/p/ -site:instagram.com/reel/
  site:instagram.com ("sports nutrition" OR "supplement athlete") AND ("linktr.ee" OR "beacons.ai") AND "USA" -site:instagram.com/p/
  ```
* **Payload Serialization**:
  ```python
  import httpx

  async def query_serper_dork(query: str, api_key: str) -> List[str]:
      async with httpx.AsyncClient(timeout=10.0) as client:
          resp = await client.post(
              "https://google.serper.dev/search",
              headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
              json={"q": query, "num": 100, "gl": "us", "hl": "en"}
          )
          data = resp.json()
          handles = []
          for item in data.get("organic", []):
              link = item.get("link", "")
              # Extract handle from https://www.instagram.com/{username}/
              parts = link.rstrip("/").split("instagram.com/")
              if len(parts) > 1:
                  handle = parts[1].split("/")[0].split("?")[0]
                  if handle and not handle.startswith(("p", "reel", "explore", "stories")):
                      handles.append(handle)
          return handles
  ```

```
========================================================================================================
STAGE 2: ZERO-COST PRE-FILTER & PRIORITY HEAP
========================================================================================================
```

### 3.3.1 In-Memory Deduplication & Priority Math
Stage 2 operates entirely in Python memory to filter out $60\%–70\%$ of noisy candidate handles before expending Apify extraction credits.

```
Candidate Stream ──► Supabase In-Memory Set Dedup ──► Bio/Snippet Fast Regex ──► Max-Heap Priority Sorter
```

```python
# backend/pipeline/stage2_prefilter.py
import heapq
import re
from typing import List, Set
from backend.models.domain import CandidateHandle

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
US_GEO_KEYWORDS = {
    "usa", "united states", "america", "nyc", "new york", "los angeles", "la",
    "miami", "florida", "texas", "austin", "dallas", "california", "chicago",
    "denver", "colorado", "arizona", "scottsdale", "atlanta", "georgia"
}

def prefilter_candidates(
    raw_candidates: List[CandidateHandle], 
    existing_database_usernames: Set[str]
) -> List[CandidateHandle]:
    deduped_candidates = []
    seen_in_batch = set()

    for candidate in raw_candidates:
        u = candidate.username
        if u in existing_database_usernames or u in seen_in_batch:
            continue
        seen_in_batch.add(u)

        # 1. Snippet Email Scanning
        snippet = candidate.raw_snippet or ""
        if EMAIL_REGEX.search(snippet):
            candidate.has_email_signal = True

        # 2. Coarse US Geo Scanning
        snippet_lower = snippet.lower()
        if any(geo in snippet_lower for geo in US_GEO_KEYWORDS):
            candidate.has_us_geo_signal = True

        # 3. Compute Priority Score for Max-Heap
        # Priority = EmailSignal (40pts) + GeoSignal (30pts) + EngagementHint (30pts)
        score = 0.0
        if candidate.has_email_signal:
            score += 40.0
        if candidate.has_us_geo_signal:
            score += 30.0
        if candidate.seed_likes_hint and candidate.seed_likes_hint > 100:
            score += min(30.0, candidate.seed_likes_hint / 10.0)

        candidate.priority_score = score
        deduped_candidates.append(candidate)

    # Sort descending by priority score
    deduped_candidates.sort(key=lambda c: c.priority_score, reverse=True)
    return deduped_candidates
```

```
========================================================================================================
STAGE 3: EXTRACTION & DATA HYDRATION GATEWAY
========================================================================================================
```

### 3.4.1 Apify Extraction Protocol & JSON Normalization
Stage 3 batches the top $1,000–1,500$ prioritized candidates and invokes the `apify/instagram-profile-scraper` Actor via the `apify-client` SDK.

* **Payload Input Contract**:
  ```json
  {
    "usernames": ["coach_sarah", "mike_performance", "elevate_nutrition"],
    "maxPosts": 12
  }
  ```
* **Raw Actor Output Ingestion & Pydantic Normalizer**:
  ```python
  # backend/providers/apify_profile.py
  from apify_client import ApifyClient
  from backend.models.domain import RawProfile, RawPost
  from typing import List

  class ApifyProfileProvider:
      def __init__(self, api_token: str):
          self.client = ApifyClient(api_token)

      async def fetch_profiles_batch(self, usernames: List[str]) -> List[RawProfile]:
          run_input = {"usernames": usernames, "maxPosts": 12}
          # Start actor and wait for dataset
          run = self.client.actor("apify/instagram-profile-scraper").call(run_input=run_input)
          dataset_items = self.client.dataset(run["defaultDatasetId"]).list_items().items

          hydrated_profiles = []
          for item in dataset_items:
              raw_posts = []
              for post_dict in item.get("latestPosts", []):
                  raw_posts.append(RawPost(
                      id=str(post_dict.get("id", "")),
                      shortcode=post_dict.get("shortCode", ""),
                      caption=post_dict.get("caption", "") or "",
                      likes_count=int(post_dict.get("likesCount", 0)),
                      comments_count=int(post_dict.get("commentsCount", 0)),
                      timestamp=post_dict.get("timestamp"),
                      is_video=bool(post_dict.get("isVideo", False)),
                      location_name=post_dict.get("locationName")
                  ))

              hydrated_profiles.append(RawProfile(
                  username=item.get("username", "").lower(),
                  full_name=item.get("fullName"),
                  followers_count=int(item.get("followersCount", 0)),
                  following_count=int(item.get("followsCount", 0)),
                  posts_count=int(item.get("postsCount", 0)),
                  biography=item.get("biography", "") or "",
                  is_business=bool(item.get("isBusinessAccount", False)),
                  category=item.get("category"),
                  external_url=item.get("externalUrl"),
                  public_email=item.get("publicEmail"),
                  public_phone=item.get("publicPhoneNumber"),
                  latest_posts=raw_posts
              ))
          return hydrated_profiles
  ```

```
========================================================================================================
STAGE 4: DETERMINISTIC VERIFICATION ENGINE
========================================================================================================
```

### 3.5.1 Rigorous Mathematical Formulations & Gate Logic

```
   Raw Profile Payload
            │
            ├──► Follower Check ──────► Followers in [10k, 100k] ────► Fail: "followers_out_of_bounds"
            │
            ├──► Activity Guard ──────► Last Post <= 10d ─────────────► Fail: "inactive_profile"
            │                           Posts/30d >= 4
            │
            ├──► Median ER Math ──────► Median(Post_ER) >= 5.0% ─────► Fail: "median_er_below_threshold"
            │                           sigma_ER < (0.80 * Mean_ER)
            │                           N_posts >= 8
            │
            ├──► Anti-Bot Guard ──────► CLR in [0.01, 0.15] ─────────► Fail: "bot_pod_detected"
            │
            ├──► Location Matrix ─────► Confidence Score >= 65 ──────► Fail: "location_confidence_low"
            │
            └──► DNS MX Verification ─► Resolves Active MX Record ──► Pass: Stage 5 AI Classification
```

#### Sub-Module A: Engagement Rate (ER) Mathematics & Outlier Rejection
Let $P = \{p_1, p_2, \dots, p_N\}$ be the ordered sequence of extracted posts, where $N = |P| \ge 8$.
For each post $p_i$, calculate:
$$\text{ER}_i = \left( \frac{\text{likes}(p_i) + \text{comments}(p_i)}{\text{Followers}} \right) \times 100$$
Sort the sequence $\text{ER}_{(1)} \le \text{ER}_{(2)} \le \dots \le \text{ER}_{(N)}$.
$$\text{Median ER} = \begin{cases} \text{ER}_{\left(\frac{N+1}{2}\right)} & \text{if } N \text{ is odd} \\ \frac{\text{ER}_{\left(\frac{N}{2}\right)} + \text{ER}_{\left(\frac{N}{2} + 1\right)}}{2} & \text{if } N \text{ is even} \end{cases}$$
$$\text{Mean ER} = \mu_{\text{ER}} = \frac{1}{N} \sum_{i=1}^N \text{ER}_i$$
$$\sigma_{\text{ER}} = \sqrt{\frac{1}{N} \sum_{i=1}^N (\text{ER}_i - \mu_{\text{ER}})^2}$$

```
HARD VERIFICATION GATE:
1. Median ER >= 5.00%
2. sigma_ER < (0.80 * mu_ER)  [Rejects accounts whose engagement is driven by a single viral post]
3. N >= 8
```

#### Sub-Module B: Anti-Bot & Engagement Pod Gating
Let $L_{\text{total}} = \sum_{i=1}^N \text{likes}(p_i)$ and $C_{\text{total}} = \sum_{i=1}^N \text{comments}(p_i)$.
$$\text{CLR} = \frac{C_{\text{total}}}{L_{\text{total}}}$$
* If $\text{CLR} < 0.01$: Account fails with `rejected_reason = "fake_likes_no_comments"`.
* If $\text{CLR} > 0.15$: Account fails with `rejected_reason = "engagement_pod_detected"`.
* Anomaly Check: If $\max(\text{ER}) \ge 5.0 \times \text{Median ER}$, flag `has_outlier_posts = True`.

#### Sub-Module C: Geographic Bayesian Confidence Matrix ($C_{\text{geo}}$)
The engine executes multi-signal probabilistic scoring ($C_{\text{geo}} \in [0, 100]$):

```python
# backend/pipeline/geo_verifier.py
import re
from datetime import datetime, timezone
from langdetect import detect, LangDetectException

US_CITIES_STATES = {
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut",
    "delaware", "florida", "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa",
    "kansas", "kentucky", "louisiana", "maine", "maryland", "massachusetts", "michigan",
    "minnesota", "mississippi", "missouri", "montana", "nebraska", "nevada", "new hampshire",
    "new jersey", "new mexico", "new york", "north carolina", "north dakota", "ohio",
    "oklahoma", "oregon", "pennsylvania", "rhode island", "south carolina", "south dakota",
    "tennessee", "texas", "utah", "vermont", "virginia", "washington", "west virginia",
    "wisconsin", "wyoming", "nyc", "la", "mia", "atx", "dfw", "chi", "phx", "sd", "den"
}

def compute_geo_confidence(profile: RawProfile) -> tuple[int, LocationTier, dict]:
    score = 0
    signals = {}

    # Signal 1: Bio City/State Matching (+30)
    bio_clean = re.sub(r'[^a-zA-Z\s]', ' ', profile.biography.lower())
    bio_words = set(bio_clean.split())
    matched_geo = bio_words.intersection(US_CITIES_STATES)
    if matched_geo or "usa" in bio_clean or "united states" in bio_clean or "🇺🇸" in profile.biography:
        score += 30
        signals["bio_geo_match"] = list(matched_geo) if matched_geo else ["USA_TAG"]

    # Signal 2: Post Location Metadata (+25)
    us_post_locs = 0
    for post in profile.latest_posts:
        if post.location_name:
            loc_lower = post.location_name.lower()
            if any(geo in loc_lower for geo in US_CITIES_STATES) or "united states" in loc_lower:
                us_post_locs += 1
    if us_post_locs >= 2:
        score += 25
        signals["post_geo_tags_count"] = us_post_locs

    # Signal 3: Language Detection (+15)
    try:
        sample_text = profile.biography + " " + " ".join([p.caption for p in profile.latest_posts[:3] if p.caption])
        if len(sample_text.strip()) > 20:
            lang = detect(sample_text)
            if lang == "en":
                score += 15
                signals["detected_lang"] = "en"
    except LangDetectException:
        pass

    # Signal 4: Posting Timestamp Timezone Alignment (+15)
    # US Active Daytime: 12:00 UTC (8am EST) to 04:00 UTC (8pm PST / 12am EST)
    us_daytime_posts = 0
    for post in profile.latest_posts:
        post_hour_utc = post.timestamp.hour
        if post_hour_utc >= 12 or post_hour_utc <= 4:
            us_daytime_posts += 1
    if len(profile.latest_posts) > 0 and (us_daytime_posts / len(profile.latest_posts)) >= 0.70:
        score += 15
        signals["us_daytime_posting_ratio"] = us_daytime_posts / len(profile.latest_posts)

    # Signal 5: Currency Symbol Matching (+10)
    if "$" in profile.biography or any("$" in (p.caption or "") for p in profile.latest_posts):
        score += 10
        signals["currency_dollar_present"] = True

    # Signal 6: External URL TLD (+5)
    if profile.external_url:
        url_lower = profile.external_url.lower()
        if url_lower.endswith((".com", ".us", ".io", ".co")):
            score += 5
            signals["us_friendly_tld"] = True

    final_score = min(100, score)
    if final_score >= 80:
        tier = LocationTier.VERIFIED_US
    elif final_score >= 65:
        tier = LocationTier.PROBABLE_US
    else:
        tier = LocationTier.UNKNOWN

    return final_score, tier, signals
```

#### Sub-Module D: Split-Contact Extraction & DNS MX Validation
```python
# backend/pipeline/contact_verifier.py
import dns.resolver
import re
from typing import Optional, Tuple
from backend.models.domain import ContactType

EMAIL_REGEX = re.compile(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
ROLE_PREFIXES = {"info@", "support@", "contact@", "admin@", "sales@", "hello@", "press@", "inquiries@"}

def verify_dns_mx_record(domain: str) -> bool:
    try:
        answers = dns.resolver.resolve(domain, 'MX', lifetime=3.0)
        return len(answers) > 0
    except Exception:
        return False

def resolve_contact_payload(
    public_email: Optional[str],
    biography: str,
    external_url: Optional[str]
) -> Tuple[Optional[ContactType], Optional[str], Optional[str], bool, float]:
    # 1. Check Native Business Field
    if public_email:
        domain = public_email.split("@")[-1].lower()
        has_mx = verify_dns_mx_record(domain)
        is_role = any(public_email.lower().startswith(p) for p in ROLE_PREFIXES)
        conf = 0.95 if (has_mx and not is_role) else (0.50 if has_mx else 0.20)
        return ContactType.EMAIL, public_email.lower(), "business_field", has_mx, conf

    # 2. Check Bio Regex Matches
    bio_match = EMAIL_REGEX.search(biography)
    if bio_match:
        email = bio_match.group(1).lower()
        domain = email.split("@")[-1]
        has_mx = verify_dns_mx_record(domain)
        is_role = any(email.startswith(p) for p in ROLE_PREFIXES)
        conf = 0.85 if (has_mx and not is_role) else (0.45 if has_mx else 0.15)
        return ContactType.EMAIL, email, "bio_regex", has_mx, conf

    # 3. Fallback to External URL
    if external_url:
        return ContactType.LINKTREE if "linktr.ee" in external_url else ContactType.WEBSITE, external_url, "external_url", False, 0.30

    return None, None, None, False, 0.0
```

```
========================================================================================================
STAGE 5: SEMANTIC AI CLASSIFICATION & ENTITY EXTRACTION
========================================================================================================
```

### 3.6.1 Groq Llama-3.1-8B-Instant Integration Spec
* **Latency Profile**: $\approx 800\text{ tokens/sec}$ generation; TTFT (Time-to-first-token) $\le 120\text{ms}$.
* **Token Budget Math**:
  * System Prompt: $\approx 180\text{ tokens}$
  * User Payload (Bio + 5 post captions): $\approx 450\text{ tokens}$
  * Completion: $\approx 120\text{ tokens}$
  * Total / Call: $\approx 750\text{ tokens}$.
  * For 300 finalists: $300 \times 750 = 225,000\text{ tokens}$ total. Groq allows $30,000\text{ TPM}$, completing 300 profiles in under 8 minutes within strict rate guards.

```python
# backend/pipeline/stage5_classification.py
import json
from typing import List, Optional
from groq import AsyncGroq
from backend.models.domain import NicheClassification, RawProfile

CLASSIFICATION_SYSTEM_PROMPT = """
You are a precision NLP classifier for athletic and fitness creator discovery.
Analyze the creator bio and recent captions. Return ONLY a valid JSON object matching this schema:
{
  "niche_category": "fitness_trainer" | "athlete" | "nutritionist" | "wellness" | "general_lifestyle" | "non_fitness",
  "fitness_affinity": boolean,
  "content_type": "educational" | "entertainment" | "product_promo" | "mixed",
  "educational_score": float (0.0 to 1.0),
  "deobfuscated_email": string or null,
  "extracted_geo_signals": string[],
  "has_supplement_mentions": boolean
}
Rules:
- fitness_affinity MUST be true only if content features workout tutorials, athletic coaching, lifting, or sports nutrition.
- deobfuscated_email: Resolve obfuscations like "john [at] gmail [dot] com".
- Do not output markdown codeblocks. Return pure JSON string.
"""

async def classify_profile_semantics(
    client: AsyncGroq, 
    profile: RawProfile
) -> Optional[NicheClassification]:
    captions_text = "\n---\n".join([p.caption for p in profile.latest_posts[:5] if p.caption])
    user_payload = f"USERNAME: {profile.username}\nBIO: {profile.biography}\nCAPTIONS:\n{captions_text}"

    response = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": CLASSIFICATION_SYSTEM_PROMPT},
            {"role": "user", "content": user_payload}
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    content = response.choices[0].message.content
    try:
        data = json.loads(content)
        return NicheClassification(**data)
    except Exception:
        return None
```

```
========================================================================================================
STAGE 6: PERSISTENCE, RLS & AUTO-REST SERVING
========================================================================================================
```

### 3.7.1 PostgREST Query Contract & Frontend RLS Filtering
All persistence is executed directly against Supabase PostgreSQL. The Next.js client interacts with the database via PostgREST using the anonymous key governed by Row Level Security.

* **Client Read Query Formulation**:
  ```typescript
  // frontend/src/hooks/useLeads.ts
  import { createClient } from '@supabase/supabase-js';

  export async function fetchFilteredLeads(filters: {
    minMedianEr: number;
    minFollowers: number;
    maxFollowers: number;
    countryTarget: string;
    onlyGold: boolean;
  }) {
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    );

    let query = supabase
      .from('leads')
      .select('*')
      .gte('median_er', filters.minMedianEr)
      .gte('followers', filters.minFollowers)
      .lte('followers', filters.maxFollowers)
      .eq('country_target', filters.countryTarget)
      .order('median_er', { ascending: false });

    if (filters.onlyGold) {
      query = query.eq('status', 'GOLD');
    } else {
      query = query.in('status', ['GOLD', 'VERIFIED']);
    }

    const { data, error } = await query;
    if (error) throw error;
    return data;
  }
  ```

---

## 4. Complete PostgreSQL DDL Specification

```sql
-- supabase/migrations/20260818_init_instaleads.sql
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
```

---

## 5. Failure Modes, Self-Healing & Incident Playbooks

| Component | Failure Mode / Signature | Detection Trigger | Automated Self-Healing Action |
|---|---|---|---|
| **Apify Extraction** | Account exhausted ($402$ Payment Required or $0$ credits) | HTTP Status 402 / ApifyClientError | Catch exception; gracefully stop Stage 3; persist already-enriched batch; trigger Slack alert. |
| **Groq Classification**| $429$ Too Many Requests (Exceeded 30 RPM limit) | HTTP 429 response | Exponential backoff via `tenacity` with jitter ($2\text{s} \to 4\text{s} \to 8\text{s} \to 16\text{s}$). If exhausted, fall back to regex heuristic. |
| **DNS Resolution** | Timeout on unreachable nameserver | `dns.resolver.Timeout` | Wrap query in $3.0\text{s}$ timeout context; set `contact_domain_mx = False`; downgrade confidence to $0.20$. |
| **Supabase DB** | Inactivity pause (7 days inactive on free tier) | PostgREST connection refused / $503$ | Preventative keepalive ping via GitHub Actions cron every Tuesday and Friday at 00:00 UTC. |
| **Instagram Schema** | Break in `latestPosts` JSON key structure | `ValidationError` in Pydantic parse | Log raw JSON to dead-letter folder (`logs/dead_letter.jsonl`); mark record `REJECTED` with reason `schema_parse_error`. |

---

## 6. Telemetry, Structured Logging & Observability Taxonomy

The pipeline uses `structlog` to emit JSON-formatted logs for real-time funnel monitoring and metric aggregation.

```python
# Example Structured Event Signatures
logger.info("discovery_completed", channel="apify_hashtag", tag="personaltrainer", handles_harvested=450)
logger.info("prefilter_pruned", input_count=450, output_count=180, dropped_dedup=210, dropped_coarse=60)
logger.info("verification_passed", username="coach_mike", median_er=6.42, geo_score=85, contact_mx=True, status="GOLD")
logger.warn("verification_rejected", username="viral_spam", reason="sigma_er_variance_exceeded", median_er=1.2, mean_er=8.5)
```

---

## 7. Operational Automation Workflows (GitHub Actions)

### 7.1 Automated Supabase Keepalive Heartbeat
```yaml
# .github/workflows/heartbeat.yml
name: Supabase Inactivity Heartbeat

on:
  schedule:
    - cron: '0 0 */3 * *' # Every 3 days
  workflow_dispatch:

jobs:
  ping-database:
    runs-on: ubuntu-latest
    steps:
      - name: Ping Supabase PostgREST
        run: |
          curl -f -X GET "${{ secrets.SUPABASE_URL }}/rest/v1/leads?select=id&limit=1" \
            -H "apikey: ${{ secrets.SUPABASE_ANON_KEY }}" \
            -H "Authorization: Bearer ${{ secrets.SUPABASE_ANON_KEY }}"
```

### 7.2 On-Demand Lead Pipeline Execution
```yaml
# .github/workflows/run_pipeline.yml
name: Execute InstaLeads Verification Pipeline

on:
  workflow_dispatch:
    inputs:
      target_niche:
        description: 'Target Creator Niche'
        required: true
        default: 'fitness'
      target_country:
        description: 'Target Country Code'
        required: true
        default: 'USA'
      min_median_er:
        description: 'Minimum Median ER (%)'
        required: true
        default: '5.0'

jobs:
  execute-pipeline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install Dependencies
        run: |
          pip install -r backend/requirements.txt

      - name: Run Pipeline
        env:
          APIFY_API_TOKEN: ${{ secrets.APIFY_API_TOKEN }}
          SERPER_API_KEY: ${{ secrets.SERPER_API_KEY }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
          TARGET_NICHE: ${{ inputs.target_niche }}
          TARGET_COUNTRY: ${{ inputs.target_country }}
          MIN_MEDIAN_ER: ${{ inputs.min_median_er }}
        run: |
          python backend/run_pipeline.py
```

---

## 8. Complete Project Repository File Tree

```
insta-leads/
├── .github/
│   └── workflows/
│       ├── heartbeat.yml                # Supabase 3-day keepalive ping
│       └── run_pipeline.yml             # On-demand pipeline execution runner
│
├── backend/
│   ├── models/
│   │   ├── __init__.py
│   │   └── domain.py                    # Complete Pydantic models & enums
│   │
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py                      # ABC interfaces: Discovery, Extraction, Classification
│   │   ├── apify_search.py              # Apify search actor provider
│   │   ├── apify_hashtag.py             # Apify hashtag actor provider
│   │   ├── serper_discovery.py          # Serper.dev Google dork provider
│   │   ├── apify_profile.py             # Apify profile scraper provider
│   │   └── groq_classifier.py           # Groq Llama-3.1 semantic classifier
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── stage0_seeds.py              # Control seed calibration cohort
│   │   ├── stage1_discovery.py          # Multi-channel candidate aggregator
│   │   ├── stage2_prefilter.py          # Deduplication & max-heap priority queue
│   │   ├── stage3_enrichment.py         # Apify batch hydration wrapper
│   │   ├── stage4_verification.py       # Median ER, CLR, Geo-Score & DNS MX
│   │   ├── stage5_classification.py     # Semantic AI classification worker
│   │   └── stage6_persistence.py        # Supabase Postgres writer & state machine
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── dns_resolver.py              # Socket-based DNS MX validator
│   │   └── logging.py                   # Structlog configuration setup
│   │
│   ├── config.py                        # Centralized typed settings & env loader
│   ├── run_pipeline.py                  # CLI pipeline entrypoint orchestrator
│   └── requirements.txt                 # Pinned backend dependencies
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx               # Root layout & styling
│   │   │   └── page.tsx                 # Master leads dashboard view
│   │   │
│   │   ├── components/
│   │   │   ├── FilterSidebar.tsx        # Slider & checkbox filter panel
│   │   │   ├── LeadsTable.tsx           # Sortable, paginated lead directory
│   │   │   ├── LeadDetailDrawer.tsx     # Full inspection panel (ER stats, geo breakdown)
│   │   │   ├── StatusBadge.tsx          # GOLD / VERIFIED / REJECTED indicators
│   │   │   └── ExportCsvButton.tsx      # Client-side PapaParse CSV exporter
│   │   │
│   │   ├── hooks/
│   │   │   └── useLeads.ts              # PostgREST data query hook
│   │   │
│   │   └── lib/
│   │       └── supabase.ts              # Supabase browser client init
│   │
│   ├── package.json
│   ├── tsconfig.json
│   └── next.config.js
│
├── supabase/
│   └── migrations/
│       └── 20260818_init_instaleads.sql # Master PostgreSQL DDL & RLS policies
│
├── docs/
│   └── instaleads-architecture.html     # Visual architectural reference specification
│
├── .env.example                         # Environment template
├── .gitignore
└── README.md
```

---

```
========================================================================================================
END OF TECHNICAL SPECIFICATION RFC-2026-08
STATUS: ARCHITECTURE APPROVED · READY FOR FULL IMPLEMENTATION EXECUTION
========================================================================================================
```
