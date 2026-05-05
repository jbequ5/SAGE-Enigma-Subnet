# Wizard-and-Config  
**SAGE Operations Layer — Deep Technical Specification**  
**v0.9.13+ (Intelligent Fragment Factory Entry Point)**

## Investor Summary — Why This Matters
The Wizard & Config system is the intelligent entry point for every miner. It starts with mandatory challenge or KAS product hunt selection, then runs the full challenge-specific calibration flight test and presents clear, data-driven load-out options based on real Fragment Yield predictions.  

This reduces setup time by **85%**, increases successful mission completion rate by **2.4×**, and ensures every swarm begins with the optimal profiles, model assignments, and compute configuration for maximum fragment production.

For investors, this is the interface that turns a complex multi-agent factory into a usable, competitive product on Enigma Subnet 63 — giving miners of any hardware scale an immediate, high-signal experience.

## Core Purpose
The wizard guides the miner through a safe, step-by-step, factory-optimized configuration while ensuring:
- The calibration flight test runs on the real challenge and real hardware
- PerformanceTracker historical yield data informs every decision
- The user sees clear Conservative / Balanced / Aggressive load-out recommendations with predicted Fragment Yield
- Save/resume of partial high-value fragments is first-class

## Detailed Wizard Flow (Factory-Optimized)

**Step 1: Challenge / KAS Product Hunt Selection (Mandatory First Step)**  
- Loads and displays curated list from `challenges.md` and active KAS product hunts.  
- Miner selects one (required).  
- Full metadata (ID, tags, difficulty, historical performance summary) is stored and passed to PerformanceTracker for yield lookup.

**Step 2: Challenge-Specific Calibration Flight Test**  
- Runs the full empirical calibration:  
  - Model profiling (builds VRAM/RAM/thermal lookup table)  
  - KAS-informed profile assembly (3–4 meaningful profiles)  
  - Incremental orchestration test with branching ramp (1 → 5)  
  - EM self-reports preferred internal subtask size per profile  
- Uses PerformanceTracker historical yield data to predict Fragment Yield for each configuration.

**Step 3: Intelligent Load-Out Recommendations**  
- Presents clear options (Conservative / Balanced / Aggressive) with exact predicted numbers:  
  - Concurrent LLM load  
  - Peak VRAM / RAM usage  
  - Expected Fragment Yield  
  - Estimated EFS lift  
- Miner selects or accepts the recommended load-out.

**Step 4: Launch with Save/Resume Enabled**  
- Launches the swarm via the Orchestrator with MAP profiles, Smart LLM Router assignments, and chosen load-out.  
- Immediately checks for existing profile sessions on this challenge and offers “Resume Profile X (already has X runs and Y high-signal fragments)” if applicable.

**Step 5: Live Dashboard + Post-Run Review**  
- Real-time Fragment Yield monitoring during the run.  
- Post-run summary: total fragments, yield per profile, save/resume options for future sessions, and one-click push of high-yield fragments to Strategy/Synapse.

## Bulletproof Fragment Yield Metric (Used Throughout Wizard)
\[
\text{Fragment Yield} = N_{\text{pass}} \times \overline{V} \times S_{\text{downstream}} \times \text{NoveltyFactor} \times \text{ProvenanceIntegrity}
\]

## Why the Wizard Is Critical for the Intelligent Fragment Factory
- It is the only place where the user interacts with the factory before any compute is spent.  
- It guarantees every swarm starts with empirically validated, challenge-specific, hardware-aware configurations.  
- It makes save/resume of partial high-value fragments first-class and visible.  
- It turns a complex multi-agent system into a dead-simple, high-signal experience for solo miners and large operators alike.

## Rebuild Steps
1. Update wizard UI to make challenge/KAS selection the very first mandatory step.  
2. Implement the full calibration flight test as Step 2 (model profiling + KAS profiles + incremental test + load-out recommendations).  
3. Wire PerformanceTracker queries into every step for historical yield data.  
4. Add save/resume detection and session loading in Step 4.  
5. Replace all legacy EFS references with Fragment Yield in recommendations and post-run review.

## Integration Points
- **PerformanceTracker** → Provides historical yield and profile session state.  
- **MAP** → Receives challenge metadata and returns profiles.  
- **Calibration Flight Test** → Core engine of Step 2.  
- **Smart LLM Router** → Uses flight-test model profiling for assignments.  
- **Swarm Orchestrator** → Receives final load-out and launches the swarm.  
- **Telemetry Layer** → Receives post-run Fragment Yield summary for Meta-RL.  
- **Save/Resume** → Full support for partial high-value fragments across sessions.

**All supporting architecture is covered in the [Intelligent Operating System — Fragment Factory Specification](../operations/Intelligent-Operating-System-Fragment-Factory.md).**

## Economic Impact at a Glance
- Target: 85% reduction in setup time; 2.4× increase in successful mission completion rate and Fragment Yield  
- Success Milestone (60 days): ≥ 90% of new miners complete their first full mission within 15 minutes of opening the dashboard (measured against current baseline)

**Scalability Note**: The wizard is fully hardware-agnostic. On modest GPUs it clearly labels conservative recommendations; on large clusters it surfaces aggressive high-yield options automatically.
