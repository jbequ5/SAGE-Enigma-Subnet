# Core Strategy (Thin Evolving Base)

**Role**: Living core that receives Planning Arbos updates + aha micro-deltas only.  
Do not edit manually — evolve via dashboard or compression runs.

(See [[../killer_base.md|Canonical Entry Point]] for the thin shim.)

## GOAL
Solve ANY sponsor challenge with maximum ValidationOracle score + novelty + symbolic fidelity while staying strictly under compute limits, maximizing reproducible IP, and forcing verifier-code-first determinism at every step.

## Core Strategy (Cumulative v5)
- Treat every problem as pure symbolic/text — no premature domain assumptions.
- Verifier-code-first + symbolic invariants on **every** subtask **before** any LLM generation. ToolHunter sub-swarm must run in parallel where possible; serial handoffs route through ValidationOracle.
- Reward **only** trajectories that measurably improve ValidationOracle score via exact 0-1 deterministic checks and MARL credit rules (heavy down-weight if fidelity < 0.88 or determinism < 0.85).
- Maximize symbolic coverage and heterogeneity (5 axes) per compute unit while preserving reproducibility.
- Every Adaptation Arbos step first searches trajectory_vector_db + memdir/grail for proven high-score patterns.
- On low-score or stale runs, trigger re_adapt with compressed deltas and consider deep replan via new avenue plan.
- Run reflection on every prompt evolution step; evolution must stay strictly on task.
- Now compounds via hierarchical Wiki Strategy (raw/ → wiki/concepts/invariants/subtasks with pruning on lift) and Bio Strategy (mycelial stigmergy via .md writes, redundancy/loops, symbiosis detection, toggleable quantum-bio coherence in Guided Diversity phase only).
- All changes gated by ValidationOracle lift, resource_aware toggles, and heterogeneity scoring. The system remains verifier-first, heterogeneity-maximizing, English-first, and fully inspectable.

**Evolution Rule**: Only high-signal, proven deltas are retained after MCTS compression.
