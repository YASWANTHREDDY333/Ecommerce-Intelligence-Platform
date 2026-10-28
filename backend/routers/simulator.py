from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import SimulationRequest, SimulationResponse
from backend.services.simulator_service import SimulatorService

router = APIRouter(prefix="/api/simulator", tags=["What-If Scenario Simulator"])

@router.post("/project", response_model=SimulationResponse, summary="Simulate revenue and CSAT impact under custom operational scenarios")
def project_scenario(req: SimulationRequest, db: Session = Depends(get_db)):
    return SimulatorService.run_simulation(db, req)
