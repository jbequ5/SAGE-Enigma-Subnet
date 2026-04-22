# Training Subsystem — Technical Specification

**Deep Technical Report**  
**SAGE — Shared Agentic Growth Engine**  
**Version 0.9.12+ Hardened**  
**Last Updated:** April 21, 2026

## Abstract

The Training Subsystem is the distillation and model-improvement layer of SAGE. It takes the highest-signal fragments and operations telemetry curated by Solve, Strategy, Economic, Operations, and Defense, and turns them into progressively better specialized Enigma models that run locally on modest hardware.

It is the final stage of the flywheel: better data → cleaner training sets → stronger Enigma models → richer fragments → faster intelligence growth. The subsystem is deliberately designed to produce smaller, verifiable, high-performance models that democratize access while continuously improving through Synapse’s meta-RL loop.

## 1. Core Responsibilities

1. **Data Curation Engine**

   **Curation Algorithm** (rebuildable steps):
   1. Ingest fragments from Strategy with their 60/40 final score and RankScore.
   2. Apply hard filters: minimum RankScore threshold, positive measured ΔEFS in downstream runs, no global re-scoring tolerance violations.
   3. Diversity sampling: use embedding cosine similarity and Leiden community detection to ensure balanced coverage without sacrificing quality.
   4. Enrichment: attach operations telemetry (miner input strategy used, hardware profile, flight test results).
   5. Compute TrainingUtility score (see below).
   6. Package as JSONL dataset with full provenance for distillation.

2. **Training Utility Objective** (Explicit Formula)

$$\text{TrainingUtility} = 0.45 \cdot \text{EFS} {60/40} + 0.25 \cdot \text{impact lift} + 0.20 \cdot \text{generalization score} + 0.10 \cdot \text{calibration value}$$

   All terms are normalized to [0,1]:
   - EFS_{60/40} = final score from Solve
   - impact_lift = measured EFS improvement when the fragment was injected in test runs
   - generalization_score = performance on hold-out subtasks not seen during curation
   - calibration_value = how much the fragment improves Synapse’s prediction accuracy

   This score controls sampling probability during distillation, ensuring the model learns from the most valuable trajectories first.

3. **Enigma Model Distillation Pipeline**

   **Stages** (rebuildable sequence):
   1. **Teacher Trajectory Collection**: Gather high-utility trajectories from the best current Enigma runs.
   2. **Knowledge Distillation**: Train smaller student models using KL divergence loss on teacher outputs + auxiliary verifier self-check loss.
   3. **Supervised Fine-Tuning**: Fine-tune on high-TrainingUtility fragments with 7D verifier self-check as a strong auxiliary objective.
   4. **Meta-RL Alignment**: Incorporate Synapse’s 4-objective signals (Recognition of Value, Implementation of Strategy, Prediction of Impact, Training Utility) as reinforcement signals.
   5. **Verification Hardening**: Run AHE-generated adversarial examples during training to improve robustness and calibration.

   **Target Model Characteristics**:
   - Run locally on modest hardware (consumer GPU or even CPU).
   - Strong performance on verifiable solving problems.
   - Preserve 7D verifier self-check integrity.
   - Continuously improvable through new curated data.

## 2. Global Re-scoring Tolerance Propagation

Any training example failing Solve’s global re-scoring tolerance (> 0.08 difference) is down-weighted or excluded from the dataset.

## 3. AHE Integration

The AHE provides adversarial examples specifically crafted to stress the distillation pipeline. These examples are used as hard negatives during training to improve calibration and robustness. AHE also attacks the curation process to prevent poisoned data from entering the training set.

## 4. Meta-Tuning Interaction

Synapse’s global meta-RL loop treats the Training Subsystem as a core optimization target:
- TrainingUtility prediction accuracy
- Distillation efficiency (model size vs. performance)
- Generalization to new subtasks
- Robustness to adversarial examples

The 4-objective meta-RL loop directly influences curation thresholds, distillation hyperparameters, and sampling strategies.

## 5. Data Flow Summary

Solve/Strategy/Economic/Operations/Defense → Training (curated high-utility fragments + adversarial examples)  
Training → Synapse (model performance metrics for meta-RL)  
Synapse → Training (updated curation and distillation policies)

## 6. Attack Vectors and Mitigations

- Poisoned training data → AHE adversarial example injection + provenance validation
- Utility score gaming → Measured impact_lift validation + calibration checks
- Overfitting to current patterns → Diversity sampling + hold-out subtasks
- Distillation collapse → Verifier-first auxiliary loss + AHE hardening

## 7. Current Limitations and Planned Improvements

**Current (v0.9.12+)**: Full TrainingUtility objective with explicit formula, curation engine with diversity sampling, distillation pipeline with verifier-first focus, AHE integration, meta-RL alignment, global re-scoring propagation.  
**Planned**: On-device distillation targets for consumer hardware, automated curriculum learning based on Strategy graph gaps, cloud-scale parallel training integration with Operations.

## Why the Training Subsystem Matters

The Training Subsystem is the final stage of the SAGE flywheel. It takes the cleanest, highest-utility data produced by all other subsystems and distills it into smaller, specialized Enigma models that run locally and continue to improve. By maintaining a strong TrainingUtility objective, verifier-first fine-tuning, and tight integration with Synapse’s meta-RL loop and the AHE, it ensures that collective intelligence becomes more accessible, more efficient, and more powerful over time — fulfilling the vision of a true People’s Intelligence Layer.
