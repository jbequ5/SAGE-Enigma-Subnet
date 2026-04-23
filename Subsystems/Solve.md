# Solve Subsystem — Technical Specification

**Deep Technical Report**  
**SAGE — Shared Agentic Growth Engine**  
**Version 0.9.13 Hardened**  
**Last Updated:** April 23, 2026

## Abstract

The Solve Subsystem is the intake and quality-control layer of SAGE. It is the first and most critical filter in the entire flywheel. Every output from an Enigma Machine run passes through Solve before any fragment can enter the shared Strategy Layer or contribute to Synapse’s intelligence.

**Core Scoring Rule**:  
Final fragment score = 0.6 × Base EFS + 0.4 × Refined Value-Added.

This 60/40 split ensures fragments are judged on both immediate quality and predicted future impact, strongly discouraging piggybacking.

Solve runs locally in every EM instance in the sage-core repository to keep instances lightweight and enable high parallelism. Only gated fragments are pushed to secure feed vaults for central processing by global Strategy and Intelligence in the sage-intelligence repository.

## 1. Fragment Creation and Atomization

At the conclusion of every Enigma Machine run, the ArbosManager invokes the fragmenter. The fragmenter decomposes outputs into small self-contained fragments (maximum 50 KB each). Each fragment receives a unique `fragment_id` and an immutable provenance block containing run ID, loop number, subtask ID, miner identity, timestamp, origin, raw EFS components, and 7D verifier results. The block is hashed so any tampering is detectable downstream.

## 2. Seven-Dimension Verifier Self-Check

Any fragment containing executable code or a verifier snippet is passed to the DVRPipeline for an immediate 7D self-check. The seven dimensions are: edge coverage, invariant tightness, adversarial resistance, consistency safety, symbolic strength, composability tightness, and fidelity. The check executes the snippet inside the RestrictedPython sandbox via `safe_exec` and records both pass/fail and a normalized tightness score [0,1] for each dimension. Critical failures cause immediate downgrade or rejection before final scoring.

## 3. Intelligent Fragment Scoring — 60% Base EFS + 40% Refined Value-Added

Final fragment score:

$$
\text{Final Score} = 0.6 \times \text{Base EFS} + 0.4 \times \text{Refined Value-Added}
$$

**Base EFS (60%)** — Immediate execution quality:

$$
\text{Base EFS} = 0.40 \cdot \text{validation score} + 0.20 \cdot \text{verifier 7D average} + 0.20 \cdot \text{composability score} + 0.20 \cdot \theta\text{dynamic}
$$

**θ_dynamic** (dynamic uncertainty gate):

$$
\theta\text{dynamic} = 1.0 - \left( \text{calibration error} \times 0.6 + \text{score variance} \times 0.25 + \text{replan rate} \times 0.15 \right)
$$

- calibration_error = average absolute difference between predicted and actual EFS over recent runs (normalized to [0,1])
- score_variance = standard deviation of recent EFS scores (normalized)
- replan_rate = fraction of recent runs that triggered replanning or stall recovery

**Refined Value-Added (40%)** — Predicted future impact:

$$
\text{Refined Value-Added} = \alpha \cdot \text{historical EFS lift} + \beta \cdot \text{calibration accuracy} + \gamma \cdot \text{reuse multiplier}
$$

Current default coefficients (tuned by Synapse meta-RL):
- α = 0.50 (historical_EFS_lift)
- β = 0.30 (calibration_accuracy)
- γ = 0.20 (reuse_multiplier)

## 4. Global Re-scoring with Tolerance Check

After initial scoring, every fragment is re-scored using the latest global weights and parameters received from Synapse. The re-scoring uses the same 60/40 formula above but with current global values. If the absolute difference between the local score and the global re-score exceeds the tolerance threshold (currently 0.08), the fragment is flagged as a potential weight-fixing or gaming attempt and is downgraded or sent for AHE review.

## 5. ByteRover MAU Mechanics

After final scoring and global re-scoring, Solve applies ByteRover MAU reinforcement:

$$
\text{reinforcement} = \text{base} + \text{hetero bonus}
$$

where

$$
\text{base} = \text{score} \times \text{fidelity}^{1.5} \times \text{symbolic coverage}
$$

and

$$
\text{hetero bonus} = 0.3 \times \text{heterogeneity score} \times \text{score}^{1.2} \times \text{fidelity}^{1.5}
$$

High-reinforcement fragments are promoted aggressively; low-reinforcement fragments are compressed or pruned.

## 6. Gating Decision Tree

Solve runs this deterministic decision tree:

1. Hard final-score floor check (60/40) → reject if below threshold
2. Replay-rate guard against fragment graph → throttle or reject near-duplicates
3. 7D verifier critical failure check → block promotion
4. Global re-score tolerance check → flag or downgrade if difference > 0.08
5. Refined value-added gate (ensures positive predicted future impact)
6. Final MAU reinforcement decision

Fragments passing all gates are marked high-signal and forwarded to secure feed vaults for global processing. Failures are either minimally compressed (provenance-only) or fully pruned based on decay score.

## 7. Cosmic Compression and Memory Management

Low-value fragments are sent to Cosmic Compression: a targeted LLM prompt distills the fragment to 1–3 key sentences plus provenance tags. The original is archived for audit; the compressed version is stored in long-term memory. High-value fragments bypass compression and are promoted immediately to global Strategy.

## 8. Provenance and Contribution Tracking

Every surviving fragment carries a complete immutable metadata block. The block is hashed, ensuring tamper-proof attribution for downstream reward calculation and Synapse meta-RL learning.

## 9. AHE — Adversarial Hardening Engine Integration

The Adversarial Hardening Engine (AHE) is Synapse’s built-in white-hat hacker. It runs a six-phase loop to attack Solve (and every other subsystem) on the global dataset:

1. Plan attack + define evaluation criteria
2. Predict outcomes
3. Independent CritiqueArbos pass
4. Execute attack in sandbox
5. Evaluate vs. planned and predicted metrics
6. Log, learn, distribute validated fixes (3–5 re-tests required)

AHE forces Solve to defend against spam, gaming, poisoning, and distribution shift in real time. Local Defense during runs provides immediate protection and feeds findings upward.

## 10. Meta-Tuning at EM and Synapse Levels

**Local EM level**: TPE (Tree-structured Parzen Estimator) optimizes constants such as decay_k, high_signal_threshold, and the internal EFS weights for the specific hardware and usage pattern.

**Global Synapse level**: The full meta-RL loop aggregates data from all participating EM instances and tunes the 60/40 ratio, the four Base EFS weights, the three Refined Value-Added coefficients, θ_dynamic coefficients, and global re-score tolerance.

This dual-level meta-tuning keeps the entire scoring system trending toward optimal gating, anti-piggybacking protection, and intelligence extraction over time. Updated meta-weights are pushed down from sage-intelligence to local Strategy gates.

## Data Flow Summary

Solve (local) → secure feed vaults → Global Strategy (sage-intelligence)  
Solve → Defense Subsystem (adversarial analysis)  
Solve → Training Subsystem (high-utility fragments)  
Solve → Economic Subsystem (weak impact signals only)

## Attack Vectors and Mitigations

- Spam/low-effort flooding → replay-rate guard + minimum quality threshold
- EFS gaming / weight fixing → global re-score tolerance check + AHE red-team
- Poisoned fragments → sandboxed dry-run + 7D verifier
- Cold-start/noisy early data → Phase 0 seed period + bootstrapped approximation
- Distribution shift → EFS reliability score + uncertainty floor in Synapse meta-RL

All mitigations are continuously monitored and hardened by the AHE.

## Current Limitations and Planned Improvements

**Current (v0.9.13)**: 60/40 scoring split with explicit global re-scoring tolerance, ByteRover MAU, AHE integration, dual-level meta-tuning, local gating for EM lightness.  
**Planned**: Dynamic tuning of the 60/40 ratio itself, stronger temporal graph edges, automated fragment utility prediction for Training.

## Why the Solve Subsystem Matters

Solve is the gatekeeper that protects the entire SAGE flywheel. The 60/40 scoring rule — 60% immediate quality + 40% predicted future impact — combined with global re-scoring tolerance and the full set of deterministic gates, makes Solve a rigorously intelligent foundation that continuously trends toward optimal quality control and prevents piggybacking. The combination of 7D verifier self-check, hardened EFS formula, ByteRover MAU reinforcement, deterministic decision tree, AHE adversarial hardening, and dual-level meta-tuning ensures that only high-signal, high-utility fragments advance to global Strategy and the Intelligence Subsystem.
