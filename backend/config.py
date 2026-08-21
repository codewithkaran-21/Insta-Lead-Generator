"""Typed application settings for the InstaLeads pipeline.

Loads configuration from environment variables (and a local ``.env`` in dev) into a single
validated ``Settings`` object. This is the *only* place env vars should be read — stages and
providers receive settings via injection, never by calling ``os.getenv`` themselves.

Mirrors ``.env.example`` and ``docs/configuration.md``. See spec §2.

Secrets note: ``SUPABASE_SERVICE_ROLE_KEY`` is backend-only and must never be exposed to the
frontend or logged. See docs/security.md.

TODO(M0): implement with pydantic-settings ``BaseSettings``; validate required keys at startup
and fail fast with a clear message listing any missing vars.
"""

from __future__ import annotations

# from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings:  # TODO: subclass pydantic_settings.BaseSettings
    """Validated runtime configuration.

    Fields (see .env.example for the full list):
        Secrets:  APIFY_API_TOKEN, SERPER_API_KEY, GROQ_API_KEY,
                  SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
        Run params: TARGET_NICHE, TARGET_COUNTRY
        Thresholds: MIN_MEDIAN_ER, MIN_FOLLOWERS, MAX_FOLLOWERS
        Ops:      SLACK_WEBHOOK_URL, LOG_LEVEL
    """

    # model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    ...


def get_settings() -> "Settings":
    """Return a cached, validated ``Settings`` instance.

    Raises a clear error if any required secret is missing.
    """
    raise NotImplementedError("TODO(M0): load and validate settings")
