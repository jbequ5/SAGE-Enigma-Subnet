# SAGE Core Mechanics Reference

**Single Source of Truth — v0.9.12+**  
**All scoring, gating, contribution, and data-flow definitions**

## 1. Scoring Foundations

**60/40 EFS Split** (used in Solve and propagated everywhere)
- **Base EFS** = 0.40·validation_score + 0.20·verifier_7D_average + 0.20·composability_score + 0.20·θ_dynamic
- **Refined Value-Added** = 0.50·historical_EFS_lift + 0.30·calibration_accuracy + 0.20·reuse_multiplier
- **Final EFS** = 0.60·Base EFS + 0.40·Refined Value-Added

**θ_dynamic** (dynamic calibration factor)
θ_dynamic = 1.0 - (0.6·calibration_error + 0.25·score_variance + 0.15·replan_rate)

**Global Re-scoring Tolerance**
Any proposed change (weight tweak, gating rule, ranking adjustment) that would shift a fragment’s Final EFS by more than 0.08 is automatically flagged for review or rejected. This is the primary anti-gaming mechanism.

## 2. Contribution Scoring
**ContributionScore** (used for rewards and access tiers)
ContributionScore = 0.40·Final EFS + 0.25·utilization_EMA + 0.20·graph_centrality + 0.15·refined_value_added

- Utilization_EMA uses λ = 0.85 decay.
- Graph centrality uses PageRank (damping 0.85).
- Score is re-evaluated globally on every major update with the 0.08 tolerance.

## 3. Key Data Flows

**Core Intelligence Pipeline**
Solve (gated fragments) → Strategy (ranked & enriched) → Defense (adversarial hardening) → Intelligence (Meta-RL + NN Head + distillation) → Synapse (Meta-Agent)

**Economic Value Pipeline**
Raw BD/PD artifacts → Economic (upgrade using Strategy + Defense) → Marketplace → Revenue → larger prize pools → new challenges → Solve

**Feedback Loops**
- Landed proposals generate new challenges that feed Solve.
- Real usage data and EFS impact feed back into Intelligence for calibration.
- Adversarial examples from Defense feed Training.

## 4. Safety & Anti-Gaming Rules
- All fragments must pass deterministic gates in Solve (official challenge, EFS floor, replay match, provenance validation).
- High-value artifacts use tiered access + selective encryption.
- All Meta-RL proposals in Intelligence are subject to global re-scoring tolerance and human/governance gates for major changes.
- Defense Subsystem (AHE) continuously red-teams every layer.

## 5. Contribution & Reward Principles
- Every surviving fragment in Solve is immediately credited with immutable provenance.
- ContributionScore determines reward share in marketplace revenue and access tier to Synapse.
- Honest participation is rewarded; cherry-picking or gaming is penalized via tolerance checks and decay.

All other documents in the suite (Solve, Strategy, Economic, Intelligence, Defense, Operations, VISION, SAGE Architecture) now reference this Core Mechanics Reference for formulas and rules. No formula should appear in multiple places without linking back here.
