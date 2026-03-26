# Enigma Machine Miner - Killer Base Strategy & Toggles
# Bittensor SN63 - Arbos-centric Solver

## GOAL
Solve the sponsor challenge with maximum novelty and verifier score while staying under the *DESIRED COMPUTE LIMIT*.

## Core Strategy (Miner Customizes)
Produce novel, verifier-strong, licensable solutions for SN63 challenges while staying strictly within compute limits and maximizing IP/value.

Always prioritize:
- High novelty + verifier potential on Quantum Rings
- Efficient use of compute
- Clear, reproducible outputs

## Toggles & Explanations

### Core Behavior
miner_review_after_loop: false     # true = pause after every major loop for miner input
max_loops: 5                       # Maximum automatic loops when review is off
miner_review_final: true           # Always require final miner review before submission

### Compute & Resource Management
max_compute_hours: 3.8             # Dynamic maximum compute time for the entire challenge
resource_aware: true               # Actively enforces time budgets, early aborts slow branches, adjusts swarm size

### Safety & Quality
guardrails: true                   # Applies output cleaning and sanity checks after each sub-Arbos and final synthesis

### ToolHunter
toolhunter_escalation: true        # Enables ToolHunter to generate manual recommendations on failure
manual_tool_installs_allowed: true # Shows manual installation instructions when needed

### Routing & LLM
chutes: true
chutes_llm: mixtral

### Swarm Efficiency (vLLM)
tensor_parallel_size: 1            # Set to 2 or 4 if you have multiple GPUs. Keep 1 for single H100
vllm_model: mistralai/Mistral-7B-Instruct-v0.2   # Change this to any model you want to use with vLLM
