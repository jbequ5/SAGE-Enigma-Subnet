# Synapse Nightly Polishing Loop
**SAGE Economic Subsystem — Deep Technical Specification**  
**v0.9.13+**

The Synapse Nightly Polishing Loop is the **continuous improvement engine** of the Economic Subsystem. It runs once per day and systematically upgrades open drafts and live marketplace products using the full global intelligence of SAGE.

### Core Purpose

The polishing loop ensures that SAGE products do not become stale. It turns good drafts into excellent, marketplace-ready toolkits and keeps live products fresh and competitive. This continuous refinement is what drives sustained revenue, buyer trust, and compounding value in the flywheel.

### High-Level Workflow

1. **Prioritization** — Opportunity Ranker selects the most promising items.
2. **Enrichment** — Pulls latest relevant intelligence.
3. **Synthesis Arbos Pass** — Core intelligence amplification step.
4. **Benchmark & Validation** — Ensures quality and executability.
5. **Variant Generation** — Creates family extensions from strong products.
6. **Decision & Routing** — Updates listings, feeds learning signals, and notifies contributors.

This loop runs automatically every night, creating measurable improvement with every cycle.

### Why This Loop Matters

- It turns fragmented local work into polished, high-value products that actually sell.
- It keeps the marketplace dynamic and trustworthy.
- It feeds real performance data back into Meta-RL, making the entire Economic Subsystem smarter over time.
- It rewards contributors whose work continues to improve products long after initial creation.

### Detailed Process Flow

**Step 1: Prioritization (Opportunity Ranker)**  
Every eligible draft and live product is ranked by Revenue Potential Score. Only the top items receive full polishing passes. This prevents wasting compute on low-potential work.

**Step 2: Enrichment**  
Targeted KAS hunts and Strategy layer retrieval bring in the freshest, most relevant fragments and patterns.

**Step 3: Synthesis Arbos Pass**  
The heart of the loop. Multiple proposals are generated, debated, refined, and enforced against the product contract. This is where global intelligence is deeply injected.

**Step 4: Benchmark & Validation**  
Full 7D verifier self-check, executability tests, and benchmark updates ensure the polished version is production-ready.

**Step 5: Family Variant Generation**  
Strong products automatically spawn lighter or specialized variants, expanding their reach.

**Step 6: Final Decision & Routing**  
The polished item receives a Final Polished Score that determines promotion, listing updates, or de-listing. Impact Scores for contributors are updated, and signals flow to Meta-RL.

### Post-Polish Integration

- Health Score (7-day refresher) is recalculated.
- Contributor Impact Scores are retroactively adjusted based on improvement.
- Strategy and Intelligence layers receive enriched patterns for future learning.
- Miners receive clear notifications about how their contributions helped.

This creates a true compounding cycle: better products → stronger signals → smarter polishing → even better products.

**All detailed scoring formulas used in the polishing loop are provided in the reference section below.**

---

### Reference: Key Scoring Formulas

**Revenue Potential Score** (Opportunity Ranker)  
`0.40 × BD Demand Velocity + 0.25 × (Gap Pain × Intervention Success) + 0.20 × Market Proxy Strength + 0.15 × Miner Investment Level`

**Enrichment Quality Score**  
`(new relevant fragments added / expected) × freshness weighting`

**Synthesis Improvement Score**  
`0.35 × Technical Quality Lift + 0.30 × Verifier Tightness Gain + 0.20 × Composability & Coherence + 0.15 × Revenue Projection Uplift`

**Validation Strength Score**  
Average normalized 7D scores + benchmark improvement % + executability pass rate

**Final Polished Score**  
`0.30 × Enrichment Quality + 0.35 × Synthesis Improvement + 0.25 × Validation Strength + 0.10 × Variant Potential (if generated)`

**Health Score** (7-Day Refresher)  
`0.35 × Usage & Adoption + 0.25 × Performance Metrics + 0.20 × Buyer Feedback + 0.15 × Freshness + 0.05 × Compliance`

**Decision Thresholds**  
- ≥ 0.82 → Excellent (promote)  
- 0.65 – 0.81 → Healthy (update)  
- 0.45 – 0.64 → Warning (heavy polish)  
- < 0.45 → De-list / Archive
