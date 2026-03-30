# Enigma Machine Miner - Killer Base Strategy & Toggles
# Bittensor SN63 - Arbos-centric Solver

## GOAL
Solve the sponsor challenge with maximum novelty and verifier score while staying under the *DESIRED COMPUTE LIMIT*.

## Core Strategy (Miner Customizes)
Produce novel, verifier-strong, licensable solutions for SN63 challenges while staying strictly within compute limits and maximizing IP/value.

Always prioritize:
- High novelty + verifier potential
- Efficient use of compute
- Clear, reproducible outputs
- Verifier-code-first execution

## Toggles & Explanations

### Core Behavior
miner_review_after_loop: false     # true = pause after every major loop for miner input
max_loops: 5                       # Maximum automatic loops when review is off
miner_review_final: true           # Always require final miner review before submission

### Compute & Resource Management
use_openrouter_first: false     # Set to true if you want OpenRouter as primary gateway
openrouter_model_preference: "anthropic/claude-3.5-sonnet"   # or "openai/gpt-4o", etc.
compute_source: chutes             # Options: local, chutes, already_running, custom
max_compute_hours: 3.8             # Dynamic maximum compute time for the entire challenge
resource_aware: true               # Actively enforces time budgets, early aborts slow branches, adjusts swarm size

### Core Mechanisms (Hardened)
quasar_attention: true             # Enables 5M+ stable context for Planning / Adaptation Arbos
dynamic_swarm: true                # Swarm size automatically computed from available VRAM
verifier_first: true               # Symbolic module runs challenge-provided verifier code first
light_compression: true            # Automatic low-value context pruning when >150k tokens

### Safety & Quality
guardrails: true                   # Applies output cleaning and sanity checks after each sub-Arbos and final synthesis

### Tool Handling
toolhunter_escalation: true        # Enables ToolHunter to generate manual recommendations on failure
manual_tool_installs_allowed: true # Shows manual installation instructions when needed
runtime_tool_creation: false       # Disabled for launch (proposals only)

### Self-Improvement
grail_on_winning_runs: true        # Enables lightweight verifiable post-training only on >0.92 runs
self_critique_enabled: true        # Runs Arbos self-critique on recent trajectories

# Swarm & Reflection
max_swarm_size: 20
default_reflection_iterations: 3
max_iterations: 8

## Local Compute Settings (vLLM)
tensor_parallel_size: 1          # 1 for single H100, 2 or 4 for multi-GPU
vllm_model: mistralai/Mistral-7B-Instruct-v0.2   # fallback model when Quasar

## Notes for Miner
- Quasar Attention is used automatically for planning, orchestration, and every re_adapt loop.
- Swarm size is dynamically calculated based on real VRAM — no hard cap at 6.
- Tool creation is disabled for safety. Only proposals are generated for next runs.
- All self-improvement flows through Adaptation Arbos + light memory compression.
