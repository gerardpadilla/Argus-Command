import httpx
import os
from dotenv import load_dotenv

load_dotenv()

OPENCLAW_BASE_URL = os.getenv("OPENCLAW_BASE_URL", "http://127.0.0.1:18789/v1")
OPENCLAW_API_KEY = os.getenv("OPENCLAW_API_KEY", "")
OPENCLAW_MODEL = os.getenv("OPENCLAW_MODEL", "qwen-3.5")

async def analyze_scan_results(scan_data: dict, packet_data: list):
    """
    Sends the scan topology and captured packets to the OpenClaw AI gateway.
    """
    headers = {
        "Authorization": f"Bearer {OPENCLAW_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Simplify the data to save token size
    summary = "Discovered Hosts & Ports:\n"
    for node in scan_data.get('nodes', []):
        if node.get('group') == 'host':
            summary += f"- Host: {node.get('label')}\n"
        elif node.get('group') == 'port':
            summary += f"  - {node.get('title', '').replace(chr(10), ' ')}\n"
            
    summary += f"\nTotal Packets Captured: {len(packet_data)}\n"
    
    prompt = f"""
You are an expert red team "Junior Pentest Mentor".
Evaluate the following scan summary and suggest exact local Kali tools and commands to run next.
Focus on open ports like 445 (enum4linux), 80 (nikto, sqlmap), 22 (hydra), etc.

Scan Summary:
{summary}

Provide a concise, action-oriented response.
"""

    payload = {
        "model": OPENCLAW_MODEL,
        "messages": [
            {"role": "system", "content": "You are a specialized pentest module. Keep answers short and specific."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500
    }
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(f"{OPENCLAW_BASE_URL}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        # Provide fallback behavior for when OpenClaw isn't running on MacBook
        return "**[Fallback Offline Mode]** The specialized AI Gateway is not connected or the endpoint is mismatched. Operating without AI.\n\n*General Open-Port Advice:*\n- SMB (445): Run `enum4linux -a <target>` to enumerate shares.\n- HTTP (80/443): Run `nikto -h <target>` to find vulnerabilities.\n- SSH (22): Attempt brute-force with `hydra -l root -P dict.txt ssh://<target>`."
