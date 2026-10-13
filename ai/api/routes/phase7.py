from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ai.phase7.orchestrator import Phase7Orchestrator

router=APIRouter(prefix="/phase7",tags=["Phase 7"])

class Phase7Request(BaseModel):
    repository_path: str
    push: bool=False

@router.post("/prepare")
def prepare(req: Phase7Request):
    try:
        r=Phase7Orchestrator().start(req.repository_path,push=req.push)
        return r.__dict__
    except Exception as exc:
        raise HTTPException(status_code=500,detail=str(exc))
