# Defense Subsystem — Full Technical Specification
**SAGE — Shared Agentic Growth Engine**  
**v0.9.13+**  
**Last Updated:** April 27, 2026

### Investor Summary — Why This Matters
The Defense Subsystem is the proactive hardening and anti-gaming guardian of SAGE. It continuously attacks the platform — from verifiers and scoring formulas to Economic upgrades and marketplace logic — to discover and fix weaknesses before they can be exploited. In simulations, consistent Defense activity reduces successful gaming attempts by 70–85% and significantly improves overall system robustness, data quality, and long-term trustworthiness. For investors, this is the layer that protects the economic flywheel, builds sponsor and participant confidence, and ensures SAGE remains fair, secure, and defensible as it scales to community size.

### Core Purpose
The Defense Subsystem operates at two complementary levels — lightweight local protection during EM runs and centralized global coordination — to generate adversarial examples, hardening rules, and validated fixes that strengthen every other subsystem in SAGE.

## Five Core Documents (Navigation)

- **[Adversarial Hardening Engine (AHE)](./defense/Adversarial-Hardening-Engine.md)** — The 6-phase attack generation and fix loop
- **[RedTeamVault & Attack Vectors](./defense/RedTeamVault-and-Attack-Vectors.md)** — Centralized storage and key attack surfaces
- **[Local vs Global Defense](./defense/Local-vs-Global-Defense.md)** — Execution model and coordination
- **[Defense Integration & Flywheel](./defense/Defense-Integration-and-Flywheel.md)** — How Defense strengthens all subsystems
- **[Defense Metrics & Meta-Learning](./defense/Defense-Metrics-and-Meta-Learning.md)** — Scoring, contribution tracking, and continuous improvement

---

## High-Level Architecture

**Global Defense (sage-intelligence)**  
- Runs the full Adversarial Hardening Engine on aggregated data from across the network.  
- Maintains the central RedTeamVault with authoritative attack vectors and fixes.  
- Produces and distributes versioned global hardening packages to all EM instances.

**Local Defense (during EM runs)**  
- Uses the latest global package for fast, targeted red-teaming at key checkpoints (post-planning, post-synthesis, stall detection, before feed vault push).  
- Pushes new discoveries and local attack results back to global feed vaults.

This dual-layer design delivers immediate local protection while enabling systematic global strengthening and learning.

### Key Design Principles
- **Proactive Hardening**: Attack the system ourselves before external actors do.  
- **Verifier-First Everywhere**: Every fix and component must survive multiple adversarial re-tests.  
- **Contribution Rewards**: Successful red-team discoveries earn meaningful Impact Score credit.  
- **No Leakage & Strong Sandboxing**: All attacks run in isolated environments with full provenance.  
- **Hierarchical Learning**: Defense telemetry feeds Meta-RL to improve both Defense itself and the broader platform.

**Economic Impact at a Glance**  
- Target: 70–85% reduction in successful gaming vectors  
- Success Milestone (60 days): Average Attack Success Score on hardened components ≤ 0.15

**All detailed mechanics are covered in the linked deep-dive documents 
