# tools/archive_hunter.py
# v0.9.11 MAXIMUM SOTA ArchiveHunter — Hybrid Genome/Paper Ingestion
# Ingest EvoAgent / Sakana / arXiv / llms.txt archives → MAU atomization → reinforcement → 
# stigmergy write to memory, FragmentTracker, VaultRouter, and Wiki. Full SOTA/EFS/7D wiring.

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from agents.validation_oracle import ValidationOracle
from agents.tools.readyai_tool import readyai_tool

logger = logging.getLogger(__name__)

class ArchiveHunter:
    def __init__(self, oracle: ValidationOracle):
        self.oracle = oracle
        self.arbos = None  # wired by ArbosManager
        self.fragment_tracker = None
        self.intelligence = None
        self.pd_arm = None
        logger.info("✅ ArchiveHunter v0.9.11 MAX SOTA initialized — full hybrid genome/paper ingestion with MAU atomization")

    def set_arbos(self, arbos):
        self.arbos = arbos
        if arbos:
            self.fragment_tracker = getattr(arbos, 'fragment_tracker', None)
            self.intelligence = getattr(arbos, 'intelligence', None)
            self.pd_arm = getattr(arbos, 'pd_arm', None)

    def ingest_genome_or_paper(self, payload: dict) -> Dict[str, Any]:
        """Full SOTA ingestion pipeline: atomize → score → reinforce → stigmergy write."""
        if not payload:
            return {"status": "error", "reason": "Empty payload"}

        logger.info(f"ArchiveHunter ingesting payload: {payload.get('title', 'Untitled')} | source: {payload.get('source', 'unknown')}")

        # 1. Atomize external knowledge using ValidationOracle
        mau_atoms = self.oracle.atomize_external_knowledge(payload)

        ingested_count = 0
        high_signal_atoms = 0

        for atom in mau_atoms:
            # 2. Reinforce with EFS scoring and 7D signals
            reinforcement_result = self.oracle.reinforce_mau(
                atom, 
                source="hybrid_ingest",
                context=payload
            )

            if reinforcement_result.get("efs_delta", 0.0) > 0.08:
                high_signal_atoms += 1

            # 3. Stigmergy write to memory layers + FragmentTracker
            if self.fragment_tracker:
                self.fragment_tracker.add_fragment({
                    "content": atom.get("content", ""),
                    "metadata": {
                        "type": "hybrid_knowledge",
                        "source": payload.get("source", "unknown"),
                        "title": payload.get("title", ""),
                        "efs_contrib": reinforcement_result.get("efs_delta", 0.0),
                        "timestamp": datetime.now().isoformat()
                    }
                })

            ingested_count += 1

        # 4. High-signal routing to VaultRouter + PD Arm
        if high_signal_atoms > 2 and self.intelligence:
            run_data = {
                "insight_score": 0.88,
                "key_takeaway": f"ArchiveHunter ingested {ingested_count} atoms ({high_signal_atoms} high-signal)",
                "predictive_power": getattr(self.arbos, 'predictive_power', 0.0) if self.arbos else 0.0,
                "flywheel_step": "hybrid_ingest_to_vaults_pd"
            }
            self.intelligence.route_to_vaults(run_data)

            if self.pd_arm:
                self.pd_arm.synthesize_product(
                    vault_data=[], 
                    market_signals={"market_signal": f"Hybrid knowledge from {payload.get('source')}"}
                )

        # 5. Trigger pattern surfacers on high-signal ingestion
        if high_signal_atoms > 1 and self.arbos and hasattr(self.arbos, 'rps'):
            self.arbos.rps.surface_resonance({"efs": 0.82, "heterogeneity_score": 0.88})

        result = {
            "status": "ingested",
            "ingested_count": ingested_count,
            "high_signal_atoms": high_signal_atoms,
            "efs_delta": round(sum(a.get("efs_delta", 0.0) for a in mau_atoms), 3),
            "source": payload.get("source", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "flywheel_signal": "hybrid_knowledge_injected"
        }

        logger.info(f"ArchiveHunter completed ingestion — {ingested_count} atoms | {high_signal_atoms} high-signal | EFS delta: {result['efs_delta']:.3f}")
        return result

    def ingest_from_readyai(self, query: str) -> Dict[str, Any]:
        """Convenience method: ingest structured knowledge from ReadyAI."""
        readyai_result = readyai_tool.get_structured_knowledge(query, limit=6)
        if readyai_result.get("success"):
            payload = {
                "title": f"ReadyAI Knowledge: {query}",
                "source": "readyai_llms.txt",
                "content": readyai_result.get("summary", ""),
                "results": readyai_result.get("results", [])
            }
            return self.ingest_genome_or_paper(payload)
        return {"status": "failed", "reason": "ReadyAI query unsuccessful"}

# Global instance (instantiated in ArbosManager)
archive_hunter = None
