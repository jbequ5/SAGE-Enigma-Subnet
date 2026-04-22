import argparse
import uvicorn
from fastapi import FastAPI
from operations.orchestrator import EMOperationsOrchestrator

app = FastAPI()
orchestrator = EMOperationsOrchestrator()

@app.post("/start_swarm")
def start_swarm(max_instances: int = None):
    orchestrator.launch_swarm(max_instances)
    return {"status": "swarm started", "instances": max_instances or "auto"}

@app.get("/status")
def status():
    return {"active_instances": len(orchestrator.active_instances)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--wizard", action="store_true")
    parser.add_argument("--autonomous", action="store_true")
    parser.add_argument("--config", default="operations_config.json")
    parser.add_argument("--max-instances", type=int, default=None)
    args = parser.parse_args()

    if args.wizard:
        # Run existing 0.9.10 wizard here (or call it)
        print("Launching 0.9.10 wizard...")
        # subprocess.call(["streamlit", "run", "your_wizard_script.py"])
    elif args.autonomous:
        orchestrator.launch_swarm(args.max_instances)
        orchestrator.monitor()
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000)
