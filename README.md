# Enigma Machine Miner – Bittensor SN63

**Arbos-centric primary solver with intelligent planning, dynamic swarm, and real-time ToolHunter**

The most intelligent and resource-efficient miner on Subnet 63 (Quantum Innovate / qBitTensor Labs). Designed from first principles to solve extremely hard, well-defined computational challenges across quantum and any industry — within the strict ~4-hour H100 limit.

### Core Architecture – The Intelligent Loop

```mermaid
flowchart TD
    A["GOAL.md<br/>Clear Challenge Definition +<br/>Miner Context/Strategy"] 
    --> B["🔬 Intelligent Planning Arbos<br/>High-level plan + suggested swarm size + tool hunts"]

    B --> C["Miner Approval<br/>(Streamlit UI)"]
    C -->|"✅ Approve"| D["🧠 Orchestrator Arbos<br/>Plan Refinement → Executable Blueprint<br/>(decomposition + swarm_config + tool_map)"]
    C -->|"🔄 Tweak"| B
    C -->|"❌ Reject"| A

    D --> E["🚀 Dynamic Subprocess Agent Swarm<br/>Parallel Sub-Arbos Instances<br/>(3–6 on one H100)"]

    E --> F1["Sub-Arbos 1<br/>Subtask + Hypothesis<br/>→ Specific ToolHunter if needed"]
    E --> F2["Sub-Arbos 2<br/>Subtask + Hypothesis<br/>→ Specific ToolHunter if needed"]
    E --> FN["Sub-Arbos N<br/>Subtask + Hypothesis<br/>→ Specific ToolHunter if needed"]

    F1 & F2 & FN --> G["🔄 Reconvene with Main Arbos<br/>Synthesis of all sub-results"]

    G --> H["📊 Final Quality Gate<br/>Structured SN63 Evaluation<br/>(novelty, verifier potential, alignment, completeness, efficiency, IP)"]

    H -->|"✅ Pass"| I["Final Miner Review<br/>+ One-click SN63 Packaging"]
    H -->|"❌ Fail"| J["Arbos Improvement Loop<br/>Re-reflect → Re-refine → Re-swarm"]

    J --> G

    I --> K["Submit to SN63<br/>submission_package.zip"]
```

**Key Intelligence Highlights**
- **Intelligent Planning Arbos** creates the high-level strategy and swarm guidance.
- **Orchestrator Arbos** intelligently breaks the problem into subprocesses with a precise `tool_map` per subtask.
- **Subprocess Agent Swarm** runs true parallel exploration, with **subtask-specific ToolHunter** calls when gaps are detected.
- **Main Arbos Reconvene** synthesizes results intelligently.
- **Adaptive Re-loop Decision** at the quality gate keeps the system reflective and self-improving until the solution passes or the compute budget is reached.
  
### How ToolHunter Works

ToolHunter is a **dynamic meta-tool** that allows the swarm to discover, evaluate, and integrate new tools on-the-fly when the current solution has a knowledge or capability gap.

**Process**:
1. A sub-Arbos detects a gap during its mini-reflection (or the blueprint `tool_map` flags it).
2. ToolHunter generates precise search queries and performs real searches on GitHub and arXiv.
3. It ranks candidates by relevance, GPU-friendliness, and SN63/Quantum Rings compatibility.
4. It attempts safe cloning and basic testing in a temporary sandbox (with timeouts).
5. **Success** → Returns integration code + patch. The tool is stored in long-term memory for future reuse.
6. **Failure** (dependency issues, build errors, etc.) → Generates a clear **miner escalation recommendation** with copy-paste commands, risks, and a suggested wrapper. This appears prominently in the final review screen.

This keeps the system autonomous where possible while intelligently escalating hard cases to the miner.


### GOAL.md / killer_base.md Configuration

Your main strategy and control file is **`goals/killer_base.md`**. It is injected at every stage (Planning Arbos, Orchestrator Arbos, reflections, and quality gates).

```markdown
## GOAL
Solve the sponsor challenge with maximum novelty and verifier score while staying under *DESIRED COMPUTE LIMIT* 

## Core Strategy Example (MINER EDIT/ADD)
Produce novel, verifier-strong, licensable solutions for extremely SN63 challenges (quantum circuits, stabilizer preprocessing, hybrid optimization, etc.) while staying strictly within compute limits and maximizing IP/value.

Always prioritize:
- High novelty + verifier potential
- Efficient use of Compute
- Clear, reproducible outputs

## Toggles & Explanations

### Core Behavior
reflection: 4                    # Number of reflection cycles per sub-Arbos or main loop
miner_review_after_loop: false   # If true, pause after each major loop for miner input
max_loops: 5                     # Maximum improvement loops before forcing finalization
miner_review_final: true         # Always require final miner review before submission (recommended)

### Compute & Resource Management
max_compute_hours: 3.8           # Dynamic maximum compute time for the entire challenge
resource_aware: true             # ACTIVELY ENFORCED - monitors time, aborts slow branches, 
                                 # adjusts swarm size, and feeds remaining time into prompts

### Safety & Quality
guardrails: true                 # Applies output cleaning, verifier hooks, and sanity checks 
                                 # after each sub-Arbos and after final synthesis

### Routing
chutes: true                     # Enable dynamic routing to external compute (Chutes/Celium)
chutes_llm: claude              # LLM used when routing heavy tasks
```

The full content of `killer_base.md` is loaded at startup and strongly injected into every Arbos decision.

### Quick Start

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

(Optional: Add `GITHUB_TOKEN` to `.env` for richer ToolHunter searches.)

### Why This Wins on SN63

- True **intelligent decomposition** via Planning + Orchestrator Arbos
- Parallel hypothesis exploration with per-subtask ToolHunter
- Closed-loop reflection and re-looping at the quality gate
- Full transparency and miner control at every critical decision
- Self-improving via contextual and long-term memory

**Phase 2 ready.**

---

Made with focus on first-principles agentic design for Bittensor SN63.  
Questions or feature requests? Open an issue or ping @dTAO_Dad on X.
