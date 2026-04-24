# 🛡️ Argus Command v2.0

**Argus Command** (formerly Aegis-Recon) is the central operations hub that coordinates human operators and AI agents during red team engagements, providing real-time situational awareness, automated evidence collection, and intelligent action recommendations. 

*100 Eyes on Your Target Network*

## 🛠️ Core Capabilities

### 1. AI Agent Integration
- Argus coordinates directly with an OpenClaw AI pentesting agent, communicating via real-time JSON state tracking (`/tmp/argus_agent_state.json`).
- Automatically feeds discovered ports, cracked credentials, and topology structure to the LLM agent for continuous intelligence-gathering recommendations.

### 2. Password & Credential Cracking
- Automatically parses intercepted password hashes.
- Spawns background CPU-optimized threads of `John the Ripper` using native Kali wordlists (`rockyou.txt`).
- Features local SQLite persistence to permanently log any breached credentials.

### 3. Actionable Pentest Modules
- Fully integrated web-execution of `nikto`, `enum4linux`, and `hydra`.
- Sandbox container limits all spawned attacks to standard timeouts to ensure Kali doesn't overheat.
- Output from live terminal sessions perfectly streams strictly to an embedded Hacker-Green Modal Console.

### 4. Reconnaissance & Topology
- **Nmap Orchestrator**: Executes stealth `-sS` scans to bypass rudimentary endpoint loggers and graphs them beautifully using **Vis.js**.
- **Scapy Wiretap**: Quietly listens to network traffic concurrently alongside active scans.

## 🚀 Deployment Guide (Kali Linux)
This is an air-gapped system designed specifically for Kali Linux virtual machines.

```bash
# Provide permissions and set up environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start Argus Command Server
sudo $(which python3) backend/main.py
```
*Note: Ensure you are running Python 3 with `sudo` permissions so Scapy can legally attach to your raw network interface adapters to sniff packets!*
