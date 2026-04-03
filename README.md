# THE ENIGMA MACHINE – Arbos-Led Intelligent Solver

**English-first • Verifier-first • Biologically-evolving • Maximum Heterogeneity**

The Enigma Machine is a closed-loop, biologically-inspired agentic system designed to solve extremely hard, well-defined sponsor challenges — quantum, cryptographic, mathematical, symbolic, or otherwise — while permanently upgrading its own intelligence.

What makes it unique is its **living second brain**: a deliberately .md-heavy architecture that treats every run as both a problem-solving episode and a permanent evolutionary step. High-signal outcomes are distilled, reinforced, and folded back into the system’s principles, memory, compression strategy, and prompt substrate. The result is compounding discovery capability that grows measurably stronger with each use.

### Top-Down Intelligence Architecture

The system is deliberately layered from the most flexible to the most rigorous:

1. **Natural Language Substrate**  
2. **Core Principles**  
3. **Prompt Evolution & Compression**  
4. **Arbos Self-Learning Loop** (inner + outer)  
5. **Verification Intelligence**

This hierarchy keeps the miner fully human-inspectable, English-editable, and self-improving while enforcing verifier-first rigor at every level.

#### 1. Natural Language Substrate

Natural language is the most powerful, flexible, and human-augmentable medium for intelligence. Unlike rigid code or vector embeddings that become opaque, natural language remains readable, editable, and evolvable by both humans and the system itself.

The Enigma Machine embraces this fully with a deliberately .md-heavy brain. Every piece of intelligence — strategies, principles, patterns, and findings — lives in Markdown files that are both human-readable and machine-actionable. This design gives domain experts (physicists, mathematicians, cryptographers) low-friction access to inject deep knowledge simply by dropping `.md` files into the `experts/` folder.

The system maintains a hierarchical **wiki database** (`goals/knowledge/<challenge_id>/wiki/`) of the most impactful findings and patterns. Sub-Arbos workers write directly to this database as stigmergy signals, creating a living, inspectable archive of concepts, invariants, subtasks, and cross-field synthesis. Over time, the miner does not just solve problems — it builds and refines its own structured knowledge base, turning isolated wins into permanent, reusable intelligence.

#### 2. Core Principles

The stable axioms that govern all reasoning live in `goals/brain/principles/` and are referenced by **every** prompt via `brain_loader.py`.

- **`shared_core.md`** establishes verifier-first discipline and MARL credit rules. It ensures symbolic invariants and determinism thresholds (≥0.85) are enforced on every subtask, preventing drift and rewarding only reproducible, high-fidelity paths.
- **`heterogeneity.md`** is the decisive scaling principle. It forces systematic diversity across five axes (agent styles, hypotheses, tool paths, interaction graphs, compute substrates) at every decision point, preventing mode-collapse on novel problems.
- **`wiki_strategy.md`** defines hierarchical knowledge management. Raw material is ingested into `knowledge/raw/`, then distilled, pruned, and promoted into `wiki/concepts/`, `wiki/invariants/`, and `wiki/subtasks/`. It outputs structured JSON deltas for dynamic folder creation and upward promotion.
- **`bio_strategy.md`** brings mycelial heuristics to life and introduces **Symbiosis Arbos**. Sub-Arbos workers act as hyphal tips that perform local sensing, stigmergy (direct `.md` writes), redundancy/loops, and aggressive pruning of low-signal paths. **Symbiosis Arbos** specifically scans for and synthesizes cross-subtask symbiotic opportunities, writing them as BIO_MYCELIAL_DELTA sections in the wiki so later phases can exploit emergent synergies. Optional quantum-bio coherence (tunneling/entanglement heuristics) is toggleable in guided diversity phases.
- **`english_evolution.md`** supplies challenge-specialized modules that auto-specialize per run to maximize the effectiveness of the tools they're feeding in a challenge specific way.

These principles are not passive documentation — they are actively loaded with `lean`/`rich` depth toggling and aggressive pruning. Once introduced, they are integrated throughout the system: every Planning, Orchestration, Sub-Arbos, and Adaption step explicitly references the relevant principle files, ensuring the entire swarm operates under the same high-signal axioms.

#### 3. Prompt Evolution & Compression

The system does not just use prompts — it evolves them in a closed outer loop.

The core strategy prompt begins challenge agnostic and evolves with every inner-loop run. High-signal patterns and mid swarm "aha" insights are automatically promoted back into it, making the canonical entry point smarter and more battle-tested over time.

The principled prompts (`brain/principles/*.md`) evolve from high-signal system input. On strong runs or aha moments, `evolve_principles_post_run` generates targeted, concise deltas that are appended directly to the principle files **(including Symbiosis Arbos patterns)**. The Compression Arbos distills raw trajectories using the reinforcement formula `reinforcement_score = validation_score × fidelity^1.5 × symbolic_coverage × heterogeneity_bonus`, ensuring only the most impactful patterns survive and compound.

This dual evolution — base prompt growing through inner-loop success, principled prompts refining through high-signal feedback — turns the entire prompt ecosystem into a self-improving substrate.

#### 4. Arbos Self-Learning Loop (Inner + Outer)

**Inner Loop** (per-challenge execution):  
Planning Arbos → Orchestrator Arbos → Dynamic Swarm (Sub-Arbos workers + parallel ToolHunter sub-swarms) → Synthesis Arbos → ValidationOracle → Adaptation Arbos (`re_adapt`) if score is low.

Sub-Arbos workers act as hyphal tips: they run verifier-first symbolic checks, guided diversity, tool calls, and local reflection loops. Aha moments (local score jumps or heterogeneity spikes) are detected at the Sub-Arbos level and gated by toggles.High-signal findings trigger immediate stigmergy writes to the wiki hierarchy.

**Outer Loop** (cross-run brain evolution):    
- ValidationOracle + WikiHealthOracle boost scores from high-signal wiki contributions.  
- **Grail RL** reinforces high-value trajectories via `memory_reinforcement_signal` (using the same reinforcement formula) and stores them in the persistent memdir-backed Grail DB for future recall.  
- **Deep Replan** triggers automatically on stale-regime detection (z-score drop or prolonged low scores), generating an entirely new strategic avenue while preserving all prior Grail patterns and forcing a fresh Planning Arbos run.

The result is a true self-compounding system: intelligence is accumulated and refined across runs.

#### 5. Verification Intelligence

Verification is the unbreakable core pillar. The miner (human or automated) provides exact verification requirements and code snippets at the start of every challenge. These feed directly into the ValidationOracle, which adapts dynamically with the system.

The oracle propagates task-specific validation criteria (self-check prompts, symbolic invariants, success thresholds) all the way down to Sub-Arbos level detail. Every worker runs continuous self-checks against these criteria throughout its execution. The oracle further strengthens this pillar by intelligently hunting tools, papers, and data via the parallel ToolHunter sub-swarms (ModelHunter, ToolHunter, PaperHunter, ReadyAI-DataHunter), ensuring the verification layer is always armed with the best available resources.

This creates an early, continuous verification signal that dramatically reduces drift and wasted compute while keeping the entire swarm tightly aligned to the miner’s exact success definition.

### Miner Actions

The miner itself performs a small but critical set of high-leverage actions:
- Edits the Brain Suite via the Streamlit dashboard.
- Provides challenge description + verification code/requirements.
- Reviews and edits the Planning-generated enhancement prompt.
- Saves strong patterns as Grail entries.
- Triggers Scientist Mode for synthetic benchmarking and progress measurement.
- Monitors wiki growth and principle evolution over multiple runs.

All other intelligence emerges from the Arbos loops and the evolving brain.

### Unified Execution Flow

1. Edit the Brain via the Streamlit Brain Dashboard.  
2. Enter challenge + verification requirements/code.  
3. Planning Arbos (all principles injected) → editable enhancement prompt.  
4. Orchestrator Arbos → blueprint with task-specific validation criteria.  
5. Launch Dynamic Swarm + parallel ToolHunter sub-swarms (Amdahl-aware).  
6. Sub-Arbos workers execute with continuous self-checks and stigmergy wiki writes.  
7. Synthesis → Sybiosis (Check for simbiotic patterns) → ValidationOracle
8. Low score → re_adapt (using compressed deltas + bio heuristics).  
9. High score → Grail RL reinforcement + outer-loop brain evolution (including Deep Replan if stale).

### Quick Start

```bash
pip install -r requirements.txt
# Follow AutoHarness setup instructions in requirements.txt
streamlit run streamlit_app.py
```

Create the `experts/` folder for domain knowledge. Use the Brain Dashboard to inspect and evolve principles directly. Run Scientist Mode for synthetic benchmarking.

**The bunker is open.**

Questions or sponsor challenges? Ping @dTAO_Dad on X.

Built with first-principles agentic design for Bittensor Subnet 63, Enigma.
