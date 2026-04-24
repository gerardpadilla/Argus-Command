import os
import subprocess
import xml.etree.ElementTree as ET
import json
import time

OUTPUT_XML = "nmap_scan.xml"

def run_nmap_scan(target="127.0.0.1", ports="1-1000"):
    """
    Runs nmap and saves to XML. If it fails, produces a mock XML for testing.
    """
    # Clean previous
    if os.path.exists(OUTPUT_XML):
        os.remove(OUTPUT_XML)
        
    cmd = ["nmap", "-sS", "-sV", "-O", "-p", ports, "-oX", OUTPUT_XML, target]
    try:
        # Run process safely without aggressive timeouts for /24 subnets
        subprocess.run(cmd, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Nmap failed or not found: {e}. Generating Mock Data for Demo.")
        _generate_mock_xml(target)
        
    return parse_nmap_xml(OUTPUT_XML)

def _generate_mock_xml(target):
    mock_data = f"""<?xml version="1.0"?>
    <nmaprun scanner="nmap" args="nmap -sS -sV -O -p 1-1000 -oX scan.xml {target}">
      <host starttime="1623456789" endtime="1623456790">
        <status state="up" reason="localhost-response"/>
        <address addr="{target}" addrtype="ipv4"/>
        <ports>
          <port protocol="tcp" portid="22"><state state="open" reason="syn-ack"/><service name="ssh" product="OpenSSH" version="8.2p1"/></port>
          <port protocol="tcp" portid="80"><state state="open" reason="syn-ack"/><service name="http" product="Apache httpd" version="2.4.41"/></port>
          <port protocol="tcp" portid="445"><state state="open" reason="syn-ack"/><service name="microsoft-ds" product="Samba smbd" version="4.6.2"/></port>
        </ports>
      </host>
      <host starttime="1623456790" endtime="1623456791">
        <status state="up" reason="arp-response"/>
        <address addr="10.0.0.5" addrtype="ipv4"/>
        <ports>
          <port protocol="tcp" portid="3389"><state state="open" reason="syn-ack"/><service name="ms-wbt-server" product="Microsoft Terminal Services"/></port>
        </ports>
      </host>
    </nmaprun>
    """
    with open(OUTPUT_XML, "w") as f:
        f.write(mock_data)

def parse_nmap_xml(xml_file):
    """
    Parses Nmap XML output into a JSON graph payload for Vis.js representation. (Option A Redesign)
    """
    if not os.path.exists(xml_file):
        return {"nodes": [], "edges": []}
        
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    nodes = []
    edges = []
    
    # Root node (Scanner)
    nodes.append({"id": "scanner", "label": "Scanner\n(Kali Base)", "group": "scanner", "shape": "image", "image": "https://img.icons8.com/color/48/000000/kali-linux.png"})
    
    actionable_ports = {"80", "443", "8080", "445", "139"}
    blocked_ports = {"22", "21", "3389"}
    
    host_id = 1
    for host in root.findall('host'):
        os_elem = host.find('os/osmatch')
        os_guess = os_elem.get('name') if os_elem is not None else "Unknown OS"
        os_accuracy = os_elem.get('accuracy') if os_elem is not None else "0"
        
        hostname_elem = host.find('hostnames/hostname')
        hostname = hostname_elem.get('name') if hostname_elem is not None else None
        
        status = host.find('status')
        if status is not None and status.get('state') == 'up':
            address = host.find('address')
            ip = address.get('addr') if address is not None else f"Unknown-{host_id}"
            
            h_id = f"host_{host_id}"
            
            # Extract Ports
            host_ports = []
            ports = host.find('ports')
            if ports is not None:
                for port in ports.findall('port'):
                    state = port.find('state')
                    if state.get('state') == 'open':
                        service = port.find('service')
                        host_ports.append({
                            "port": port.get('portid'),
                            "service": service.get('name') if service is not None else "unknown",
                            "product": service.get('product') if service is not None else "",
                            "notes": None
                        })
                        
            # Determine semantic status
            node_status = "unknown"
            node_color = "#9ca3af" # Gray
            if host_ports:
                port_ids = [p["port"] for p in host_ports]
                if any(p in actionable_ports for p in port_ids):
                    node_status = "caution"
                    node_color = "#facc15" # Yellow
                elif any(p in blocked_ports for p in port_ids):
                    node_status = "blocked"
                    node_color = "#f87171" # Red
                else:
                    node_status = "accessible"
                    node_color = "#4ade80" # Green
            
            # Form Label Output
            host_label = f"{ip}\n{hostname or 'Unknown Host'}\n{os_guess}"
            
            # Master Node Append
            nodes.append({
                "id": h_id,
                "label": host_label,
                "group": "host",
                "shape": "box",
                "color": node_color,
                "status": node_status,
                "os_info": f"{os_guess} | {os_accuracy}%",
                "hostname": hostname,
                "ports": host_ports,
                "font": {"multi": True, "align": "left"}
            })
            
            # Single Edge (Scanner to Host)
            edges.append({"from": "scanner", "to": h_id})
            
            host_id += 1
            
    return {"nodes": nodes, "edges": edges}
