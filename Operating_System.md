# Operating System — Technical Specification

**Deep Technical Report**  
**SAGE — Shared Agentic Growth Engine**  
**Version 0.9.13-FeedbackUpdate1**  
**Last Updated:** April 23, 2026

## Abstract

The Operating System (OS) is the intelligent conductor layer of SAGE. It manages the execution of Enigma Machine (EM) instances at scale — from a single local run to a full swarm of parallel operators — while integrating the existing 0.9.10 full setup UI (wizard) as the primary entry point.

It provides:
- Wizard-first UX for solo miners with shared config for all instances.
- Compute-aware swarm size recommendation and dynamic adjustment.
- Smart LLM router with automatic downscaling as swarm size grows.
- Lightweight ping-only flight test (compute + LLM connectivity verification).
- Per-instance miner input strategy assignment for A/B testing effectiveness at inserted miner points.
- Full API / endpoint support for fully autonomous/headless operation.
- Operations telemetry feed to the Intelligence Subsystem for hierarchical learning.

This subsystem keeps the system dead-simple for a solo miner while delivering SOTA operations intelligence through hierarchical self-improvement. It is the bridge that turns individual EM runs into a scalable data factory feeding the entire SAGE flywheel.

## 1. Integration with Full Setup UI (Wizard)

The existing wizard remains the official human-friendly entry point and is the recommended starting point for all users:

- User runs the wizard once (or loads a saved config).
- Wizard collects global settings (compute sources, API keys, preferred models per task type, default contract queue, telemetry export path, miner input strategy templates, budget limits, autonomy preferences, etc.).
- Output is saved as a single shared `operations_config.json`.
- Every EM instance launched by the Orchestrator inherits this exact config — no per-instance re-setup is required.

**Autonomous Mode**  
The wizard can be fully bypassed via CLI or API for headless/large-scale operation:
```bash
python em_operations.py --autonomous --config operations_config.json --max-instances 24 --strategy-set "quantum_phd,conservative,diversity_max"
```

