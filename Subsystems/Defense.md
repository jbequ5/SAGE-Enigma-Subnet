# Defense Subsystem — Full Technical Specification
**SAGE — Shared Agentic Growth Engine**  
**v0.9.13+**  
**Last Updated:** April 27, 2026

### Investor Summary — Why This Matters
The Defense Subsystem is the proactive hardening and anti-gaming guardian of SAGE. It continuously attacks the platform — from verifiers and scoring formulas to Economic upgrades and marketplace logic — to discover and fix weaknesses before they can be exploited. By combining lightweight local protection during EM runs with centralized global coordination, it reduces successful gaming attempts by 70–85% in simulations and builds long-term trust with sponsors and participants. For investors, this is the layer that protects the economic flywheel, ensures fairness, and makes SAGE increasingly antifragile as it scales.

### Core Purpose
The Defense Subsystem (RedTeamVault) operates at two complementary levels for both speed and consistency: lightweight local red-teaming during EM runs and deep global coordination in sage-intelligence. It generates adversarial examples, hardening rules, and validated fixes that strengthen every subsystem while feeding learning signals back into Meta-RL.

## Five Core Documents (Navigation)

- **[Adversarial Hardening Engine (AHE)](./defense/Adversarial-Hardening-Engine.md)** — The 6-phase attack generation and fix loop
- **[RedTeamVault & Attack Vectors](./defense/RedTeamVault-and-Attack-Vectors.md)** — Centralized storage and key attack surfaces
- **[Local vs Global Defense](./defense/Local-vs-Global-Defense.md)** — Execution model and coordination
- **[Defense Integration & Flywheel](./defense/Defense-Integration-and-Flywheel.md)** — How Defense strengthens all subsystems
- **[Defense Metrics & Meta-Learning](./defense/Defense-Metrics-and-Meta-Learning.md)** — Scoring, contribution tracking, and continuous improvement

---

## High-Level Architecture

**Global Defense Coordination (sage-intelligence)**  
- Runs the full Adversarial Hardening Engine on aggregated global data.  
- Generates authoritative adversarial examples, attack templates, hardening rules, and verified fixes.  
- Maintains the central RedTeamVault with specialized scoring.  
- Pushes versioned global Defense packages to all EM instances via Operations.

**Local Defense Execution (sage-core, during EM runs)**  
- Uses the latest global package for fast, targeted red-teaming on the current run.  
- Triggered at key moments: after planning/decomposition, after synthesis, on stall detection, and before pushing to feed vaults.  
- Qualified high-contribution miners can enable deeper local passes.  
- Local findings are pushed back to global feed vaults.

**6-Phase AHE Loop (Primarily Global)**  
1. **Plan** — Identify high-value targets using risk scoring and telemetry.  
2. **Predict** — Forecast impact using Neural-Net Scoring Head.  
3. **Critique** — Second-pass review to prevent self-gaming.  
4. **Execute** — Run attacks in fully sandboxed environments.  
5. **Evaluate** — Compare predicted vs actual outcomes.  
6. **Log & Learn** — Store in RedTeamVault and feed Training/Meta-RL.

### Key Attack Vectors (Examples)
- Verifier snippet gaming  
- EFS weight manipulation  
- Fragment replay flooding  
- Synapse recommendation poisoning  
- Economic artifact upgrade exploits  
- Contribution score inflation

All attacks are logged with full provenance.

### Contribution Tracking and Rewards
Successful red-team attacks and fixes (local or global) earn Impact Score credit for the contributor who surfaced the vulnerability. This creates direct incentive to expose edge cases.

### No Leakage and Strong Protection
- Strict sandboxing and provenance on all attacks.  
- High-value artifacts protected by tiered access and selective encryption.  
- All access logged and auditable.  
- Shared intelligence stays inside the community.

**Economic Impact at a Glance**  
- Target: 70–85% reduction in successful gaming vectors  
- Success Milestone (60 days): Average Attack Success Score on hardened components ≤ 0.15

**All detailed mechanics are covered in the linked deep-dive documents above.**
