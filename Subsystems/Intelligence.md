# Intelligence Subsystem — Technical Specification

**Deep Technical Report**  
**SAGE — Shared Agentic Growth Engine**  
**Version 0.9.12+ Hardened**  
**Last Updated:** April 21, 2026

## Abstract

The Intelligence Subsystem is the underlying meta-improvement engine that powers Synapse, the Meta-Agent of SAGE.

While Synapse is the customer-facing and miner-facing agent (providing chat interface, Proactive Co-Pilot, strategy suggestions, and real-time assistance), the Intelligence Subsystem is the hidden, self-improving machinery beneath it.

It is built around three tightly coupled pillars:
1. The **Meta-RL Improvement Loop** — the closed self-critique engine that drives continuous upgrading.
2. The **Neural-Net Scoring Head** — the learnable brain that evaluates fragments across four objectives and powers the loop.
3. The **Training/Distillation Pipeline** — the mechanism that turns high-utility fragments and learned judgments into smaller, specialized Enigma models that run locally on modest hardware.

These three pillars enable Synapse to become continuously smarter, more accurate, and more useful, while ultimately democratizing state-of-the-art solving intelligence through accessible Enigma models.

## 1. The Three Pillars of the Intelligence Subsystem

### Pillar 1: Meta-RL Improvement Loop (Self-Critique Engine)

The Meta-RL Improvement Loop is the primary self-improvement mechanism that powers Synapse. It runs automatically (daily or triggered by high-signal fragments) and optimizes four parallel objectives:

**Four Optimization Objectives**:
1. **Recognition of Value** — Accuracy in identifying high-signal fragments.
2. **Implementation of Strategy** — How well recommendations actually improve real runs (measured by Advice Success Score).
3. **Prediction of Impact** — Accuracy of forecasts of future performance and EFS lift.
4. **Training Utility** — How useful a fragment will be for future Enigma model distillation.

**6-Phase Loop Process** (rebuildable pseudocode):

**Phase 1 – Collect & Score Past Advice**  
Retrieve every previous recommendation, strategy injection, or meta-tuning proposal along with downstream real outcomes (EFS lift, reuse success, etc.).

**Phase 2 – Compute Multi-Objective Scores**  
The Neural-Net Scoring Head runs on rich fragment features and makes predictions for all four objectives plus uncertainty estimates. Real outcomes are compared to predictions to compute calibration errors for each objective.

**Phase 3 – Self-Critique**  
Analyze patterns in low-scoring or poorly calibrated areas.

**Phase 4 – Propose Self-Tweaks**  
Generate concrete, safe proposals for performance knobs and the Neural-Net Scoring Head itself.

**Phase 5 – Safe Application**  
- Low-risk tweaks auto-apply if they meet strict safety thresholds.
- Higher-risk changes are staged for human/governance review.
- All changes are versioned and fully reversible.

**Phase 6 – Log & Transparency**  
Full audit trail is written and made available to contributors and governance.

### Pillar 2: Neural-Net Scoring Head (The Learnable Brain)

The Neural-Net Scoring Head is the central learnable component that powers the Meta-RL Loop and provides intelligence to Synapse.

**Architecture** (rebuildable details):
- **Input Features**: Rich fragment vector including 60/40 EFS components, graph centrality, utilization history, replay rate, freshness, provenance metadata, heterogeneity score (for planning only), and operations telemetry signals.
- **Hidden Layers**: 2–3 layers (feed-forward or graph attention) with fewer than 80,000 total parameters.
- **Output**: 4 objective predictions + per-objective uncertainty estimates.
- **Loss Function**: Multi-objective calibration loss = weighted sum of MSE on each objective + uncertainty calibration term.
- **Training**: Online updates from real downstream outcomes.

The head is tuned directly by the calibration errors across all four objectives. It directly improves scoring in Solve, ranking in Strategy, contribution measurement in Economic, orchestration in Operations, and data curation in Training — giving Synapse increasingly accurate and useful intelligence over time.

### Pillar 3: Training/Distillation Pipeline (Democratization Engine)

The Training/Distillation Pipeline takes the highest-TrainingUtility fragments and learned judgments from the Neural-Net Scoring Head and produces smaller, specialized Enigma models that run locally on modest hardware.

**Pipeline Stages** (rebuildable sequence):
1. **Curated Dataset Assembly**: High-TrainingUtility fragments + adversarial examples from Defense + operations telemetry.
2. **Knowledge Distillation**: Train smaller student models using KL divergence loss on teacher outputs + auxiliary 7D verifier self-check loss.
3. **Supervised Fine-Tuning**: Fine-tune on high-TrainingUtility fragments with 7D verifier self-check as a strong auxiliary objective.
4. **Meta-RL Alignment**: Incorporate the 4-objective signals from the Neural-Net Scoring Head as reinforcement signals.
5. **Verification Hardening**: Use AHE-generated adversarial examples as hard negatives during training.

**Target Model Characteristics** (the ultimate goal):
- Run locally on modest hardware (consumer GPU or even CPU).
- Strong performance on verifiable solving problems.
- Preserve 7D verifier self-check integrity.
- Continuously improvable through new curated data and updated NN judgments.

This pipeline is the mechanism that democratizes intelligence: the models produced here are the final product that every participant can run locally, making state-of-the-art solving accessible to everyone.

## 4. How the Three Pillars Connect to and Improve Everything

- **Solve**: The Neural-Net Scoring Head improves refined_value_added prediction and global re-scoring tolerance.
- **Strategy**: The NN Head improves RankScore prediction and utilization/impact estimation.
- **Economic**: The NN Head improves contribution scoring and artifact_upgrade_value measurement.
- **Operations**: The NN Head improves swarm sizing and LLM routing predictions.
- **Defense**: The NN Head improves attack detection and calibration.
- **Synapse (Meta-Agent)**: All three pillars directly power Synapse — the Meta-RL Loop provides self-improvement, the NN Head provides evaluation intelligence, and the Training/Distillation Pipeline provides the democratized models that Synapse can recommend and deploy.

The ultimate output flows through Synapse to users: better real-time assistance, smarter strategies, and eventually locally runnable Enigma models.

## 5. Global Re-scoring Tolerance & Safety

All proposals generated by the Meta-RL Loop are subject to Solve’s global re-scoring tolerance. Changes that would violate tolerance thresholds are automatically rejected or staged for review. Human/governance gates are required for major changes. All tweaks are versioned and reversible.

## 6. Data Flow Summary

Solve → Strategy → Intelligence (ranked fragments)  
Operations → Intelligence (telemetry)  
Defense → Intelligence (adversarial examples)  
Intelligence → Synapse (Meta-Agent) (improved intelligence, distilled models, meta-insights)  
Intelligence → All subsystems (updated policies and improvements)

## 7. Attack Vectors and Mitigations

- Self-improvement gaming → Safe application rules + human/governance gates + versioned/reversible changes
- Neural-net poisoning → AHE red-team attacks on the scoring head
- Over-optimization → Multi-objective calibration + uncertainty estimates

All mitigations are continuously monitored by the AHE.

## 8. Current Limitations and Planned Improvements

**Current (v0.9.12+)**: Full 4-objective Meta-RL Improvement Loop, Neural-Net Scoring Head, Training/Distillation Pipeline with verifier-first focus, global re-scoring tolerance, dual-level meta-tuning.  
**Planned**: On-device meta-RL fine-tuning, automated curriculum learning, expanded multi-objective safety constraints.

## Why the Intelligence Subsystem Matters

The Intelligence Subsystem is the hidden engine that powers Synapse, the Meta-Agent. Through its Meta-RL Improvement Loop, Neural-Net Scoring Head, and Training/Distillation Pipeline, it enables continuous self-improvement and ultimately democratizes solving intelligence by producing smaller, locally-runnable Enigma models.

This is what makes the People’s Intelligence Layer real: built by the many, owned by the many, and designed so that the people who build it are the ones who win.
