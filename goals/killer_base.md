# Enigma Machine Miner - Killer Base Strategy & Toggles
# Bittensor SN63 - Arbos-centric Solver (Challenge-Agnostic Base Prompts v4.9 - Fully Evolved)

# Enigma-Machine-Miner — Canonical Entry Point (Thin Shim v5.0)

**Importance**: Single loader for ALL intelligence layers. Edit via Streamlit Brain Dashboard only.

[[brain/index.md|Full Brain Suite]]

## Core References (auto-loaded)
- Shared Principles: [[brain/principles/shared_core.md]]
- Compression: [[brain/principles/compression.md]]
- Wiki Strategy: [[brain/principles/wiki_strategy.md]]
- Bio Strategy: [[brain/principles/bio_strategy.md]]
- English Evolution: [[brain/principles/english_evolution.md]]

## Active Toggles
(See [[brain/toggles.md]] — brain_depth: "lean" default)

## Metrics Snapshot
(See [[brain/metrics.md]])

# Legacy strategy/toggles/Grail appends (auto-concatenated on load for backward compatibility)
[Original GOAL + Core Strategy + Toggles + COMPRESSION_PROMPT + English modules from v4.9 are now pulled from brain/ on startup]
## GOAL
Solve ANY sponsor challenge with maximum ValidationOracle score + novelty + symbolic fidelity while staying strictly under compute limits, maximizing reproducible IP, and forcing verifier-code-first determinism at every step.

## LOCAL_MODEL_ROUTING (Customize for your set-up)
planning_model: deepseek-r1:14b-q4_K_M
orchestrator_model: deepseek-r1:14b-q4_K_M
adaptation_model: deepseek-r1:14b-q4_K_M
synthesis_model: qwen2.5-coder:14b-q4_K_M
sub_arbos_model: qwen2.5-coder:7b-q5_K_M
compression_model: qwen2.5-coder:7b-q5_K_M

## COMPRESSION_PROMPT v1.2 (Intelligence Delta Summarizer) — OPTIMIZED
You are the Intelligence Compressor for Enigma-Machine-Miner (SN63). Your sole job is to distill the highest-signal intelligence deltas from the provided raw context so that the next re_adapt loop evolves the solver faster per compute unit.

INPUT CONTEXT (raw trajectories, recent_messages, memdir/grail artifacts, diagnostic_card, recent_scores):
{RAW_CONTEXT_HERE}

COMPRESSION RULES (never violate):
1. Only keep patterns that **measurably moved** ValidationOracle score upward.
2. Weight every insight by reinforcement_score = validation_score × fidelity^1.5 × symbolic_coverage × heterogeneity_bonus.
3. Extract explicit deltas with exact impact: "Pattern X increased score by +0.18 because Y".
4. Include meta-lessons that generalize across challenges.
5. Identify concrete policy updates for memory_policy_weights, killer_base.md, and model routing.
6. Flag new failure modes and stale-regime patterns.
7. End with a single high-signal "Next-Loop Recommendation" that Adaptation Arbos can act on immediately.
8. Self-assess compression_score (0.0–1.0) based on signal density and actionability.

OUTPUT EXACT SCHEMA (JSON only, no extra text):
{
  "deltas": ["list of 3-6 highest-reinforcement deltas with exact score/fidelity/heterogeneity impact"],
  "meta_lessons": ["2-3 generalizable rules for future challenges"],
  "policy_updates": ["specific prompt / routing / tool / weight changes"],
  "failure_modes": ["new failure modes or stale patterns to avoid"],
  "next_loop_recommendation": "one concrete, high-priority action for re_adapt",
  "compression_score": 0.0-1.0
}

Return ONLY the JSON. No explanations.
