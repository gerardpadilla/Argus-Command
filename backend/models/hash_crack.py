import subprocess
import os

def start_cracking(hash_string: str) -> dict:
    hash_file = "/tmp/argus_target_hash.txt"
    wordlist = "/usr/share/wordlists/rockyou.txt"
    
    with open(hash_file, "w") as f:
        f.write(hash_string + "\n")
        
    if not os.path.exists(wordlist):
        return {"status": "error", "message": f"Dictionary missing: {wordlist}. Cannot crack."}

    # Spawning process without blocking. We route output to a log file.
    log_file = "/tmp/argus_john_output.log"
    with open(log_file, "w") as lf:
        subprocess.Popen(
            ["john", "--wordlist=" + wordlist, hash_file],
            stdout=lf, stderr=subprocess.STDOUT
        )
        
    return {"status": "started", "message": "John The Ripper attack spawned."}

def check_progress() -> dict:
    hash_file = "/tmp/argus_target_hash.txt"
    if not os.path.exists(hash_file):
        return {"status": "idle", "cracked": False}
        
    # Check if there's any cracked output
    try:
        result = subprocess.run(["john", "--show", hash_file], capture_output=True, text=True)
        if "0 password hashes cracked" not in result.stdout and "1 password hash cracked" in result.stdout:
            # Parse cracked string
            lines = result.stdout.split('\n')
            cracked_line = [l for l in lines if ':' in l and l.split(':')[0] != '?'][0] if lines else ""
            return {"status": "complete", "cracked": True, "details": cracked_line}
        
        # If still running, tail the log file
        log_file = "/tmp/argus_john_output.log"
        tail = ""
        if os.path.exists(log_file):
            with open(log_file, "r") as lf:
                lines = lf.readlines()
                tail = "".join(lines[-5:]) if lines else "Initializing..."
                
        return {"status": "running", "cracked": False, "log": tail}
    except Exception as e:
        return {"status": "error", "message": str(e)}
