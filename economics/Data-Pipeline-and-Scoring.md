# Pipeline & Scoring — Economic Subsystem
**SAGE — Shared Agentic Growth Engine**  
**v0.9.13+**  
**Last Updated:** April 27, 2026

### Investor Summary — Why This Matters
The scoring pipeline is the decision-making nervous system of the Economic Subsystem. It determines which gaps receive attention, which drafts get polished, which contributors earn rewards, and which products reach the marketplace. Well-tuned scoring directly accelerates revenue while reducing wasted effort. In replay simulations, Meta-RL improvements to these scorers have increased average toolkit revenue contribution by 40–65% and cut low-value polishing compute by more than 50%. This is the measurable mechanism that turns collective solving intelligence into predictable economic return with lower risk.

### Core Purpose
This document serves as the single source of truth for every major scoring formula in the Economic Subsystem. Each score includes:
- Exact formula
- What it optimizes
- **How business data is acquired** (sources and methods)
- Meta-RL tuning notes

All scores are normalized 0–1 unless otherwise noted and are updated daily.

### How Business Data Flows Into the Pipeline
Business data is continuously collected from multiple sources:
- Enigma Machine runs (fragments, EFS, DOUBLE_CLICK experiments)
- Synapse Chat / Copilot interventions
- Product KAS hunts (miner-funded web + internal enrichment)
- BD Hunter (automated scraping of sponsor roadmaps, industry reports, public pain points)
- Marketplace usage telemetry and buyer feedback
- Strategy & Intelligence layer global graph patterns

This data is aggregated nightly and used to update all scores.

---

### Key Scoring Formulas & Data Acquisition

**1. Gap Pain Score** — Identifying High-Value Problems  
**Formula**: `0.35 × Frequency + 0.20 × Severity + 0.20 × Commercial Blocking + 0.25 × Intervention Failure Rate / DOUBLE_CLICK`  
**Optimizes**: Prioritizes gaps that are frequent, painful, commercially relevant, and resistant to quick fixes.  
**Business Data Acquisition**:  
- Frequency & Severity: From EM run logs, Scientist Mode DOUBLE_CLICK triggers, and stall analysis.  
- Commercial Blocking: From BD Hunter scans of sponsor roadmaps, chat/copilot queries, and marketplace search volume.  
- Intervention Failure: From DOUBLE_CLICK experiments and Synapse intervention logs.  
**Threshold**: ≥ 0.78 triggers Product KAS recommendations.  
**Meta-RL Tuning**: Adjusts component weights based on correlation with actual revenue and sponsor interest.

**2. BD Relevance Score** — Market Signal Strength (Lane 1 — PD Data Optimization)  
**Formula**: `0.45 × Sponsor/Chat Frequency + 0.30 × Demand Velocity + 0.15 × Similar Revenue Proxy + 0.10 × Conversion Probability`  
**Optimizes**: Quantifies how commercially promising a gap is.  
**Business Data Acquisition**:  
- Sponsor/Chat Frequency & Demand Velocity: Direct from Synapse Chat logs, copilot interventions, and sponsor query history.  
- Similar Revenue Proxy: From historical marketplace sales and external KAS scans of comparable products.  
- Conversion Probability: Learned from past proposal landing rates.  
**Meta-RL Tuning**: Learns which signals (chat vs. external searches) best predict closed deals.

**3. Revenue Potential Score** (Synapse Opportunity Ranker)  
**Formula**: `0.40 × BD Demand Velocity + 0.25 × (Gap Pain × Intervention Success) + 0.20 × Market Proxy Strength + 0.15 × Miner Investment Level`  
**Optimizes**: Decides nightly polishing priority and global push-down.  
**Business Data Acquisition**: Combines outputs from Gap Pain, BD Relevance, KAS results, and miner investment logs (self-funded hunts).  
**Meta-RL Tuning**: Directly tied to expected revenue — strongest economic signal in the system.

**4. Proposal Readiness Score** (Lane 2 — Business Growth)  
**Formula**: `0.35 × BD Relevance Match + 0.25 × SAGE Technical Strength + 0.20 × Sponsor Fit + 0.15 × Verifiability + 0.05 × Novelty`  
**Optimizes**: Determines when a proposal is sponsor-ready.  
**Business Data Acquisition**: BD Relevance from Lane 1 + technical metrics from EM runs + sponsor fit from BD Hunter matching.  
**Threshold**: ≥ 0.75 for sponsor outreach or marketplace listing.  
**Meta-RL Tuning**: Learns which factors best predict landing rates.

**5. Impact Score** (Contributor Pool — 25% of Revenue)  
**Formula**: `0.40 × Technical Value + 0.30 × Data Quality & Confidence + 0.20 × Uniqueness + 0.10 × Effort`  
(1.5× multiplier for self-funded Product KAS hunts)  
**Optimizes**: Fairly distributes rewards based on real contribution to value.  
**Business Data Acquisition**: Technical Value from EFS/7D, Confidence from DOUBLE_CLICK scores, Effort from KAS compute logs.  
**Meta-RL Tuning**: Retroactively adjusts using real sales and Health Score performance.

**6. Health Score** (7-Day Refresher)  
**Formula**: `0.35 × Usage & Adoption + 0.25 × Performance Metrics + 0.20 × Buyer Feedback + 0.15 × Freshness + 0.05 × Compliance`  
**Optimizes**: Monitors live product quality.  
**Business Data Acquisition**: Usage telemetry, buyer feedback, and polishing history.

**7. Synthesis Improvement Score** (Polishing Loop)  
**Formula**: `0.35 × Technical Quality Lift + 0.30 × Verifier Tightness Gain + 0.20 × Composability & Coherence + 0.15 × Revenue Projection Uplift`

**8. Double-Click Confidence Score** (Quality Gate)  
Weights experimental data (0–1.5×) based on statistical power, reproducibility, design quality, and verifier pass rate.

### Meta-RL Interaction
All formulas are actively tuned daily by the Meta-RL Loop. The Value Prediction NN forecasts revenue impact of proposed changes, ensuring the system maximizes economic return.

**Success Milestones**  
- Month 1: Average Pipeline Health ≥ 0.72  
- Month 3: Average Proposal Readiness ≥ 0.82 and 40%+ revenue contribution lift from polishing
