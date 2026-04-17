# agents/commons_meta_agent.py
import json
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CommonsMetaAgent:
    """
    v0.9.11 SAGE Commons Meta-Agent
    Lightweight strategy provider that supplies reusable, high-signal patterns
    for orchestration, synthesis, replanning, heterogeneity, and stall recovery.
    Pulls from memory graph + curated commons knowledge base.
    """

    def __init__(self, arbos=None):
        self.arbos = arbos
        self.memory_layers = getattr(arbos, "memory_layers", None) if arbos else None
        self.fragment_tracker = getattr(arbos, "fragment_tracker", None) if arbos else None
        
        # Curated commons strategies (can be extended via memory)
        self.commons_strategies = {
            "orchestration": [
                "Prioritize deterministic paths first, then hybrid workers",
                "Use per-subtask contract slices for tighter verification",
                "Inject high-signal fragments early in synthesis",
                "Apply heterogeneity veto before debate"
            ],
            "synthesis": [
                "Light compose-to-spec before debate to reduce bad proposals",
                "Critique-first structured debate with contract as anchor",
                "Inject deterministic results directly into base assembly",
                "Final strict contract enforcement pass after debate"
            ],
            "replan": [
                "On DOUBLE_CLICK or severe stall → trigger narrow scientist mode",
                "On moderate verifier quality drop → targeted contract fixes",
                "On tool gap → escalate to ToolHunter with context",
                "Always run light compose-to-spec after any replan"
            ],
            "heterogeneity": [
                "Enforce minimum model diversity across roles",
                "Boost low-scoring subtasks with guided diversity candidates",
                "Use commons strategies to restore swarm heterogeneity",
                "Apply heterogeneity veto on proposal generation"
            ],
            "stall_recovery": [
                "Early severe stall → full replan or scientist mode",
                "Moderate stall → local repair + diversity boost",
                "Post-dry-run stall → strengthen verifier snippets and adversarial mocks"
            ]
        }

        self._ensure_commons_dir()
        logger.info("✅ SAGE Commons Meta-Agent initialized")

    def _ensure_commons_dir(self):
        """Ensure commons knowledge directory exists"""
        commons_dir = Path("goals/brain/commons")
        commons_dir.mkdir(parents=True, exist_ok=True)

    def query_strategies(self, task_type: str = "orchestration", domain: str = None, limit: int = 5) -> list:
        """Query high-signal strategies for a given task type and optional domain."""
        strategies = self.commons_strategies.get(task_type, self.commons_strategies.get("orchestration", []))
        
        # Pull additional strategies from memory graph if available
        if self.memory_layers and hasattr(self.memory_layers, "query_relevant_fragments"):
            try:
                query = f"commons strategy {task_type} {domain or ''}"
                memory_strategies = self.memory_layers.query_relevant_fragments(query, top_k=limit)
                for frag in memory_strategies:
                    if isinstance(frag, dict) and "content" in frag:
                        strategies.append(frag["content"][:300])
            except Exception as e:
                logger.debug(f"Memory strategy pull failed (safe): {e}")

        # Return top N unique strategies
        unique_strategies = list(dict.fromkeys(strategies))  # preserve order, remove duplicates
        return unique_strategies[:limit]

    def query_rescue_strategies(self, stall_reason: str) -> list:
        """Quick rescue strategies for stall recovery."""
        rescue = self.commons_strategies.get("stall_recovery", [])
        
        # Add domain-specific rescue if available
        if "verifier" in stall_reason.lower():
            rescue.append("Strengthen verifier snippets with more symbolic invariants")
        if "composability" in stall_reason.lower():
            rescue.append("Add explicit merge interfaces and artifact definitions")
        if "double_click" in stall_reason.lower() or "DOUBLE_CLICK" in stall_reason:
            rescue.append("Trigger narrow scientist mode on the specific gap")

        return rescue[:6]

    def add_strategy(self, task_type: str, strategy_text: str):
        """Add a new strategy to the commons (persisted in memory)"""
        if task_type not in self.commons_strategies:
            self.commons_strategies[task_type] = []
        self.commons_strategies[task_type].append(strategy_text)
        
        # Also save to memory layers for long-term reuse
        if self.memory_layers:
            self.memory_layers.add(
                text=strategy_text,
                metadata={
                    "type": "commons_strategy",
                    "task_type": task_type,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        logger.info(f"Added new {task_type} strategy to Commons: {strategy_text[:80]}...")

    def get_stats(self) -> dict:
        """Return basic stats about available commons strategies"""
        return {
            "total_strategies": sum(len(v) for v in self.commons_strategies.values()),
            "categories": list(self.commons_strategies.keys()),
            "last_updated": datetime.now().isoformat()
        }
