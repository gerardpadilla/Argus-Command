import json
import os
import time

STATE_FILE = "/tmp/argus_agent_state.json"

DEFAULT_STATE = {
    "current_phase": 1,
    "current_target": None,
    "target_status": {},
    "credentials_tested": [],
    "blocked_vectors": [],
    "pending_actions": [],
    "last_updated": 0
}

def init_state():
    if not os.path.exists(STATE_FILE):
        _write_state(DEFAULT_STATE)

def _read_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_STATE

def _write_state(state):
    state["last_updated"] = time.time()
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=4)
    except Exception as e:
        print(f"Error writing state: {e}")

def get_state():
    return _read_state()

def update_phase(phase: int):
    state = _read_state()
    state["current_phase"] = phase
    _write_state(state)

def set_target(target: str):
    state = _read_state()
    state["current_target"] = target
    if target not in state["target_status"]:
        state["target_status"][target] = "scanned"
    _write_state(state)

def add_credential_tested(cred_string: str):
    state = _read_state()
    if cred_string not in state["credentials_tested"]:
        state["credentials_tested"].append(cred_string)
        _write_state(state)

# Initialize on import
init_state()
