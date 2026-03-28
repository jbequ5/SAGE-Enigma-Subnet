import numpy as np
from validation_oracle import ValidationOracle
from trajectories.trajectory_vector_db import vector_db
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def compute_energy(candidate: dict, oracle: ValidationOracle, rank: int = 8) -> float:
    val_result = oracle.run(candidate.get("solution", {}))
    candidate["validation_score"] = val_result["validation_score"]
    
    novelty = candidate.get("novelty_proxy", 0.5)
    verifier = val_result["validation_score"]
    base_cost = candidate.get("est_compute", 1.0)
    cost = base_cost * (rank / 64.0) + 1e-5
    energy = (novelty * verifier) / cost
    
    logger.info(f"EGGROLL Energy: {energy:.4f} (rank={rank}, score={verifier:.4f}, cost={cost:.2f})")
    return energy
