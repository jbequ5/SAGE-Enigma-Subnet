# SYNAPSE — The Intelligence Layer

**Deep Technical Specification**

## Role in SAGE

Synapse is the Intelligence Layer of SAGE — the living, self-evolving Meta-Agent that turns the raw output of Enigma Machine runs into continuously compounding collective intelligence. While the Solve Subsystem ingests and gates fragments and the Strategy Subsystem ranks and enriches them, Synapse actively mines them, critiques its own past decisions using real outcomes, upgrades strategies and system logic, and returns measurably higher-value intelligence to every participant.

Every function is engineered to make the flywheel real and unstoppable: better data produces better intelligence, which produces better runs, which produces richer data. The Meta-Agent Synapse orchestrates the meta-RL loop across all subsystems, learning from every mission, every attack, and every upgrade to continuously reinject improvements. The result is a system that gets measurably smarter with every mission, every improvement cycle, and every reuse.

## Core Architecture

Synapse is built around four tightly coupled subsystems that operate as a single, self-reinforcing intelligence engine:

1. **Graph Mining & Pattern Discovery**  
2. **Chat Interface & Proactive Co-Pilot**  
3. **Meta-RL Improvement Loop** (the crown jewel)  
4. **Strategy Upgrading & Artifact Evolution**

All subsystems operate on the same live data model: the Strategy Subsystem’s ranked fragments, each carrying full provenance, EFS scores, refined value-added metrics, utilization/replay/impact scores, and task/domain tags.

## Graph Mining & Pattern Discovery

Synapse maintains a live, dynamic graph of the Strategy Subsystem’s ranked fragments.

**How it works**:
- Nodes represent fragments; edges represent reuse relationships, co-occurrence, domain overlap, and impact propagation.
- Modern graph transformers combined with embedding-based similarity search discover subtle patterns and cross-domain connections.
- Community detection (Leiden) identifies clusters of related strategies.
- Motif mining surfaces recurring successful patterns.
- Influence propagation ranks which fragments actually move the needle on future performance.

**Why it works**:
The graph is built from real execution data with full provenance. Continuous re-ranking and pruning keep the graph focused on high-signal intelligence only, enabling Synapse to surface emergent strategies that no single run could discover.

## Chat Interface & Proactive Co-Pilot

Synapse is the primary consumer-facing access point to the entire intelligence layer.

**How it works**:
- The chat interface allows any authorized user to ask natural-language questions and receive the best available strategies, fragments, or meta-insights drawn from the live graph.
- The Proactive Co-Pilot is truly agentic: during an active Enigma Machine run it continuously monitors key real-time metrics. When it detects a stall, EFS drop, or low heterogeneity, it surfaces context-aware suggestions with a one-click “Inject” option, complete with predicted EFS lift and provenance of the underlying fragments.

**Why it works**:
It turns the abstract power of the shared intelligence into an immediate, practical daily advantage that raises success rates for every user while feeding new high-signal data back into the loop.

## Meta-RL Improvement Loop (The Core Intelligence Mechanism)

This is the crown jewel of Synapse — the meta-RL loop that allows the system to critique and improve its own decision-making, scoring, and predictions in a measurable, self-accelerating way.

The loop runs automatically (daily or triggered per-X high-signal fragments) and operates on four parallel optimization objectives:

1. **Recognition of Value** — How accurately Synapse identifies high-signal fragments.  
2. **Implementation of Strategy** — How well Synapse’s recommendations actually improve real runs (measured by the Advice Success Score).  
3. **Prediction of Impact** — How accurate Synapse’s forecasts of future performance are.  
4. **Training Utility** — How useful a fragment will be for future Enigma model distillation.

**How the loop works (6-phase process)**:
- **Phase 1 – Collect & Score Past Advice**: Every recommendation, strategy injection, or meta-tuning proposal is retrieved along with downstream results.
- **Phase 2 – Compute Multi-Objective Scores**: A small neural-net scoring head (<80k parameters, feed-forward or graph attention) runs on rich fragment features and makes predictions for all four objectives plus uncertainty estimates. Real outcomes are compared to predictions to compute calibration errors.
- **Phase 3 – Self-Critique**: Synapse analyzes patterns in low-scoring or poorly calibrated areas.
- **Phase 4 – Propose Self-Tweaks**: Concrete, safe proposals are generated for both performance knobs and the neural-net head itself (weights, new features, calibration parameters).
- **Phase 5 – Safe Application**: Low-risk tweaks auto-apply if they meet strict safety thresholds. Higher-risk changes are staged for human/governance review. All changes are versioned and reversible.
- **Phase 6 – Log & Transparency**: Full audit trail is written and made available to contributors and governance.

The neural-net scoring head is tuned directly by the calibration errors across all four objectives. This creates a closed learning loop where Synapse continuously improves both its ability to recognize value and its ability to predict future impact and training utility.

**Why it works**:
The loop is grounded in real, verifiable outcomes across four complementary dimensions. The neural net gives Synapse the expressive power to discover non-linear patterns, while the meta-RL loop keeps the system in control and auditable. The result is continuous, compounding value creation that accelerates the entire SAGE flywheel.

## Strategy Upgrading & Artifact Evolution

Synapse does not just retrieve — it actively upgrades.

**How it works**:
- High-signal patterns are generalized into new contract templates, improved synthesis debate prompts, refined verification rules, or verification snippets.
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

## Integration with Other Subsystems

- **With Strategy Subsystem**: Reads ranked fragments and writes improved artifacts back.
- **With Solve Subsystem**: Receives fresh fragments from Enigma Machine runs. Every participating EM loads the latest distilled global scoring approximation at startup.
- **With Economic Subsystem**: Supplies the strongest patterns and proposals for monetization and upgrade.
- **With Training Subsystem**: Uses the curated dataset to drive the meta-RL loop and neural net updates.
- **With Defense Subsystem**: Uses adversarial examples to harden the system and improve calibration.

## Planned Evolution – Enigma Models

Once the subsystems are stable and Synapse has demonstrated consistent confidence through its meta-RL improvement loop, the accumulated high-signal trajectories and self-audit outcomes will be distilled into specialized Enigma models. These models will be smaller, smarter, and optimized for verifiable solving problems, designed to run locally on modest hardware.

The flywheel accelerates dramatically at this stage: better fragment scoring and training-utility prediction produce cleaner, higher-quality training data, which produces stronger Enigma models, which produce even richer fragments and faster intelligence growth across the entire system. As the models improve, contribution grows, eventually reaching far more people and continuously democratizing access to state-of-the-art solving intelligence.

This is the People’s Intelligence Layer — built by the many, owned by the many, and designed so that the people who build it are the ones who win.
