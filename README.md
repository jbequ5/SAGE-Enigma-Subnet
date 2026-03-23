# Enigma Machine – Agentic Miner Starter Kit for SN63

**The easiest way to build a winning miner for Enigma** — the decentralized innovation engine where anyone posts capital and “impossible” problems, and miners compete to solve them in ≤4 hours on a single H200 GPU.

**Powered by Arbos + 8 proven agentic patterns** (from Antonio Gulli’s *Agentic Design Patterns*).  
Everything is **100% optional** and miner-customizable. No black boxes. No forced settings.

### Two Modes – Your Choice
- **Optimal Mode** → One-click team-curated best stack (great for beginners)  
- **Self-Built Mode** → Full control — tune or disable anything (where top miners create their edge)

---

### Quickstart (5 minutes)

```bash
git clone https://github.com/YOUR-USERNAME/enigma-machine.git
cd enigma-machine
pip install -e .
```

1. Edit `config/miner.yaml` (your wallet + subnet details)  
2. Choose mode in `config/arbos.yaml`:
   ```yaml
   mode: optimal          # or "self-built"
   ```
3. Pick or create a GOAL.md (see templates below)  
4. Run: `./scripts/run_miner.sh`

That’s it. The miner starts and Arbos begins solving challenges immediately.

---

### The Enigma Machine – Your Fully Tunable Agent Brain

Arbos (Const’s recursive Ralph loop) is the conductor.  
You give it a simple `GOAL.md` file. Arbos then recursively improves everything — code, strategy, tools, and output — until the challenge is solved or the 4h H200 limit is reached.

**Everything below is optional.**  
You can enable, disable, or tune any pattern with **one line** in your GOAL.md.  
If you don’t like it, just turn it off — no code changes needed.

### The 8 Core Patterns – All Optional & Easy to Tune

| Pattern                        | What it does for you                                      | Impact if enabled                              | One-line toggle in GOAL.md          | Default |
|--------------------------------|-----------------------------------------------------------|------------------------------------------------|-------------------------------------|---------|
| **Reflection**                 | Agent self-critiques and improves its own output          | +3–5× quality & prize win rate                 | `reflection: 4` (or `false`)       | 3      |
| **Planning**                   | Breaks challenge into smart sub-tasks                     | Fewer wasted loops, better efficiency          | `planning: true` (or `false`)      | true   |
| **Multi-Agent**                | Runs ScienceClaw-style swarm of specialized agents        | Massive parallel breakthroughs                 | `multi_agent: true` + `swarm_size: 20` | true   |
| **Tool Use**                   | Smartly calls GPD, simulators, ScienceClaw, etc.         | Better tool selection & fewer errors           | `tool_use: true` (or `false`)      | true   |
| **Resource-Aware Optimization**| Tracks time & auto-compresses to stay under 4h H200     | **Required for prize eligibility**             | `resource_aware: true` (or `false`)| true   |
| **Exploration & Discovery**    | Generates truly novel variants others miss                | Higher novelty = bigger prize wins             | `exploration: true` (or `false`)   | false  |
| **Guardrails**                 | Hard safety checks (runtime, quality, verifier score)     | Prevents disqualification                      | `guardrails: true` (or `false`)    | true   |
| **Human-in-the-Loop**          | Your domain expertise guides the agent                    | You stay in control with simple edits          | `human_in_loop: true`              | true   |

### Where to Edit – Super Simple Breakdown

| What you want to change                  | Where you edit it                              | How easy?          |
|------------------------------------------|------------------------------------------------|--------------------|
| Toggle patterns on/off or change numbers | `goals/your_strategy.md` (your GOAL.md file)   | Just edit text     |
| Change default values for new GOALs      | `config/arbos.yaml`                            | One line change    |
| Modify how a tool works                  | `agents/tools/*.py`                            | Edit Python (optional) |
| Deep changes to Arbos core (very rare)   | `agents/arbos/` (vendored copy)                | Only if you really want to |

---

### How to Create Killer GOAL.md Files (Super Simple)

**Ready-to-use Killer Base Template** (copy this into `goals/killer_base.md` later):

```markdown
GOAL: Solve the sponsor challenge with maximum novelty and verifier score while staying under 3.8h on H200.

reflection: 4
planning: true
multi_agent: true
swarm_size: 20
exploration: true
resource_aware: true
guardrails: true

Steps per Ralph loop:
1. Plan the attack
2. Execute with tool swarm
3. Reflect and improve
4. Explore one novel variant
5. Resource check + compress if needed
```

**Pro Tips from Winning Miners**:
- Add your domain knowledge at the top (e.g., “Prioritize stabilizer formalism and error mitigation”)
- For small prizes → turn `exploration: false` and lower `swarm_size` to save TAO
- For big prizes → turn `exploration: true` and increase reflection iterations
- Create 5–10 different GOAL.md files and switch between them

---

### Optimal Subnet Integrations (All Plug-and-Play)

- **Chutes** — Private, fast LLM inference (default)  
- **Targon** — Secure TEE GPUs  
- **Celium** — Heavy parallel compute  

---

### Philosophy: Your Machine, Your Rules

This repo is built so **you** stay in full control:
- Use the Optimal stack if you want speed
- Turn off any pattern you don’t like
- Add your own secret sauce in Self-Built mode
- Edit GOAL.md anytime — no restarts needed beyond the current loop

Top miners separate themselves by experimenting with these toggles and building their own signature strategies.

**This is designed to feel like a transparent machine you can fine-tune — no mysteries, no black boxes.**

---

Ready to dominate Enigma?  
Fork the repo, create your first custom GOAL.md, and start competing.

$TAO 🚀
```
