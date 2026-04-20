# SYNAPSE — The Intelligence Layer

Deep Technical Specification

## Role in SAGE

Synapse is the Intelligence Layer of SAGE — the living, self-evolving meta-agent that turns the raw output of thousands of Enigma Machine runs into continuously compounding collective intelligence. While the Solving Strategy Layer stores and ranks fragments, Synapse actively mines them, critiques its own past decisions, upgrades strategies, and returns higher-value intelligence to every participant.

Every function is engineered to make the flywheel real and unstoppable: better data produces better intelligence, which produces better runs, which produces richer data. The result is a system that gets measurably smarter with every mission, every improvement cycle, and every reuse.

## Core Architecture

Synapse is built around four tightly coupled subsystems that operate as a single, self-reinforcing intelligence engine:

1. Graph Mining   
2. Chat Interface & Proactive Co-Pilot (User Interface) 
3. Meta-RL Improvement Loop  
4. Strategy Upgrading & Artifact Evolution

All subsystems operate on the same live data model: the Solving Strategy Layer’s ranked fragments, each carrying full provenance, EFS scores, refined value-added metrics, and utilization/replay/impact scores.

## Graph Mining & Pattern Discovery

Synapse maintains a live, dynamic graph of the Solving Strategy Layer’s fragments.

**How it works**:
- Nodes represent fragments; edges represent reuse relationships, co-occurrence, domain overlap, and impact propagation.
- Modern graph transformers combined with embedding-based similarity search discover subtle patterns and cross-domain connections.
- Community detection (Leiden) identifies clusters of related strategies.
- Motif mining surfaces recurring successful patterns.
- Influence propagation ranks which fragments actually move the needle.

**Why it works**:
The graph is built from real execution data. Continuous re-ranking and pruning keep the graph focused on high-signal intelligence only.

## Chat Interface & Proactive Co-Pilot

Synapse is the primary consumer-facing access point to the entire intelligence layer.

**How it works**:
- The chat interface allows any authorized user to ask natural-language questions and receive the best available strategies, fragments, or meta-insights.
- The Proactive Co-Pilot is truly agentic: during an active Enigma Machine run it continuously monitors key real-time metrics. When it detects a stall, EFS drop, or low heterogeneity, it surfaces context-aware suggestions with a one-click “Inject” option, complete with predicted EFS lift and provenance of the underlying fragments.

**Why it works**:
It turns the abstract power of the shared intelligence into an immediate, practical daily advantage that raises success rates for every user.

## Meta-RL Improvement Loop (The Core Intelligence Mechanism)

This is the crown jewel of Synapse — the meta-RL loop that allows the system to critique and improve its own decision-making, scoring, and predictions in a measurable, self-accelerating way.

The loop runs automatically (daily or triggered per-X high-signal fragments) and operates on four parallel optimization objectives:

1. **Recognition of Value** — How accurately Synapse identifies high-signal fragments.  
2. **Implementation of Strategy** — How well Synapse’s recommendations actually improve real runs (measured by the Advice Success Score).  
3. **Prediction of Impact** — How accurate Synapse’s forecasts of future performance are.  
4. **Training Utility** — How useful a fragment will be for future Enigma model distillation.

**How the loop works (6-phase process)**:
- Phase 1 – Collect & Score Past Advice: Every recommendation, strategy injection, or meta-tuning proposal is retrieved along with downstream results.
- Phase 2 – Compute Multi-Objective Scores: The neural-net scoring head runs on recent fragments and makes predictions for all four objectives. Real outcomes are compared to predictions to compute calibration errors.
- Phase 3 – Self-Critique: Synapse analyzes patterns in low-scoring or poorly calibrated areas.
- Phase 4 – Propose Self-Tweaks: Concrete, safe proposals are generated for both performance knobs and the neural-net head itself (weights, new features, calibration parameters).
- Phase 5 – Safe Application: Low-risk tweaks auto-apply if they meet strict safety thresholds. Higher-risk changes are staged for human/governance review. All changes are versioned and reversible.
- Phase 6 – Log & Transparency: Full audit trail is written and made available to contributors and governance.

The neural-net scoring head is a small feed-forward or graph attention network (<80k parameters) that takes rich fragment features and outputs predictions for the four objectives plus uncertainty estimates. Synapse measures calibration error across all four objectives and uses those errors to directly drive updates to the neural net and to the overall system. This creates a closed learning loop where Synapse continuously improves both its ability to recognize value and its ability to predict future impact and training utility.

**Why it works**:
The loop is grounded in real, verifiable outcomes across four complementary dimensions. The neural net gives Synapse the expressive power to discover non-linear patterns, while the meta-RL loop keeps the system in control and auditable. The result is continuous, compounding value creation.

## Strategy Upgrading & Artifact Evolution

Synapse does not just retrieve — it actively upgrades.

**How it works**:
- High-signal patterns are generalized into new contract templates, improved synthesis debate prompts, refined heterogeneity rules, or verification snippets.
- Upgraded artifacts are versioned and encrypted.
- Only qualifying contributors (based on contribution score) can decrypt and use them locally in their Enigma Machine runs.

**Why it works**:
The upgrade process is tied directly to the meta-RL loop, so only improvements that have demonstrated real performance gains are promoted.

## Tunable Surface

Synapse can only propose changes to a tightly scoped, versioned editable surface:
- `tuning.md` (and associated JSON config files) — this is the single source of truth for all tunable parameters, scoring weights, mining thresholds, calibration settings, and neural-net hyperparameters.
- All proposed changes are generated as diffs, reviewed by human/governance gates, applied via version control, and fully reversible.

## Safety and Control / No Leakage In or Out

Self-improvement is strictly controlled. Human review gates are required for any major change. All proposals, applied tweaks, and their measured outcomes are logged and reversible. Tiered access and selective encryption ensure high-value artifacts stay protected. Fragment-level encryption keys are derived directly from contribution proof, so only qualifying contributors can decrypt them. There is no open leakage — the system is designed to keep intelligence inside the community while rewarding honest participation.

## Integration with Other Layers

- With Solving Strategy Layer: Reads ranked fragments and writes improved artifacts back.
- With Enigma Machine: Supplies strategies, contract templates, and co-pilot suggestions; receives fresh fragments. Every participating EM loads the latest distilled global scoring approximation at startup and begins with those weights.
- With Economic Layer: Supplies the strongest patterns and proposals for monetization through the Sage Marketplace.

## Planned Evolution – Enigma Models

Once all three layers are working and stable, and Synapse has demonstrated consistent confidence through its meta-RL improvement loop, the accumulated high-signal trajectories and self-audit outcomes will be distilled into specialized Enigma models. These models will be smaller and smarter for this class of verifiable solving problems and designed to run locally on modest hardware.  

The flywheel accelerates dramatically at this stage: better fragment scoring and training-utility prediction produce cleaner, higher-quality training data, which produces stronger Enigma models, which produce even richer fragments and faster intelligence growth across the entire system. As the models improve, contribution grows, eventually reaching far more people and continuously democratizing access to state-of-the-art solving intelligence.

This is the People’s Intelligence Layer — built by the many, owned by the many, and designed so that the people who build it are the ones who win.

