# THE ENIGMA MACHINE – Arbos-Led Intelligent Solver

**English-first • Verifier-first • Self-evolving • Maximum Heterogeneity**

Built from first principles to solve extremely hard sponsor challenges — quantum, cryptographic, mathematical, symbolic, or any well-defined problem — while maximizing novelty, ValidationOracle score, and reproducible IP.

What makes it unique is not just another multi-agent swarm. It is a **closed-loop self-improving system** where every run permanently upgrades the miner’s own reasoning, memory, compression strategy, graph relationships, and prompt intelligence. The result is compounding discovery capability that gets measurably stronger over time.

The **Principle of Maximum Heterogeneity** is the decisive advantage that allows it to break novel problems with no obvious solutions. While most agent systems quickly collapse into mode-collapse or local optima, the Enigma Machine deliberately forces systematic exploration across five axes — agent styles, hypotheses, tool paths, interaction graphs, and compute substrates — at every decision point. This diversification, tightly gated by verifier-first symbolic checks and ValidationOracle scoring, enables genuine discovery on open-ended, high-difficulty challenges where traditional approaches fail. Heterogeneity scoring, adaptive weighting, and stale-regime deep replanning ensure the system does not just optimize known patterns — it systematically expands its ability to find breakthroughs.

### Unified Execution Flow with Integrated Intelligence

1. **Edit `killer_base.md`** — the single living source of truth. Contains the challenge-agnostic foundation, toggles, English Evolution Modules, and the self-evolving COMPRESSION_PROMPT that improves with every strong run.

2. **(Optional but powerful)** Drop domain-expert knowledge into the `experts/` folder — any `.md` file is automatically loaded as an **Expert Module** and injected into all downstream prompts.

3. **Enter the challenge + verification instructions**.

4. **Click “Generate High-Level Plan”** → Planning Arbos creates a detailed strategy and auto-populates a challenge-specific post-planning enhancement prompt (now enriched with any active Expert Modules).

5. **Review & edit** the enhancement prompt to inject human intelligence.  
   **(Optional)** Save the edited enhancement as a Grail pattern — instantly appended to `killer_base.md` and stored in `memdir/grail`.

6. **Approve the Plan** → Orchestrator Arbos refines the blueprint and generates a specialized Pre-Launch Context that includes graph relationships.

7. **Post-Orchestration Review Dashboard** — full visibility into swarm strategy, ToolHunter sub-swarm recommendations (including Onyx RAG execution when enabled), validation criteria, and pre-launch context.

8. **Launch the Swarm** → Dynamic Swarm + parallel ToolHunter sub-swarm (ModelHunter / ToolHunter / PaperHunter / ReadyAI-DataHunter) with Amdahl-aware routing and optional Onyx hybrid RAG execution for high-signal gap filling.

9. **Sub-Arbos Workers** — each worker receives **intelligently determined verification criteria** set by Orchestrator Arbos during the blueprint phase. They perform verifier-first symbolic execution, Guided Diversity exploration (structured heterogeneity maximization instead of random perturbations), ToolHunter + Onyx calls, and real-time inter-worker messaging via the lightweight message bus. This early, precise validation guidance keeps every sub-Arbos tightly on track from the very first step.

10. **Synthesis Arbos** — MARL-weighted aggregation that only credits paths meeting strict fidelity and determinism thresholds.

11. **ValidationOracle + Intelligent Verification Techniques** — the unbreakable gate. Executes your exact verifier code snippets + SymPy invariants + 0-1 edge-case checks on the synthesized solution.  

12. **Low Score?** → Adaptation Arbos (`re_adapt`) uses compressed intelligence deltas, vector DB recall, graph relationships, and Expert Modules for fast, precise adaptation.

13. **High Score?** → Grail extraction, reinforcement, MCTS-guided compression evolution, and one-click SN63 packaging.

14. **Scientist Mode** — on-demand or automatic synthetic challenge generation + progress benchmarking.

### Natural Language Intelligence: The Evolving Prompt Ecosystem

One of the most powerful aspects of the Enigma Machine is that intelligence lives primarily in **natural language** — a flexible, human-augmentable, self-improving substrate.

- **`killer_base.md`** serves as the root prompt ecosystem. It contains the challenge-agnostic core strategy, toggles, English Evolution Modules, and the live, self-evolving COMPRESSION_PROMPT.
- **Planning Arbos** starts deliberately agnostic and specializes into a challenge-specific enhancement prompt, automatically injecting Expert Modules.
- **Enhancement Prompt Layer** is fully editable by the human and can be permanently saved as Grail patterns.
- **Orchestrator Arbos**, synthesis, re_adapt, diversity generation, and Scientist Mode prompts all inherit and build upon this evolving English foundation.

This design gives world-class physicists and mathematicians an extremely low-friction way to inject deep domain knowledge without touching Python. More importantly, the prompts themselves evolve: strong runs permanently improve the compression prompt via MCTS-guided self-play, and Grail patterns become part of the permanent reasoning repertoire. The miner is not just solving problems — it is literally improving how it *thinks* about problem decomposition, hypothesis generation, and symbolic reasoning over time.

### Maximum Heterogeneity Principle – The Core Scaling Strategy

On problems with zero obvious solutions, heterogeneity is the decisive advantage.

The system deliberately maximizes diversity across five axes at every decision point:
- Agent diversity
- Hypothesis diversity
- Tool-path diversity
- Interaction-graph diversity
- Compute-substrate diversity

Heterogeneity scoring is computed live on every Grail extraction and re_adapt. Adaptive EMA weights slowly reinforce the axes that actually move ValidationOracle scores. When progress stalls, stale-regime detection triggers **Deep Replan**, generating an entirely new strategic avenue while preserving all prior knowledge.

A heterogeneity bonus is baked into every reinforcement signal and compression delta. This prevents mode-collapse and forces systematic exploration of the full solution space, while the verifier-first gate ensures only high-fidelity paths survive. This combination is the primary reason the Enigma Machine can attack open-ended, high-difficulty problems with genuine discovery power.

### Bittensor Subnet Inspired Intelligence

The miner compounds intelligence from multiple subnets (SN11 TrajectoryRL, SN33 ReadyAI, SN24 Quasar, SN64 Chutes, SN81 Grail) into a single, verifiable self-improvement loop.

### Strict Verification Intelligence at Every Level
During orchestration, Orchestrator Arbos analyzes the challenge and generates **task-specific validation_criteria** (including self-check prompts, symbolic invariants, and success thresholds) that are passed down to every Sub-Arbos worker. Each worker runs continuous self-checks against these criteria throughout its execution loop. This creates an early, continuous verification signal rather than a single end-of-pipeline check. The result is dramatically reduced drift: agents stay aligned to the exact success definition from the moment they begin work, wasted compute on off-track paths is minimized, and only high-fidelity trajectories reach Synthesis Arbos. AgentFixer-style multi-detector diagnostics (symbolic invariants, prompt coherence, parsing schema, novelty drift, cross-stage coherence) run at every stage and feed directly into Grail extraction, compression, and re_adapt loops.

### Compute Flexibility

You have the option to run whatever compute you want, and the intelligence of the system automatically manages your compute resources with dynamic swarm sizing and resource-aware early-abort logic.

### Quick Start

```bash
pip install -r requirements.txt
# AutoHarness requires one manual git clone + pip install -e . step (see requirements.txt)
streamlit run streamlit_app.py
```

Create the `experts/` folder and start dropping domain knowledge. Use the Streamlit Expert Input panel to propose new tools. Run Scientist Mode whenever you want to measure real progress.

**The bunker is open.**

Questions or feature requests? Ping @dTAO_Dad on X.

Made with focus on first-principles agentic design for Bittensor Subnet 63, Enigma. 

