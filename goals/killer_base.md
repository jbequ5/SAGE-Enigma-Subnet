GOAL: Solve the sponsor challenge with maximum novelty and verifier score while staying under 3.8h on H100.

# ============== CORE TOGGLES ==============
# Edit these lines to customize how Arbos behaves. All are optional.

**reflection: 4**                   #Self-critique iterations (higher = better quality, slower)

**planning: true**                 #Break challenge into structured sub-tasks

**hyper_planning: true**          #Use HyperAgent for intelligent self-improving planning (powerful but heavier - turn on for hard challenges)

**multi_agent: true**              #ScienceClaw swarm for parallel discovery

**swarm_size: 20**                 #Number of agents in swarm (lower = faster, higher = more creative)

**exploration: true**              #Generate truly novel variants (big prize potential)

**resource_aware: true**           #Auto-compress to enforce 4h H200 limit (highly recommended)

**guardrails: true**               #Safety checks before final submission

# ============== RALPH LOOP STEPS ==============
# You can reorder or customize these steps

Steps per Ralph loop:
1. Plan the attack (uses HyperAgent if hyper_planning: true)
2. Execute with smart tool routing (GPD, ScienceClaw, AI-Researcher)
3. Reflect and improve (self-critique loop)
4. Explore one novel variant (if exploration: true)
5. Resource check + compress if needed
6. Final guardrails validation
