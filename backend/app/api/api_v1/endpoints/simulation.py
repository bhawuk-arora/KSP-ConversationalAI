# backend/app/api/api_v1/endpoints/simulation.py

"""Scenario simulation endpoint.

Provides a simple simulation engine that processes a scenario definition and returns simulated results.
This is a placeholder implementation returning deterministic mock data.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any

# Dependency for authentication (reuse existing get_current_user)
from app.api.deps import get_current_user
from app.schemas.user import UserBase

router = APIRouter()


class ScenarioStep(BaseModel):
    action: str
    parameters: Dict[str, Any] = {}

class SimulationRequest(BaseModel):
    scenario_name: str
    steps: List[ScenarioStep]

class SimulationResult(BaseModel):
    scenario_name: str
    outcome: str
    details: Dict[str, Any]


@router.post("/simulate", response_model=SimulationResult, tags=["simulation"])
def run_simulation(request: SimulationRequest, user: UserBase = Depends(get_current_user)):
    """Run a mock simulation for the given scenario.
    In a full implementation this would invoke a sophisticated engine.
    """
    # Simple deterministic mock logic: count steps and produce a summary.
    step_count = len(request.steps)
    outcome = "Success" if step_count > 0 else "No steps provided"
    details = {
        "executed_steps": step_count,
        "actions": [step.action for step in request.steps],
    }
    return SimulationResult(
        scenario_name=request.scenario_name,
        outcome=outcome,
        details=details,
    )
