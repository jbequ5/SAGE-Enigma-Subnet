# SAGE — Platform Architecture

**Shared Agentic Growth Engine for Bittensor Subnet 63**

## Why This Matters to Sponsors and Alpha Holders

SAGE turns the competitive pressure and prize pools of Subnet 63 into a self-reinforcing intelligence flywheel. Sponsors get faster, higher-quality solutions and intelligent challenge-design tooling that advances their roadmaps. Alpha holders benefit from increased subnet value through higher solver success rates, marketplace revenue, and expanded sponsor participation. Miners see their contributions directly rewarded through transparent provenance and contribution scoring. The result is a system where honest participation creates real economic value that flows back to the people who build it.

## Overview

SAGE is the overarching platform that converts individual Enigma Machine runs on Subnet 63 into a compounding, community-owned intelligence system. It is composed of five interconnected subsystems that operate together in a self-reinforcing flywheel:

- **Solve Subsystem** — ingests and gates raw fragments from Enigma Machine runs.  
- **Strategy Subsystem** — mines, ranks, and enriches fragments into usable shared intelligence.  
- **Economic Subsystem** — upgrades raw BD/PD artifacts using intelligence from other subsystems and creates real economic value.  
- **Training Subsystem** — curates high-quality data for the neural net, meta-RL loop, and future Enigma model distillation.  
- **Defense Subsystem** — proactively attacks the system to discover and harden weaknesses.

Each subsystem has its own storage, scoring logic, outputs, access patterns, and internal operations. They interface through narrow, controlled data flows, ensuring purity in training data while preserving economic value and defensive capability.

The Meta-Agent Synapse sits at the heart of the system. It orchestrates the meta-RL loop, learns from every subsystem, and continuously reinjects improvements across the entire platform. The entire system is designed for transparency, safety, steady improvement, and measurable compounding. Every fragment carries full provenance so contribution can be accurately tracked and fairly rewarded — making every participant feel valued for their honest contributions.

## The Five Subsystems

### Solve Subsystem

The entry point that ingests raw outputs from every participating Enigma Machine run and ensures only high-quality fragments enter the shared intelligence.

**How it works:**

Local Enigma Machine instances generate high-signal fragments during each run. These fragments are automatically transmitted to the Solve Subsystem with full provenance metadata.

Upon arrival, fragments pass strict deterministic gates: they must originate from official Subnet 63 challenges or Scientist Mode experiments, meet an EFS floor, demonstrate replay match reproducibility, and show genuine refined value-added. Spamming protection is enforced through rate limits per miner, duplicate detection via embedding similarity, and provenance validation.

Accepted fragments are intelligently split into self-contained units (≤50 KB) and enriched with basic metadata (task type, domain, raw EFS, provenance).

**Contribution Tracking and Rewards:**

Every surviving fragment is immediately credited to the contributor with full provenance. This transparent tracking ensures miners see their exact impact on the shared intelligence and receive fair rewards through contribution scoring. Honest participation is directly valued and incentivized from the very first step.

**Outputs and contribution to the flywheel:**

This subsystem feeds the Strategy Subsystem and (indirectly) the Economic upgrade step. It provides the raw material that powers all downstream intelligence, red teaming, and debrief analysis.

### Strategy Subsystem

The central intelligence hub that mines, ranks, and enriches fragments into highly valuable shared intelligence.

**How it works:**

The Strategy Subsystem takes output from the Solve Subsystem and applies deep graph mining to discover patterns, cross-domain connections, and emergent strategies. Fragments are ranked using a multi-signal system (utilization, replay rate, refined value-added, graph centrality). ByteRover-style reinforcement and Cosmic Compression keep the dataset focused on high-signal intelligence while pruning low-value items.

Rich metadata (task type, domain, provenance, utilization statistics) is added to make the intelligence effective for co-pilot and chat interactions.

**Data Value Transformation and Reinjection:**

By the time data reaches the Strategy Subsystem it has already been filtered, ranked, and enriched. The Meta-Agent Synapse actively learns from this high-value intelligence through its meta-RL loop. Synapse mines patterns, runs self-audits using the Advice Success Score, evaluates real-world performance, and continuously reinjects improvements (new strategies, refined scoring weights, updated contract templates) back into the Strategy Subsystem and other subsystems. This creates a compounding cycle where intelligence becomes measurably smarter with every mission.

**Outputs and contribution to features:**

This subsystem is the primary source of ranked, tagged intelligence used during miner and customer interactions. It powers the chat interface and proactive co-pilot, supplies intelligence for Economic upgrades, and provides data for Training and Defense subsystems. It is the foundation for smart stopping decisions and meta-debrief recommendations.

### Economic Subsystem

The value creation subsystem and economic capstone that turns intelligence into tangible revenue and product outcomes.

**How it works:**

The Economic Subsystem receives raw BD and PD artifacts generated from local runs (sponsor proposals, tools, curricula, services, etc.). It actively upgrades these artifacts by pulling relevant ranked intelligence from the Strategy Subsystem and adversarial insights from the Defense Subsystem.

The upgrade step is a controlled, scripted process: Synapse identifies the most relevant high-signal fragments and patterns from the Strategy Subsystem, injects proven solving strategies, verifier rules, and economic impact data into the raw artifact, and produces a higher-quality version. Revenue, usage, and downstream EFS impact are measured transparently.

Landed proposals and upgraded tools don’t just sit on a shelf — they collect real performance data when used in subsequent EM challenges. This creates a powerful feedback loop: successful proposals generate new, higher-value challenges that feed back into the Solve Subsystem, producing richer data and stronger intelligence.

The Sage Marketplace serves as the authorized monetization channel for these upgraded outputs. It turns collective intelligence into real revenue streams that can fund larger prize pools, attract more sponsors, and expand the subnet’s reach. Business and sponsor integration is supported through data-driven insights that deliver better and faster results on challenges, plus intelligent challenge-design tooling that helps advance roadmaps and co-creation opportunities.

**Contribution Tracking and Rewards:**

Every upgraded BD/PD artifact credits the original contributors through transparent provenance and contribution scoring. Participants see exactly how their solving fragments and intelligence helped generate real economic value and receive fair rewards. This makes every honest contribution feel valued and directly tied to marketplace revenue and landed proposals.

**Outputs and contribution to features:**

This subsystem is the economic capstone of SAGE. Its upgraded BD/PD artifacts and landed proposals drive real-world value, sponsor engagement, and a self-sustaining revenue engine while feeding weak impact signals back to the Strategy Subsystem.

### Training Subsystem

The curated data engine that prepares high-quality input for learning and distillation.

**How it works:**

The Training Subsystem pulls from the Solve, Strategy, and Defense Subsystems via the DataCurationEngine. It applies strict filtering, balancing, augmentation, and trajectory grouping to produce a clean, versioned dataset optimized for the four meta-RL objectives:

- Recognition of Value — how accurately high-signal fragments are identified  
- Implementation of Strategy — how well recommendations improve real runs (measured by the Advice Success Score)  
- Prediction of Impact — how accurate forecasts of future performance are  
- Training Utility — how useful a fragment will be for future Enigma model distillation  

The neural net scoring head runs on rich fragment features and outputs predictions plus uncertainty estimates. Prediction evaluation compares these outputs against actual outcomes to compute calibration error — the primary signal that drives the meta-RL loop. This calibration-aware process ensures the system learns from verified performance rather than proxy metrics, continuously improving its ability to recognize value and predict impact.

**Outputs and contribution to features:**

This subsystem feeds the neural net scoring head and the Meta-Agent Synapse’s meta-RL loop. It ensures the learning systems receive the best possible data feed top to bottom, enabling sophisticated red teaming, smart stopping, and continuous self-improvement that powers the entire flywheel. The curated dataset also serves as the foundation for the Enigma model distillation pipeline, where high-signal trajectories and self-audit outcomes are progressively distilled into smaller, specialized models optimized for verifiable solving problems and designed to run locally on modest hardware.

### Defense Subsystem (RedTeamVault)

The proactive hardening subsystem that attacks the entire SAGE system to discover and fix weaknesses.

**How it works:**

The Defense Subsystem runs targeted red-team attacks against all other subsystems. It plans attacks, predicts outcomes, applies a critique step to prevent gaming, executes in sandbox, evaluates results, and generates validated fixes.

All adversarial data, attack vectors, failure modes, and validation re-test results are stored in the RedTeamVault with specialized scoring.

**No Leakage, Strong Protection, and Confidence**

The Defense Subsystem is the guardian of the entire system. It enforces strict no-leakage rules: fragments can only enter through deterministic gates, high-value artifacts are protected by tiered access and selective encryption, and all access is logged and auditable. It actively defends against scoring gaming, Sybil attacks, and data leakage while continuously hardening the system. Participants can have high confidence that their contributions remain protected, that the shared intelligence stays inside the community, and that honest participation is directly rewarded.

**Outputs and contribution to features:**

This subsystem feeds adversarial examples into the Training Subsystem and the Economic upgrade step, continuously hardening scoring, gates, contracts, and the overall system. It powers the sophisticated red teaming capability and contributes critical data for comprehensive debriefs and smart stopping decisions.

## How the Subsystems Work Together

The five subsystems form two main pipelines that operate in tandem:

**Core Intelligence Pipeline** (Solve → Strategy → Defense → Training)  
Raw fragments are gated, mined into ranked intelligence, hardened through red-teaming, and curated into clean training data for continuous self-improvement.

**Economic Value Pipeline** (Economic + Strategy + Defense)  
Raw BD/PD artifacts are upgraded using intelligence and adversarial insights from Strategy and Defense, then measured for real-world impact. Landed proposals and upgraded tools collect real performance data when used in subsequent EM challenges, feeding richer data back into the Solve Subsystem and strengthening the entire flywheel.

Controlled interfaces and weak feedback loops ensure each subsystem stays focused while contributing to the overall flywheel. The Meta-Agent Synapse orchestrates the meta-RL loop across all subsystems, learning from every mission, every attack, and every upgrade to continuously reinject improvements.

## Key Features and Outputs

The subsystems produce sophisticated, user-facing capabilities as natural outcomes of their coordinated operation:

- **Sophisticated Red Teaming**: Powered by the Defense Subsystem, Synapse proactively attacks contracts, verifiers, composability rules, and the full pipeline. Attacks are planned, predicted, critiqued, executed in sandbox, and validated with 3–5 re-tests. Findings harden the entire system and feed the Training Subsystem.

- **Smart Stopping (Learning Saturation Detector)**: The system monitors EFS improvement rate, calibration error trend, replan cycles, red-team findings, and resource pressure in real time. It recommends graceful early stopping when additional runtime would yield diminishing returns, maximizing learning efficiency on local hardware.

- **Comprehensive End-of-Run Debriefs**: After every mission, a lightweight Synapse meta-analysis generates targeted Scientist Mode recommendations, plateau analysis, and next-action priorities. Debriefs include deep insights from red teaming and smart stopping signals, turning every run into a strategic learning step.

- **High-Value Chat and Co-Pilot Access**: The Strategy Subsystem provides the ranked, richly tagged intelligence that powers real-time strategy suggestions, stall assistance, and proactive co-pilot capabilities during runs. Miners and users get immediate, context-aware help drawn from the shared intelligence.

These features emerge directly from the subsystems working in tandem and are what make SAGE a practical, compounding intelligence layer rather than a static repository.

## Why This Flywheel Is Different

This is not another shared database or static knowledge repository. This is a true self-reinforcing intelligence flywheel composed of five purpose-built subsystems.

Every Enigma Machine run feeds gated fragments into the Solve Subsystem. The Strategy Subsystem turns them into ranked intelligence. The Defense Subsystem proactively hardens the system. The Training Subsystem curates clean data for continuous learning. The Economic Subsystem converts intelligence into real value — landing proposals that collect performance data and marketplace revenue that funds larger prize pools — while feeding impact signals back.

The Meta-Agent Synapse orchestrates the meta-RL loop, learning from every subsystem and continuously reinjecting improvements across the platform. The result is a compounding cycle where intelligence gets measurably smarter with every mission, every attack, and every upgrade. Local innovation is enhanced by collective breakthroughs. Honest contribution is rewarded. And the entire system grows stronger together.

This is the People’s Intelligence Layer — built by the many, owned by the many, and designed so that the people who build it are the ones who win.
