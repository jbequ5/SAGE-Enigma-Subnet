# HETEROGENEITY_PRINCIPLE (Maximize Across 5 Axes)

Reference: [[../shared_core.md|Shared Core]]

**Core Mandate**: Heterogeneity is a primary scoring dimension alongside ValidationOracle score.  
We actively maximize difference across 5 axes on every decision:

1. Agent style & perspective diversity  
2. Hypothesis framing & conceptual angle  
3. Tool path & compute substrate variety  
4. Graph & memory substrate diversity  
5. Symbolic vs heuristic approach balance  

**Operational Rules**
- In Planning Arbos: Force diverse decomposition and hypothesis sets.
- In Sub-Arbos / ToolHunter: Penalize similar approaches; reward novel paths that still pass verifier-first checks.
- In Adaptation & re_adapt: When stale regime is detected, prioritize actions that restore heterogeneity (new avenue plans, guided diversity, symbiosis scanning).
- In MARL credit: Heterogeneity acts as a strong positive multiplier. Down-weight solutions that reduce overall diversity even if they score well on fidelity.
- In Wiki Strategy: Maintain cross-field synthesis and avoid clustering similar concepts/subtasks.
- In Compression: Favor deltas that increase heterogeneity; flag and prune low-heterogeneity patterns.

**Measurement**
Use the 5-axis breakdown from heterogeneity_weights.json.  
Target: Keep heterogeneity_score > 0.70 on average.  
Stale regime = prolonged low heterogeneity + low ValidationOracle.

**Evolution Rule**: Only promote or retain patterns that measurably increase heterogeneity while preserving verifier-first constraints.  
Low-heterogeneity paths are aggressively pruned unless they deliver exceptional ValidationOracle lift.

# v1.0 Heterogeneity Update

Heterogeneity now explicitly includes embodiment-driven axes:
- Structural diversity from Neurogenesis spawns
- Novelty diversity from Microbiome injections
- Hardware-state diversity from Vagus feedback

When computing heterogeneity_score, add bonus for active embodiment modules and surfaced RPS/PPS patterns.
