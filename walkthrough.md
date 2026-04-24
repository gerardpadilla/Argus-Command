# Aegis-Recon Deployment & Walkthrough

This document outlines everything completed to build the Aegis-Recon platform and provides step-by-step instructions on deploying it to your Kali VM and operating it in an air-gapped environment.

## What Was Completed

1. **Lightweight Backend Framework (FastAPI)**:
   Created a minimal FastAPI application (`backend/main.py`) running via `uvicorn` to maintain a low active memory footprint suitable for 4GB of RAM.
2. **Reconnaissance Engine Integration**:
   Built endpoints to spawn Nmap scans securely and a Scapy daemon configured to write strictly to `scapy_capture.json` on disk to limit active memory usage.
3. **AI Advisor Connectivity**:
   Created `backend/core/ai_advisor.py` to communicate synchronously with the OpenClaw Gateway at `127.0.0.1:18789/v1` utilizing standard OpenAI-SDK payloads with the `.env` standard Bearer token schema.
4. **Offline Premium UI**:
   - Downloaded and statically bundled `vis-network.min.js`.
   - Setup a high-fidelity glassmorphic dark-mode dashboard using Vanilla JS/CSS avoiding the overhead of compiling React/Vue frameworks offline. 
5. **System Resource Guardrails**:
   Developed the active `psutil` dashboard widget, memory polling, and a Python Subprocess Safety Kill Switch to nuke rogue `nmap`/`scapy` executions.

---

## Deployment Instructions (Pre-Air Gap)

While you still have internet access today, perform the following steps to ensure everything transfers optimally:

### 1. Git Initialization & Commit
If you haven't already, push these changes to GitHub:

```bash
cd /Users/gerardpadilla/Documents/CSUSB2026/Aegis-Recon
git init
git add .
git commit -m "Initial Aegis-Recon v4.0 Commit"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

### 2. Pull down securely onto your Kali VM
SSH or open a terminal in your Proxmox Kali Linux VM today:

```bash
# Pull the repository
git clone <YOUR_GITHUB_REPO_URL> Aegis-Recon
cd Aegis-Recon

# Set up a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install the locked dependencies (Must happen WITH Internet)
pip install -r requirements.txt
```

---

## Operating Instructions (Tomorrow - Air Gapped)

Once the system is air-gapped tomorrow, run the following exactly in the `Aegis-Recon` directory on your Kali VM:

### 1. Configure the AI Gateway Key

> [!IMPORTANT]
> The OpenClaw Gateway requires the Admin API key to answer prompts. 
> Edit the `.env` file to insert the key before the mission.

```bash
# In the Aegis-Recon folder:
nano .env

# Change this value:
OPENCLAW_API_KEY="THE_REAL_ADMIN_KEY_HERE"
```

Also, ensure the OpenClaw service is running natively on Port `18789`.

### 2. Launch the Platform

Due to the packet capturing (Scapy) and Nmap requirements, it is essential to run the server entirely as root.

```bash
# 1. Activate the environment if you used one
source venv/bin/activate

# 2. Run the application as root
sudo $(which python3) backend/main.py
```

### 3. Using the Web Interface

> [!TIP]
> **Access the Dashboard:** Open `http://localhost:8000` in the Kali VM's browser (Firefox/Chromium). Since the entire frontend payload and `vis-network.min.js` map engine are loaded via `<script src="/static/...">`, it will render perfectly without an internet connection.

1. **System Monitor Widget**: At the top right, observe the RAM and CPU tracker. Given the 4GB cap, keep an eye out for RAM spilling over 85%, at which point the font will organically turn red.
2. **Start Recon Workflow**: 
   - Enter your target IP or CIDR scope.
   - Click "Start Recon".
   - *Behind the Scenes*: The app spawns an isolated subprocess listening via Scapy, concurrently executes `Nmap`, dumps results, kills Scapy, generates JSON, and ships everything across to the `127.0.0.1:18789` OpenClaw port.
3. **Emergency Disconnect**: If your VM is bogging down unexpectedly, use the red "KILL SCANS" button natively integrated into the system header; it will systematically purge any active child nmap/scapy threads created by the backend.
