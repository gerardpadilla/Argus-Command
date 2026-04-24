class PhaseGate:
    PHASE_CONFIG = {
        1: {
            "name": "Reconnaissance",
            "allowed_tools": ["nmap", "nikto", "enum4linux"]
        },
        2: {
            "name": "DMZ Attacks",
            "allowed_tools": ["nmap", "nikto", "enum4linux", "hydra", "john"]
        },
        3: {
            "name": "Internal LAN",
            "allowed_tools": ["all"]
        }
    }

    current_phase = 1

    @classmethod
    def set_phase(cls, phase_level: int):
        if phase_level in cls.PHASE_CONFIG:
            cls.current_phase = phase_level
            return True
        return False

    @classmethod
    def get_current_phase_info(cls):
        return {
            "phase": cls.current_phase,
            "name": cls.PHASE_CONFIG[cls.current_phase]["name"]
        }

    @classmethod
    def is_tool_allowed(cls, tool_name: str) -> bool:
        allowed = cls.PHASE_CONFIG[cls.current_phase]["allowed_tools"]
        if "all" in allowed:
            return True
        return tool_name.lower() in allowed
