from fastapi import APIRouter
from pydantic import BaseModel
from backend.models import credential
from backend.core import state_manager

router = APIRouter()

class CredentialAttempt(BaseModel):
    target_ip: str
    service: str
    username: str
    password: str
    result: str

@router.post("/agent/credential-add")
def add_credential(req: CredentialAttempt):
    credential.log_credential(req.target_ip, req.service, req.username, req.password, req.result)
    return {"status": "success", "message": "Credential logged to database"}

@router.get("/agent/status")
def get_agent_status():
    return {"status": "success", "agent_state": state_manager.get_state()}
    
@router.post("/agent/next-target")
def next_target(target: str):
    state_manager.set_target(target)
    return {"status": "success", "target": target}

@router.get("/agent/findings")
def get_findings():
    state = state_manager.get_state()
    return {"status": "success", "credentials": state.get("credentials_tested")}
