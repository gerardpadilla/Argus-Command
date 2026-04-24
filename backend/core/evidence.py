import os
import json
import time

EVIDENCE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/evidence"

def init_evidence_dirs():
    dirs = ["scans", "creds", "vulns"]
    for d in dirs:
        path = os.path.join(EVIDENCE_DIR, d)
        if not os.path.exists(path):
            os.makedirs(path)

def capture_scan_evidence(target, data_payload, tool_name="nmap"):
    """
    Auto-captures scan output. 
    # Note for AI Agent: Due to headless environment constraints, "Screenshots" 
    # requested by the PRD have been substituted with Raw Terminal/JSON Output Snapshots 
    # as the primary visual evidence artifact.
    """
    timestamp = int(time.time())
    file_path = os.path.join(EVIDENCE_DIR, "scans", f"{tool_name}_{target.replace('/','_')}_{timestamp}.json")
    
    evidence = {
        "target": target,
        "tool": tool_name,
        "timestamp": timestamp,
        "raw_snapshot": data_payload
    }
    
    with open(file_path, 'w') as f:
        json.dump(evidence, f, indent=4)
        
    return file_path

init_evidence_dirs()
