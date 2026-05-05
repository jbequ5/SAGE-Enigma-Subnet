# operations/em_operations.py
import argparse
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from .config import OperationsConfig
from .performance_tracker import PerformanceTracker
from .flight_test import CalibrationFlightTest
from .MAP import MultiApproachPlanner
from .router import SmartLLMRouter
from .orchestrator import SwarmOrchestrator

app = FastAPI(title="SAGE EM Operations — Intelligent Fragment Factory")

config = OperationsConfig.load()
tracker = PerformanceTracker()
flight_test = CalibrationFlightTest(config, tracker)
map_planner = MultiApproachPlanner()
router = SmartLLMRouter(config, tracker)
orchestrator = SwarmOrchestrator(config, tracker, router)

class ChallengeRequest(BaseModel):
    id: str
    description: str
    verification_contract: str = ""
    tags: List[str] = []
    difficulty: str = "medium"
    historical_yield: Dict = {}

@app.post("/start_swarm")
async def start_swarm(challenge: ChallengeRequest):
    """Full intelligent factory flow: challenge → calibration → MAP → router → orchestrator."""
    challenge_metadata = challenge.model_dump()

    # Step 1–2: Run full calibration flight test (real model benchmarking + intelligent profiles)
    loadout = flight_test.run(challenge_metadata)

    # Step 3: Generate KAS-informed profiles
    profiles = map_planner.generate_profiles(challenge_metadata)

    # Step 4: Smart model assignment based on historical Fragment Yield
    model_assignments = router.assign_models(challenge_metadata["id"], profiles, loadout)

    # Step 5: Launch swarm with full smart stopping and save/resume support
    run_id = orchestrator.launch(challenge_metadata, loadout, profiles)

    return {
        "status": "swarm started",
        "run_id": run_id,
        "loadout": loadout,
        "profiles": len(profiles),
        "model_assignments": model_assignments,
        "recommended": loadout.get("recommended")
    }

@app.get("/status")
async def status():
    return {
        "status": "factory running",
        "active_instances": 0,  # real monitoring added in orchestrator
        "database": str(tracker.db_path)
    }

@app.post("/stop")
async def stop(run_id: str = None):
    """Graceful stop with partial fragment save."""
    orchestrator.stop()
    return {"status": "stopping", "run_id": run_id, "partial_fragments_saved": True}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SAGE EM Operations Orchestrator")
    parser.add_argument("--wizard", action="store_true", help="Run wizard mode (full factory)")
    parser.add_argument("--autonomous", action="store_true", help="Run headless")
    args = parser.parse_args()

    if args.wizard:
        print("🚀 SAGE Intelligent Fragment Factory — Wizard mode ready")
        print("Real model benchmarking + dynamic MAP + smart stopping + save/resume enabled")
    elif args.autonomous:
        print("🚀 SAGE Intelligent Fragment Factory — Autonomous mode running")
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000)
