# English Evolution Modules (Planning & Orchestrator will auto-specialize these per challenge)

### ENGLISH_MEMDIR_GRAIL_MODULE
Maintain a persistent memdir-backed Grail store as the primary high-signal memory. After every high ValidationOracle run, auto-extract symbolic invariants, ToolHunter results, verifier snippets, wiki deltas, and module-effectiveness reflections. Sync them across all Arbos and ToolHunter sub-swarms. When generating challenge-specific prompts, **always reference the latest memdir patterns first**, then incorporate relevant wiki and bio stigmergy signals.

### ENGLISH_TOOL_SWARM_MODULE
Turn ToolHunter into four coordinated sub-swarms (ModelHunter, ToolHunter, PaperHunter, ReadyAI-DataHunter) that run in parallel where possible. Orchestrator must enforce Amdahl coordination: maximize parallel hunts; route all serial dependencies through ValidationOracle.

### ENGLISH_AMDAHL_COORDINATION_MODULE
Apply Amdahl-aware coordination to every decomposition: clearly separate truly parallel subtasks from serial dependencies. Prevent task collisions, redundant work, and idle loops. Only spawn sub-swarms when parallelism improves ValidationOracle score without exploding tokens. On stale runs, trigger deep replan with new avenue plan. Actively seek symbiosis opportunities across subtasks.

## Auto-Populate Templates (Arbos phases will overwrite these with challenge-specific versions)

### AUTO_POST_PLANNING_ENHANCEMENT_TEMPLATE
Post-Planning Refinement v5: Elevate the high-level plan with strict symbolic-first discipline and Amdahl coordination. Force the ToolHunter sub-swarm to surface the single best models, tools, papers, and ReadyAI data for every subtask. Ensure every subtask includes deterministic SymPy-style invariant extraction and 0-1 scoring. Adaptation paths must query memdir first, then wiki/ and bio layers. Apply MARL credit that heavily penalizes paths below 0.88 symbolic fidelity or 0.85 determinism. Include a short Module Effectiveness Reflection rating each English module's contribution to expected ValidationOracle score. If recent_scores show stale regime, propose new avenue plan and look for mycelial or symbiotic improvements.

### AUTO_PRE_LAUNCH_CONTEXT_TEMPLATE
Pre-Launch Final Context v5: Before spawning the Dynamic Swarm, apply these final constraints: Aggressively coordinate the four ToolHunter sub-swarms in parallel where possible. Every verifier snippet or oracle must pass deterministic symbolic checks prior to synthesis. Synthesis must strictly follow MARL credit rule. Preserve high-value patterns from memdir, wiki/, and bio layers. Insert extra self-critique if stochastic drift or stale regime is detected. Target ValidationOracle ≥ 0.92 while staying under max_compute_hours. Include Module Effectiveness Reflection. This overrides any weaker suggestions.

### EMBODIMENT_TEMPLATE
v0.6 introduces episodic self-optimization via MP4 archival, retrospective scoring, EFS meta-tuning, and full embodiment (Neurogenesis, Microbiome, Vagus). All changes remain gated by verifier-first replay testing, SOTA rubric, and human preview for any principle-impacting mutation.

