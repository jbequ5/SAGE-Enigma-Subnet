# Meta-RL Improvement Loop
**Intelligence Subsystem — Deep Technical Specification**  
**SAGE — Shared Agentic Growth Engine**  
**v0.9.13+ Meta-Learning Upgrade**

**Investor Summary — Why This Matters**  
The Meta-RL Improvement Loop is the central self-improving brain of SAGE. It is the final pass for all data flowing through every layer of the system. It continuously analyzes real outcomes from Enigma Machine runs, Intelligent Operating System telemetry, KAS hunt results, Defense AHE reports, Economic artifacts, and MOPE training results. Using a 5-objective vector (with an optional 6th novelty objective for MOPE models), it proposes safe, versioned, measurable improvements that raise solution quality, fragment value, model performance, and overall flywheel velocity.

This loop turns raw fragments into continuously compounding intelligence. It is what makes SAGE more than a collection of tools — it makes SAGE a living, self-optimizing intelligence substrate.

**The Five Optimization Objectives**  
The loop optimizes the following measurable objectives using real downstream performance as the primary signal:

1. Recognition of Value — Accuracy in identifying high-signal fragments versus noise (measured by correlation with actual EFS lift and downstream reuse success).  
2. Implementation of Strategy (Advice Success Score) — How effectively Synapse recommendations improve real EM runs (measured by post-recommendation EFS delta, replan reduction, and reuse rate).  
3. Prediction of Impact — Accuracy of forecasts about future EFS lift, performance gain, or model improvement.  
4. Training Utility — How useful a fragment will be for future MOPE distillation and model training (measured by downstream model performance gain).  
5. Defense & Robustness — How well the system resists gaming, poisoning, and attack vectors (measured by red-team success rate and Defense Health Score).  

**Optional 6th Objective (Novelty Preservation for MOPE)**  
Maintain a healthy novelty vector across MOPE specialists so the system does not collapse into local optima. Measured by diversity metrics in the distilled model set and cross-domain generalization.

**The 7-Phase Loop Process**  
The Meta-RL loop runs nightly (or on high-signal triggers) and follows this repeatable, auditable process:

**Phase 1 – Collect All Data**  
Pulls high-signal fragments (from Solve), Intelligent Operating System telemetry and profile performance, KAS hunt results, Defense AHE reports, Economic artifacts, and recent MOPE training outcomes from the secure shared vaults.

**Phase 2 – Compute the 5-Objective Vector**  
The Neural-Net Scoring Head evaluates every fragment and run against the five (plus optional sixth) objectives. Real outcomes are compared to predictions to compute calibration error. The primary input signal is the 60/40 EFS scoring pipeline (60% Base EFS via 7D geometric mean + 40% refined value-added with noise penalty).

**Phase 3 – Self-Critique & Pattern Detection**  
Analyzes patterns in low-scoring or poorly calibrated areas. Identifies systematic weaknesses across layers (e.g., under-weighting verifier tightness, weak novelty in MOPE specialists, IOS profile drift, KAS hunt inefficiency).

**Phase 4 – Propose Self-Tweaks**  
Generates concrete, safe proposals: weight adjustments in scoring formulas, gating threshold changes, KAS hunt refinements, IOS profile biases, MOPE training data curation rules, or NN hyperparameter updates.

**Phase 5 – Safe Application & Versioning**  
Low-risk tweaks are auto-applied if they meet strict safety thresholds (global re-scoring tolerance ≤ 0.08). Higher-risk changes are staged for governance review. All changes are versioned and fully reversible.

**Phase 6 – Log & Transparency**  
Full audit trail (before/after metrics, calibration curves, proposed vs. applied tweaks) is written to the Defense Subsystem and made available to contributors.

**Phase 7 – Meta-Stall Reflection & Idea-Bank Recommendation**  
When multi-signal stall detection triggers (calibration error plateau, Advice Success Score stagnation, Training Utility flattening, Flywheel Velocity drop, etc.), the system performs structured reflection, queries the living learning_ideas.md backlog, re-scores top ideas using sandbox replay and NN inference, and generates 1–3 concrete, testable proposals. These are then sandbox-tested by DefenseRedTeam and gated by current tuning.md freedom levels.

**Inputs to the Neural-Net Scoring Head by Subsystem**  
The NN Scoring Head receives the following specific inputs from each major subsystem:

- **Solve / Fragment Pipeline**  
  7D verifier scores, Base EFS (60%), refined value-added (40% with noise penalty), provenance hash, creator_id, em_instance_id, timestamp, local_score.

- **Intelligent Operating System (IOS)**  
  Profile performance metrics (fragment yield per profile), calibration flight test results, swarm size used, concurrent LLM load, smart-stop triggers, save/resume session data.

- **KAS (Knowledge Acquisition System)**  
  Hunt results (relevance, freshness, novelty), domain overlap scores, new tool/model/paper proposals, cache miss rate, success rate of prior hunts.

- **Defense Subsystem**  
  Red-team success rate, Defense Health Score, attack vectors detected, mitigation effectiveness, AHE cycle results.

- **Economic Subsystem**  
  Gap pain scores, BD relevance scores, product/proposal draft readiness, marketplace performance metrics (if any), sponsor interest signals.

- **Graph Mining / Strategy**  
  Centrality scores, community detection results, cross-domain connections, reuse/replay rates, novelty vector metrics.

**Distillation Prep Vault Section**  
After Phase 2 scoring, the loop writes a dedicated training batch to the Distillation Prep Vault (data/training_batches/).  

For each high-utility fragment the following is prepared:  
- Full fragment content + metadata  
- 5-objective NN vector  
- 60/40 EFS breakdown  
- Refined value-added components  
- Provenance hash  
- Decay factor (to prioritize fresh data)  
- Novelty score (for the 6th objective)  

The vault is used directly by the MOPE distillation pipeline to create the next set of process-specialist models. This ensures the training data is clean, weighted, and directly tied to real performance outcomes.

**Why the Meta-RL Improvement Loop Matters**  
This loop is the mechanism that turns every real Enigma Machine run into training data for the entire platform. It is the final pass that upgrades scoring, gating, strategy recommendations, KAS hunts, IOS profiles, MOPE data preparation, and model distillation. It ensures the system gets measurably smarter every day while remaining safe, auditable, and fully reversible.

**Reference: Key Decision Formulas**  

Multi-Objective Calibration Loss  
$$ L = w_1 \cdot \text{MSE_value} + w_2 \cdot \text{MSE_strategy} + w_3 \cdot \text{MSE_impact} + w_4 \cdot \text{MSE_utility} + w_5 \cdot \text{MSE_defense} + \lambda \cdot \text{calibration_penalty} $$

Global Re-scoring Tolerance Check  
If $$ | \text{Local Score} - \text{Global Re-Score} | > 0.08 $$ → flag for AHE review or downgrade.

AHA / Stall Detection  
$$ \text{AHA} = (\text{current_score} - \text{previous_score} > 0.12) \lor (\text{heterogeneity_spike} > 0.78) \lor (\text{calibration_error_plateau} > 3 \text{ cycles}) $$
