# SAGE — Platform Architecture

**Shared Agentic Growth Engine for Bittensor Subnet 63**

## Why This Matters
SAGE turns the competitive pressure and prize pools of Subnet 63 into a genuine self-reinforcing intelligence flywheel. Sponsors receive faster, higher-quality solutions and intelligent challenge-design tooling that advances their roadmaps. Alpha holders benefit from increased subnet value through higher solver success rates, marketplace revenue, and expanded sponsor participation. Miners see their honest contributions directly rewarded through transparent provenance tracking and contribution scoring. The system is designed so that real participation creates measurable economic value that flows back to the people who build it.

## Overview
SAGE converts individual Enigma Machine runs into a compounding, community-owned intelligence system. It consists of five interconnected subsystems that operate in a self-reinforcing flywheel. See core-mechanics.md for all scoring formulas and data flows.

The system uses two repositories for clarity, safety, and performance:
- **sage-core**: Execution runtime focused on lightweight local operation (Enigma Machine, Solve, lightweight local Strategy and Defense during runs for qualified users, Economic raw artifact generation, Operations).
- **sage-intelligence**: Central privileged brain containing Synapse (the Meta-Agent) and the full Intelligence Subsystem.

Local EM instances remain lightweight to enable high parallelism and efficient Solve data production. They apply Solve gates locally, run lightweight Strategy and Defense passes when qualified, generate raw Economic artifacts, and push gated fragments, telemetry, and raw BD/PD data to secure feed vaults. sage-intelligence pulls from the vaults, performs global Strategy (graph mining and ranking on the full aggregated dataset), global Defense coordination, daily Meta-RL loops, and all self-improvement functions, then pushes global approximations, meta-weights, distilled models, and consistent Defense packages back down.

**Synapse** is the Meta-Agent — the customer-facing and miner-facing access point. It provides the chat interface, proactive co-pilot, real-time strategy suggestions, and stall assistance. Synapse is powered by the Intelligence Subsystem and orchestrates improvements across the entire platform using the global view of all data.

Every fragment carries full provenance. Data flows are narrow and controlled. High-value artifacts are protected by tiered access and selective encryption.

## The Five Subsystems

### Solve Subsystem
The strict entry point that ingests raw outputs from every participating Enigma Machine run and ensures only high-quality fragments enter the shared intelligence. Runs locally in every EM instance.

**How it works**:
- Fragments arrive with complete provenance metadata.
- They must pass deterministic gates: official challenge/experiment origin, minimum EFS floor, replay reproducibility, and genuine refined value-added.
- Spamming is blocked via per-miner rate limits, embedding-based duplicate detection, and provenance validation.
- Accepted fragments are atomized into self-contained units (≤50 KB) and enriched with basic metadata.

**Contribution Tracking and Rewards**:
Every surviving fragment is immediately credited to its contributor with immutable provenance. This transparent tracking ensures miners see their exact impact and receive fair rewards through ContributionScore.

**Outputs**:
Clean, gated fragments fed to the Strategy Subsystem and (selectively) weak impact signals to the Economic Subsystem. Data is pushed to secure feed vaults for central processing.

### Strategy Subsystem
The central intelligence hub that mines, ranks, and enriches fragments into highly valuable shared intelligence.

**How it works**:
- Lightweight local execution occurs during runs for qualified users (immediate feedback).
- Full global Strategy (NetworkX graph mining, Leiden community detection, motif discovery, ranking, enrichment on the aggregated dataset) runs centrally in sage-intelligence.
- Ranks fragments using a multi-signal system that includes the 60/40 EFS split, utilization, replay rate, and graph centrality.
- ByteRover-style reinforcement and Cosmic Compression keep the dataset focused on high-signal content.
- Rich metadata is added for immediate usability.
- Updated meta-weights are pushed down to local Strategy gates.

**Outputs**:
Ranked, richly tagged intelligence that powers Synapse’s chat interface, proactive co-pilot, Economic upgrades, and data for Training and Defense subsystems.

### Economic Subsystem
The value creation and economic capstone subsystem that turns intelligence into tangible revenue and product outcomes.

**How it works**:
- Receives raw BD/PD artifacts from local runs and pushes them to feed vaults.
- Central upgrade in sage-intelligence pulls relevant ranked intelligence from global Strategy and adversarial insights from global Defense.
- Synapse injects proven strategies, verifier rules, and economic impact data in a controlled upgrade step.
- Measures real-world usage, revenue, and downstream EFS impact transparently.
- Landed proposals generate new challenges that feed back into Solve, closing the loop.
- The Sage Marketplace serves as the authorized monetization channel.

**Contribution Tracking and Rewards**:
Every upgraded artifact credits original contributors through provenance and ContributionScore. Participants see exactly how their fragments helped generate economic value and receive fair rewards.

**Outputs**:
Upgraded BD/PD artifacts, landed proposals, marketplace revenue, and impact signals that strengthen the flywheel.

### Intelligence Subsystem
The underlying meta-improvement engine that powers Synapse and centralizes all intelligence functions.

**How it works**:
This subsystem runs centrally in sage-intelligence and contains three tightly coupled pillars plus meta-stall detection and continuous idea-bank scoring:

1. **Meta-RL Improvement Loop** — closed self-critique engine that evaluates past recommendations against four objectives using real downstream outcomes and calibration error. Includes Phase 7 meta-stall reflection that queries the idea bank and generates proposals.
2. **Neural-Net Scoring Head** — learnable brain that takes rich fragment features and outputs predictions for the four objectives plus uncertainty estimates. Calibration error drives its continuous improvement.
3. **Training/Distillation Pipeline** — curates high-utility data and progressively distills it into smaller, specialized Enigma models optimized for verifiable solving problems and designed to run locally on modest hardware.

Synapse orchestrates this subsystem, maintains learning_ideas.md and tuning.md, and uses its outputs to deliver better real-time assistance and smarter strategies.

**Outputs**:
Continuous self-improvement of scoring, strategies, and models across all subsystems, plus progressively better local Enigma models.

### Defense Subsystem (RedTeamVault)
The proactive hardening subsystem that attacks the entire SAGE system to discover and fix weaknesses before they can be exploited.

**How it works**:
- Lightweight local execution during EM runs for immediate protection (quick passes after planning, synthesis, stall detection, and before pushing to vaults; deeper passes for qualified users).
- Global coordination, rule authoring, adversarial example generation, and consistency enforcement occur centrally in sage-intelligence.
- Updated global packages are pushed down to all local instances.

**No Leakage and Strong Protection**:
Enforces strict no-leakage rules: fragments can only enter through deterministic gates, high-value artifacts are protected by tiered access and selective encryption, and all access is logged and auditable. Participants can have high confidence that their contributions remain protected and that the shared intelligence stays inside the community.

**Outputs**:
Adversarial examples for Training and Economic upgrade steps, plus continuous hardening of the entire platform.

## How the Subsystems Work Together
Local EM instances (sage-core) run Solve gating and lightweight Strategy/Defense, then push data to secure feed vaults. sage-intelligence pulls from the vaults, runs full global Strategy and Defense coordination, performs daily Meta-RL loops (including meta-stall handling), and pushes approximations, meta-weights, distilled models, and global rules back down.

**Core Intelligence Pipeline**: Solve (local) → Strategy (global) → Defense (global) → Intelligence.  
**Economic Value Pipeline**: Raw BD/PD (local) → central upgrade in Intelligence → Marketplace.

Synapse orchestrates improvements across the platform using the global view.

## Operations — The Operating System Layer
Operations is not a traditional subsystem — it is the intelligent operating system layer that makes the entire SAGE platform practical, scalable, and accessible at every level of participation.

It manages the full lifecycle of execution: initial setup, resource allocation, swarm orchestration, package distribution, telemetry collection, and autonomous operation. This layer is what turns SAGE from a single-instance tool into a true data factory capable of running from one local EM instance to hundreds in parallel, all while feeding high-quality signals back into the Intelligence Subsystem.

**Key Capabilities**:
- **0.9.10+ Streamlit Wizard**: Guides users through compute selection, smart LLM router with automatic downscaling as swarm size grows, budget setting, ping-only flight test validation, and autonomy mode configuration.
- **Swarm Orchestration**: Central orchestrator launches and monitors multiple EM instances, assigns different miner input strategies for A/B testing, enforces hard time limits, and triggers smart stopping when learning saturates.
- **Telemetry and Feedback**: Collects rich operations data (swarm size, resource pressure, per-instance performance, A/B test results) and pushes it to secure feed vaults. This telemetry is critical for the Neural-Net Scoring Head and Meta-RL Loop to learn optimal configurations over time (e.g., best LLM per task type for given compute, ideal swarm size, early stopping thresholds).
- **Global Package Distribution**: Reliably delivers updated global approximations, meta-weights, distilled models, and Defense packages from sage-intelligence to all participating EM instances.
- **Lightness and Parallelism**: Ensures baseline EM instances remain minimal (Solve gating + push to vaults) so users can run many parallel instances on modest hardware, maximizing Solve data production and contribution to the flywheels.

Operations is the layer that makes high-scale, efficient participation possible while turning execution telemetry into actionable intelligence. Without it, the system would be limited to single-instance runs and would lose the compounding feedback from large-scale experimentation. It is one of the most intelligent and enabling components of SAGE — the bridge between individual runs and collective self-improvement.

## Example End-to-End Flow
(Previous example remains, now implicitly supported by the Operations layer for scaling and package distribution.)

## The Three Core Flywheels – Deep Dive
(Full mechanics remain integrated for flow.)

## Why This Flywheel Is Different
This is a true self-reinforcing intelligence flywheel. Local execution stays efficient. Global intelligence compounds centrally. Honest contribution is rewarded through transparent provenance and ContributionScore. And the entire system grows stronger together.

This is the People’s Intelligence Layer — built by the many, owned by the many, and designed so that the people who build it are the ones who win.
