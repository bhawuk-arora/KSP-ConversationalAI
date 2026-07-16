# backend/app/api/api_v1/endpoints/simulation.py

"""Scenario simulation endpoint — Supervisor/DGP only.

Returns patrol vs crime rate simulation with basic linear model.
Only accessible to Supervisor role.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, RoleChecker
from app.schemas.user import UserBase
from app.core.database import get_db
from app.models.ksp_models import CaseMaster

router = APIRouter()

# Only Supervisors and above can run simulations
supervisor_only = RoleChecker(["Supervisor"])

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
def run_simulation(
    request: SimulationRequest,
    db: Session = Depends(get_db),
    user: UserBase = Depends(supervisor_only),
):
    """Run a scenario simulation — Supervisor role required.

    Uses real case count from DB to model patrol density impact.
    The model: increasing patrol frequency by X% reduces property crimes by 0.6X%.
    """
    step_count = len(request.steps)

    # Pull real total case count from DB for context
    total_cases = db.query(CaseMaster).count()

    # Simple linear patrol-impact model
    patrol_increase = 0.0
    for step in request.steps:
        if step.action.lower() in ("increase_patrol", "add_patrol", "patrol"):
            patrol_increase += float(step.parameters.get("percent", 10))

    estimated_reduction = round(patrol_increase * 0.6, 1)
    projected_cases = max(0, round(total_cases * (1 - estimated_reduction / 100)))

    outcome = "Positive Impact" if patrol_increase > 0 else "No change modelled"
    details = {
        "executed_steps": step_count,
        "actions": [s.action for s in request.steps],
        "patrol_increase_percent": patrol_increase,
        "estimated_crime_reduction_percent": estimated_reduction,
        "current_total_cases_in_db": total_cases,
        "projected_cases_after_intervention": projected_cases,
        "model": "Linear patrol-density model (beta)",
    }
    return SimulationResult(
        scenario_name=request.scenario_name,
        outcome=outcome,
        details=details,
    )
