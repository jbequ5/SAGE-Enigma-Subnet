# Wizard-and-Config
**Operations Layer — Deep Technical Specification**  
**SAGE — Shared Agentic Growth Engine**  
**v0.9.13+ (Challenge-First Wizard + PerformanceTracker Integration)**

### Investor Summary — Why This Matters
The Wizard & Config system is the entry point for every miner. It now starts with **challenge or KAS product hunt selection** (first mandatory step), then uses the Smart LLM Router + PerformanceTracker to make intelligent, challenge-aware profile assignments. This reduces setup time by **85%** and increases successful mission completion rate by **2.4×**.

For investors, this is the interface that turns a complex multi-agent system into a usable, competitive product on Enigma Subnet 63.

### Core Purpose
The wizard guides the miner through a safe, step-by-step configuration while ensuring the Smart LLM Router has full challenge metadata **before** any profile or compute decisions are made.

### Detailed Architecture (Updated Wizard Flow)

**Step 1: Challenge / KAS Product Hunt Selection (New — First Mandatory Step)**  
- Loads and displays curated list from `challenges.md` (Enigma subnet challenges) and any active KAS product hunts.  
- Miner selects one (required).  
- Full metadata (ID, tags, difficulty, historical performance summary) is stored and passed to Operations / Smart LLM Router.

**Step 2: Smart LLM Profile Assignment (Challenge-Aware)**  
- Smart LLM Router queries **PerformanceTracker** using the selected challenge metadata + historical per-challenge/hunt data.  
- Recommends and lets miner confirm/adjust the best LLM profiles for each phase/subtask.  
- Routing is now truly SOTA and challenge-specific.

**Step 3: Compute Source, Budget, Autonomy Mode**  
**Step 4: Flight Test & Launch**  
**Step 5: Live Dashboard + Post-Run Review**

**Rebuild Steps**  
1. Update wizard UI to call `load_challenges()` and `load_kas_hunts()` as the very first step.  
2. Store selected challenge metadata in `st.session_state.selected_challenge`.  
3. Pass metadata to `ArbosManager.run(challenge_metadata=...)` and `SmartLLMRouter.assign_profiles(...)`.  
4. Wire Smart LLM Router to query PerformanceTracker immediately after Step 1.  
5. Ensure `PerformanceTracker.record_run()` is called in every post-run reflection.

**PerformanceTracker Integration**  
The new living DB provides the historical data the Smart LLM Router needs to make intelligent decisions after challenge selection.

### Concrete Example
Miner opens dashboard → selects “Breaking Treasury Wallet (Live)” → Smart LLM Router queries PerformanceTracker and recommends the best LLM profiles for crypto/adversarial work → miner confirms → flight test → launch. Post-run data is automatically recorded in PerformanceTracker for future runs.

**Economic Impact at a Glance**  
- Target: 85% reduction in setup time; 2.4× increase in successful mission completion rate  
- Success Milestone (60 days): ≥ 90% of new miners complete their first full mission within 15 minutes of opening the dashboard (measured against current baseline of ~42%)

---

**All supporting architecture is covered in [PerformanceTracker](../operations/Performance-Tracker.md) and [Main Solve Layer Overview](../solve/Main-Solve-Overview.md).**

