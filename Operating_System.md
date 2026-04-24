# Operating System — Technical Specification

**Deep Technical Report**  
**SAGE — Shared Agentic Growth Engine**  
**Version 0.9.13-FeedbackUpdate1**  
**Last Updated:** April 23, 2026

## Abstract

The Operating System (OS) is the intelligent conductor layer of SAGE. It manages the execution of Enigma Machine (EM) instances at scale — from a single local run to a full swarm of parallel operators — while integrating the existing 0.9.10 full setup UI (wizard) as the primary entry point.

It provides:
- Wizard-first UX for solo miners with shared config for all instances.
- Intelligent Multi-Approach Planner that determines optimal diversity and assigns profiles.
- Compute-aware swarm size recommendation and dynamic adjustment.
- Smart LLM router with automatic downscaling as swarm size grows.
- Lightweight ping-only flight test.
- Controlled inter-agent communication for emergent collaboration.
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
The wizard can be fully bypassed via CLI or API for headless/large-scale operation.

## 2. EM OS Orchestrator + Multi-Approach Planner

The central conductor (single process or lightweight distributed swarm) that:

- Loads the shared wizard config.
- Scans live compute via ResourceMonitor.
- Runs the **Multi-Approach Planner (MAP)** to intelligently determine optimal N and generate distinct high-value approach profiles.
- Recommends swarm size N based on available resources, historical telemetry, and planner output.
- Runs the Smart LLM Router with automatic downscaling.
- Performs a lightweight ping-only flight test.
- Assigns each instance (or sub-swarm) one dedicated approach profile.
- Launches, monitors, recovers, and gracefully shuts down the swarm.
- Facilitates controlled inter-agent communication.
- Collects and forwards rich operations telemetry to the Intelligence Subsystem.

**Multi-Approach Planner (MAP)**  
- Analyzes the challenge, verification contract, current compute, and latest meta-weights.
- Generates N distinct, well-justified approach profiles (reasoning style, tool preferences, temperature, emphasis areas, risk profile).
- Dynamically chooses N to balance exploration and resource efficiency.
- Outputs structured JSON profiles for reproducibility and A/B analysis.

## 3. Smart LLM Router & Downscaling

The router profiles the task queue and current compute, then recommends LLM size per task type. As swarm size N grows, it automatically downscales to stay within resource limits.

**Model Registry** includes name, VRAM requirement, relative capability score, latency estimate, and supported features.

## 4. Lightweight Flight Test (Ping Only)

Before committing to the full swarm, the Orchestrator performs a pure connectivity and sanity test (ResourceMonitor + quick LLM pings). No full EM instance is run.

## 5. Miner Input Strategy Assignment & Controlled Communication

Each instance is assigned one primary approach profile from the Multi-Approach Planner.

**Mid-Run Flexibility**  
On stall or low progress, an instance can request a temperature boost or minor profile adjustment. The planner approves or rejects in real time.

**Controlled Inter-Agent Communication**  
- Lightweight, structured message bus between the N instances.
- Only high-confidence, verifier-checked insights are allowed.
- Rate-limited (max 3–5 messages per instance per run).
- Optional subscription to insights from specific approaches.
- All communication is logged with provenance and fed back to Intelligence for meta-learning.

This enables strong approaches to build on each other without turning the swarm into a single chatty entity.

## 6. OS Telemetry Collection

Operations data is collected in a dedicated telemetry stream and sent to the Intelligence Subsystem. This includes per-approach performance, communication events, and adjustment outcomes.

## 7. Recovery and Dynamic Adjustment

The Orchestrator includes robust recovery and rebalancing logic, including mid-swarm profile adjustments and approach merging when beneficial.

## 8. API and Endpoint Options

Simple FastAPI endpoints for headless control.

## 9. Synapse & Intelligence Connections

Operations telemetry (including approach effectiveness and communication patterns) feeds the Intelligence Subsystem for meta-learning. Updated global approximations and meta-weights are automatically applied.

## 10. Data Flow Summary

Wizard → Shared Config → Multi-Approach Planner + Orchestrator → EM Instances (parallel with assigned profiles + controlled communication) → Solve + Operations Logger → Intelligence Subsystem.

## 11. Attack Vectors and Mitigations

Resource exhaustion, task queue poisoning, strategy gaming, and telemetry tampering are mitigated through existing guards plus approach-level validation.

## 12. Meta-Tuning Interaction

The Intelligence Subsystem’s global Meta-RL loop tunes both inner EM parameters and outer OS parameters, including planner behavior, communication policies, and role/approach effectiveness.

## Why the Operating System Matters

The Operating System, with its intelligent Multi-Approach Planner, turns SAGE from a single-run tool into a scalable, self-improving parallel data factory. It intelligently determines optimal diversity, assigns focused approach profiles, enables controlled cross-approach collaboration, and feeds rich telemetry back into the global intelligence loop. This hierarchical orchestration maximizes EFS, resource efficiency, and learning velocity while remaining dead-simple for a solo miner to run fully autonomously.

This layer is essential for turning SAGE into a true community-scale intelligence engine.
