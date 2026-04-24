// Handles the Network Topology Parsing (ASCII Format)

function initTopology(containerId) {
    const container = document.getElementById(containerId);
    if(container) {
        container.innerHTML = "Awaiting scan results...";
    }
}

function updateTopology(scanData) {
    const container = document.getElementById("vis-network-container");
    if (!container) return;
    
    // Map JSON status colors to ASCII emojis
    const statusMap = {
        "accessible": "🟢",
        "caution": "🟡",
        "blocked": "🔴",
        "unknown": "⚪"
    };

    let mapHtml = `┌─────────────────────────────────────────────────────────────┐\n`;
    mapHtml    += `│  🖥️  SCANNER (Kali Base)                                    │\n`;
    mapHtml    += `│    │                                                         │\n`;
    
    if (scanData.nodes && scanData.nodes.length > 0) {
        // Filter out scanner node (it's hardcoded at the top)
        const hosts = scanData.nodes.filter(n => n.id !== "scanner");
        
        hosts.forEach((host, index) => {
            const isLastBox = index === hosts.length - 1;
            const branch = isLastBox ? "└──" : "├──";
            const line   = isLastBox ? " " : "│";
            
            const emoji = statusMap[host.status] || "⚪";
            
            // Format IP, Hostname, OS
            const ipLines = host.label.split("\\n");
            let targetIP = ipLines[0] || host.id;
            let hostname = (host.hostname && host.hostname !== "None") ? `(${host.hostname})` : "(Unknown)";
            let os_info = host.os_info ? `🔵 ${host.os_info}` : "🔵 Unknown OS";
            
            // Padding
            const ipPad = targetIP.padEnd(16, " ");
            
            mapHtml += `│    ${branch} ${emoji} ${ipPad} ${hostname} ${os_info}\n`;
            
            // Format Ports
            if (host.ports && host.ports.length > 0) {
                host.ports.forEach((p, pIndex) => {
                    const pIsLast = pIndex === host.ports.length - 1;
                    const pBranch = pIsLast ? "└──" : "├──";
                    const note = p.notes ? ` [${p.notes}]` : "";
                    mapHtml += `│    ${line}   ${pBranch} ${p.port}/${p.service}/${p.product}${note}\n`;
                });
            } else {
                mapHtml += `│    ${line}   └── ⚪ No open ports discovered\n`;
            }
            
            if (!isLastBox) {
                mapHtml += `│    ${line}                                                         │\n`;
            }
        });
    } else {
        mapHtml += `│    └── ⚪ No hosts found in scan.                            │\n`;
    }
    
    mapHtml += `└─────────────────────────────────────────────────────────────┘`;
    container.innerHTML = mapHtml;
}
