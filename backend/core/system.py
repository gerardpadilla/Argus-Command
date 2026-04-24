import psutil
import os
import signal

def get_system_stats():
    mem = psutil.virtual_memory()
    return {
        "cpu_percent": psutil.cpu_percent(interval=None),
        "ram_percent": mem.percent,
        "ram_used_mb": mem.used / (1024 * 1024),
        "ram_total_mb": mem.total / (1024 * 1024)
    }

def kill_python_scans():
    """
    Safety kill switch to terminate all Nmap and Python-spawned scan processes.
    """
    killed_procs = []
    current_pid = os.getpid()
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.info.get('name', '')
            cmdline = proc.info.get('cmdline', [])
            pid = proc.info['pid']
            
            if pid == current_pid:
                continue
                
            # Target nmap, scapy, or tools
            if name in ['nmap', 'nikto', 'enum4linux', 'hydra'] or (cmdline and any(arg in ['nmap', 'nikto', 'enum4linux', 'hydra'] for arg in cmdline)):
                os.kill(pid, signal.SIGKILL)
                killed_procs.append({"pid": pid, "type": name})
                
            elif name == 'python' or name == 'python3':
                # Check if it's running our packet_monitor or other background scans
                if cmdline and any('packet_monitor' in arg for arg in cmdline):
                    os.kill(pid, signal.SIGKILL)
                    killed_procs.append({"pid": pid, "type": "scapy"})
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    return {"status": "success", "killed_processes": killed_procs}
