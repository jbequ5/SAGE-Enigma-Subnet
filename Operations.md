# Operations Subsystem — Technical Specification

**Deep Technical Report**  
**SAGE — Shared Agentic Growth Engine**  
**Version 0.9.12+ Hardened**  
**Last Updated:** April 21, 2026

## Abstract

The Operations Subsystem is the intelligent conductor layer of SAGE. It manages the execution of Enigma Machine (EM) instances at scale — from a single local run to a full swarm of parallel operators — while integrating the existing 0.9.10 full setup UI (wizard) as the primary entry point.

It provides:
- Wizard-first UX for solo miners with shared config for all instances.
- Compute-aware swarm size recommendation.
- Smart LLM router with automatic downscaling as swarm size grows.
- Lightweight ping-only flight test (compute + LLM connectivity verification).
- Per-instance miner input strategy assignment for A/B testing effectiveness at inserted miner points.
- Full API / endpoint support for fully autonomous/headless operation.
- Operations telemetry feed to Synapse for hierarchical learning.

This subsystem keeps the system dead-simple for a solo miner while delivering SOTA operations intelligence through hierarchical self-improvement.

## 1. Integration with 0.9.10 Full Setup UI (Wizard)

The existing 0.9.10 wizard remains the official human-friendly entry point:
- User runs the wizard once (or uses a saved config).
- Wizard collects global settings (API keys, preferred models, default contract queue, telemetry export path, miner input strategy templates, etc.).
- Output is saved as a single shared `operations_config.json`.
- Every EM instance launched by the Orchestrator inherits this exact config — no per-instance re-setup is required.

**Autonomous Mode**  
The wizard can be bypassed via CLI or API:
```bash
python em_operations.py --autonomous --config operations_config.json --max-instances 12
```
## 2. EM Operations Orchestrator

The central conductor (single process or lightweight swarm) that:

•  Loads the shared wizard config.

•  Scans live compute via ResourceMonitor.

•  Recommends optimal swarm size N.

•  Runs the Smart LLM Router with downscaling.

•  Performs a lightweight ping-only flight test.

•  Assigns different miner input strategies per instance for A/B testing.

•  Launches, monitors, and recovers the swarm.

•  Collects and forwards operations telemetry.

## 3. Smart LLM Router & Downscaling
The router profiles the task queue and current compute, then recommends LLM size per task type. As swarm size N grows, it automatically downscales:

$$text{Effective Model Size} = \text{Base Recommendation} \times \left(1 - \text{downscale factor} \times (N - 1)\right)$$

•  Base Recommendation is determined by task-type profiling (symbolic-heavy, numeric/optimization, graph-heavy, verification-light, synthesis-heavy) using contract analysis and embedding similarity.

•  downscale_factor is learned over time by Synapse meta-RL.

•  Router always respects total available VRAM with an 80% safety margin.

Model Registry (stored in shared config or models.json): Each model entry includes: name, VRAM requirement, relative capability score, latency estimate, and supported features.

## 4. Lightweight Flight Test (Ping Only)

Before committing to the full swarm, the Orchestrator performs a pure ping test:

•  ResourceMonitor.scan() to verify compute availability and VRAM/CPU headroom.

•  Quick LLM health check (dummy API call or status endpoint ping) for each recommended model to verify connectivity, credentials, and basic rate limits.

•  No full EM instance is run.

•  Produces a simple availability and estimated cost summary.

If any ping fails, the Orchestrator re-recommends and retries.

## 5. Miner Input Strategy Assignment (A/B Testing)
The Orchestrator assigns different miner input strategies to different EM instances only at the inserted miner input points (hypothesis refinement, next-contract choice, etc.).

•  Strategies are stored as prompt templates or decision heuristics in the shared config.

•  Examples: “PhD-level quantum physics knowledge injection”, “conservative verification-first”, “aggressive synthesis-first”, “diversity-maximizing”.

•  Each instance receives one strategy for its run.

•  All outcomes (EFS lift, fragment quality, stall rate) are logged with the strategy ID.

•  This enables direct A/B measurement of which miner input strategies produce the best results.

•  Synapse meta-RL can later learn and recommend the best strategies over time.

## 6. Operations Telemetry Collection

Operations data is collected in a dedicated telemetry stream (JSONL files or database table) and sent to Synapse. No new 60/40-style scoring is applied.

Telemetry Schema (each record includes):

•  launch_timestamp

•  instance_id

•  assigned_hardware (GPU ID, VRAM, etc.)

•  assigned_model

•  assigned_miner_input_strategy

•  flight_test_results (ping success, latency)

•  resource_peaks (VRAM, CPU, duration)

•  fragments_produced

•  final_efs_achieved

•  stall_count

•  estimated_cost_per_fragment

Telemetry is batched and forwarded to Synapse meta-RL as additional features/objectives for learning better orchestration policies.

## 7. Recovery and Dynamic Adjustment

The Orchestrator includes basic recovery logic:

•  If an instance stalls (> T minutes without fragments), it is restarted with a different seed or strategy.

•  If total resource usage exceeds safety margins, N is dynamically reduced and instances are rebalanced.

•  Circuit-breaker: if > 30% of instances fail, the swarm pauses and alerts.

## 8. API and Endpoint Options

The Orchestrator exposes simple FastAPI endpoints for headless control:

•  POST /start_swarm — launch with config and optional overrides

•  GET /status — current swarm health, telemetry summary, and A/B results

•  POST /stop — graceful shutdown

•  POST /flight_test — run on-demand ping test

•  POST /adjust_swarm — change N or force strategy assignments

## 9. Synapse Connections

•  Normal fragments → Solve → Strategy → Synapse (unchanged).

•  Operations telemetry → Operations Logger → Synapse meta-RL (additional learning signal for orchestration policies, 
swarm sizing, LLM routing, and miner input strategies).

## 10. Data Flow Summary

Wizard (or API) → Shared Config → Orchestrator (compute scan + router + ping flight test + strategy assignment)

Orchestrator → EM Instances (parallel, shared config)

EM Instances → Solve (fragments) + Operations Logger (telemetry)

Solve → Strategy → Synapse

Operations Logger → Synapse (learning signal)

## 11. Attack Vectors and Mitigations

•  Resource exhaustion → ResourceMonitor + safety margins + flight test

•  Task queue poisoning → provenance validation on assigned contracts

•  Strategy gaming → A/B results validated against actual EFS lift

•  Telemetry tampering → hashed records with provenance

All operations are logged with full provenance and can be audited by the AHE.

## 12. Meta-Tuning Interaction

Synapse’s global meta-RL loop tunes both inner EM parameters and outer Operations parameters (swarm size rules, LLM 
routing policy, miner input strategy effectiveness, recovery thresholds). Local TPE tuning in each EM instance remains unchanged.

This creates a clean hierarchical meta-learning system.

## Why the Operations Subsystem Matters

The Operations Subsystem turns SAGE from a single-run tool into a scalable, self-improving parallel data factory. By integrating the familiar 0.9.10 wizard, adding compute-aware routing with intelligent downscaling, a lightweight ping-only flight test, per-instance miner input strategy assignment for A/B testing, full API support, and a dedicated telemetry feed to Synapse, it delivers SOTA operations intelligence while remaining dead-simple for a solo miner to run fully autonomously. The hierarchical learning loop (inner EM solving + outer orchestration learning) accelerates the entire SAGE flywheel faster than any individual miner could achieve alone.

