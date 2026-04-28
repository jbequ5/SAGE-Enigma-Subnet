# Strategy Layer — Master Overview & Navigation
**SAGE — Shared Agentic Growth Engine**  
**v0.9.13+**

The Strategy Layer is the central intelligence hub that transforms Solve’s rigorously gated, 60/40-scored fragments into ranked, enriched, queryable intelligence that powers every subsequent layer of SAGE.

While Solve enforces strict quality gates, Strategy performs the following core functions:
- Builds and maintains a living NetworkX directed graph of fragments with rich provenance.
- Computes an explicit, tunable **RankScore** for every fragment (anchored to the 60/40 final score from Solve).
- Enriches the graph with cross-domain patterns and meta-fragments via community detection, motif mining, and embedding similarity.
- Serves the highest-value intelligence to Enigma Machine runs and Synapse’s meta-RL loop on demand.
- Closes the feedback loop by updating utilization, impact, and centrality scores based on real downstream outcomes.

Strategy operates at two levels for performance and scale:
- **Lightweight local execution** during runs for qualified users (immediate feedback).
- **Full global Strategy** on the aggregated dataset in `sage-intelligence` (graph mining, ranking, enrichment).

This subsystem is what makes SAGE more than the sum of individual runs. It compounds collective intelligence and prevents the flywheel from stalling on low-value or repetitive data.

### Navigation — Core Deep Dives

1. **[Global Ranking & Re-Scoring](../strategy/Global-Ranking-&-Re-Scoring.md)**  
   Multi-signal RankScore formula, weights, replay penalty, global re-scoring tolerance (0.08), and anti-gaming protection.

2. **[Graph Mining, Enrichment & Pattern Surfacing](../strategy/Graph-Mining-Enrichment-&-Pattern-Surfacing.md)**  
   Leiden community detection, motif mining, embedding similarity, meta-fragment generation, and pattern promotion.

3. **[ByteRover MAU, Closed Feedback Loop & Serving Intelligence](../strategy/ByteRover-MAU-Closed-Feedback-Loop-&-Serving-Intelligence.md)**  
   MAU reinforcement mechanics, utilization update rule, closed feedback loop, serving ranked intelligence to EM runs and Synapse, and the Strategy-Economic bridge.

### How to Use This Suite
- Start with this **Master Overview** for the big picture and data flow.
- Read the deep dives in the order above for a full walkthrough of how the Strategy Layer works.
- Each document includes investor summaries, concrete examples, rebuild steps, and reference formulas.

The Strategy Layer is the **upgraded gas** that powers the entire SAGE flywheel. It takes Solve’s rigorously gated 60/40-scored fragments and turns them into ranked, enriched, searchable intelligence that Synapse can mine and that every Enigma Machine run can borrow from.

**All supporting architecture is covered in the Solve Layer suite, Intelligence Subsystem suite, and the main SAGE vision documents.**

**Economic Impact at a Glance**  
- Target: 2.7× increase in high-signal fragment reuse across runs; 41% contribution to high-impact toolkits and proposals  
- Success Milestone (60 days): ≥ 80% of promoted fragments show positive downstream EFS lift or Economic contribution within 14 days (measured against current baseline of ~31%
