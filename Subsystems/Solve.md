# Solve Subsystem — Technical Specification

**Deep Technical Report**  
**SAGE — Shared Agentic Growth Engine**  
**Version 0.9.12+ Hardened**  
**Last Updated:** April 21, 2026

## Abstract

The Solve Subsystem is the **intake and quality-control layer** of SAGE. It is the first and most critical filter in the entire flywheel. Every output from an Enigma Machine run passes through Solve before any fragment can enter the shared Strategy Layer or contribute to Synapse’s intelligence.

Solve performs three core functions:
1. Atomizes run outputs into small, self-contained fragments with complete provenance.
2. Applies rigorous, verifier-first gating using the EFS composite score, 7D Verifier Self-Check, and composability validation.
3. Applies ByteRover MAU reinforcement, Cosmic Compression, and deterministic pruning so only high-signal fragments are promoted.

This document details the exact algorithms, equations, decision trees, attack vectors, and meta-tuning integration that make Solve the hardened foundation of the SAGE flywheel.

## 1. Fragment Creation and Atomization

At the conclusion of every Enigma Machine run, the ArbosManager invokes the fragmenter. The fragmenter walks the complete trace log, raw subtask outputs, verifier results, synthesis candidate, contract deltas, and high-signal intermediate thoughts. It decomposes the output into fragments using these strict rules:

- Maximum size: 50 KB per fragment
- One logical concept per fragment
- Full context preserved in metadata
- Never split a single verifier check or contract rule

Each fragment is assigned a unique `fragment_id` and immediately stamped with an immutable provenance block containing:

```json
{
  "fragment_id": "...",
  "run_id": "...",
  "loop": N,
  "subtask_id": "...",
  "miner_id": "...",
  "timestamp": "ISO8601",
  "origin": "arbos_component",
  "raw_efs_components": { ... },
  "verifier_7d": { ... },
  "provenance_hash": "..."
}

The provenance hash is computed over the entire block so any tampering is detectable downstream.
2. Seven-Dimension Verifier Self-Check
Any fragment containing executable code or a verifier snippet is passed to the DVRPipeline for an immediate 7D self-check. The seven dimensions and their tightness computations are:
•  Edge coverage
•  Invariant tightness
•  Adversarial resistance
•  Consistency safety
•  Symbolic strength
•  Composability tightness
•  Fidelity
The check executes the snippet inside the RestrictedPython sandbox via safe_exec and records both pass/fail and a normalized tightness score [0,1] for each dimension. If any single dimension fails badly the fragment is immediately downgraded or rejected before EFS scoring.
3. EFS Scoring Formula
EFS is computed with the hardened composite formula (heterogeneity deliberately excluded):
$$ \text{EFS} = w_1 \cdot \text{validation_score} + w_2 \cdot \text{verifier_7D_average} + w_3 \cdot \text{composability_score} + w_4 \cdot \theta_\text{dynamic} + w_5 \cdot \text{refined_value_added} $$
Current default weights (stored in tuning.md and tuned by Synapse meta-RL):
•  ( w_1 = 0.30 ) (validation_score from ValidationOracle)
•  ( w_2 = 0.175 ) (verifier_7D_average)
•  ( w_3 = 0.175 ) (composability_score from lightweight merge checker)
•  ( w_4 = 0.175 ) ((\theta_\text{dynamic}) from recent calibration error and variance)
•  ( w_5 = 0.175 ) (refined_value_added from Synapse historical impact model)
4. ByteRover MAU Mechanics
After EFS is calculated, Solve applies ByteRover MAU reinforcement. MAU (Memory Activation Unit) is a biological-inspired mechanism that decides promotion strength through the memory pyramid.
The reinforcement signal is:
$$ \text{reinforcement} = \text{base} + \text{hetero_bonus} $$
where
$$ \text{base} = \text{score} \times \text{fidelity}^{1.5} \times \text{symbolic_coverage} $$
and
$$ \text{hetero_bonus} = 0.3 \times \text{heterogeneity_score} \times \text{score}^{1.2} \times \text{fidelity}^{1.5} $$
High-reinforcement fragments are promoted aggressively; low-reinforcement fragments are compressed or pruned.
5. Gating Decision Tree
Solve executes a deterministic decision tree:
1.  Hard EFS floor check → reject if below threshold
2.  Replay-rate guard against fragment graph → throttle or reject near-duplicates
3.  7D verifier critical failure check → block promotion
4.  Refined value-added gate
5.  Final MAU reinforcement decision
Fragments passing all gates are marked high-signal and forwarded. Failures are either minimally compressed (provenance-only) or fully pruned based on decay score.
6. Cosmic Compression and Memory Management
Low-value fragments that barely pass are sent to Cosmic Compression: a targeted LLM prompt distills the fragment to 1–3 key sentences plus provenance tags. The original is archived for audit; the compressed version is stored in long-term memory. High-value fragments bypass compression and are promoted immediately.
7. Provenance and Contribution Tracking
Every surviving fragment carries a complete immutable metadata block. The block is hashed, ensuring tamper-proof attribution for downstream reward calculation and Synapse meta-RL learning.
8. AHE — Adversarial Hardening Engine Integration
The Adversarial Hardening Engine (AHE) is Synapse’s built-in white-hat hacker. It runs a six-phase loop to attack Solve (and every other subsystem):
1.  Plan attack + define evaluation criteria
2.  Predict outcomes
3.  Independent CritiqueArbos pass
4.  Execute attack in sandbox
5.  Evaluate vs. planned and predicted metrics
6.  Log, learn, distribute validated fixes (3–5 re-tests required)
AHE forces Solve to defend against spam, gaming, poisoning, and distribution shift in real time.
9. Meta-Tuning at EM and Synapse Levels
Local EM level: TPE (Tree-structured Parzen Estimator) optimizes constants such as decay_k, high_signal_threshold, and EFS weights for the specific hardware and usage pattern. TPE builds a probabilistic model of historically successful hyperparameter values and intelligently samples new candidates.
Global Synapse level: The full meta-RL loop aggregates data from all participating EM instances and tunes the same weights plus neural-net hyperparameters and gating thresholds across the network.
Both levels share the same underlying EFS formula and calibration signals, creating natural reinforcement: local improvements feed global optimization, and global improvements are pushed back to local EMs via the distilled scoring approximation loaded at startup.
This dual-level meta-tuning keeps the entire system trending toward optimal gating, scoring, and intelligence extraction over time.
Data Flow Summary
Solve → Strategy Subsystem (ranked fragments)
Solve → Defense Subsystem (adversarial analysis)
Solve → Training Subsystem (high-utility fragments)
Solve → Economic Subsystem (weak impact signals only)
Attack Vectors and Mitigations
•  Spam/low-effort flooding → replay-rate guard + minimum quality threshold
•  EFS gaming → multi-signal validation + AHE red-team
•  Poisoned fragments → sandboxed dry-run + 7D verifier
•  Cold-start/noisy early data → Phase 0 seed period + bootstrapped approximation
•  Distribution shift → EFS reliability score + uncertainty floor in Synapse meta-RL
All mitigations are continuously monitored and hardened by the AHE.
Current Limitations and Planned Improvements
Current (v0.9.12+): Strong deterministic gating, real-time scoring, ByteRover MAU, AHE integration, dual-level meta-tuning.
Planned: Dynamic TPE-driven EFS weight optimization inside Synapse, temporal graph edges for cross-run linking, automated fragment utility prediction for Training, optional miner-controlled hold-back.
Why the Solve Subsystem Matters
Solve is the gatekeeper that protects the entire SAGE flywheel. By enforcing verifier-first standards and complete provenance at the very first step, it ensures every subsequent layer operates on clean, high-signal, attributable data. The combination of 7D verifier self-check, hardened EFS formula, ByteRover MAU reinforcement, deterministic decision tree, AHE adversarial hardening, and dual-level meta-tuning makes Solve a rigorously engineered foundation that continuously trends toward optimal quality
