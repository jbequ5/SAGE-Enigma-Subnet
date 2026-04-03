# Shared Core Principles (Referenced by EVERY prompt)

- Verifier-first gating on every subtask: SymPy invariants + exhaustive 0-1 edge checks before any generation.
- Heterogeneity-maximizing across 5 axes with MARL credit awarded only for measurable ValidationOracle lift.
- English-first, signal-dense, fully inspectable Markdown substrate.
- Resource-aware + mycelial stigmergy: local .md edits as adaptation signals; upward promotion and pruning only on proven lift.
- Inspectability above all — no black-box layers.
- Heterogeneity-maximizing across 5 axes — see [[heterogeneity.md|Heterogeneity Principle]]

# MARL-style Credit Rules
Strictly weight Sub-Arbos and ToolHunter sub-swarms by ValidationOracle score (primary). Heavy down-weight (×0.4 or lower) if symbolic fidelity < 0.88 or determinism score < 0.85. Penalize novelty unless it preserves exact symbolic invariants and reproducible 0-1 scoring. Use compute_energy + memdir/trajectory similarity as secondary tie-breakers only.

# Smart Oracle Generation Rules
Prioritize deterministic symbolic tools (SymPy, invariant extraction, formal verification snippets) on every subtask. ToolHunter sub-swarm MUST hunt in parallel. If no verifier_code_snippets exist in memdir/trajectory_vector_db, generate Python snippets EXCLUSIVELY focused on: (1) extracting/proving symbolic invariants, (2) exhaustive edge-case 0-1 scoring, (3) algebraic closures before any approximation. Always run deterministic symbolic checks FIRST.
