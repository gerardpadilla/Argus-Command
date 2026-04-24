document.addEventListener('DOMContentLoaded', () => {
    
    // Initialize Vis.js
    initTopology('vis-network-container');

    // UI Elements
    const btnStart = document.getElementById('btn-start-recon');
    const btnKill = document.getElementById('btn-kill-switch');
    const targetInput = document.getElementById('target-ip');
    const statusMsg = document.getElementById('recon-status');
    const aiOutput = document.getElementById('ai-output');
    const actionContainer = document.getElementById('action-modules-container');
    const actionPlaceholder = document.getElementById('actions-placeholder');
    const activityFeed = document.getElementById('live-activity-feed');
    
    // Live Activity Feeder
    function logActivity(message, color = '#a3e635') {
        const now = new Date();
        const timeStr = now.toTimeString().split(' ')[0];
        
        const line = document.createElement('div');
        line.innerHTML = `<span class="timestamp">[${timeStr}]</span> <span style="color: ${color};">${message}</span>`;
        activityFeed.appendChild(line);
        activityFeed.scrollTop = activityFeed.scrollHeight;
    }
    
    // Stat Elements
    const cpuVal = document.getElementById('cpu-val');
    const ramVal = document.getElementById('ram-val');
    const ramMb = document.getElementById('ram-mb');

    // Polling System Stats
    async function fetchSysStats() {
        try {
            const res = await fetch('/api/v1/system/stats');
            if (res.ok) {
                const data = await res.json();
                cpuVal.innerText = `${data.cpu_percent.toFixed(1)}%`;
                ramVal.innerText = `${data.ram_percent.toFixed(1)}%`;
                ramMb.innerText = `(${data.ram_used_mb.toFixed(0)} / ${data.ram_total_mb.toFixed(0)} MB)`;
                
                // Alert if RAM limits approached (Kali has 4GB)
                if (data.ram_percent > 85) {
                    ramVal.style.color = '#f43f5e';
                } else {
                    ramVal.style.color = '';
                }
            }
        } catch (e) {
            console.error("Failed to fetch sys stats", e);
        }
    }
    
    setInterval(fetchSysStats, 3000);
    fetchSysStats(); // initial fetch

    // Modal Elements
    const terminalModal = document.getElementById('terminal-modal');
    const closeTerminal = document.getElementById('close-terminal');
    const terminalOutput = document.getElementById('terminal-output');
    const terminalTitle = document.getElementById('terminal-title');
    const actionGrid = document.getElementById('action-buttons-grid');
    // actionContainer already declared at top

    closeTerminal.addEventListener('click', () => {
        terminalModal.style.display = 'none';
    });

    // Run Tool Logic
    window.runActionTool = async function(toolName, target, port, btnElement) {
        // UI lock
        btnElement.classList.add('running');
        btnElement.disabled = true;
        const ogText = btnElement.innerText;
        btnElement.innerHTML = `Running ${toolName}...`;
        
        // Open Modal
        terminalModal.style.display = 'flex';
        let titleSuffix = port ? `${target}:${port}` : target;
        terminalTitle.innerText = `Argus Console // ${toolName} -> ${titleSuffix}`;
        terminalOutput.innerHTML = `<p>Executing ${toolName} against ${titleSuffix}...\n(Please standby, this may take several minutes)...</p>`;

        try {
            const res = await fetch('/api/v1/tools/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tool_name: toolName, target: target, port: port })
            });

            const data = await res.json();
            if (res.ok) {
                // Escape HTML tags to prevent XSS from unescaped terminal output
                let safeOutput = data.output.replace(/</g, "&lt;").replace(/>/g, "&gt;");
                terminalOutput.innerHTML = safeOutput;
            } else {
                terminalOutput.innerHTML = `<p style="color:red;">Server error: ${data.detail || 'Unknown error'}</p>`;
            }
        } catch (e) {
            terminalOutput.innerHTML = `<p style="color:red;">Network or Timeout Error communicating with backend.</p>`;
        } finally {
            btnElement.classList.remove('running');
            btnElement.disabled = false;
            btnElement.innerText = ogText;
        }
    };

    function generateActionButtons(scanData) {
        let injectedHTML = '<div style="margin-top: 15px; border-top: 1px solid #333; padding-top: 10px;">';
        injectedHTML += '<h3 style="font-size: 0.95rem; margin-bottom: 10px; color: var(--accent);">Actionable Modules:</h3>';
        injectedHTML += '<div style="display: flex; flex-wrap: wrap; gap: 10px;">';
        let foundTargets = 0;

        if (!scanData || !scanData.nodes) return; 

        let hostsMap = {}; 
        scanData.nodes.forEach(n => {
            if (n.group === 'host') hostsMap[n.id] = n.label;
        });

        scanData.nodes.forEach(n => {
            if (n.group === 'port') {
                let connectedEdge = scanData.edges.find(e => e.to === n.id);
                if (connectedEdge && hostsMap[connectedEdge.from]) {
                    const targetIp = hostsMap[connectedEdge.from];
                    
                    const firstLine = n.label.split('\n')[0];
                    const portStr = firstLine.replace(/[^0-9]/g, '');
                    
                    if (portStr) {
                        if (portStr === '80' || portStr === '443') {
                            injectedHTML += `<button class="btn-action" onclick="runActionTool('nikto', '${targetIp}', '${portStr}', this)">Run Nikto (${portStr}) on ${targetIp}</button>`;
                            foundTargets++;
                        }
                        if (portStr === '445' || portStr === '139') {
                            injectedHTML += `<button class="btn-action" onclick="runActionTool('enum4linux', '${targetIp}', '${portStr}', this)">Run Enum4Linux on ${targetIp}</button>`;
                            foundTargets++;
                        }
                        if (portStr === '22' || portStr === '3389' || portStr === '21') {
                            injectedHTML += `<button class="btn-action" onclick="runActionTool('hydra', '${targetIp}', '${portStr}', this)">Run Hydra on ${targetIp}</button>`;
                            foundTargets++;
                        }
                    }
                }
            }
        });

        injectedHTML += '</div></div>';

        // Force inject buttons into the middle stats panel natively
        if (foundTargets > 0) {
            actionGrid.innerHTML = injectedHTML;
            actionContainer.style.display = 'block';
            actionPlaceholder.style.display = 'none';
        } else {
            actionContainer.style.display = 'none';
            actionPlaceholder.style.display = 'block';
        }
    }

    // Start Recon Process
    btnStart.addEventListener('click', async () => {
        const target = targetInput.value.trim();
        if (!target) return;

        // UI Update
        btnStart.disabled = true;
        btnStart.innerHTML = `<span class="icon">🔄</span> Scanning...`;
        statusMsg.innerText = "Scanning...";
        logActivity(`Initiating active scan & scapy intercept against ${target}...`, '#38bdf8');
        aiOutput.innerHTML = `<p class="placeholder-text">Analyzing ${target}... querying OpenClaw Gateway.</p>`;
        actionContainer.style.display = 'none'; // reset buttons
        actionPlaceholder.style.display = 'block';
        
        try {
            const res = await fetch('/api/v1/recon/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target })
            });
            
            const data = await res.json();
            
            if (res.ok) {
                // Formatting markdown slightly
                let formattedAi = data.ai_analysis
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\*(.*?)\*/g, '<em>$1</em>')
                    .replace(/\n/g, '<br>');
                    
                statusMsg.innerText = `Scan Complete.`;
                statusMsg.className = "status-msg success";
                logActivity(`Scan completed. Discovered ${data.scan_data?.nodes?.length || 0} entities. Captured ${data.packets_captured} packets.`, '#10b981');
                
                aiOutput.innerHTML = `${formattedAi}`;
                
                // Update graph
                if (data.scan_data) {
                    updateTopology(data.scan_data);
                    generateActionButtons(data.scan_data);
                }
            } else {
                throw new Error("Server returned error.");
            }
            
        } catch (e) {
            statusMsg.innerText = "Scan failed or timed out.";
            statusMsg.className = "status-msg";
            aiOutput.innerHTML = `<p style="color:var(--danger)">Error communicating with backend.</p>`;
        } finally {
            btnStart.disabled = false;
            btnStart.innerHTML = `<span class="icon">⚡</span> Start Recon`;
        }
    });

    // Kill Switch
    btnKill.addEventListener('click', async () => {
        try {
            logActivity("Executing hard kill-switch on all running subsystems...", "#f43f5e");
            const res = await fetch('/api/v1/system/kill', { method: 'POST' });
            if (res.ok) {
                const data = await res.json();
                logActivity(`Kill Switch Activated. Terminated ${data.killed_processes.length} frozen processes.`, "#f43f5e");
            }
        } catch (e) {
            logActivity("Failed to activate kill switch server endpoint.", "red");
        }
    });
    // Hash Cracking Integration
    window.submitHash = async function() {
        const hashInput = document.getElementById('hash-input').value;
        const hashStatus = document.getElementById('hash-status');
        const btnHash = document.getElementById('btn-hash');
        
        if (!hashInput) return;
        
        btnHash.disabled = true;
        btnHash.classList.add('running');
        hashStatus.style.color = '#eab308'; // Yellow
        hashStatus.innerText = "Spawning John The Ripper background thread...";
        
        try {
            const res = await fetch('/api/v1/tools/hashcrack/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ hash_value: hashInput })
            });
            const data = await res.json();
            
            if (data.status === 'started') {
                pollHashStatus();
            } else {
                hashStatus.style.color = 'red';
                hashStatus.innerText = data.message || "Failed to start crack.";
                btnHash.disabled = false;
                btnHash.classList.remove('running');
            }
        } catch(e) {
            hashStatus.style.color = 'red';
            hashStatus.innerText = "Network error starting tool.";
            btnHash.disabled = false;
            btnHash.classList.remove('running');
        }
    };
    
    function pollHashStatus() {
        const hashStatus = document.getElementById('hash-status');
        const btnHash = document.getElementById('btn-hash');
        
        let pollInterval = setInterval(async () => {
            try {
                const res = await fetch('/api/v1/tools/hashcrack/status');
                const data = await res.json();
                
                if (data.status === 'running') {
                    hashStatus.innerText = "Running... " + (data.log || "");
                } else if (data.status === 'complete') {
                    clearInterval(pollInterval);
                    btnHash.disabled = false;
                    btnHash.classList.remove('running');
                    hashStatus.style.color = '#22c55e'; // Green
                    hashStatus.innerHTML = `<strong>CRACKED:</strong> ${data.details}`;
                } else {
                    clearInterval(pollInterval);
                    btnHash.disabled = false;
                    btnHash.classList.remove('running');
                    hashStatus.style.color = 'red';
                    hashStatus.innerText = data.message || "Cracking idle/failed.";
                }
            } catch(e) {
                // Ignore silent poll fails
            }
        }, 5000); // 5 sec interval
    }
});
