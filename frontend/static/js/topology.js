// Handles the Vis.js Network Topology

let network = null;

function initTopology(containerId) {
    const container = document.getElementById(containerId);
    
    const data = {
        nodes: new vis.DataSet([
            { id: 'scanner', label: 'Scanner\n(Kali Base)', shape: 'image', image: 'https://img.icons8.com/color/48/000000/kali-linux.png' }
        ]),
        edges: new vis.DataSet([])
    };
    
    const options = {
        nodes: {
            font: { color: '#e2e8f0' },
            shadow: {
                enabled: true,
                color: 'rgba(0,0,0,0.5)',
                size: 10,
                x: 5,
                y: 5
            }
        },
        edges: {
            color: { color: '#3c4b6e', highlight: '#38bdf8' },
            width: 2,
            smooth: { type: 'cubicBezier', forceDirection: 'horizontal' }
        },
        layout: {
            hierarchical: {
                enabled: true,
                direction: 'LR',
                sortMethod: 'directed',
                levelSeparation: 300,
                nodeSpacing: 100
            }
        },
        physics: {
            enabled: false
        },
        interaction: {
            hover: true,
            tooltipDelay: 200
        }
    };
    
    network = new vis.Network(container, data, options);
    
    // Node click to view details (optional extra interactivity)
    network.on("click", function (params) {
        if (params.nodes.length > 0) {
            console.log("Clicked Node:", params.nodes[0]);
        }
    });
}

function renderServiceList(ports) {
    if (!ports || ports.length === 0) return "⚪ No open ports";
    
    let lines = ports.map(p => {
        let note = p.notes ? ` [${p.notes}]` : "";
        return `├── ${p.port}/${p.service}/${p.product}${note}`;
    });
    
    return lines.join("\n");
}

function updateTopology(scanData) {
    if (!network) return;
    
    // Process incoming nodes to format the label
    if (scanData.nodes) {
        scanData.nodes.forEach(node => {
            if (node.ports) {
                node.label += "\n" + renderServiceList(node.ports);
            }
        });
    }
    
    const nodesDataset = new vis.DataSet(scanData.nodes);
    const edgesDataset = new vis.DataSet(scanData.edges);
    
    network.setOptions({
        nodes: {
            shape: "box",
            margin: 10,
            font: { color: "#000000", multi: true, align: "left" }
        },
        edges: {
            color: { color: "#94a3b8" },
            width: 2
        }
    });
    
    network.setData({
        nodes: nodesDataset,
        edges: edgesDataset
    });
}
