# Meta-RL Value Learning in the Economic Subsystem
**SAGE Intelligence Layer — Deep Technical Specification**  
**v0.9.13+**

The Meta-RL (Meta-Reinforcement Learning) Loop is the **self-improvement engine** of the Economic Subsystem. It continuously learns which data, processes, and configurations create the highest long-term economic value while protecting the intelligence moat and growing participation.

### Core Goal
Discover and amplify the pathways that turn raw Enigma Machine solving data into monetizable products (toolkits, proposals, services) that generate real revenue and strengthen the overall flywheel.

### Dual Neural Net Architecture

**1. Main Intelligence NN (Core Meta-RL Head)**  
Focuses on long-term system health: technical quality, prediction calibration, data valuation accuracy, and participation growth.

**2. Dedicated Value Prediction NN**  
A narrower specialist that predicts revenue impact, attribution, and economic outcomes. Its signal serves as an additional reward term (weighted 0.25–0.35) in the main loop.

This separation gives clean specialization while allowing rich interaction: the Value NN supplies strong economic feedback that the main loop uses to guide broader intelligence improvements.

### Daily Meta-RL Cycle

1. **Outcome Collection**  
   Gather real performance signals from the Economic Subsystem: polishing improvement deltas, 7-day Health Score changes, draft-to-readiness conversion rates, participation metrics (new gap finders, Product KAS hunts), and any available revenue or buyer feedback.

2. **Value NN Evaluation**  
   The Value NN assesses proposed changes and predicts their likely economic impact. It identifies which current scoring components best correlate with positive outcomes.

3. **Weight Proposal & Simulation**  
   TPE + small evolutionary tournament generates candidate weight updates across the Economic Subsystem. These are tested offline against recent historical data to simulate expected gains.

4. **Conservative Update**  
   Only the strongest improvements are applied, with a maximum daily change of 8%. High-impact changes (>5%) receive an additional human review gate. A 48-hour A/B test runs on a small subset of drafts before full deployment.

5. **Feedback & Calibration**  
   Results from the cycle feed back into both neural nets, closing the learning loop. The system steadily discovers high-leverage patterns and refines its own decision-making.

### What the System Learns Over Time

The Meta-RL loop identifies repeatable drivers of value creation, for example:
- High-confidence double-click experiments on commercially blocked gaps tend to produce toolkits with stronger marketplace performance.
- Self-funded Product KAS hunts on persistent gaps yield higher long-term revenue contribution.
- Certain cross-domain fragments (e.g., battery control theory applied to quantum stabilizer decoding) dramatically improve polishing outcomes.
- Specific polishing tactics (heavy contract enforcement + targeted novelty injection) produce better sustained Health Scores.

These insights are automatically translated into updated weights, prioritization rules, and polishing strategies — making the entire Economic Subsystem measurably smarter with every cycle.

### Proxy Metrics (Pre-Revenue Phase)

Until meaningful sales volume exists, the Value NN trains on strong leading proxies:
- Polished Score improvement
- Health Score trajectory
- Draft-to-readiness conversion rate
- Opportunity Ranker prediction accuracy
- Participation growth in high-pain gaps

These proxies enable effective learning from day one and create a smooth transition once real revenue data becomes available.

### Edge Cases & Safeguards

- **Short-termism**: Participation Growth objective acts as a tie-breaker to prevent over-optimization on immediate revenue.
- **Sparse early data**: Bayesian priors and heavy regularization protect against noise.
- **Gaming attempts**: Low-confidence data is heavily penalized; full provenance and audit trails are enforced.
- **Major changes**: Human review gate on any weight shift >5% in high-impact formulas.

### Why This Is SOTA for Value Creation

The dual-NN design + explicit multi-objective optimization allows the system to discover what *actually* creates economic value — not just technical quality — while keeping the core intelligence moat protected. It turns the Economic Subsystem into a true learning organism that gets better at monetizing collective solving intelligence every single day.

**Detailed scoring formulas used throughout the Economic Subsystem are provided in the reference section below for technical completeness.**

---

### Reference: Key Scoring Formulas

**Gap Pain Score**  
`0.35×Frequency + 0.20×Severity + 0.20×Commercial Blocking + 0.25×Intervention Failure Rate / DOUBLE_CLICK`

**BD Relevance Score**  
`0.45×Sponsor/Chat Frequency + 0.30×Demand Velocity + 0.15×Similar Revenue Proxy + 0.10×Conversion Probability`

**Revenue Potential Score** (Opportunity Ranker)  
`0.40×BD Demand Velocity + 0.25×(Gap Pain × Intervention Success) + 0.20×Market Proxy Strength + 0.15×Miner Investment Level`

**Proposal Readiness Score**  
`0.35×BD Relevance Match + 0.25×SAGE Technical Strength + 0.20×Sponsor Fit + 0.15×Verifiability + 0.05×Novelty`

**Impact Score** (Contributor Pool)  
`0.40×Technical Value + 0.30×Data Quality & Confidence + 0.20×Uniqueness + 0.10×Effort`  
(1.5× multiplier for self-funded Product KAS hunts)

**Health Score** (7-Day Refresher)  
`0.35×Usage & Adoption + 0.25×Performance Metrics + 0.20×Buyer Feedback + 0.15×Freshness + 0.05×Compliance`

**Synthesis Improvement Score** (Polishing Loop)  
`0.35×Technical Quality Lift + 0.30×Verifier Tightness Gain + 0.20×Composability & Coherence + 0.15×Revenue Projection Uplift`

--
