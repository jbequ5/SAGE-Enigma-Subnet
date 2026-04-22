# Economic Subsystem — Technical Specification

**Deep Technical Report**  
**SAGE — Shared Agentic Growth Engine**  
**Version 0.9.12+ Hardened**  
**Last Updated:** April 21, 2026

## Abstract

The Economic Subsystem is the value-distribution and incentive layer of SAGE. It converts high-signal intelligence artifacts discovered by Strategy into monetizable or rewardable assets while ensuring honest contribution is accurately measured and rewarded.

It sits downstream of Strategy and upstream of Synapse’s meta-RL loop, closing the economic feedback that makes the “People’s Intelligence Layer” self-sustaining. Every artifact carries full provenance, so contribution scoring is tamper-proof and transparent.

## 1. Core Responsibilities

1. **Artifact Upgrading**  
   High-signal patterns discovered in Strategy are generalized into reusable assets: new contract templates, improved synthesis debate prompts, refined verification rules, or verification snippets. The upgrade process is deterministic and measurable:

   **Artifact Upgrade Algorithm**:
   1. Generalization: Convert concrete fragment into a reusable template using a fixed prompt template + diff generation.
   2. Versioning: Assign semantic version (e.g., v1.2.3) and store the diff from the previous version.
   3. Impact Measurement: Deploy the upgraded artifact in a set of test runs and measure ΔEFS (change in 60/40 final score).
   4. Encryption: Encrypt the artifact with a key derived from the contributor’s ContributionScore proof (only qualifying contributors can decrypt).

   Only artifacts that demonstrate positive measured impact (ΔEFS > threshold) are promoted.

2. **Contribution Scoring** (Full Explicit Formula)

   $$
   \text{ContributionScore} t = \lambda \cdot \text{ContributionScore} {t-1} + (1 - \lambda) \cdot \text{new impact}$$

   where λ = 0.92 (exponential decay factor, tunable by Synapse meta-RL), and

$$
   \text{new impact} = 0.40 \cdot \text{fragment impact} + 0.25 \cdot \text{reuse count} + 0.20 \cdot \text{artifact upgrade value} + 0.15 \cdot \text{telemetryquality}$$

   All four terms are normalized to [0,1]:
   - fragment_impact = downstream EFS lift caused by the fragment (from Strategy’s impact tracking)
   - reuse_count = normalized successful reuses in other runs (decaying count)
   - artifact_upgrade_value = measured ΔEFS from the upgraded artifact in test runs
   - telemetry_quality = completeness and usefulness of operations telemetry provided by the Operations Subsystem (0.0–1.0 scale)

3. **Reward Distribution**

   Prize pool share for participant i:

   $$\text{RewardShare} i = \frac{\text{ContributionScore} i}{\sum j \text{ContributionScore} j}$$

   Rewards include prize pool allocation, priority access to upgraded artifacts, and sponsorship opportunities.

4. **Sage Marketplace Mechanics**

   - Contributors can list upgraded artifacts with an asking price or sponsorship terms.
   - Sponsors can bid or sponsor specific contract domains or high-priority tasks.
   - A tunable marketplace fee (default 5%, stored in `tuning.md`) funds the prize pool or Synapse development.
   - All transactions are recorded with full provenance for auditability.

## 2. Global Re-scoring Tolerance Propagation

The Economic Subsystem inherits Solve’s global re-scoring tolerance check. Any contribution claim where |local_score - global_re_score| > 0.08 has its new_impact multiplied by a penalty factor (default 0.6) and is flagged for AHE review. This prevents weight-fixing and gaming at the economic layer.

## 3. AHE — Adversarial Hardening Engine Integration

The AHE periodically attacks the Economic Subsystem:
- Fake contribution inflation (inflating reuse_count or fragment_impact)
- Low-value artifact promotion (pushing templates with negligible ΔEFS)
- Marketplace manipulation (collusive bidding or fake sponsorships)

All proposed fixes are validated with 3–5 re-tests on hold-out runs before being applied.

## 4. Meta-Tuning Interaction

Synapse’s global meta-RL loop tunes:
- The four ContributionScore weights (0.40 / 0.25 / 0.20 / 0.15)
- The decay factor λ
- Artifact upgrade impact threshold
- Marketplace fee rate
- Penalty factor for tolerance violations

Local EM meta-tuning (TPE) has no direct effect on Economic parameters.

## 5. Data Flow Summary

Strategy → Economic (high-signal patterns and ranked fragments)  
Operations → Economic (telemetry_quality input for contribution scoring)  
Economic → Synapse (contribution scores and impact signals for meta-RL)  
Economic → Marketplace (upgraded artifacts for sale/sponsorship)  
Solve → Economic (weak impact signals only)

## 6. Attack Vectors and Mitigations

- Contribution score gaming → global re-scoring tolerance + AHE red-team
- Artifact upgrade spam → measured ΔEFS validation + version diff review
- Marketplace manipulation → provenance + on-ledger audit trail
- Reward pool draining → contribution score decay and penalty factors

## 7. Current Limitations and Planned Improvements

Explicit contribution scoring formula with all terms defined, artifact upgrade recipe with impact measurement, marketplace mechanics, global re-scoring propagation, AHE integration, dual-level meta-tuning.  

**Planned**: On-chain reward distribution, dynamic marketplace pricing based on impact, automated artifact monetization suggestions, full integration with Bittensor token mechanics.

## Why the Economic Subsystem Matters

The Economic Subsystem is the incentive engine that makes the People’s Intelligence Layer self-sustaining. By converting raw intelligence into measurable contribution, upgraded artifacts, and fair rewards, it ensures that the people who build SAGE are the ones who win. Combined with Solve’s 60/40 gating, Strategy’s ranking, Operations’ orchestration, and Synapse’s meta-RL, it closes the economic flywheel that compounds value for every honest participant.

