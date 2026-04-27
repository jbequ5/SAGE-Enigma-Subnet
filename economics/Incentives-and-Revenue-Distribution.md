# Incentives & Revenue Distribution
**SAGE Economic Subsystem — Deep Technical Specification**  
**v0.9.13+**

### Investor Summary — Why This Matters
Incentives & Revenue Distribution is the fairness and motivation layer that makes the entire Economic Subsystem sustainable and scalable. It ensures every meaningful contribution — gap origination, high-quality fragments, Product KAS hunts, and polishing improvements — is transparently tracked and fairly rewarded. In simulations, this model has driven 2.5–4× higher high-quality participation compared to volume-only systems, while maintaining strong alignment with long-term value creation. For investors, this is the mechanism that turns decentralized solving effort into a self-reinforcing flywheel: honest contributors earn real money, sponsors receive high-quality deliverables, and alpha token demand grows as the ecosystem expands and prize pools increase.

### Core Purpose
This subsystem distributes revenue from marketplace sales and sponsor deals in a transparent, merit-based way that rewards quality, effort, and origination while feeding impact signals back into Meta-RL for continuous improvement. It protects against free-riding and gaming through immutable provenance and retroactive scoring.

### Revenue Split Model (25/25/25/25)

On every marketplace sale or sponsor deal, revenue is automatically and transparently split as follows:

- **25% Gap Originator (Locked Cut)**  
  Permanent share for the miner(s) who first surfaced and validated the high-pain gap. This reward is locked at the moment of global acceptance and never diluted.

- **25% BD Pool**  
  Rewards the Business Development effort (Lane 2) that identified the commercial opportunity, enriched the proposal or product, and closed the deal.

- **25% Contributor Pool**  
  Distributed proportionally by **Impact Score** to all miners whose fragments, KAS hunts, double-click experiments, or polishing contributions materially improved the final product.

- **25% Alpha Token Flywheel**  
  Used for buyback and burn, larger prize pools, and ecosystem incentives — directly increasing token value and attracting more participants.

### Impact Score (Contributor Pool Distribution)
**Formula**:  
`Impact Score = 0.40 × Technical Value + 0.30 × Data Quality & Confidence + 0.20 × Uniqueness + 0.10 × Effort`  
(1.5× multiplier for self-funded Product KAS hunts)

**Components**:
- Technical Value (40%): EFS lift, 7D verifier contribution, benchmark improvement.
- Data Quality & Confidence (30%): Double-Click Confidence Score and verifier self-check tightness.
- Uniqueness (20%): Novelty and cross-domain resonance.
- Effort (10%): Self-funded compute and volume of useful contributions.

Scores are calculated at ingestion and **retroactively updated** when real performance data (sales, Health Score changes, buyer feedback) becomes available.

### Anti-Gaming & Fairness Mechanisms
- **Confidence Gates**: Low-confidence experimental data is heavily down-weighted or excluded.
- **Provenance Enforcement**: Immutable chain for every fragment ensures traceability and prevents disputes.
- **Retroactive Adjustments**: Impact Scores are updated after sales or Health Score improvements, rewarding long-term value.
- **Participation Floor**: Minimum quality thresholds prevent spam while still allowing new contributors to earn.

### Contributor Experience
- **Dashboard Visibility**: Real-time view of personal Impact Score, contribution history, and earnings per product.
- **Notifications**: Clear alerts such as “Your contribution to Quantum Stabilizer Toolkit helped generate $85k — you earned $X this month.”
- **Payout Flow**: Automatic, periodic distributions with full audit trail.

### Concrete Worked Revenue Example
**Product**: Quantum Stabilizer Code Optimization Toolkit — sold for $85,000.

**Distribution**:
- Gap Originator (Miner A): **25%** = **$21,250** (locked)
- BD Pool: **25%** = **$21,250**
- Contributor Pool ($21,250):
  - Miner A (strong KAS + fragments): Impact Score 1.48 → **$9,800**
  - Miner B (solid fragments): Impact Score 0.67 → **$4,430**
  - Miner C (high-confidence double-click): Impact Score 0.92 → **$6,080**
  - Global Synapse enrichment: Impact Score 0.45 → **$940**
- Alpha Token Flywheel: **25%** = **$21,250**

**Total**: $85,000 (100%)

### Why This Incentive Model Works
- **Strong Alignment**: Rewards origination, quality, and effort — not just volume.
- **Long-Term Compounding**: Retroactive updates mean early contributors continue earning as products improve.
- **Participation Flywheel**: Transparent rewards encourage more miners to run careful experiments and invest compute in promising gaps.
- **Economic Flywheel Closure**: Alpha token share increases token demand, funds larger prize pools, and attracts more participants and sponsors.

**Economic Impact at a Glance**  
- Target: 2.5–4× increase in high-quality participation within 90 days  
- Success Milestone (60 days): Average Impact Score accuracy ≥ 0.85 (correlation with actual revenue)  
- Projected: Sustainable contributor earnings that scale with marketplace growth and alpha value

**All supporting scoring formulas are centralized in [Pipeline-and-Scoring.md](../Pipeline-and-Scoring.md).**

---

