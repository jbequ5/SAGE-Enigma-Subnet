# Targeted KAS Hunts & Contextual Search
**SAGE Knowledge Acquisition Subsystem — Deep Technical Specification**  
**v0.9.13+**

### Investor Summary — Why This Matters
Targeted KAS Hunts & Contextual Search is the precision engine of the Knowledge Acquisition Subsystem. It intelligently decides when, what, and how deeply to hunt for new knowledge, avoiding wasteful broad searches while maximizing high-signal returns. In simulations, intelligent targeted hunting improves EFS contribution from acquired knowledge by 40–65% compared to naive or always-on searches. For investors, this is what makes KAS efficient and cost-effective at scale — turning external information into high-value, verifiable intelligence that directly feeds better toolkits and stronger Economic outputs.

### Core Purpose
This component intelligently triggers and scopes KAS hunts based on context, calibration signals, and value prediction, ensuring hunts are timely, focused, and high-ROI.

### Detailed Targeted Hunt Workflow

**Step 1: Trigger Detection**  
Cache miss on high-importance query, calibration drift, high uncertainty, or explicit high-value signal from EM stall, polishing, or Meta-RL.

**Step 2: Context Packaging**  
Rich context (challenge, approach profile, telemetry, layer needs, meta-weights) is assembled and injected into the hunt prompt.

**Step 3: Hunt Scoping & Execution**  
Determines hunt type, depth, sources, and budget. Executes via tool calls with rate limiting and deduplication. On failure, falls back gracefully to cache or lower-confidence alternatives.

**Step 4: Result Scoring & Filtering**  
Multi-dimensional scoring and success prediction. Only high-value fragments proceed.

**Step 5: Integration & Feedback**  
Standardized fragments returned with provenance. Predicted vs actual outcomes update calibration and Meta-RL.

### Concrete Example
**During a quantum stabilizer polishing pass**  
The loop detects a syndrome decoding gap. Targeted KAS triggers with full context. It returns a recent paper + verified dataset on hardware noise. The fragment is scored highly, integrated, and produces a measurable EFS lift. Cache prevents redundant hunts elsewhere in the swarm.

### Why Targeted Hunts Are Critical
- Prevents wasteful broad searching that wastes compute and introduces noise.  
- Makes KAS responsive to real, high-leverage needs rather than running constantly.  
- Directly improves cost-efficiency and quality of intelligence feeding the Economic Subsystem.  
- Enables recursive and hierarchical specialization across all layers.

**All supporting architecture is covered in [Main KAS Overview](../kas/Main-KAS-Overview.md).**

**Economic Impact at a Glance**  
- Target: 40–65% higher value from acquired knowledge  
- Success Milestone (60 days): ≥ 85% of hunts triggered by meaningful signals (not blind polling)

---

### Reference: Key Decision Formulas

**1. Hunt Trigger Score**  
`Hunt Trigger Score = 0.40 × Calibration Drift + 0.30 × Cache Miss Severity + 0.20 × Economic Downstream Potential + 0.10 × Meta-RL Priority`  
**Optimizes**: Decides whether a hunt is justified versus using cache.  
**Meta-RL Tuning**: Weights refined based on actual downstream EFS and Economic contribution from hunted fragments.

**2. Hunt Scope Score**  
`Hunt Scope Score = 0.35 × Task Urgency + 0.30 × Expected Novelty Gain + 0.20 × Compute Budget Fit + 0.15 × Layer-Specific Needs`  
**Optimizes**: Determines depth and breadth of the hunt.  
**Meta-RL Tuning**: Adjusted using historical hunt ROI and calibration accuracy.
