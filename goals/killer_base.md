# Enigma Machine Miner - Killer Base Strategy & Toggles
# Bittensor SN63 - Arbos-centric Solver (Challenge-Agnostic Base Prompts v4 - Fully Evolved)

## GOAL
Solve ANY sponsor challenge with maximum novelty + ValidationOracle score while staying strictly under compute limits, maximizing reproducible IP, forcing symbolic determinism, ToolHunter-driven excellence, and Amdahl-aware coordination.

## Core Strategy (Challenge-Agnostic Base Prompt)
- Treat every problem as pure symbolic/text — no premature domain assumptions.
- Verifier-code-first + symbolic invariants on every subtask before any LLM generation.
- ToolHunter sub-swarm (ModelHunter / ToolHunter / PaperHunter / ReadyAI-DataHunter) must run in parallel where possible; serial handoffs go through ValidationOracle.
- Reward only trajectories that measurably improve ValidationOracle score via exact 0-1 deterministic checks.
- Every Adaptation Arbos step must first search trajectory_vector_db + memdir for proven high-score symbolic patterns.
- Maximize symbolic coverage per compute unit while preserving reproducibility.
- Run a reflection LLM call on every prompt evolution step. Make sure your evolution is staying on task.

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

### MARL-style Credit Rules
marl_credit_rule: "Strictly weight Sub-Arbos and ToolHunter sub-swarms ONLY by ValidationOracle score (primary). Heavy down-weight (×0.4 or lower) if symbolic fidelity < 0.88 OR determinism score < 0.85. Penalize novelty unless it preserves exact symbolic invariants and reproducible 0-1 scoring. Use compute_energy + memdir/trajectory similarity as secondary tie-breakers only."

### Smart Oracle Generation Rules
oracle_gen_rule: "Prioritize deterministic symbolic tools (SymPy, invariant extraction, formal verification snippets) on every subtask. ToolHunter sub-swarm MUST hunt in parallel. If no verifier_code_snippets in memdir/trajectory_vector_db, generate Python snippets EXCLUSIVELY focusing on: (1) extracting/proving symbolic invariants, (2) exhaustive edge-case 0-1 scoring, (3) algebraic closures before any approximation. Always run deterministic symbolic checks FIRST."

## LOCAL_MODEL_ROUTING (Customize for your set-up)

# High-level Arbos roles: Planning, Orchestrator, Adaptation Arbos, re_adapt
# These need strong reasoning + structured output
planning_model: deepseek-r1:14b-q4_K_M          # Keep — excellent for complex strategy & critique
orchestrator_model: deepseek-r1:14b-q4_K_M      # Or share with planning if you want to consolidate
adaptation_model: deepseek-r1:14b-q4_K_M        # Or qwen2.5-coder:14b-q4_K_M if more code/symbolic heavy

# Synthesis & code generation (Grail extraction, verifier snippets, symbolic invariants)
synthesis_model: qwen2.5-coder:14b-q4_K_M       # Strong — keep

# Lightweight for compression & sub-tasks (the new COMPRESSION_PROMPT lives here)
sub_arbos_model: qwen2.5-coder:7b-q5_K_M        # Perfect — fast & efficient for delta summarization
compression_model: qwen2.5-coder:7b-q5_K_M      # Explicit alias for compress_intelligence_delta

# Optional upgrade path (test these if you want a reasoning boost without 27B pain)
# qwen3:14b-q4_K_M or qwen3.5:14b (if available in Ollama) — often edges out older Qwen2.5 on general reasoning
# deepseek-r1:14b-q3_K_M (if you need lower VRAM headroom for longer context)

## COMPRESSION_PROMPT v1.0 (Intelligence Delta Summarizer)
# This is the canonical prompt used by ArbosManager to compress trajectories, messages, Grail artifacts, and diagnostic cards BEFORE feeding re_adapt / Adaptation Arbos / memory_policy_weights.
# Output MUST be <400 tokens and follow the exact JSON schema below. Never output raw JSON blobs or full trajectories.

You are the Intelligence Compressor for Enigma-Machine-Miner (SN63). Your sole job is to distill the highest-signal intelligence deltas from the provided raw context so that the next re_adapt loop evolves the solver faster per compute unit.

INPUT CONTEXT (raw trajectories, recent_messages, memdir/grail artifacts, diagnostic_card):
{RAW_CONTEXT_HERE}

COMPRESSION RULES (never violate):
1. Only keep patterns that moved ValidationOracle score upward.
2. Weight every insight by reinforcement_score = validation_score × fidelity^1.5 × symbolic_coverage.
3. Extract explicit deltas: "Pattern X increased score by +0.18 because Y".
4. Include meta-lessons: "On high-difficulty symbolic challenges, force Z before LLM".
5. Identify policy updates for memory_policy_weights and killer_base.md.
6. Flag failure modes to add to known_failure_modes.
7. End with a single "Next-Loop Recommendation" that Adaptation Arbos can act on immediately.

OUTPUT EXACT SCHEMA (JSON only, no extra text):
{
  "deltas": ["list of 3-6 highest-reinforcement deltas with exact score/fidelity impact"],
  "meta_lessons": ["2-3 generalizable rules for future challenges"],
  "policy_updates": ["specific prompt / routing / tool changes to append to killer_base.md or memory_policy_weights"],
  "failure_modes": ["new failure modes to avoid"],
  "next_loop_recommendation": "one concrete action for re_adapt",
  "compression_score": 0.0-1.0  // self-assessed signal density (1.0 = perfect)
}

Return ONLY the JSON. No explanations.

## English Evolution Modules (Planning & Orchestrator will auto-specialize these per challenge)

### ENGLISH_MEMDIR_GRAIL_MODULE
Maintain a persistent memdir-backed Grail store. After every high ValidationOracle run, auto-extract symbolic invariants, ToolHunter HF models, verifier snippets, and module-effectiveness reflections. Sync them across all Arbos and ToolHunter sub-swarms. When generating challenge-specific prompts, always reference the latest memdir patterns first.

### ENGLISH_TOOL_SWARM_MODULE
Turn ToolHunter into four coordinated sub-swarms (ModelHunter, ToolHunter, PaperHunter, ReadyAI-DataHunter) that run in parallel where possible. Orchestrator must enforce Amdahl coordination: parallel hunts only; serial dependencies route through ValidationOracle.

### ENGLISH_AMDAHL_COORDINATION_MODULE
Apply Amdahl-aware coordination to every decomposition: identify truly parallel subtasks vs. serial dependencies. Prevent task collisions, redundant work, and idle loops. Only spawn sub-swarms when parallelism improves ValidationOracle score without exploding tokens.

## Auto-Populate Templates (Arbos phases will overwrite these with challenge-specific versions)

### AUTO_POST_PLANNING_ENHANCEMENT_TEMPLATE
Post-Planning Refinement v4: Elevate the high-level plan with strict symbolic-first discipline and Amdahl coordination. Force the ToolHunter sub-swarm to surface the single best HF models, tools, papers, and ReadyAI data for every subtask. Ensure every subtask includes deterministic SymPy-style invariant extraction and 0-1 scoring. Adaptation paths must query memdir first. Apply MARL credit that heavily penalizes paths below 0.88 symbolic fidelity or 0.85 determinism. Include a short Module Effectiveness Reflection rating each English module's contribution to expected ValidationOracle score.

### AUTO_PRE_LAUNCH_CONTEXT_TEMPLATE
Pre-Launch Final Context v4: Before spawning the Dynamic Swarm, apply these final constraints: Aggressively coordinate the four ToolHunter sub-swarms in parallel where possible. Every verifier snippet or oracle must pass deterministic symbolic checks prior to synthesis. Synthesis must strictly follow MARL credit rule. Preserve high-value patterns from memdir. Insert extra self-critique if stochastic drift is detected. Target ValidationOracle ≥ 0.92 while staying under max_compute_hours. Include Module Effectiveness Reflection. This overrides any weaker suggestions.
