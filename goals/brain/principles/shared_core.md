# Shared Core Principles (Referenced by EVERY prompt)

- Verifier-first gating on every subtask: SymPy invariants + exhaustive 0-1 edge checks before any generation.
- Heterogeneity-maximizing across 5 axes (agent style, hypothesis framing, tool path, graph/substrate diversity, symbolic approach) — treated as a primary scoring dimension alongside ValidationOracle lift. See [[heterogeneity.md|Heterogeneity Principle]].
- MARL credit awarded only for trajectories that improve ValidationOracle score **while increasing heterogeneity**.
- English-first, signal-dense, fully inspectable Markdown substrate.
- Resource-aware + mycelial stigmergy: local .md edits as adaptation signals; upward promotion and pruning only on proven lift.
- Inspectability above all — no black-box layers.

## MARL-style Credit Rules
Strictly weight Sub-Arbos and ToolHunter sub-swarms by ValidationOracle score (primary). 
Heavy down-weight (×0.4 or lower) if symbolic fidelity < 0.88 or determinism score < 0.85. 
Penalize novelty unless it preserves exact symbolic invariants and reproducible 0-1 scoring. 
Use compute_energy + trajectory similarity as secondary tie-breakers only. 
Heterogeneity acts as a strong positive multiplier.

## Smart Oracle Generation Rules
Prioritize deterministic symbolic tools (SymPy, invariant extraction, formal verification snippets) on every subtask. 
ToolHunter sub-swarm MUST hunt in parallel. 
If no verifier_code_snippets exist, generate Python snippets EXCLUSIVELY focused on: 
(1) extracting/proving symbolic invariants, 
(2) exhaustive edge-case 0-1 scoring, 
(3) algebraic closures before any approximation. 
Always run deterministic symbolic checks FIRST.

These rules ensure the swarm remains verifier-first while allowing controlled heterogeneity and novelty. 
All credit assignment and oracle generation passes SOTA replay testing and EFS impact checks.

# v5.1 Intelligence Hardening — C3A + Decision Journal + Dynamic Tool Creation

## C3A (Confidence-aware Continuous Convergent Annealing)
At every Planning / Orchestrator / re_adapt and Sub-Arbos level:
m = exp(-k·d) × c^β
where:
- d = normalized distance from current best (0..1)
- c = deterministic confidence = 0.4·edge_coverage + 0.4·invariant_tightness + 0.2·ByteRover_historical_reliability
- novelty_floor = 0.20 (never drops below this even on completely new subtasks)

This replaces binary Exploit Lock with smooth, progress-and-confidence-aware tightening.

## Decision Journal (new outer-loop memory)
Every re_adapt and every Sub-Arbos now writes:
- hypothesis
- evidence_vs_instinct
- performance_delta (Δc, Δs, context_cost)
- organic_thought / aha

These entries drive:
- re_adapt prompts
- principle evolution
- ByteRover curation
- ValidationOracle replay tests

## Dynamic Tool Creation (gated)
In Sub-Arbos:
if dynamic_tool_creation_enabled and (tool gap detected or critique signals novelty):
    proposed_tool = llm_generate_tool_proposal(subtask_description)
    execution_result = sandbox_execute(proposed_tool)
    critique_delta = critique_loop(execution_result, current_criteria)
    if validation_oracle.replay_test(critique_delta) and critique_delta.c_increase > 0:
        brv_curate(critique_delta, subtask_id)
        register_new_tool(proposed_tool)

## ByteRover / MAU Pyramid Upgrades
- Minimal Atomic Units (MAU) representation for wiki entries
- Progressive pyramid retrieval under token budget
- LEANN embeddings on-demand (when leann_efficiency_enabled)
- High-degree preserving pruning

## SimulationHunter / The Well Integration
ToolHunter and ValidationOracle can now pull physics traces from The Well (15 TB simulation corpus) to recompute confidence c when symbolic or quantum claims are made.

# v1.0 Shared Core Extension

The core now includes self-optimization as a first-class invariant:
- Meta-tuning cycles battle-test genome mutations via EFS tournaments.
- Retrospective scoring converts past runs into evolutionary fuel.
- Pattern surfacers (RPS + PPS) surface hidden invariants that human or LLM planners might miss.
- All changes remain verifier-first, replay-tested, and human-previewed before principle mutation.
