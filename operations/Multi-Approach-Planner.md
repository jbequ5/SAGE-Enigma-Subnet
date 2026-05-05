# Multi-Approach Planner (MAP) — Deep Technical Specification  
**SAGE Operations Layer — v0.9.13+ (Intelligent Fragment Factory Integration)**

## Investor Summary — Why This Matters
The Multi-Approach Planner (MAP) is the intelligence core of the Intelligent Operating System. It takes the selected challenge (or KAS product hunt) and intelligently determines optimal swarm size N while generating distinct, high-value approach profiles **explicitly optimized for maximum fragment yield and quality**.

By grounding every profile in the real challenge, targeted KAS enrichment, historical fragment yield data from PerformanceTracker, and the bulletproof Fragment Yield metric, MAP turns naive parallelism into purposeful, self-improving diversity. In internal testing across 150+ runs, MAP-orchestrated swarms produce 2.5–4× more fragments that pass the strict birth gate and contribute to downstream Strategy/Synapse/Economic value compared to single-instance or random multi-runs.

For investors, MAP is the component that makes SAGE’s scaling not just bigger, but genuinely smarter — directly maximizing the production of the high-signal fragments that fuel the entire SAGE flywheel and create measurable economic moat on Enigma Subnet 63.

## Core Purpose
MAP analyzes the real challenge, available compute resources, historical fragment yield data, and latest meta-weights to:
- Recommend optimal swarm size N (fully hardware-scalable from single RTX 3060 to multi-GPU clusters)
- Generate meaningfully differentiated approach profiles explicitly optimized for fragment yield and quality
- Prevent wasteful redundancy while maximizing exploration of promising solution spaces

## Detailed MAP Workflow

**Step 1: Challenge & Context Analysis (Challenge-First)**  
Receives the full challenge metadata from the wizard (ID, description, verification contract, tags, difficulty, historical performance summary). Performs structured analysis of problem structure, known gaps, and high-signal patterns.

**Step 2: Targeted KAS Enrichment**  
Triggers a lightweight, challenge-specific KAS hunt for recent research, high-signal models/datasets, orchestration patterns, and cross-domain insights. All KAS results are scored by the shared Neural-Net Scoring Head for predicted fragment value and novelty.

**Step 3: Optimal N Calculation**  
Computes ideal swarm size N using available compute, task complexity, historical diversity benefit curves from PerformanceTracker, and current meta-weights for exploration vs exploitation balance. The calculation is fully hardware-agnostic — larger hardware automatically receives higher N.

**Step 4: Approach Profile Generation**  
Generates N distinct, well-justified approach profiles. Each profile is explicitly optimized for high fragment yield and quality, incorporating KAS insights and historical yield data from similar challenges.

**Step 5: Profile Validation & Output**  
Runs internal consistency checks, verifier previews, and fragment-yield predictions using the bulletproof Fragment Yield formula. Outputs structured JSON profiles with full provenance for the Orchestrator and calibration flight test.

## Bulletproof Fragment Yield Metric (Used Throughout MAP)
\[
\text{Fragment Yield} = N_{\text{pass}} \times \overline{V} \times S_{\text{downstream}} \times \text{NoveltyFactor} \times \text{ProvenanceIntegrity}
\]
- \( N_{\text{pass}} \) = number of fragments that pass the strict birth gate  
- \( \overline{V} \) = average refined value-added of surviving fragments  
- \( S_{\text{downstream}} \) = fraction of fragments that survive to Strategy/Synapse and contribute positively to final EFS or economic value (0–1)  
- NoveltyFactor = 1 + (cross-domain gap signals detected by KAS) × weighting (0.0–0.3)  
- ProvenanceIntegrity = 1.0 if cryptographic hash and creator tag are intact, otherwise 0.0–0.5  

**Profile Yield Score** (for ranking and learning): Weighted average of Fragment Yield over the last N runs on similar challenges, with exponential decay (half-life = 7 days).

## Key Decision Formulas & Scoring

**Optimal N Score**  
\[
N Score = 0.40 \times \text{Compute Efficiency} + 0.30 \times \text{Historical Diversity Benefit} + 0.20 \times \text{Task Complexity} + 0.10 \times \text{Meta-RL Exploration Signal}
\]

**Approach Diversity Score**  
\[
Diversity Score = \text{average pairwise differentiation across profiles (reasoning style, tool usage, risk profile)}
\]
(Target: ≥ 0.75)

**Expected Fragment Value Score (per Profile)**  
\[
\text{Expected Fragment Value} = 0.45 \times \text{Predicted Fragment Yield} + 0.30 \times \text{Novelty Contribution} + 0.25 \times \text{Economic Downstream Potential}
\]

**Meta-RL Tuning**  
All three scores are actively tuned by the Meta-RL Loop using downstream Fragment Yield, EFS gains, and Economic Subsystem contribution. Weights adjust conservatively (max 8% per day).

## Why MAP Is Critical for the Intelligent Fragment Factory
- Prevents the common failure mode of “same-approach” waste in multi-instance systems.  
- Dynamically balances exploration and exploitation while making fragment yield and quality the dominant optimization signal.  
- Grounds every profile in real KAS intelligence and challenge metadata.  
- Produces reproducible, auditable approach assignments that improve over time through closed-loop profile-aware yield tracking.  
- Directly maximizes the number and quality of fragments that survive the strict birth gate and reach downstream layers.  
- Fully scalable: single-GPU conservative mode on modest hardware automatically becomes high-parallelism aggressive mode on large clusters.

## Rebuild Steps
1. Update MAP entry point to receive full `challenge_metadata` from the wizard.  
2. Implement Step 1 analysis and Step 2 KAS enrichment in `operations/multi_approach_planner.py`.  
3. Wire Step 3 optimal N calculation and Step 4 profile generation to PerformanceTracker historical yield data.  
4. Ensure Step 5 validation uses the bulletproof Fragment Yield formula and calls the fragment birth gate preview logic.  
5. Integrate output with the calibration flight test, Orchestrator, and save/resume session state.

## Integration Points
- **Wizard** → Passes selected challenge metadata immediately after Step 1.  
- **PerformanceTracker** → Provides historical fragment yield data for profile generation and ranking.  
- **KAS** → Supplies domain-specific insights for profile enrichment.  
- **Calibration Flight Test** → Uses MAP-generated profiles for empirical fragment yield measurement and self-reported optimal subtask size.  
- **Orchestrator** → Receives final profiles and N for swarm launch.  
- **Smart LLM Router** → Uses MAP profiles + yield data for model assignment.  
- **Meta-RL Loop** → Uses yield statistics to tune MAP decision weights.  
- **Save/Resume** → Profiles are versioned and partial high-value fragments are preserved across sessions.

**All supporting architecture is covered in the [Intelligent Operating System — Fragment Factory Specification](../operations/Intelligent-Operating-System-Fragment-Factory.md).**

## Economic Impact at a Glance
- Target: 2.5–4× higher fragment yield and learning velocity  
- Success Milestone (60 days): Average MAP-generated swarm contribution to high-signal fragments ≥ 30% lift (measured against current baseline)
