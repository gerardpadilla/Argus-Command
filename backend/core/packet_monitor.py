import os
import time
import json
import multiprocessing
from scapy.all import sniff
from scapy.layers.inet import IP, TCP, UDP

SCAPY_PID = None
SCAPY_PROCESS = None
OUTPUT_FILE = "scapy_capture.json"

def capture_packets(output_file):
    """
    Function to run in a separate process that sniffs packets.
    """
    packets_data = []
    
    def packet_callback(packet):
        if IP in packet:
            p_data = {
                "src": packet[IP].src,
                "dst": packet[IP].dst,
                "proto": packet[IP].proto,
                "timestamp": time.time()
            }
            if TCP in packet:
                p_data["sport"] = packet[TCP].sport
                p_data["dport"] = packet[TCP].dport
                p_data["type"] = "TCP"
            elif UDP in packet:
                p_data["sport"] = packet[UDP].sport
                p_data["dport"] = packet[UDP].dport
                p_data["type"] = "UDP"
            else:
                p_data["type"] = "OTHER"
                
            packets_data.append(p_data)
            
            # Write intermittently
            if len(packets_data) % 10 == 0:
                with open(output_file, "w") as f:
                    json.dump(packets_data, f)
                    
    try:
        sniff(prn=packet_callback)
    except Exception as e:
        print(f"Scapy error: {e}")
    finally:
        with open(output_file, "w") as f:
            json.dump(packets_data, f)

def start_capture():
    global SCAPY_PROCESS
    
    # Clean previous JSON
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
        
    SCAPY_PROCESS = multiprocessing.Process(target=capture_packets, args=(OUTPUT_FILE,))
    SCAPY_PROCESS.start()
    return SCAPY_PROCESS.pid

def stop_capture():
    global SCAPY_PROCESS
    if SCAPY_PROCESS and SCAPY_PROCESS.is_alive():
        SCAPY_PROCESS.terminate()
        SCAPY_PROCESS.join()
        
def get_capture_results():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []
