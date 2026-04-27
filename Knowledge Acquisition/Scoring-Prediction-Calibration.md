# Scoring, Prediction & Calibration
**SAGE Knowledge Acquisition Subsystem — Deep Technical Specification**  
**v0.9.13+**

### Investor Summary — Why This Matters
Scoring, Prediction & Calibration is the quality-control brain of the Knowledge Acquisition Subsystem. It assigns precise multi-dimensional scores to every acquired fragment, predicts its downstream value before integration, filters aggressively, and continuously calibrates KAS itself so that only high-signal knowledge reaches the rest of SAGE. In simulations, this layer improves the effective value of acquired knowledge by 45–70% while dramatically reducing noise and low-value integration. For investors, this is what ensures KAS delivers reliable, high-ROI intelligence — directly boosting EFS, polishing quality, and Economic Subsystem outputs instead of flooding the system with marginal data.

### Core Purpose
This layer evaluates every KAS result with explicit, computable scoring, predicts real-world impact before integration, filters aggressively, records outcomes for calibration, and triggers recursive improvement when drift is detected.

### Detailed Scoring & Calibration Workflow

**Step 1: Multi-Dimensional Scoring**  
Every returned fragment receives the following scores (all normalized 0–1):

- **Relevance**  
  `Relevance = cosine_similarity(context_embedding, fragment_embedding) × freshness_factor`  
  - context_embedding = combined embedding of challenge + approach profile + recent telemetry.  
  - freshness_factor = exponential decay (1.0 for < 3 months → 0.4 for > 2 years).  
  **Purpose**: Measures direct applicability to the current task.

- **Verifier Compatibility**  
  `Verifier Compatibility = (fraction_of_7D_checks_passed_in_sandbox) × consistency_score`  
  - Sandbox run against current 7D verifier contract.  
  - consistency_score = agreement rate with existing high-confidence fragments.  
  **Purpose**: Ensures the fragment can be used without breaking verifiers.

- **Expected EFS Lift**  
  Predicted by the Success Predictor Head (lightweight feed-forward NN).  
  Inputs: fragment embedding, current approach EFS, historical similar fragments.  
  **Purpose**: Forecasts real performance gain before integration.

- **Training / Distillation Utility**  
  `Training Utility = 0.40 × diversity_contribution + 0.35 × rarity_score + 0.25 × predicted_distillation_gain`  
  - diversity_contribution = 1 - cosine similarity to training corpus centroid.  
  - rarity_score = inverse document frequency in global graph.  
  **Purpose**: Measures usefulness for improving base models and LoRAs.

- **Meta-Acquisition Value**  
  `Meta-Acquisition Value = 0.50 × new_pattern_density + 0.30 × tool_introduction_score + 0.20 × calibration_improvement_potential`  
  **Purpose**: Quantifies how much this fragment improves future KAS performance.

- **Overall Confidence / Uncertainty**  
  `Confidence = weighted average of above scores (layer-specific priorities); Uncertainty = 1 - Confidence`

**Step 2: Success Prediction**  
A lightweight Success Predictor Head (feed-forward NN) forecasts downstream outcomes (especially Expected EFS Lift) before any integration decision.

**Step 3: Filtering & Prioritization**  
- High-confidence, high-predicted-value fragments (Fragment Value Score ≥ 0.72 and Confidence ≥ 0.65) are promoted immediately.  
- Low-value items are down-weighted, cached for later, or discarded.  
- High-risk / high-uncertainty fragments are routed to AHE sandboxing for safety.

**Step 4: Post-Integration Calibration**  
After the fragment is used in an EM run, polishing pass, or other layer:  
- Actual outcomes are recorded.  
- **Prediction Error = |Predicted Value - Actual Observed Value|** (tracked per dimension).  
- Error data is fed back into Meta-RL.

**Step 5: Recursive Meta-Improvement**  
Persistent high calibration error or meta-stall signals trigger recursive KAS hunts focused specifically on improving scoring heuristics, the Success Predictor Head, or acquisition strategies themselves.

### Overall Fragment Value Score
`Fragment Value Score = 0.35 × Relevance + 0.25 × Expected EFS Lift + 0.20 × Verifier Compatibility + 0.10 × Training Utility + 0.10 × Meta-Acquisition Value`

**Filtering Rule**: Fragments with Fragment Value Score ≥ 0.72 and Confidence ≥ 0.65 are promoted for immediate use.

### Concrete Example
**During battery optimization polishing**  
KAS returns a new control-theory paper.  
Scoring shows high Relevance and Expected EFS Lift.  
Success Predictor Head forecasts +14% EFS gain.  
Fragment is integrated → actual gain is +12%.  
Calibration error is low, reinforcing trust in the predictor. Meta-RL slightly boosts weights for control-theory cross-domain signals.

### Why Scoring, Prediction & Calibration Are Critical
- Prevents ingestion of low-value or noisy knowledge through explicit, computable filters.  
- Turns raw acquisition into high-ROI intelligence via prediction before integration.  
- Enables continuous self-calibration so KAS remains accurate as the external world and SAGE evolve.  
- Directly protects Economic Subsystem quality by ensuring only well-scored fragments reach polishing and marketplace toolkits.

**All supporting architecture is covered in [Main KAS Overview](../kas/Main-KAS-Overview.md).**

**Economic Impact at a Glance**  
- Target: 45–70% higher effective value from acquired knowledge  
- Success Milestone (60 days): Calibration error ≤ 0.12 across major layers and ≥ 80% of integrated fragments delivering positive EFS contribution

---

### Reference: Key Decision Formulas (Full Definitions)

**1. Overall Fragment Value Score**  
`Fragment Value Score = 0.35 × Relevance + 0.25 × Expected EFS Lift + 0.20 × Verifier Compatibility + 0.10 × Training Utility + 0.10 × Meta-Acquisition Value`  
**Optimizes**: Ranks fragments for immediate use vs. caching vs. discard.  
**Meta-RL Tuning**: Weights refined based on actual downstream EFS and Economic contribution.

**2. Hunt Trigger Score**  
`Hunt Trigger Score = 0.40 × Calibration Drift + 0.30 × Cache Miss Severity + 0.20 × Economic Downstream Potential + 0.10 × Novelty Potential`  
**Cache Miss Severity** = (1 - max semantic similarity to cached items) × importance_weight  
**Optimizes**: Decides whether to trigger a live hunt.  
**Meta-RL Tuning**: Adjusted using historical ROI of hunts.

All variables are normalized 0–1 and computed using embeddings, sandbox tests, historical data, and NN 
