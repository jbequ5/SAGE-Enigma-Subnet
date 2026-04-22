# Defense Subsystem — Technical Specification

**Deep Technical Report**  
**SAGE — Shared Agentic Growth Engine**  
**Version 0.9.12+ Hardened**  
**Last Updated:** April 21, 2026

## Abstract

The Defense Subsystem is the white-hat adversarial hardening layer of SAGE, also known as the RedTeamVault and the Adversarial Hardening Engine (AHE). It continuously attacks every other subsystem (Solve, Strategy, Economic, Operations, Training) to surface vulnerabilities, generate adversarial examples, and harden the entire flywheel against gaming, poisoning, spam, and distribution shift.

It operates as a closed 6-phase loop that runs automatically and on-demand, ensuring that the 60/40 scoring, ranking, contribution scoring, orchestration policies, and meta-RL learning remain robust. All attacks and fixes are logged with full provenance for auditability.

## 1. Core Responsibilities

1. **6-Phase Adversarial Hardening Loop (AHE)**

   The core engine runs the following deterministic and repeatable 6-phase loop:

   **Phase 1: Plan Attack**  
   Generate a targeted attack vector (e.g., spam flooding, EFS gaming, graph poisoning, contribution inflation, strategy manipulation) with explicit evaluation criteria and success metrics.

   **Phase 2: Predict Outcomes**  
   Use a small neural-net scoring head to predict how the attack would affect downstream metrics (EFS, RankScore, ContributionScore, telemetry quality).

   **Phase 3: Independent Critique**  
   Run a deterministic CritiqueArbos pass to validate the attack plan against known safety rules and invariants.

   **Phase 4: Execute Attack**  
   Run the attack in a fully sandboxed environment, isolated from production data and scoring.

   **Phase 5: Evaluate Results**  
   Compare actual outcomes against predicted outcomes and compute calibration error.

   **Phase 6: Log, Learn, Distribute Fixes**  
   Log the full attack with provenance, update Synapse meta-RL training data, and propose safe fixes. Fixes are only applied after 3–5 re-tests on hold-out runs.

2. **RedTeamVault**  
   A curated library of adversarial examples, attack templates, and known vulnerabilities, stored with full provenance and searchable by subsystem and attack type.

3. **Continuous Hardening of All Layers**  
   The AHE attacks:
   - Solve’s 60/40 gating, global re-scoring tolerance, and 7D verifier.
   - Strategy’s ranking formula, graph construction, enrichment, and feedback loop.
   - Economic’s contribution scoring, artifact upgrade process, and marketplace mechanics.
   - Operations’ swarm sizing, Smart LLM Router, downscaling logic, and miner input strategy assignment.
   - Training’s data curation and Enigma model distillation pipeline.

4. **Adversarial Example Generation for Training**  
   Generated attacks are turned into high-utility training examples that Synapse uses to improve calibration and robustness of the neural-net scoring head.

## 2. Global Re-scoring Tolerance Propagation

The Defense Subsystem actively tests and hardens Solve’s global re-scoring tolerance (difference > 0.08 flags gaming). Any subsystem that fails the tolerance check during an AHE attack has its outputs downgraded and is flagged for immediate review.

## 3. AHE Integration with Other Subsystems

The AHE has dedicated attack surfaces for every layer and feeds results back into Synapse’s meta-RL loop as one of the four core optimization objectives:
- Recognition of Value (how well attacks are detected)
- Implementation of Strategy (how effectively fixes are applied)
- Prediction of Impact (calibration error on attack outcomes)
- Training Utility (how useful the generated adversarial examples are for Enigma model distillation)

## 4. Data Flow Summary

AHE → All subsystems (targeted attacks)  
All subsystems → AHE (attack results and calibration errors)  
AHE → Synapse (adversarial examples + learning signals)  
Synapse → AHE (updated attack generation policy and fix rules)

## 5. Attack Vectors and Mitigations (Comprehensive)

- **Spam / Low-Effort Flooding** → Replay-rate guard + minimum quality threshold + AHE replay attacks
- **EFS Gaming / Weight Fixing** → Global re-scoring tolerance check + AHE targeted gaming attempts
- **Graph Poisoning** → Provenance validation on every edge + AHE graph poisoning simulations
- **Contribution Score Inflation** → Measured ΔEFS validation + AHE fake contribution attacks
- **Artifact Upgrade Gaming** → Impact measurement in test runs + AHE low-value promotion attacks
- **Swarm Manipulation** → ResourceMonitor safety margins + AHE resource exhaustion attacks
- **Miner Input Strategy Gaming** → A/B validation against actual EFS lift + AHE strategy manipulation tests

All mitigations are continuously monitored and improved by the AHE itself.

## 6. Current Limitations and Planned Improvements

Full 6-phase AHE loop, RedTeamVault, attacks on all subsystems, global re-scoring integration, meta-RL tuning of attack/fix policies, provenance logging.  
**Planned**: On-demand red-team API for external researchers, automated generation of synthetic adversarial training data for Enigma models, integration with cloud-scale Operations for large-fleet hardening.

## Why the Defense Subsystem Matters

The Defense Subsystem is the immune system of SAGE. By continuously attacking every layer with the 6-phase AHE loop, generating adversarial examples, and hardening the system in real time, it ensures that the 60/40 scoring, ranking, contribution scoring, orchestration policies, and meta-RL learning remain robust against gaming, poisoning, and distribution shift. It is the layer that makes the entire People’s Intelligence Layer trustworthy and self-hardening over time.
