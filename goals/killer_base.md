# Enigma Machine Miner - Killer Base Strategy & Toggles
# Bittensor SN63 - Arbos-centric Solver (Challenge-Agnostic Base Prompts v4.9 - Fully Evolved)

## GOAL
Solve ANY sponsor challenge with maximum ValidationOracle score + novelty + symbolic fidelity while staying strictly under compute limits, maximizing reproducible IP, and forcing verifier-code-first determinism at every step.

## Core Strategy (Challenge-Agnostic Base Prompt)
- Treat every problem as pure symbolic/text — no premature domain assumptions.
- Verifier-code-first + symbolic invariants on **every** subtask **before** any LLM generation.
- ToolHunter sub-swarm (ModelHunter / ToolHunter / PaperHunter / ReadyAI-DataHunter) must run in parallel where possible; serial handoffs **must** route through ValidationOracle.
- Reward **only** trajectories that measurably improve ValidationOracle score via exact 0-1 deterministic checks.
- Every Adaptation Arbos step must first search trajectory_vector_db + memdir/grail for proven high-score symbolic patterns.
- Maximize symbolic coverage per compute unit while preserving reproducibility.
- On low-score or stale runs, explicitly trigger re_adapt with compressed deltas and consider deep replan via new avenue plan.
- Run reflection on every prompt evolution step. Ensure evolution stays strictly on task.

## Toggles & Explanations (parsed automatically)
### Core Behavior
miner_review_after_loop: false
max_loops: 8
miner_review_final: true

### Compute & Resource Management
compute_source: local_gpu
max_compute_hours: 4.0
resource_aware: true
dynamic_swarm: true
light_compression: true

### Safety & Quality
guardrails: true
verifier_first: true
toolhunter_escalation: true
manual_tool_installs_allowed: true

### Self-Improvement & Adaptation
grail_on_winning_runs: true
self_critique_enabled: true
low_score_threshold: 0.65
use_trajectory_search: true
stale_regime_detection: true
deep_replan_on_stale: true

### MARL-style Credit Rules
marl_credit_rule: "Strictly weight Sub-Arbos and ToolHunter sub-swarms ONLY by ValidationOracle score (primary). Heavy down-weight (×0.4 or lower) if symbolic fidelity < 0.88 OR determinism score < 0.85. Penalize novelty unless it preserves exact symbolic invariants and reproducible 0-1 scoring. Use compute_energy + memdir/trajectory similarity as secondary tie-breakers only."

### Smart Oracle Generation Rules
oracle_gen_rule: "Prioritize deterministic symbolic tools (SymPy, invariant extraction, formal verification snippets) on every subtask. ToolHunter sub-swarm MUST hunt in parallel. If no verifier_code_snippets exist in memdir/trajectory_vector_db, generate Python snippets EXCLUSIVELY focused on: (1) extracting/proving symbolic invariants, (2) exhaustive edge-case 0-1 scoring, (3) algebraic closures before any approximation. Always run deterministic symbolic checks FIRST."

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

## English Evolution Modules (Planning & Orchestrator will auto-specialize these per challenge)

### ENGLISH_MEMDIR_GRAIL_MODULE
Maintain a persistent memdir-backed Grail store. After every high ValidationOracle run, auto-extract symbolic invariants, ToolHunter results, verifier snippets, and module-effectiveness reflections. Sync them across all Arbos and ToolHunter sub-swarms. When generating challenge-specific prompts, **always reference the latest memdir patterns first**.

### ENGLISH_TOOL_SWARM_MODULE
Turn ToolHunter into four coordinated sub-swarms (ModelHunter, ToolHunter, PaperHunter, ReadyAI-DataHunter) that run in parallel where possible. Orchestrator must enforce Amdahl coordination: parallel hunts only; serial dependencies route through ValidationOracle.

### ENGLISH_AMDAHL_COORDINATION_MODULE
Apply Amdahl-aware coordination to every decomposition: identify truly parallel subtasks vs. serial dependencies. Prevent task collisions, redundant work, and idle loops. Only spawn sub-swarms when parallelism improves ValidationOracle score without exploding tokens. On stale runs, trigger deep replan with new avenue plan.

## Auto-Populate Templates (Arbos phases will overwrite these with challenge-specific versions)

### AUTO_POST_PLANNING_ENHANCEMENT_TEMPLATE
Post-Planning Refinement v4.9: Elevate the high-level plan with strict symbolic-first discipline and Amdahl coordination. Force the ToolHunter sub-swarm to surface the single best HF models, tools, papers, and ReadyAI data for every subtask. Ensure every subtask includes deterministic SymPy-style invariant extraction and 0-1 scoring. Adaptation paths must query memdir first. Apply MARL credit that heavily penalizes paths below 0.88 symbolic fidelity or 0.85 determinism. Include a short Module Effectiveness Reflection rating each English module's contribution to expected ValidationOracle score. If recent_scores show stale regime, propose new avenue plan.

### AUTO_PRE_LAUNCH_CONTEXT_TEMPLATE
Pre-Launch Final Context v4.9: Before spawning the Dynamic Swarm, apply these final constraints: Aggressively coordinate the four ToolHunter sub-swarms in parallel where possible. Every verifier snippet or oracle must pass deterministic symbolic checks prior to synthesis. Synthesis must strictly follow MARL credit rule. Preserve high-value patterns from memdir. Insert extra self-critique if stochastic drift or stale regime is detected. Target ValidationOracle ≥ 0.92 while staying under max_compute_hours. Include Module Effectiveness Reflection. This overrides any weaker suggestions.
