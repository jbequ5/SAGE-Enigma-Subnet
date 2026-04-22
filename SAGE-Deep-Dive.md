# SAGE — Platform Architecture

**Shared Agentic Growth Engine for Bittensor Subnet 63**

## Why This Matters
SAGE turns the competitive pressure and prize pools of Subnet 63 into a genuine self-reinforcing intelligence flywheel. Sponsors receive faster, higher-quality solutions and intelligent challenge-design tooling that advances their roadmaps. Alpha holders benefit from increased subnet value through higher solver success rates, marketplace revenue, and expanded sponsor participation. Miners see their honest contributions directly rewarded through transparent provenance tracking and contribution scoring. The system is designed so that real participation creates measurable economic value that flows back to the people who build it.

## Overview
SAGE converts individual Enigma Machine runs into a compounding, community-owned intelligence system. It consists of five interconnected subsystems that operate in a self-reinforcing flywheel:

- **Solve Subsystem** — strict ingestion and gating of raw fragments.
- **Strategy Subsystem** — mining, ranking, and enrichment of fragments into usable intelligence.
- **Economic Subsystem** — upgrading BD/PD artifacts and creating real economic value.
- **Intelligence Subsystem** — the underlying meta-improvement engine that powers Synapse.
- **Defense Subsystem** — proactive red-teaming and hardening.

**Synapse** is the Meta-Agent — the customer-facing and miner-facing access point. It provides the chat interface, proactive co-pilot, real-time strategy suggestions, and stall assistance. Synapse is powered by the Intelligence Subsystem and orchestrates improvements across the entire platform.

Every fragment carries full provenance. Data flows are narrow and controlled. See Core Mechanics Reference for all scoring formulas and rules.

## The Five Subsystems

### Solve Subsystem
The strict entry point that ingests raw outputs from every participating Enigma Machine run and ensures only high-quality fragments enter the shared intelligence.

**How it works**:
- Fragments arrive with complete provenance metadata.
- They must pass deterministic gates: official challenge/experiment origin, minimum EFS floor, replay reproducibility, and genuine refined value-added.
- Spamming is blocked via per-miner rate limits, embedding-based duplicate detection, and provenance validation.
- Accepted fragments are atomized into self-contained units (≤50 KB) and enriched with basic metadata.

**Contribution Tracking and Rewards**:
Every surviving fragment is immediately credited to its contributor with immutable provenance. This transparent tracking ensures miners see their exact impact and receive fair rewards through ContributionScore.

**Outputs**:
Clean, gated fragments fed to the Strategy Subsystem and (selectively) weak impact signals to the Economic Subsystem.

### Strategy Subsystem
The central intelligence hub that mines, ranks, and enriches fragments into highly valuable shared intelligence.

**How it works**:
- Uses NetworkX graph mining (Leiden community detection, motif discovery) to uncover patterns and cross-domain connections.
- Ranks fragments using a multi-signal system that includes the 60/40 EFS split, utilization, replay rate, and graph centrality.
- ByteRover-style reinforcement and Cosmic Compression keep the dataset focused on high-signal content.
- Rich metadata (task type, domain, provenance, utilization statistics) is added for immediate usability.

**Outputs**:
Ranked, richly tagged intelligence that powers Synapse’s chat interface, proactive co-pilot, Economic upgrades, and data for Training and Defense subsystems.

### Economic Subsystem
The value creation and economic capstone subsystem that turns intelligence into tangible revenue and product outcomes.

**How it works**:
- Receives raw BD/PD artifacts (proposals, tools, curricula, services) from local runs.
- Upgrades them by pulling relevant ranked intelligence from Strategy and adversarial insights from Defense.
- The upgrade process is controlled and scripted: Synapse identifies the most relevant high-signal fragments and patterns, injects proven solving strategies, verifier rules, and economic impact data, and produces a higher-quality version.
- Measures real-world usage, revenue, and downstream EFS impact transparently.
- Landed proposals generate new challenges that feed back into Solve, closing the loop.
- The Sage Marketplace serves as the authorized monetization channel.

**Contribution Tracking and Rewards**:
Every upgraded artifact credits original contributors through provenance and ContributionScore. Participants see exactly how their fragments helped generate economic value and receive fair rewards.

**Outputs**:
Upgraded BD/PD artifacts, landed proposals, marketplace revenue, and impact signals that strengthen the flywheel.

### Intelligence Subsystem
The underlying meta-improvement engine that powers Synapse.

**How it works**:
This subsystem contains three tightly coupled pillars:

1. **Meta-RL Improvement Loop** — closed self-critique engine that evaluates past recommendations against four objectives using real downstream outcomes and calibration error.
2. **Neural-Net Scoring Head** — learnable brain that takes rich fragment features and outputs predictions for the four objectives plus uncertainty estimates. Calibration error drives its continuous improvement.
3. **Training/Distillation Pipeline** — curates high-utility data and progressively distills it into smaller, specialized Enigma models optimized for verifiable solving problems and designed to run locally on modest hardware.

Synapse (the Meta-Agent) orchestrates this subsystem and uses its outputs to deliver better real-time assistance and smarter strategies.

**Outputs**:
Continuous self-improvement of scoring, strategies, and models across all subsystems, plus progressively better local Enigma models.

### Defense Subsystem (RedTeamVault)
The proactive hardening subsystem that attacks the entire SAGE system to discover and fix weaknesses before they can be exploited.

**How it works**:
Runs targeted red-team attacks against contracts, verifiers, scoring mechanisms, and data flows. Plans attacks, predicts outcomes, applies a critique step to prevent gaming, executes in sandbox, evaluates results, and generates validated fixes. All adversarial data is stored in the RedTeamVault with specialized scoring.

**No Leakage and Strong Protection**:
Enforces strict no-leakage rules: fragments can only enter through deterministic gates, high-value artifacts are protected by tiered access and selective encryption, and all access is logged and auditable. Participants can have high confidence that their contributions remain protected and that the shared intelligence stays inside the community.

**Outputs**:
Adversarial examples for Training and Economic upgrade steps, plus continuous hardening of the entire platform.

## Example End-to-End Flow
A miner runs an Enigma Machine mission on a quantum circuit optimization challenge and produces a fragment with Final EFS = 0.82. Solve gates it, credits the miner, and passes it to Strategy. Strategy ranks it highly and enriches it with graph connections. Intelligence uses it to improve the Neural-Net Scoring Head and distill a better local model. Economic upgrades a sponsor proposal using this intelligence, lands it with a sponsor, and generates revenue that increases prize pools. The new challenge data flows back into Solve. Synapse surfaces the improved strategy to other miners in real time. The entire loop is logged with full provenance so contribution is accurately rewarded.

## Operations — The Operating System Layer
Operations is not a traditional subsystem — it is the operating system that manages scaling, setup, and execution. It includes the 0.9.10 Streamlit wizard (compute selection, smart LLM router with downscaling, budget setting, flight test ping-only validation, autonomy mode), swarm orchestration, and telemetry collection that feeds the Intelligence Subsystem. It enables everything from a solo miner running one instance to a large operation running many instances with A/B testing of miner input strategies.

## Why This Flywheel Is Different
This is a true self-reinforcing intelligence flywheel. Every Enigma Machine run feeds gated fragments into Solve. Strategy turns them into ranked intelligence. Defense hardens the system. Intelligence continuously improves itself through its three pillars. Economic converts intelligence into real value — landing proposals that collect performance data and marketplace revenue that funds larger prize pools — while feeding impact signals back.

The result is a compounding cycle where intelligence gets measurably smarter with every mission, every self-audit, and every reuse. Local innovation is enhanced by collective breakthroughs. Honest contribution is rewarded through transparent provenance and ContributionScore. And the entire system grows stronger together.

This is the People’s Intelligence Layer — built by the many, owned by the many, and designed so that the people who build it are the ones who win.
