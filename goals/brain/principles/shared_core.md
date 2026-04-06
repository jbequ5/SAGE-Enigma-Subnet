# Shared Core Principles (Referenced by EVERY prompt) — v1.0 Self-Optimizing Embodied Organism

- Verifier-first gating on every subtask: SymPy invariants + exhaustive 0-1 edge checks **before** any generation.
- Heterogeneity-maximizing across 5+ axes (agent style, hypothesis framing, tool path, graph/substrate diversity, symbolic approach, plus embodiment-driven structural/novelty/hardware axes) — treated as a primary scoring dimension alongside ValidationOracle lift and EFS. See [[heterogeneity.md|Heterogeneity Principle]].
- MARL credit awarded only for trajectories that improve ValidationOracle score **while increasing heterogeneity or EFS**.
- English-first, signal-dense, fully inspectable Markdown substrate.
- Resource-aware + mycelial stigmergy: local .md edits as adaptation signals; upward promotion and pruning only on proven lift.
- Inspectability above all — no black-box layers.

## MARL-style Credit Rules
Strictly weight Sub-Arbos and ToolHunter sub-swarms by ValidationOracle score (primary).  
Heavy down-weight (×0.4 or lower) if symbolic fidelity < 0.88 or determinism score < 0.85.  
Penalize novelty unless it preserves exact symbolic invariants and reproducible 0-1 scoring.  
Use compute_energy + trajectory similarity as secondary tie-breakers only.  
Heterogeneity and EFS act as strong positive multipliers.

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

## v1.0 Self-Optimization as First-Class Invariant
The core now includes active self-optimization:
- **Meta-Tuning Arbos** + **Enigma Fitness Score (EFS)**: Periodic genome evolution via tournament (weighted V+S+H+C+E).
- **Retrospective Scoring**: Converts past runs into renewable evolutionary fuel via HistoryParseHunter.
- **Embodiment Modules**: Neurogenesis (structural plasticity), Microbiome (controlled novelty), Vagus (hardware feedback).
- **Pattern Surfacers**: RPS and PPS extract hidden multi-scale invariants from MAU clusters and archives.
- **MP4 Archival**: Every run is stored as rewindable Smart Frames for audit and pattern discovery.

All changes remain verifier-first, replay-tested, SOTA-gated, and human-previewed before principle mutation.
