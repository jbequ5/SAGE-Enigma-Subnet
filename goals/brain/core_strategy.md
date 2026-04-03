## Core Strategy (Challenge-Agnostic Base Prompt)
- Treat every problem as pure symbolic/text — no premature domain assumptions.
- Verifier-code-first + symbolic invariants on **every** subtask **before** any LLM generation.
- ToolHunter sub-swarm (ModelHunter / ToolHunter / PaperHunter / ReadyAI-DataHunter) must run in parallel where possible; serial handoffs **must** route through ValidationOracle.
- Reward **only** trajectories that measurably improve ValidationOracle score via exact 0-1 deterministic checks.
- Every Adaptation Arbos step must first search trajectory_vector_db + memdir/grail for proven high-score symbolic patterns.
- Maximize symbolic coverage per compute unit while preserving reproducibility.
- On low-score or stale runs, explicitly trigger re_adapt with compressed deltas and consider deep replan via new avenue plan.
- Run reflection on every prompt evolution step. Ensure evolution stays strictly on task
