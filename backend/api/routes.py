from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.core import system, packet_monitor, scanner, ai_advisor, executor, netdiscover_scanner, state_manager
from backend.models import hash_crack, credential
from backend.models.phase_gate import PhaseGate

router = APIRouter()

class ScanRequest(BaseModel):
    target: str

class ToolRequest(BaseModel):
    tool_name: str
    target: str
    port: str = None

class ChatRequest(BaseModel):
    message: str
    scan_data: dict = None

class PhaseRequest(BaseModel):
    phase: int

class HashRequest(BaseModel):
    hash_value: str

class CredentialEntry(BaseModel):
    target_ip: str
    service: str
    username: str
    password: str
    result: str

class CredentialImport(BaseModel):
    lines: list

class TargetRequest(BaseModel):
    target: str

@router.post("/tools/execute")
def execute_tool_route(req: ToolRequest):
    if not PhaseGate.is_tool_allowed(req.tool_name):
        raise HTTPException(status_code=403, detail=f"Tool '{req.tool_name}' is physically blocked by Argus Phase Gate in {PhaseGate.get_current_phase_info()['name']} (Phase {PhaseGate.current_phase}).")
    output = executor.execute_tool(req.tool_name, req.target, req.port)
    return {"status": "success", "output": output}

@router.post("/tools/hashcrack/start")
def start_hashcrack_route(req: HashRequest):
    return hash_crack.start_cracking(req.hash_value)

@router.get("/tools/hashcrack/status")
def status_hashcrack_route():
    return hash_crack.check_progress()

@router.get("/system/stats")
def get_stats():
    return system.get_system_stats()

@router.post("/system/kill")
def kill_scans():
    return system.kill_python_scans()

@router.get("/system/phase")
def get_phase():
    return PhaseGate.get_current_phase_info()

@router.post("/system/phase")
def set_phase(req: PhaseRequest):
    if PhaseGate.set_phase(req.phase):
        return {"status": "success", "phase_info": PhaseGate.get_current_phase_info()}
    raise HTTPException(status_code=400, detail="Invalid phase level.")

@router.get("/credentials")
def get_credentials():
    creds = credential.get_all_credentials()
    return {"status": "success", "credentials": creds}

@router.post("/credentials")
def add_credential(req: CredentialEntry):
    credential.log_credential(
        target_ip=req.target_ip,
        service=req.service,
        username=req.username,
        password=req.password,
        result=req.result
    )
    return {"status": "success"}

@router.post("/credentials/import")
def import_credentials(req: CredentialImport):
    res = credential.batch_import_hashes(req.lines)
    return res

# ==========================================
# Section 4.5: AI Agent Integration Endpoints
# ==========================================

@router.get("/agent/status")
def get_agent_status():
    return state_manager.read_state()

@router.post("/agent/next-target")
def set_agent_target(req: TargetRequest):
    state_manager.update_state({"current_target": req.target})
    return {"status": "success", "target": req.target}

@router.get("/agent/findings")
def get_agent_findings():
    # In a full app this would query a findings DB, for now returning mocked aggregate
    return {"status": "success", "findings": ["Discovered 3 ports on 192.168.1.10", "Vuln 0 tested"]}

@router.post("/agent/credential-add")
def agent_add_credential(req: CredentialEntry):
    # This is a wrapper for the Credential Vault API specific to agents
    credential.log_credential(
        target_ip=req.target_ip,
        service=req.service,
        username=req.username,
        password=req.password,
        result=req.result
    )
    # Trigger auto-capture of cred evidence if we wanted to inside evidence.py
    return {"status": "success", "message": "Logged to vault"}

@router.get("/agent/recommendations")
async def get_agent_recommendations():
    # Wrap ai_advisor explicitly for the agent
    res = await ai_advisor.analyze_scan("Agent requesting strategic recommendations.")
    return {"status": "success", "recommendation": res}

@router.post("/agent/chat")
async def chat_with_agent(req: ChatRequest):
    response = await ai_advisor.chat_with_mentor(req.message, req.scan_data)
    return {"response": response}

@router.post("/recon/start")
async def start_recon(req: ScanRequest):
    """
    Triggers Nmap and Scapy as a single workflow, then analyzes results.
    """
    # 1. Start Scapy capture
    packet_monitor.start_capture()
    
    try:
        # 2. Run Nmap (blocking, but wait to finish)
        scan_results = scanner.run_nmap_scan(target=req.target)
    finally:
        # 3. Stop capture immediately once scan is processed
        packet_monitor.stop_capture()
        
    # 4. Gather packets
    packets = packet_monitor.get_capture_results()
    
    # 5. Send to AI
    ai_advice = await ai_advisor.analyze_scan_results(scan_results, packets)
    
    return {
        "status": "success",
        "scan_data": scan_results,
        "packets_captured": len(packets),
        "ai_analysis": ai_advice
    }

@router.post("/recon/netdiscover")
def run_netdiscover(req: ScanRequest):
    """
    Triggers ARP sweep on local subnet.
    """
    devices = netdiscover_scanner.run_netdiscover(target_subnet=req.target)
    return {
        "status": "success",
        "devices": devices
    }

@router.get("/recon/packets")
def get_latest_packets():
    return {"packets": packet_monitor.get_capture_results()}
