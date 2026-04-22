# Strategy Subsystem — Technical Specification

**Deep Technical Report**  
**SAGE — Shared Agentic Growth Engine**  
**Version 0.9.12+ Hardened**  
**Last Updated:** April 21, 2026

## Abstract

The Strategy Subsystem is the **central intelligence hub** of SAGE — the upgraded gas that turns Solve’s rigorously gated, high-signal fragments into ranked, enriched, queryable intelligence that powers every subsequent layer.

While Solve acts as the strict gatekeeper, Strategy is the engine that:
- Builds and maintains a living NetworkX graph of fragments
- Ranks them using the 60/40 final score from Solve as the primary signal
- Enriches them with cross-domain patterns and meta-fragments
- Serves the best intelligence to Enigma Machine runs and Synapse’s meta-RL loop
- Closes the feedback loop so successful outcomes improve future ranking

This subsystem is what makes SAGE more than the sum of individual runs. It is the mechanism that compounds collective intelligence and prevents the flywheel from stalling on low-value or repetitive data.

## 1. Fragment Ingestion from Solve

Every fragment that passes Solve’s gating arrives with its complete provenance block and the **60/40 final score**:

\[
\text{Final Score from Solve} = 0.6 \times \text{Base EFS} + 0.4 \times \text{Refined Value-Added}
\]

Strategy immediately adds the fragment as a node in its NetworkX directed graph. Edges are created based on:
- Shared subtask type or domain
- Contract pattern similarity
- Successful reuse history
- Co-occurrence in previous successful syntheses

## 2. Multi-Signal Ranking Formula

Each fragment receives a **RankScore** that determines its position in the queryable knowledge graph. The explicit ranking formula is:

\[
\text{RankScore} = w_1 \cdot \text{EFS}_{60/40} + w_2 \cdot \text{utilization_score} + w_3 \cdot \text{graph_centrality} + w_4 \cdot \text{freshness} - w_5 \cdot \text{replay_penalty}
\]

Current default weights (tuned by Synapse meta-RL and stored in `tuning.md`):
- \( w_1 = 0.45 \) (EFS_{60/40} from Solve — the dominant term)
- \( w_2 = 0.25 \) (utilization_score = successful reuses / total queries, with exponential decay)
- \( w_3 = 0.15 \) (graph_centrality = normalized PageRank or eigenvector centrality)
- \( w_4 = 0.10 \) (freshness = exponential decay based on timestamp)
- \( w_5 = 0.05 \) (replay_penalty = high if similarity to recent fragments exceeds threshold)

This formula ensures the ranking strongly favors fragments that both solve the current problem well (via the 60/40 EFS) and have proven long-term value (utilization and centrality).

## 3. Global Re-scoring with Tolerance Check Propagation

Strategy inherits Solve’s global re-scoring tolerance check. Every incoming fragment is re-scored using the latest global weights from Synapse. If the absolute difference between the local score and global re-score exceeds 0.08, the fragment is flagged as potential gaming and its RankScore is downgraded or sent for AHE review. This propagates Solve’s anti-gaming protection into the graph ranking.

## 4. Enrichment and Pattern Surfacing

Strategy runs periodic graph mining passes to create enriched meta-fragments:

- **Community detection**: Leiden algorithm with resolution parameter to find clusters of related strategies.
- **Motif mining**: Identifies recurring successful patterns across subtasks/domains.
- **Embedding similarity**: Uses sentence-transformer embeddings to discover unexpected cross-domain connections.

When a strong pattern is detected, Strategy generates a new meta-fragment that summarizes the pattern, links back to source fragments, and receives its own 60/40-style score. These meta-fragments become high-priority items for Synapse and EM runs.

## 5. ByteRover MAU Mechanics (Lighter Version in Strategy)

Strategy applies a lighter ByteRover MAU reinforcement when fragments are reused or promoted:

\[
\text{reinforcement} = \text{base} + \text{hetero_bonus}
\]

where

\[
\text{base} = \text{RankScore} \times \text{fidelity}^{1.5} \times \text{symbolic_coverage}
\]

and

\[
\text{hetero_bonus} = 0.25 \times \text{heterogeneity_score} \times \text{RankScore}^{1.2} \times \text{fidelity}^{1.5}
\]

(The coefficients are intentionally lighter than in Solve because Strategy is focused on ranking rather than raw promotion.)

## 6. Serving Intelligence to Consumers

When an Enigma Machine run or Synapse’s meta-RL loop queries Strategy, it returns the highest-RankScore relevant fragments plus any enriched meta-fragments, along with provenance, impact history, and predicted value-added. This is the mechanism that lets a single run borrow proven ideas from the entire community without repeating mistakes.

## 7. Feedback Loop Update Rule

Every time a fragment is used (successfully or unsuccessfully) in a new run, Strategy updates its scores with the following rule:

\[
\text{new_utilization} = \lambda \cdot \text{old_utilization} + (1 - \lambda) \cdot \text{outcome_signal}
\]

where:
- outcome_signal = +1 for successful reuse (EFS lift), -1 for failure
- λ = decay factor (typically 0.85)

Impact scores and centrality are also updated. This closes the reinforcement loop and ensures ranking continuously improves based on real downstream performance.

## 8. AHE — Adversarial Hardening Engine Integration

The AHE periodically attacks the Strategy Subsystem (graph poisoning, rank manipulation, injecting low-value but highly connected fragments). All fixes are validated with 3–5 re-tests before being applied. This keeps the ranking and enrichment logic robust.

## 9. Meta-Tuning Interaction

Synapse’s global meta-RL loop tunes the ranking weights (w1–w5), MAU coefficients, enrichment thresholds, and feedback decay factor. Local EM meta-tuning (TPE) adjusts how aggressively Strategy is queried during a run. The two levels work together: local runs stay efficient, while global tuning discovers higher-order patterns.

## Data Flow Summary

Solve → Strategy (60/40 scored fragments)  
Strategy → Synapse (ranked + enriched intelligence for meta-RL)  
Strategy → Enigma Machine runs (on-demand queries)  
Strategy → Defense (graph attack surface)  
Strategy → Economic (impact signals for artifact upgrading)

## Attack Vectors and Mitigations

- Graph poisoning (injecting low-value high-centrality nodes) → AHE red-team + provenance validation
- Rank manipulation → global re-scoring tolerance check from Solve
- Spam patterns → replay penalty + community detection anomaly detection
- Feedback loop gaming → outcome_signal validation against actual EFS lift

## Current Limitations and Planned Improvements

**Current (v0.9.12+)**: Explicit ranking formula using 60/40 score, graph construction, enrichment, feedback loop, global re-scoring propagation, AHE integration, dual-level meta-tuning.  
**Planned**: Temporal graph edges for cross-run learning, automated meta-fragment utility prediction, dynamic tuning of the ranking weights themselves.

## Why the Strategy Subsystem Matters

Strategy is the **upgraded gas** that powers the entire SAGE flywheel. It takes Solve’s rigorously gated 60/40 scored fragments and turns them into ranked, enriched, searchable intelligence that Synapse can mine and that every Enigma Machine run can borrow from. Without a strong Strategy layer, the system would waste compute on low-value data and Synapse could not discover the powerful cross-domain patterns that make collective intelligence greater than the sum of individual runs.

By maintaining a living graph, explicit ranking formula, enrichment process, closed feedback loop, global re-scoring tolerance, and AHE protection, Strategy ensures that every participating miner benefits from the best ideas the community has discovered so far — and that the entire SAGE system keeps compounding toward higher performance.

