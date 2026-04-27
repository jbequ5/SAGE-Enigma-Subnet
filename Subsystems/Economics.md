# SAGE Economic Subsystem — Full Technical Specification
**v0.9.13+**  
**Last Updated:** April 27, 2026

### Investor Summary — Why This Matters
The Economic Subsystem is the primary value-creation and revenue engine of SAGE. It transforms high-signal fragments and persistent gaps from Enigma Machine runs into monetizable outputs — sponsor proposals, gap-specific toolkits, curricula, and services — that deliver immediate ROI to sponsors while compounding intelligence across the network. In simulations, polished outputs from this subsystem achieve 45–65% higher revenue contribution than raw drafts, with strong repeat purchase rates from family variants. For investors, this is the clearest mechanism that turns collective solving intelligence into recurring revenue, expanded sponsor activity, new high-value challenges, and sustained alpha token demand.

### Core Purpose
The subsystem converts technical solving data into economic value while maintaining strong, transparent incentives for honest participation and protecting the core intelligence moat. It operates through a tightly integrated pipeline that feeds real performance signals back into Meta-RL for continuous improvement.

## Six Core Documents (Navigation)

- **[Pipeline & Scoring](economics/Pipeline-and-Scoring.md)** — All formulas, rubrics, data acquisition, and Meta-RL tuning
- **[Proposal Creation](economics/Proposal-Creation.md)** — Lane 2 Business Growth workflow and readiness scoring
- **[Product Creation & Toolkits](economics/Product-Creation-and-Toolkits.md)** — Draft accumulation, polishing, family variants, and marketplace mechanics
- **[Incentives & Revenue Distribution](economics/Incentives-and-Revenue-Distribution.md)** — 25% splits, Impact Scoring, contributor rewards, and worked examples
- **[Meta-RL & Value Learning](economics/Meta-RL-and-Value-Learning.md)** — How the system learns to create better value
- **[Synapse Nightly Polishing Loop](economics/Synapse-Nightly-Polishing-Loop.md)** — Continuous improvement mechanics

---

## High-Level Flow

1. **Local EM Runs** → Generate fragments, gap detections, Scientist Mode / DOUBLE_CLICK experiments, and Product KAS hunts.
2. **Product Draft Vault** → Fragments accumulate locally per gap. Miners can trigger targeted KAS enrichment.
3. **Global Synapse Gate** → High-quality drafts are pushed to the central Economic Subsystem.
4. **Synapse Polishing Loop** → Nightly enrichment, Synthesis Arbos refinement, validation, and family variant generation.
5. **Marketplace Listing** → Polished toolkits/proposals are listed with full provenance, benchmarks, and pricing options.
6. **Monetization** → Sales generate revenue that is automatically distributed (25/25/25/25) and feeds impact signals back to Meta-RL.
7. **Learning Loop** → Real performance + proxy metrics train the Value Prediction NN and main Meta-RL loop, continuously improving all scorers and processes.

---

## Key Design Principles

- **Toolkits-First**: Focus depth in high-value gaps before broad parallel products. Successful toolkits spawn family variants.
- **Miner-Funded Effort Rewarded**: No subsidies. Self-funded Product KAS hunts receive clear multipliers.
- **Gap Origination Highly Valued**: Originators of high-pain gaps receive a locked 25% revenue cut.
- **Verifier-First Everywhere**: Every draft and product must pass 7D verifier self-check + executability tests.
- **Immutable Provenance**: Every contribution is traceable. Impact Scores are updated retroactively with real performance data.
- **Continuous Improvement**: Synapse nightly polishing + 7-day health checks keep everything fresh.
- **No Leakage**: High-value upgraded artifacts are protected by tiered access and selective encryption. Only participating contributors benefit inside their local EM runs.

---

## Revenue Model (25/25/25/25)

On every marketplace sale:
- **25% Gap Originator** — Locked permanent cut for the miner(s) who first surfaced the high-pain gap.
- **25% BD Pool** — Rewards the effort that drove the commercial opportunity and closed the deal.
- **25% Contributor Pool** — Distributed proportionally by Impact Score (technical value, confidence, novelty, effort).
- **25% Alpha Token Flywheel** — Buyback/burn + ecosystem incentives.

**Impact Score Formula** (Contributor Pool):  
`0.40 × Technical Value + 0.30 × Data Quality & Confidence + 0.20 × Uniqueness + 0.10 × Effort` (1.5× multiplier for self-funded Product KAS hunts)

---

## Why This Subsystem Works

It creates a self-reinforcing flywheel:
- Better EM runs → richer gaps & fragments
- Stronger Synapse polishing → higher-quality toolkits & proposals
- Successful marketplace sales → real revenue + impact signals
- Meta-RL learns from outcomes → better scoring, better prioritization, better products
- Stronger incentives → more participation → richer data

The Economic Subsystem turns the People’s Intelligence Layer into a genuine economic engine that rewards honest contributors, delivers measurable value to sponsors, and increases alpha token demand — while keeping the core intelligence protected and compounding.

**All detailed scoring, workflows, and mechanics are covered in the linked deep-dive documents above.**
