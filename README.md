# Enigma Machine Miner – Bittensor SN63

**Arbos-centric primary solver with intelligent planning, dynamic vLLM swarm, real-time ToolHunter, miner-controlled executable verification, and automatic deterministic/symbolic tooling**

The most intelligent and resource-efficient solo miner on Subnet 63 (Quantum Innovate / qBitTensor Labs). Designed from first principles to solve extremely hard, well-defined computational challenges across quantum and any industry — within the strict ~4-hour H100 limit.

### Core Architecture – The Intelligent Loop

```mermaid
flowchart TD
    A["SN63 Challenge + GOAL.md"] 
    --> B["🔬 Intelligent Planning Arbos<br/>High-level plan + suggested swarm size + deterministic recommendations"]

    B --> C["Miner Approval<br/>(Streamlit UI)"]
    C -->|"✅ Approve"| D["🧠 Orchestrator Arbos<br/>Plan Refinement → Executable Blueprint"]
    C -->|"🔄 Tweak"| B
    C -->|"❌ Reject"| A

    D --> E["🚀 Dynamic Subprocess Agent Swarm<br/>Parallel Sub-Arbos Instances<br/>(3–6 on one H100 with vLLM + real-time VRAM monitoring)"]

    E --> F1["Sub-Arbos 1<br/>Subtask + Hypothesis<br/>→ Symbolic Module + ToolHunter if needed"]
    E --> F2["Sub-Arbos 2<br/>Subtask + Hypothesis<br/>→ Symbolic Module + ToolHunter if needed"]
    E --> FN["Sub-Arbos N<br/>Subtask + Hypothesis<br/>→ Symbolic Module + ToolHunter if needed"]

    F1 & F2 & FN --> G["🔄 Reconvene with Main Arbos<br/>Synthesis of all sub-results"]

    G --> H["📊 Final Quality Gate<br/>Structured SN63 Evaluation +<br/>Miner-Provided Executable Verification"]

    H -->|"✅ Pass"| I["Final Miner Review<br/>+ One-click SN63 Packaging"]
    H -->|"❌ Fail"| J["Arbos Improvement Loop<br/>Re-reflect → Re-refine → Re-swarm"]

    J --> G

    I --> K["Submit to SN63<br/>submission_package.zip"]
```

**Key Intelligence Highlights**
- **Planning Arbos** analyzes the challenge and **recommends deterministic/symbolic tools** (e.g., Stim for stabilizers, Quantum Rings for fidelity, PyTKET for optimization).
- **Miner-Controlled Deterministic Tooling** — After seeing recommendations, the miner can add/edit specific tooling requirements before the swarm runs. This gives time to install missing packages.
- **Automatic Symbolic Module** — Arbos now calls deterministic/symbolic reasoning **automatically** in sub-Arbos workers for matching subtasks (stabilizer checks, fidelity estimation, circuit optimization, preprocessing).
- **Direct Quantum Rings & OpenQuantum Support** — Built into the verification engine for real simulator execution.
- **Hybrid Reasoning** — Prefers deterministic tools first, falls back to LLM only when necessary.
- **Resource Awareness** — Real-time VRAM monitoring, dynamic tensor parallelism, early aborts, and compute limits.

### How Deterministic Tooling Works

1. Planning Arbos shows recommendations in the Streamlit approval screen.
2. Miner reviews and adds "Deterministic Tooling Requirements" (e.g., "Use stim for stabilizer checks. Run fidelity with quantum_rings. Prefer symbolic fallbacks.").
3. Miner installs any missing tools while reviewing.
4. When approved, Arbos automatically uses the symbolic module and miner-specified tools where applicable.

### GOAL.md / killer_base.md Configuration

```markdown
## Core Toggles (Actively Used)

resource_aware: true               # Enforces time budgets and early aborts
guardrails: true                   # Output cleaning and sanity checks
toolhunter_escalation: true
manual_tool_installs_allowed: true

miner_review_after_loop: false
max_loops: 5
miner_review_final: true

max_compute_hours: 3.8
chutes: true
chutes_llm: mixtral

# Swarm Efficiency
tensor_parallel_size: 1
```

### Quick Start

```bash
pip install -r requirements.txt
pip install vllm                    # Strongly recommended for swarm performance
streamlit run streamlit_app.py
```

(Optional: Add `GITHUB_TOKEN` to `.env` for richer ToolHunter searches. Install `stim`, `qiskit`, `pytket`, or `quantumrings` as needed for full deterministic power.)

### Why This Wins on SN63

- Strong intelligent decomposition with **Arbos-driven deterministic recommendations**
- Miner has precise control over both verification **and** deterministic tooling
- Automatic symbolic reasoning reduces LLM reliance on standard tasks
- Parallel hypothesis exploration with per-subtask ToolHunter + vLLM efficiency
- Real-time VRAM monitoring and strict compute awareness
- Full transparency, memory-driven learning, and one-click packaging

**Ready for Phase 2.**

---

Made with focus on first-principles agentic design for Bittensor SN63.  
Questions or feature requests? Open an issue or ping @dTAO_Dad on X.
```
