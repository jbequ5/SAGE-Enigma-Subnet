# SAGE — Shared Agentic Growth Engine

**The People’s Intelligence Layer for Bittensor Subnet 63**

SAGE uses the Enigma Machine — a powerful verifier-first agentic solver — to turn every successful mining run on Subnet 63 into fuel for a self-improving, community-owned intelligence system.

High-signal fragments from real solving runs are captured, rigorously scored with full provenance using the 60/40 rule, and continuously refined through the **Intelligence Subsystem**. The best intelligence is then converted into practical strategies, sponsor proposals, tools, and assets that create real economic value — all while rewarding honest contribution and eventually distilling the accumulated knowledge into smaller, specialized Enigma models that further democratize participation.

Built **for the people, by the people**, using decentralized incentives to compound solving intelligence instead of extracting it.

### Quick Navigation

**Vision & Overview**
- [VISION.md](VISION.md) — The big picture: opportunity, vision, flywheel, and why this matters

**Core Platform Architecture**
- [SAGE-Deep-Dive.md](SAGE-Deep-Dive.md) — Full platform architecture and data flow between all subsystems

**The Solver**
- [Enigma-Machine-Deep-Dive.md](Enigma-Machine-Deep-Dive.md) — Deep technical dive into the Enigma Machine (verifier-first design, DVR pipeline, hybrid compute, memory system, and how it feeds SAGE)
  
**Operations — Running & Scaling SAGE**
- [Operations-Subsystem.md](subsystems/Operations-Subsystem.md) — How to run, orchestrate, and scale Enigma Machine instances (from single local run to full swarm). Includes the Operations Wizard, Smart LLM Router, flight test, and autonomous mode.
  
**Meta-Agent**
- [SYNAPSE-Deep-Dive.md](SYNAPSE-Deep-Dive.md) — Deep-Dive on SAGE's Meta-Agent - Synapse.

**Subsystem Specifications** (in the `subsystems/` folder)

These deep technical reports are written to be rigorous enough to rebuild or audit each piece of the system from scratch. They are living documents that will evolve with the code.

- [Solve-Subsystem.md](subsystems/Solve-Subsystem.md)
- [Strategy-Subsystem.md](subsystems/Strategy-Subsystem.md)
- [Economic-Subsystem.md](subsystems/Economic-Subsystem.md)
- [Operations-Subsystem.md](subsystems/Operations-Subsystem.md)
- [Defense-Subsystem.md](subsystems/Defense-Subsystem.md)
- [Intelligence-Subsystem.md](subsystems/Intelligence-Subsystem.md)

See the individual documents for setup instructions, how to run the Enigma Machine, contribution guidelines, and technical details.

### Contribution & Participation

Miners, developers, researchers, and sponsors are all welcome. Every high-signal fragment you generate helps strengthen the shared intelligence. Clear contribution scoring, provenance tracking, and transparent reward mechanisms ensure that real value creation is recognized and rewarded.

### Why SAGE Matters

In a world where most AI systems extract value for private gain, SAGE does the opposite. It harnesses the competitive pressure and prize pools of Subnet 63 to generate rich, verifiable solving data, then compounds that data into shared, self-improving intelligence that benefits contributors first.

The result is a true flywheel: better runs produce richer data, richer data produces smarter strategies, smarter strategies produce stronger economic value, and that value creates larger incentives and better models — drawing in even more participation.

This doesn’t exist anywhere else today.

Built by the many. Owned by the many. Designed so the people who build it are the ones who win.

---

**Repository Structure Note**  
All deep subsystem reports live in the `subsystems/` folder so the root stays clean and focused on navigation. The documents are designed to be both inspirational for new users and technically rigorous enough for developers or researchers who want to understand or rebuild the system from scratch.
