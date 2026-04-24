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
            smooth: { type: 'continuous' }
        },
        physics: {
            forceAtlas2Based: {
                gravitationalConstant: -50,
                centralGravity: 0.01,
                springLength: 100,
                springConstant: 0.08
            },
            maxVelocity: 50,
            solver: 'forceAtlas2Based',
            timestep: 0.35,
            stabilization: { iterations: 150 }
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

function updateTopology(scanData) {
    if (!network) return;
    
    // We expect scanData to have { nodes: [...], edges: [...] }
    const nodesDataset = new vis.DataSet(scanData.nodes);
    const edgesDataset = new vis.DataSet(scanData.edges);
    
    network.setData({
        nodes: nodesDataset,
        edges: edgesDataset
    });
}
