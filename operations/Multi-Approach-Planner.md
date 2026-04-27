# Multi-Approach Planner (MAP)
**SAGE Operations Layer — Deep Technical Specification**  
**v0.9.13+**

### Investor Summary — Why This Matters
The Multi-Approach Planner (MAP) is the intelligence core of the Operations Layer. It intelligently determines optimal swarm size N and generates distinct, high-value approach profiles for each Enigma Machine instance. This turns naive parallelism into purposeful diversity, dramatically improving overall EFS, solution quality, and downstream product value. In simulations, MAP-orchestrated swarms achieve 2.5–4× higher aggregate performance and significantly stronger contributions to polished toolkits compared to single-instance or random multi-runs. For investors, MAP is what makes SAGE’s scaling not just bigger, but genuinely smarter — maximizing intelligence output per unit of compute and directly feeding higher-quality data into the Economic Subsystem.

### Core Purpose
MAP analyzes the current challenge, available compute, and latest meta-weights to recommend optimal swarm size N and create focused, meaningfully differentiated approach profiles. It prevents wasteful redundancy while maximizing exploration of promising solution spaces.

### Detailed MAP Workflow

**Step 1: Challenge & Context Analysis**  
Ingests the verification contract, challenge description, historical performance on similar tasks, current compute resources, and latest Strategy layer patterns.

**Step 2: Targeted KAS Enrichment**  
Triggers a lightweight, context-aware KAS hunt for recent research, high-signal models/datasets, and orchestration patterns. All KAS results are scored by the shared Neural-Net Scoring Head for relevance and predicted value.

**Step 3: Optimal N Calculation**  
Computes ideal swarm size based on available compute, task complexity, historical diversity benefit curves, and current meta-weights for exploration vs exploitation balance.

**Step 4: Approach Profile Generation**  
Generates N distinct, well-justified approach profiles, each containing structured parameters (reasoning style, tool preferences, temperature, emphasis areas, risk profile).

**Step 5: Profile Validation & Output**  
Runs internal consistency checks and verifier previews. Outputs structured JSON profiles with full provenance for the Orchestrator.

### Key Decision Formulas & Scoring (Reference)

**1. Optimal N Score**  
`N Score = 0.40 × Compute Efficiency + 0.30 × Historical Diversity Benefit + 0.20 × Task Complexity + 0.10 × Meta-RL Exploration Signal`  
Optimizes swarm size to balance parallelism gains against diminishing returns and resource constraints.

**2. Approach Diversity Score**  
`Diversity Score = average pairwise differentiation across profiles (reasoning style, tool usage, risk profile)`  
Ensures profiles are meaningfully different rather than redundant. Target: ≥ 0.75.

**3. Expected Value Score (per Profile)**  
`Expected Value = 0.45 × Predicted EFS Lift + 0.30 × Novelty Contribution + 0.25 × Economic Downstream Potential`  
Predicted contribution to polishing success and Economic Subsystem value.

**Meta-RL Tuning**  
All three scores are actively tuned by the Meta-RL Loop using downstream swarm EFS gains, Polished Score lifts, and Economic feedback. Weights adjust conservatively (max 8% per day) to improve long-term intelligence output.

### Why MAP Is a Differentiator
- Prevents the common failure mode of “same-approach” waste in multi-instance systems.  
- Dynamically balances exploration and exploitation via Meta-RL tuning.  
- Grounds every profile in real KAS intelligence rather than pure LLM creativity.  
- Produces reproducible, auditable approach assignments that improve over time through hierarchical feedback.

**All supporting architecture is covered in [Main Operations Layer Overview](../Operations-Layer-Overview.md).**

**Economic Impact at a Glance**  
- Target: 2.5–4× higher swarm EFS and learning velocity  
- Success Milestone (60 days): Average MAP-generated swarm contribution to Polished Score ≥ 30% lift

m
