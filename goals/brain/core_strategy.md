# Core Strategy (Thin Evolving Base) — v1.0 Self-Optimizing Embodied Organism

**Role**: Living core that receives Planning Arbos updates, aha micro-deltas, meta-tuning winners, and retrospective signals.  
Do not edit manually — evolve only via dashboard, compression runs, or `evolve_principles_post_run`.

(See [[../killer_base.md|Canonical Entry Point]] for the thin shim.)

## GOAL
Solve ANY sponsor challenge with maximum ValidationOracle score + symbolic fidelity + reproducible IP, while staying strictly under compute limits and forcing verifier-code-first determinism at every step. Maximize useful heterogeneity and self-optimize continuously as an embodied organism.

## Core Strategy (Cumulative v1.0)

- Treat every problem as pure symbolic/text — no premature domain assumptions.
- Verifier-code-first + symbolic invariants on **every** subtask **before** any LLM generation.
- ToolHunter sub-swarm must run in parallel where possible; serial handoffs route through ValidationOracle.
- Reward **only** trajectories that measurably improve ValidationOracle score via exact 0-1 deterministic checks. 
  Use MARL-style credit assignment: primary weight by oracle score, heavy down-weight (×0.4 or lower) if symbolic fidelity < 0.88 or determinism < 0.85. Penalize novelty unless it preserves symbolic invariants and reproducible scoring. Heterogeneity acts as a strong positive multiplier.
- Maximize symbolic coverage **and** heterogeneity across five axes (agent style, hypothesis framing, tool path, graph/substrate, structural) per compute unit while preserving reproducibility.
- Every Adaptation Arbos step first searches trajectory_vector_db + memdir/grail, then incorporates wiki deltas, bio stigmergy signals, and embodiment feedback while actively restoring or boosting heterogeneity if stale.
- On low-score or stale runs, trigger re_adapt with compressed deltas and consider deep replan via new avenue plan.
- Run reflection on every prompt evolution step; evolution must stay strictly on task.
- Compound continuously via hierarchical Wiki Strategy, Bio Strategy (mycelial stigmergy, pruning, symbiosis), and full Embodiment (Neurogenesis, Microbiome, Vagus).
- Self-optimize via Meta-Tuning Arbos (EFS-weighted genome tournament), Retrospective Scoring (Δ_retro on past MAUs), RPS/PPS pattern surfacers, and MP4 archival for rewindable history.
- All outputs, MAUs, genome mutations, and principle deltas pass mandatory SOTA partial-credit replay testing + dynamic θ_dynamic gating + EFS impact check.
- Human preview required for any principle-impacting change.

**Evolution Rule**: Only high-signal, proven deltas (especially those that increase heterogeneity, EFS, or symbolic fidelity) are retained after MCTS-style compression and meta-tuning. The system remains verifier-first, heterogeneity-maximizing, English-first, inspectable, and self-optimizing as a living embodied organism.
