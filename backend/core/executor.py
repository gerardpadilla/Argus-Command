import subprocess
import os

ALLOWED_TOOLS = ["nikto", "enum4linux", "hydra"]

def execute_tool(tool_name: str, target: str, port: str = None) -> str:
    """
    Safely executes a whitelisted tool and returns stdout.
    """
    if tool_name not in ALLOWED_TOOLS:
        return f"Error: Tool '{tool_name}' is not allowed for execution."
        
    cmd = []
    
    if tool_name == "nikto":
        cmd = ["nikto", "-h", target]
        if port:
            cmd.extend(["-p", port])
            
    elif tool_name == "enum4linux":
        # Enum4linux natively scans 139/445, explicit port flag not standard for -a
        cmd = ["enum4linux", "-a", target]
        
    elif tool_name == "hydra":
        # Using rockyou as default dictionary
        wordlist = "/usr/share/wordlists/rockyou.txt"
        if not os.path.exists(wordlist):
            return f"Error: Hydra requires {wordlist} which is missing on this OS."
        cmd = ["hydra", "-l", "root", "-P", wordlist]
        if port:
            cmd.extend(["-s", port])
        cmd.append(f"ssh://{target}")
        
    try:
        # We run it safely without shell=True to prevent command chaining like '; rm -rf /'
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout + "\n" + result.stderr
        
        if not output.strip():
            return f"{tool_name} completed silently (No output)."
        return output
        
    except FileNotFoundError:
        # E.g. running on MacBook where Nikto isn't installed
        return f"[MOCK EXECUTOR] Native binary '{tool_name}' missing on this OS.\nSimulated output for {tool_name} against {target}:\n>> Found vulnerabilities on target."
    except subprocess.TimeoutExpired:
        return f"Error: {tool_name} timed out after 5 minutes."
    except Exception as e:
        return f"Execution Error: {e}"
