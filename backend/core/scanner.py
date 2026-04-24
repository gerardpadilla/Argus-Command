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
    Parses Nmap XML output into a JSON graph payload for Vis.js representation.
    """
    if not os.path.exists(xml_file):
        return {"nodes": [], "edges": []}
        
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    nodes = []
    edges = []
    
    # Root node (Scanner)
    nodes.append({"id": "scanner", "label": "Scanner", "group": "scanner", "shape": "image", "image": "https://img.icons8.com/color/48/000000/kali-linux.png"})
    
    host_id = 1
    for host in root.findall('host'):
        status = host.find('status')
        if status is not None and status.get('state') == 'up':
            address = host.find('address')
            ip = address.get('addr') if address is not None else f"Unknown-{host_id}"
            
            # Host Node
            h_id = f"host_{host_id}"
            nodes.append({"id": h_id, "label": ip, "group": "host", "shape": "box", "color": "#00ffcc", "font": {"color": "#000000", "multi": True, "bold": True}})
            edges.append({"from": "scanner", "to": h_id})
            
            ports = host.find('ports')
            if ports is not None:
                for port in ports.findall('port'):
                    state = port.find('state')
                    if state.get('state') == 'open':
                        portid = port.get('portid')
                        service = port.find('service')
                        svc_name = service.get('name') if service is not None else "unknown"
                        svc_product = service.get('product') if service is not None else ""
                        
                        # Port Node
                        p_id = f"port_{host_id}_{portid}"
                        banner = f"Port: {portid}\nService: {svc_name}\nProduct: {svc_product}"
                        nodes.append({"id": p_id, "label": f"<b>{portid}</b>\n{svc_name}", "title": banner, "group": "port", "shape": "ellipse", "color": "#ffb84d", "font": {"color": "#000000", "multi": True}})
                        edges.append({"from": h_id, "to": p_id})
                        
            host_id += 1
            
    return {"nodes": nodes, "edges": edges}
