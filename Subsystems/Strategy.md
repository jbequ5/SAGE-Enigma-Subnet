# Strategy Subsystem — Technical Specification

**Deep Technical Report**  
**SAGE — Shared Agentic Growth Engine**  
**Version 0.9.13 Hardened**  
**Last Updated:** April 23, 2026

## Abstract

The Strategy Subsystem is the central intelligence hub of SAGE — the upgraded gas that transforms Solve’s rigorously gated, 60/40-scored fragments into ranked, enriched, queryable intelligence that powers every subsequent layer.

While Solve enforces strict quality gates, Strategy performs the following core functions:
- Builds and maintains a living NetworkX directed graph of fragments with rich provenance.
- Computes an explicit, tunable RankScore for every fragment, using the 60/40 final score from Solve as the dominant signal.
- Enriches the graph with cross-domain patterns and meta-fragments via community detection, motif mining, and embedding similarity.
- Serves the highest-value intelligence to Enigma Machine runs and Synapse’s meta-RL loop on demand.
- Closes the feedback loop by updating utilization, impact, and centrality scores based on real downstream outcomes.

Strategy operates at two levels for performance and scale:
- **Lightweight local execution** during runs for qualified users (immediate feedback).
- **Full global Strategy** on the aggregated dataset in sage-intelligence (graph mining, ranking, enrichment).

This subsystem is what makes SAGE more than the sum of individual runs. It compounds collective intelligence and prevents the flywheel from stalling on low-value or repetitive data.

## 1. Fragment Ingestion from Solve

Every fragment that passes Solve’s gating arrives via secure feed vaults with its complete provenance block and the **60/40 final score** from Solve:

$$
\text{Final Score from Solve} = 0.6 \times \text{Base EFS} + 0.4 \times \text{Refined Value-Added}
$$

Strategy immediately adds the fragment as a node in its NetworkX directed graph. Edges are created based on:
- Shared subtask type or domain tag
- Contract pattern similarity (Jaccard or embedding cosine)
- Successful reuse history (temporal edges)
- Co-occurrence in previous successful syntheses

Each node stores the full provenance hash, the 60/40 score, and initial utilization = 0.

## 2. Multi-Signal Ranking Formula

Each fragment receives a **RankScore** that determines its position in the queryable knowledge graph. The explicit ranking formula is:

$$
\text{RankScore} = w1 \cdot \text{EFS}_{60/40} + w2 \cdot \text{utilization score} + w3 \cdot \text{graph centrality} + w4 \cdot \text{freshness} - w5 \cdot \text{replay penalty}
$$

**Definitions of each term** (all normalized to [0,1] where applicable):

- EFS_{60/40} = the final 60/40 score received from Solve (dominant signal)
- utilization_score = exponential moving average of successful reuses:

  $$\text{utilization score}_t = \lambda \cdot \text{utilization score}_{t-1} + (1-\lambda) \cdot \text{outcome signal}$$

  where λ = 0.85 (decay factor) and outcome_signal = +1 for EFS lift above threshold, -1 for failure.
- graph_centrality = normalized PageRank (damping factor 0.85) or eigenvector centrality of the node in the current graph.
- freshness = exponential decay based on age:

  $$\text{freshness} = e^{-\frac{\text{age days}}{30}}$$
- replay_penalty = 1.0 if cosine similarity (on embeddings) to any of the last 50 fragments exceeds 0.92, otherwise 0.0 (linear ramp between 0.85 and 0.92 similarity).

Current default weights (tuned by Synapse meta-RL and stored in `tuning.md`):
- \( w_1 = 0.45 \) (EFS_{60/40})
- \( w_2 = 0.25 \) (utilization_score)
- \( w_3 = 0.15 \) (graph_centrality)
- \( w_4 = 0.10 \) (freshness)
- \( w_5 = 0.05 \) (replay_penalty)

Updated meta-weights are pushed down from sage-intelligence and loaded by local Strategy gates.

## 3. Global Re-scoring with Tolerance Check Propagation

Strategy inherits Solve’s global re-scoring tolerance check. Every incoming fragment is re-scored using the latest global weights from Synapse. If |local_score - global_re_score| > 0.08, the fragment is flagged as potential gaming and its RankScore is multiplied by a penalty factor (currently 0.7) or sent for AHE review. This propagates Solve’s anti-gaming protection into the graph ranking.

## 4. Enrichment and Pattern Surfacing

Strategy runs periodic graph mining passes on the full aggregated dataset (triggered every N new high-signal fragments or daily):

- **Community detection**: Leiden algorithm (resolution parameter = 1.0 default, tunable) to identify clusters of related strategies.
- **Motif mining**: 3-node and 4-node motifs to surface recurring successful patterns across subtasks/domains.
- **Embedding similarity**: sentence-transformers/all-MiniLM-L6-v2 embeddings to discover unexpected cross-domain connections (cosine similarity threshold 0.75).

When a strong pattern is detected, Strategy generates a new meta-fragment:
- Summarizes the pattern using a fixed prompt template.
- Links back to source fragments.
- Computes its own 60/40-style score using the same formula as regular fragments.
- Adds the meta-fragment as a high-priority node with boosted initial RankScore.

## 5. ByteRover MAU Mechanics (Lighter Version in Strategy)

Strategy applies a lighter ByteRover MAU reinforcement when fragments are reused or promoted:

$$
\text{reinforcement} = \text{base} + \text{hetero bonus}
$$

where

$$
\text{base} = \text{RankScore} \times \text{fidelity}^{1.5} \times \text{symbolic coverage}
$$

and

$$
\text{hetero bonus} = 0.25 \times \text{heterogeneity score} \times \text{RankScore}^{1.2} \times \text{fidelity}^{1.5}
$$

(The coefficients are lighter than in Solve because Strategy focuses on ranking and enrichment rather than raw promotion.)

## 6. Serving Intelligence to Consumers

When an Enigma Machine run or Synapse’s meta-RL loop queries Strategy, it returns:
- The top-k highest-RankScore relevant fragments
- Any enriched meta-fragments for the query
- Accompanying provenance, impact history, and predicted value-added

This enables a single run to borrow proven ideas from the entire community without repeating mistakes.

## 7. Feedback Loop Update Rule

Every time a fragment is used (successfully or unsuccessfully) in a new run, Strategy updates its scores with:

$$
\text{new utilization} = 0.85 \cdot \text{old utilization} + 0.15 \cdot \text{outcome signal}
$$

where outcome_signal = +1 for successful reuse that produced EFS lift above threshold, -1 for failure, or the actual normalized EFS delta when available.

Impact scores and graph centrality are updated proportionally. This closed reinforcement loop ensures ranking continuously improves based on real downstream performance.

## 8. AHE — Adversarial Hardening Engine Integration

The AHE periodically attacks the Strategy Subsystem (graph poisoning by injecting low-value high-centrality nodes, rank manipulation, feedback loop gaming). All proposed fixes are validated with 3–5 re-tests on hold-out runs before being applied. This keeps ranking and enrichment logic robust. Global Defense coordination ensures consistent attack patterns and hardening rules across the network.

## 9. Meta-Tuning Interaction

Synapse’s global meta-RL loop tunes the ranking weights (w1–w5), MAU coefficients, enrichment thresholds, feedback decay factor, and global re-score tolerance. Local EM meta-tuning (TPE) adjusts how aggressively Strategy is queried during a run. The two levels work together: local runs stay efficient while global tuning discovers higher-order patterns that no single miner could find. Updated meta-weights are pushed down to local Strategy gates.

## Data Flow Summary

Solve (local) → secure feed vaults → Global Strategy (sage-intelligence)  
Strategy (global) → Synapse (ranked + enriched intelligence for meta-RL)  
Strategy → Enigma Machine runs (on-demand queries)  
Strategy → Defense (graph attack surface)  
Strategy → Economic (impact signals for artifact upgrading)

## Attack Vectors and Mitigations

- Graph poisoning (injecting low-value high-centrality nodes) → AHE red-team + provenance validation on every edge
- Rank manipulation → global re-scoring tolerance check propagated from Solve + utilization decay
- Spam patterns → replay penalty + community detection anomaly detection
- Feedback loop gaming → outcome_signal validation against actual EFS lift (not self-reported)

## Current Limitations and Planned Improvements

**Current (v0.9.13)**: Explicit ranking formula anchored to 60/40 score, living NetworkX graph, enrichment via Leiden/motif/embedding, closed feedback loop, global re-scoring propagation, AHE integration, dual-level meta-tuning, lightweight local execution for qualified users.  
**Planned**: Temporal graph edges for better cross-run learning, automated meta-fragment utility prediction, dynamic tuning of ranking weights themselves.

## Why the Strategy Subsystem Matters

Strategy is the **upgraded gas** that powers the entire SAGE flywheel. It takes Solve’s rigorously gated 60/40-scored fragments and turns them into ranked, enriched, searchable intelligence that Synapse can mine and that every Enigma Machine run can borrow from. Without a strong Strategy layer, the system would waste compute on low-value data and Synapse could not discover the powerful cross-domain patterns that make collective intelligence greater than the sum of individual runs.

By maintaining a living graph, an explicit ranking formula, enrichment process, closed feedback loop, global re-scoring tolerance, and AHE protection, Strategy ensures that every participating miner benefits from the best ideas the community has discovered so far — and that the entire SAGE system keeps compounding toward higher performance.
