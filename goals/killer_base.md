**GOAL:** 
Solve the sponsor challenge with maximum novelty and verifier score while staying under the *DESIRED COMPUTE LIMIT*.

**STRATEGY/CONTEXT:** 
*Miner Customizes Here* — Add your specific preferences, Quantum Rings integration notes, novelty guidelines, IP focus, etc.

# CORE TOGGLES (Actively Used)

resource_aware: true               # Actively enforces time budgets, early aborts slow branches, and adjusts swarm behavior
guardrails: true                   # Applies output cleaning, verifier hooks, and sanity checks after each sub-Arbos and final synthesis

toolhunter_escalation: true        # When ToolHunter fails to auto-integrate, it generates clear manual instructions for the miner
manual_tool_installs_allowed: true # Allows miner to manually install tools recommended by ToolHunter

# Miner Input / Review Flow
miner_review_after_loop: false     # true = pause for miner review after every major loop
max_loops: 4                       # Maximum automatic loops when miner_review_after_loop is false
miner_review_final: true           # Always require final miner review before packaging/submission (recommended for prize submissions)

# Compute + Routing
max_compute_hours: 3.8             # Dynamic maximum compute time for the entire challenge
chutes: true                       # Enable dynamic routing to external compute when beneficial
chutes_llm: Claude                 # LLM used when routing heavy tasks via Chutes
