**GOAL:** Solve the sponsor challenge with maximum novelty and verifier score while staying under *DESIRED COMPUTE LIMIT* 

**STRATEGY/CONTEXT:** *Miner Customizes*

**CORE TOGGLES (Actively Used)**

reflection: 4

exploration: true

resource_aware: true

guardrails: true

toolhunter_escalation: true

manual_tool_installs_allowed: true

**Miner Input**

miner_review_after_loop: false     **#true = review after every loop**

max_loops: 4                       **#max automatic loops when review is off**

miner_review_final: true           **#always review final output**

**Compute + LLM**

chutes: true

targon: false

celium: false

chutes_llm: mixtral

**Optional: Steps description (for documentation only)**
1. Dynamic tool routing + reflection
2. Real ScienceClaw at end of each loop
3. Auto-reloop if needed (when miner_review_after_loop = false)
4. Final miner review before submission
