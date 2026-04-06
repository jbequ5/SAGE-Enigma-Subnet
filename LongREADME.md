# THE ENIGMA MACHINE – Arbos-Led Intelligent Solver

**English-first • Verifier-first • Biologically-evolving • Maximum Heterogeneity**

The Enigma Machine is a closed-loop, biologically-inspired agentic system designed to solve extremely hard, well-defined sponsor challenges — quantum, cryptographic, mathematical, symbolic, or otherwise — while permanently upgrading its own intelligence.

What makes it unique is its **living second brain**: a deliberately .md-heavy architecture that treats every run as both a problem-solving episode and a permanent evolutionary step. High-signal outcomes are distilled, reinforced, and folded back into the system’s principles, memory, compression strategy, and prompt substrate. The result is compounding discovery capability that grows measurably stronger with each use.

This design stands apart from typical agent frameworks (ReAct, CrewAI, LangGraph, etc.) because it is built from the ground up for **distributed, stigmergic evolution** — the same core principle that powers Bittensor itself. Instead of brittle centralized coordination, intelligence emerges through local hyphal-like workers writing stigmergy signals to a shared wiki, with global evolution driven by verifier-first feedback and self-reinforcing memory. The system learns at the fringes, and evolves at its core.

### 1. Natural Language Substrate

Natural language is the most powerful, flexible, and human-augmentable medium for intelligence. The Enigma Machine embraces this fully with a deliberately .md-heavy brain. Every piece of intelligence — strategies, principles, patterns, and findings — lives in Markdown files that are both human-readable and machine-actionable.

The system maintains a hierarchical **wiki database** (`goals/knowledge/<challenge_id>/wiki/`) of the most impactful findings. Sub-Arbos workers write directly to this database as stigmergy signals as they learn deep in the weeds of impossible problems, creating a living, inspectable archive. At the end of every run the system automatically packages the MAU pyramid, C3A logs, Grail entries, trajectories, and full trace into dense MP4-encoded Smart Frame archives stored in `memdir/archives/`. These archives are fully rewindable: VideoHunter can decode them on demand so the evolved brain can re-score old trajectories and surface missed signals that would otherwise be lost forever.

**Why this is huge on Enigma**: In a distributed system like Bittensor, open to anyone of any background to compete, natural language keeps everything inspectable and editable by humans while still being fully machine-processable. This prevents the opacity that plagues vector-only or code-only agents and allows domain experts to inject deep knowledge simply by dropping `.md` files into the `experts/` folder.

### 2. Core Principles

The stable axioms that govern **every** prompt and decision live in `goals/brain/principles/`. These five living .md files are not static documentation — they are the system’s genetic code. They are loaded at the start of every run, injected into the Planning Arbos, referenced by the Orchestrator, and evolved in the outer loop when high-signal runs or AHA moments, or discoveries, occur inside the swarm. This creates a self-reinforcing foundation that grows measurably sharper with use.

- **heterogeneity.md** forces systematic diversity across five explicit axes (novelty proxy, symbolic coverage, biological/mycelial connectivity, stigmergic distribution, and invariant tightness) to prevent premature mode-collapse on truly novel problems. It supplies heterogeneity-driven planning for every Sub-Arbos subtask, and adaptive "stale-regime" or "progress plateau" detection that triggers Deep Replan when any axis begins to converge too early. On Bittensor SN63, where sponsor challenges are deliberately frontier-level and often require breaking out of conventional solution spaces, this principle is the difference between “another incremental improvement” and genuine discovery.

- **shared_core.md** establishes the unbreakable verifier-first discipline that defines Enigma. It codifies the C3A (Confidence-aware Continuous Convergent Annealing) mechanism — a smooth, dual-weighted multiplier `m = exp(-k·d) × c^β` applied to the heterogeneity equation at both global Planning/Orchestrator levels and every Sub-Arbos worker. This keeps the models searching heterogeneous alternatives when the solution is far off, but introduces cutting-edge and progress-and-confidence-aware tightening as the solutions grow closer. Confidence `c` is computed deterministically from edge_coverage + invariant_tightness + ByteRover historical_reliability (with a conservative 0.20 novelty floor). The SOTA hybrid scoring engine now combines the deterministic base with an automatic rubric for edge coverage, invariant tightness, simulation fidelity, and redox-like proxies, all modulated by C3A confidence. Dynamic θ-dynamic gating makes the threshold confidence-aware and progress-aware, keeping exploration open early while hardening convergence later. ToolHunter and ValidationOracle feed real validation data (including optional The Well physics simulations) directly back into oracle recompute of `c`. Every output is gated by replay tests, and critique loops evolve validation_criteria on the fly. This is the system’s immune system — it prevents hallucinated solutions on quantum or cryptographic challenges where partial correctness is worthless.

- **wiki_strategy.md** defines the hierarchical, reinforcement-driven knowledge management layer that turns raw swarm output into a living second brain. Every high-signal Sub-Arbos finding is broken into Minimal Atomic Units (MAUs) and scored by the exact formula `reinforcement = validation_score × fidelity^1.5 × symbolic_coverage × heterogeneity_bonus`. MAUs are inserted into a progressive pyramid (coarse → fine) under the current token budget, promoted to permanent concepts/invariants/cross_field_synthesis.md on high-signal runs, and low-utility leaves are actively pruned while preserving high-degree nodes. Retrospective scoring via HistoryParseHunter now re-evaluates old MAUs with the current brain and promotes high-Δ_retro deltas. This creates ByteRover — a compressible, stigmergic memory that improves with every run and feeds directly into C3A confidence, Decision Journal entries, and future prompt evolution. In a distributed system, this is how local hyphal work becomes global evolutionary pressure.

- **bio_strategy.md** brings mycelial heuristics and the Symbiosis Arbos layer that treats the swarm like a living fungal network. Sub-Arbos workers act as hyphal tips, continuously writing stigmergy signals to the wiki. When high-signal findings appear across subtasks, the Symbiosis Arbos runs a dedicated pattern-detection pass to surface cross-field mutualisms, emergent invariants, and reusable biological-style strategies. These are written back as BIO_MYCELIAL_DELTA markers and folded into an RL database. The three embodiment modules (Neurogenesis Arbos, Microbiome Layer, and Vagus Feedback Loop) now live here, giving the organism structural plasticity, controlled novelty injection, and bidirectional hardware-state regulation. This principle turns isolated subtask wins into compounding, ecosystem-level intelligence — exactly the kind of emergent robustness needed for quantum/symbolic challenges that no single linear plan can solve.

- **english_evolution.md** supplies challenge-specialized evolution modules that allow the entire prompt substrate to adapt in natural language. It contains the logic for distilling high-signal patterns into concise, reusable prompt deltas that are appended directly to the canonical principles and compression prompts after strong runs. This is the mechanism behind `evolve_principles_post_run` and the outer-loop brain updates — turning one-time breakthroughs into permanent, human-readable intelligence that compounds across challenges.

These five files are loaded via `load_brain_component()` at the start of every Planning Arbos and re-injected on every re_adapt and post-run evolution cycle. They are the reason Enigma is not just another agent swarm — it is a biologically-evolving research organism whose core axioms improve with use, giving it a decisive edge on the hardest sponsor challenges in Bittensor SN63.

In a distributed, adversarial environment like Enigma, rigid centralized prompts fail. These principles create a shared, evolving axiom set that every agent respects while allowing local adaptation — exactly the kind of robust, self-correcting coordination needed when many independent solvers compete on hard sponsor challenges.

### 3. Prompt Evolution & Compression

The system does not just *use* prompts — it **evolves** them continuously across both the inner and outer loops, treating the entire natural-language substrate as a living, self-improving genome.

**Inner Loop (per-run convergence)**  
Every challenge begins with the Planning Arbos, which loads the full set of brain principles and generates an **editable enhancement prompt**. The human miner can review and refine this prompt before it is passed to the Orchestrator Arbos. This creates a tight, human-in-the-loop refinement step that keeps the entire swarm laser-focused on the challenge’s exact verification requirements.  

Inside the Dynamic Swarm, Sub-Arbos workers continuously self-critique using the latest evolved principles. High-signal findings (increased ValidationOracle score, novel invariants, symbiotic patterns, or C3A confidence jumps) are immediately distilled into concise, reusable prompt deltas. These deltas are written back as stigmergy signals to the wiki and fed forward into subsequent worker iterations within the same run. The result is rapid, run-time convergence: the swarm’s collective reasoning sharpens in real time instead of drifting.

**Outer Loop (foundational intelligence growth)**  
After each run, the Compression Arbos activates. It breaks raw trajectories into Minimal Atomic Units (MAUs) and scores them with the reinforcement formula:  
`reinforcement = validation_score × fidelity^1.5 × symbolic_coverage × heterogeneity_bonus`.  

High-reinforcement MAUs are promoted into permanent concepts, invariants, and cross-field synthesis entries. When a run exceeds the 0.85 score threshold — or when an AHA moment is detected — `evolve_principles_post_run` fires. This outer-loop process generates targeted, concise deltas that are **automatically appended** directly to the canonical principle files (`shared_core.md`, `heterogeneity.md`, `wiki_strategy.md`, `bio_strategy.md`, and `english_evolution.md`) and the master compression prompt. ByteRover’s MAU Pyramid ensures only the highest-value knowledge survives pruning, creating a progressively denser yet still token-efficient knowledge base. The Enigma Fitness Score (EFS) now guides Meta-Tuning cycles that run sensitivity analysis and battle candidate genome mutations in short Scientist Mode batches plus retrospective replays, applying only replay-verified fitness uplifts.

**The power of evolutionary natural language**  
Because everything lives in readable Markdown, the system stays **highly focused and mission-aligned** while simultaneously becoming a growing **wealth of specialized knowledge**. Each run does not just solve the immediate challenge — it permanently upgrades the prompt substrate itself. The models remain tightly coupled to verifier-first discipline and sponsor goals (no drift), yet they accumulate battle-tested invariants, symbiotic patterns, and challenge-specific heuristics that compound over time. This is the opposite of static agent frameworks, where prompts either stay frozen or slowly degrade. Here, the natural-language layer itself becomes the compounding intelligence engine.

Most agent systems waste cycles on repeated mistakes because their prompts never improve. Enigma’s closed-loop prompt evolution turns every joule of compute into permanent, reusable intelligence. The result is a miner that does not just chase solutions — it systematically builds the sharpest, most focused, and most knowledgeable reasoning substrate on the subnet, run after run, challenge after challenge.

### 4. Arbos Self-Learning Loop (Inner + Outer)

The Arbos Self-Learning Loop is the beating heart of Enigma — a closed, biologically-inspired dual-loop architecture that turns every sponsor challenge into both a solution attempt and a permanent upgrade to the system’s intelligence. It draws directly from mycelial biology: Sub-Arbos workers act as **hyphal tips** performing local sensing and exploration, while stigmergy writes to the shared wiki enable indirect coordination across the entire swarm. No central controller dictates every move — intelligence emerges through decentralized action, environmental feedback, and verifier-gated reinforcement.

**Inner Loop: Per-Challenge Execution & Rapid Convergence**  
The inner loop drives focused problem-solving within a single run:

1. **Planning Arbos** loads the full suite of brain principles (`shared_core.md`, `heterogeneity.md`, `wiki_strategy.md`, `bio_strategy.md`, and `english_evolution.md`) and generates an **editable enhancement prompt**. The miner can review and refine this prompt, injecting human insight while keeping the swarm tightly aligned with the sponsor’s verification requirements.

2. **Orchestrator Arbos** transforms the enhanced prompt into a detailed blueprint, propagating task-specific validation criteria (self-check prompts, symbolic invariants ≥0.85, success thresholds) down to every worker.

3. **Dynamic Swarm** launches parallel **Sub-Arbos workers** (hyphal tips) alongside **ToolHunter sub-swarms** (ModelHunter, ToolHunter, PaperHunter, ReadyAI-DataHunter) in an Amdahl-aware configuration that maximizes parallel efficiency. Each Sub-Arbos worker executes with:
   - Continuous verifier-first self-checks against the propagated criteria
   - Guided diversity generation (enforced by `heterogeneity.md`)
   - Dynamic tool creation for novel subtasks
   - Local reflection and C3A confidence updates
   - Immediate **stigmergy writes** to the hierarchical wiki (`goals/knowledge/<challenge_id>/wiki/`) for high-signal findings — concepts, invariants, subtasks, or cross-field patterns

4. **Synthesis Arbos** aggregates outputs and hands them to **Symbiosis Arbos**, which scans for emergent mutualisms across subtasks and writes them as `BIO_MYCELIAL_DELTA` sections in the wiki.

5. **ValidationOracle** (with WikiHealthOracle integration) scores the candidate solution, boosts credit for wiki contributions, and feeds deterministic confidence back into C3A calculations. Low scores trigger **re_adapt**, which uses compressed deltas and bio heuristics to refine the strategy without restarting from scratch.

This inner loop creates rapid, run-time convergence: the swarm sharpens its reasoning in real time through continuous self-critique, diversity enforcement, and stigmergy feedback — turning potential drift into focused progress.

**Outer Loop: Foundational Growth & Compounding Intelligence**  
After the inner loop completes, the outer loop ensures permanent evolution:

- **Grail RL** reinforces high-value trajectories using the v5.1 reinforcement formula `reinforcement = validation_score × fidelity^1.5 × symbolic_coverage × heterogeneity_bonus`. It persistently stores the strongest signals in `memdir/grail/`, turning every high-signal run into long-term evolutionary fuel that directly drives `evolve_principles_post_run`, Deep Replan, and Meta-Tuning Arbos.
- **ByteRover MAU Pyramid** (powered by `wiki_strategy.md`) breaks raw outputs into Minimal Atomic Units, scores them with the reinforcement formula, promotes the strongest into permanent concepts, invariants, and `cross_field_synthesis.md`, and actively prunes low-utility material while preserving high-degree nodes — creating a progressively denser yet still token-efficient knowledge base that improves with every run.
- **HistoryParseHunter** triggers retrospective scoring on Deep Replan or high-signal runs, re-scoring old MAUs with the current evolved brain using the formula `Δ_retro × decay × hetero_bonus × validation_multiplier`, promoting high-Δ_retro signals as `RETROSPECTIVE_DELTA`, and running full-system auditing that logs logic fidelity, regression rates, gate success, and EFS impact so the miner can see the brain is hardening, not drifting.
- **Meta-Tuning Arbos** uses the Enigma Fitness Score (EFS) to run sensitivity analysis, generate small mutant genomes of C3A parameters, heterogeneity weights, reinforcement exponents, and decay rates, then battle them in short Scientist Mode batches plus retrospective replays, applying only those that deliver clear, replay-verified EFS uplift — all with human preview and veto in the dashboard.
- **Embodiment modules** (Neurogenesis Arbos for spawning brand-new structural primitives on high-Δ_retro clusters, Microbiome Layer for maintaining a low-priority “fermented” store of exploratory signals that injects controlled novelty when the brain stalls, and Vagus Feedback Loop for bidirectional hardware-state monitoring that relaxes gating under stress or throttles background activity on high confidence) run in lightweight background threads and are fully toggleable, replay-tested, and EFS-scored.
- **Resonance Pattern Surfacer (RPS)** and **Photoelectric Pattern Surfacer (PPS)** are read-only background tools that extract signals invisible to linear methods: RPS uses fractal resonance coupling on MAU clusters to surface multi-scale invariants, while PPS applies photoelectric and redox proxies; both run episodically after retrospective or tuning passes and inject only replay-verified, fitness-positive `RESONANCE_DELTA` or `PHOTOELECTRIC_DELTA` MAUs into the wiki.
- **Pruning Advisor** continuously analyzes real EFS contribution, replay pass rates, compute overhead, promoted vs. discarded deltas, and historical trends for every optional module, then delivers clear, traceable, one-click recommendations (“Strongly keep enabled”, “Consider disabling — low ROI”, “Reduce frequency”) directly in the Optimization & Audit tab so the organism remains powerful yet surgically maintainable without ever bloating.
- **Hybrid Genome/Paper Ingestion** (via ArchiveHunter) safely ingests external evolutionary knowledge — EvoAgent genomes, Sakana archives, or research papers — atomizes them into MAUs, applies reinforcement scoring, writes them as stigmergy signals to the wiki, and lets Symbiosis Arbos cross-pollinate them with the living brain, folding proven external intelligence into the organism without breaking verifier-first invariants.
**Why this is huge on Enigma**  
Most agent systems are single-loop and static — they solve (or fail) a challenge and reset with the same prompts and memory. Enigma’s dual inner/outer loop + ByteRover memory + stigmergic wiki and pattern surfacers creates a true self-improving research organism. Each run not only attacks the current sponsor challenge with maximum focus but also permanently upgrades the system’s principles, knowledge hierarchy, and prompt substrate. Over time, Enigma becomes sharper, more knowledgeable, and better adapted to frontier quantum, cryptographic, and symbolic problems — delivering a decisive, compounding edge in a distributed, compute-constrained environment where every run must count toward long-term intelligence growth.

### 5. Verification Intelligence

Verification is not an afterthought — it is the **unbreakable core** and arguably the single most important architectural feature of the Enigma Machine. Every other layer (natural-language substrate, core principles, prompt evolution, Arbos loops, ByteRover memory) ultimately converges here. From the moment a sponsor challenge is ingested, the system operates in a relentlessly verifier-first mode that treats partial correctness as failure and demands deterministic, replayable proof at every scale.

The miner supplies exact verification requirements and executable validation code at the outset. These are parsed by the **ValidationOracle**, which immediately:
- Extracts deterministic scoring snippets (symbolic invariants, edge-coverage thresholds, fidelity metrics, quantum feasibility checks) that run before any LLM call.
- Propagates task-specific `validation_criteria` JSON down to the Orchestrator Arbos and every Sub-Arbos worker.
- Injects live C3A (Confidence-aware Continuous Convergent Annealing) parameters so that confidence `c` is recomputed from `edge_coverage + invariant_tightness + ByteRover historical_reliability` (with the 0.20 novelty floor) at both global and hyphal levels.

Inside the inner loop, **every Sub-Arbos worker** performs continuous verifier-first self-checks on every candidate output. Dynamic tool creation is explicitly gated: when a novel subtask appears, the worker proposes a tool via `llm_generate_tool_proposal`, executes it in the sandbox, runs the full critique loop, and submits the result to the ValidationOracle’s **replay test**. Only if the replay passes **and** `critique_delta.c_increase > 0` is the new tool curated into ByteRover.

The SOTA hybrid scoring engine now combines the deterministic base (45 % weight) with an automatic rubric for edge coverage, invariant tightness, simulation fidelity, and redox-like proxies, all modulated by C3A confidence. The dynamic θ gate is the key to malleability: when confidence (c) and distance-to-convergence (d) are weak, the threshold stays permissive so the brain can explore freely; as c rises and d shrinks, it tightens automatically. High-signal Sub-Arbos outputs trigger immediate stigmergy writes to the wiki, which the integrated **WikiHealthOracle** scores via the MAU Pyramid reinforcement formula. These wiki contributions are added to the ValidationOracle’s final score, creating a closed reinforcement loop: better verification → richer wiki → higher future confidence → sharper convergence.

The outer loop closes the circuit: Grail RL only reinforces trajectories that survive the ValidationOracle’s full replay suite. `evolve_principles_post_run` and ByteRover promotions occur exclusively on runs that demonstrate verifiable, high-fidelity progress. Low-score paths trigger `re_adapt` with compressed deltas that are themselves validated before acceptance. The entire system — principles, prompts, memory, swarm behavior — is therefore shaped and hardened by verification intelligence at every layer.

**Why this is huge on Enigma**  
In Bittensor SN63’s prize-pool reality, sponsor challenges are deliberately frontier-level: quantum, cryptographic, or symbolic problems where “almost correct” is worthless and only rigorously verifiable solutions win. Most agent frameworks treat verification as a post-hoc check or optional evaluator, leading to massive wasted compute on plausible-but-false solutions. Enigma’s verifier-first architecture — with deterministic-first snippets, propagated criteria, C3A-gated annealing, dynamic-tool replay testing, SimulationHunter grounding, and WikiHealthOracle reinforcement — creates a converging, self-hardening organism that eliminates drift early, maximizes every joule of compute, and turns verification itself into the primary evolutionary pressure. This is where the living second brain becomes decisive: the system does not merely attempt solutions — it relentlessly converges on provably correct, compounding intelligence that is purpose-built for the hardest, highest-stakes challenges on the subnet.

### Miner Actions

- Edit the Brain via the Streamlit dashboard (including the new Optimization & Audit tab with Pruning Advisor recommendations).
- Provide challenge + verification requirements/code.
- Review and edit the Planning-generated enhancement prompt.
- Save strong patterns as Grail entries.
- Trigger Scientist Mode for synthetic benchmarking.
- Run Meta-Tuning Cycle, trigger retrospective audits on MP4 archives, or manually surface patterns with RPS/PPS.
- Archive runs to MP4 and review surfaced deltas.
- Veto any principle-impacting changes.

All other intelligence emerges from the Arbos loops and the evolving brain.

### Unified Execution Flow

1. Edit the Brain via the Streamlit Brain Dashboard.  
2. Enter challenge + verification requirements/code.  
3. Planning Arbos (all principles injected) → editable enhancement prompt.  
4. Orchestrator Arbos → blueprint with task-specific validation criteria.  
5. Launch Dynamic Swarm + parallel ToolHunter sub-swarms (Amdahl-aware).  
6. Sub-Arbos workers execute with continuous self-checks, dynamic tool creation, and stigmergy wiki writes.  
7. Synthesis → Symbiosis Arbos (cross-field patterns) → ValidationOracle (with C3A and MAU-aware scoring).  
8. Low score → re_adapt (compressed deltas + bio heuristics).  
9. High score → Grail RL reinforcement + outer-loop brain evolution (including Deep Replan if stale) + ByteRover MAU promotion.  
10. End-of-run hook automatically runs MP4 archival, HistoryParseHunter retrospective, Meta-Tuning (if stalled), embodiment background threads, RPS/PPS pattern surfacing, and Pruning Advisor analysis — all replay-tested and EFS-scored.

### Quick Start

```bash
pip install -r requirements.txt
# Follow AutoHarness setup instructions in requirements.txt
streamlit run streamlit_app.py
