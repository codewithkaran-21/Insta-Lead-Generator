"""Pipeline package — the six sequential stages of the verification engine.

Each ``stageN_*`` module owns one transformation and one gate. Stages consume and emit domain
models (models/domain.py) and are wired together by ``run_pipeline.py``. Order and
responsibilities are fixed by spec §3 and summarized in docs/workflow.md:

    stage0_seeds        calibration cohort + query seeds
    stage1_discovery    seeds → CandidateLead stream
    stage2_prefilter    cheap follower/heuristic gate (drop early)
    stage3_enrichment   full profile + posts extraction (expensive)
    stage4_verification deterministic metrics + gates (median ER, variance, CLR, geo, DNS)
    stage5_classification LLM semantic labels for survivors
    stage6_persistence  upsert VERIFIED/GOLD to Supabase

Golden rule: reject early and cheaply; only survivors pay for the next stage.
"""

__all__: list[str] = []
