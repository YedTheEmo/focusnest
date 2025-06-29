// import * as d3 from 'd3';
import { API_BASE } from './state.js';
import { loadNote } from './app.js'; // Adjust if using a shared loader

let graphSvg, graphSimulation;

function toggleGraph() {
    const graphArea = document.getElementById('graph-area');
    const editorArea = document.getElementById('editor-area');

    const isHidden = graphArea.style.display === 'none' || getComputedStyle(graphArea).display === 'none';

    if (isHidden) {
        graphArea.style.display = 'flex';
        editorArea.style.display = 'none';
        loadGraphData();
    } else {
        closeGraph();
    }
}

function closeGraph() {
    document.getElementById('graph-area').style.display = 'none';
    document.getElementById('editor-area').style.display = 'flex';
}

async function loadGraphData() {
    try {
        const response = await fetch(`${API_BASE}/graph/`);
        const data = await response.json();
        renderGraph(data);
    } catch (err) {
        console.error('Failed to load graph data:', err);
        showNotification('Failed to load graph', 'error');
    }
}

function renderGraph(data) {
    const container = document.getElementById('graph-container');
    container.innerHTML = '';

    if (!data.nodes || data.nodes.length === 0) {
        container.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #6c757d;">
                No notes to visualize yet. Create some notes with [[links]] to see the graph!
            </div>`;
        return;
    }

    const width = container.clientWidth;
    const height = container.clientHeight;

    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    const g = svg.append('g');

    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });

    svg.call(zoom);
    graphSvg = svg;

    graphSimulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink(data.links).id(d => d.id).distance(80))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(30));

    const link = g.append('g')
        .attr('class', 'links')
        .selectAll('line')
        .data(data.links)
        .enter().append('line')
        .attr('class', 'graph-link')
        .attr('stroke', '#999')
        .attr('stroke-opacity', 0.6)
        .attr('stroke-width', d => Math.sqrt(d.strength || 1) * 2);

    const node = g.append('g')
        .attr('class', 'nodes')
        .selectAll('g')
        .data(data.nodes)
        .enter().append('g')
        .attr('class', 'node-group')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended))
        .on('click', handleNodeClick)
        .on('mouseover', handleNodeMouseOver)
        .on('mouseout', handleNodeMouseOut);

    node.append('circle')
        .attr('class', 'graph-node')
        .attr('r', d => Math.max(8, Math.min(20, (d.connections || 0) * 3)))
        .attr('fill', d => {
            const c = d.connections || 0;
            if (c === 0) return '#dc3545';
            if (c <= 2) return '#28a745';
            if (c <= 5) return '#007bff';
            return '#6f42c1';
        })
        .attr('stroke', '#fff')
        .attr('stroke-width', 2);

    node.append('text')
        .attr('class', 'node-label')
        .attr('dx', 0)
        .attr('dy', '.35em')
        .attr('text-anchor', 'middle')
        .attr('font-size', '10px')
        .attr('font-family', 'Arial, sans-serif')
        .attr('fill', '#333')
        .attr('pointer-events', 'none')
        .text(d => {
            const title = d.title || d.id;
            return title.length > 15 ? title.slice(0, 12) + '...' : title;
        });

    const tooltip = d3.select('body').append('div')
        .attr('class', 'graph-tooltip')
        .style('position', 'absolute')
        .style('visibility', 'hidden')
        .style('background', 'rgba(0, 0, 0, 0.8)')
        .style('color', 'white')
        .style('padding', '8px')
        .style('border-radius', '4px')
        .style('font-size', '12px')
        .style('pointer-events', 'none')
        .style('z-index', '1000');

    graphSimulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node
            .attr('transform', d => `translate(${d.x},${d.y})`);
    });

    function handleNodeClick(event, d) {
        event.stopPropagation();
        if (d.id) {
            closeGraph();
            loadNote(d.id);
        }
    }

    function handleNodeMouseOver(event, d) {
        const connected = new Set();

        link
            .style('stroke-opacity', l => {
                if (l.source.id === d.id || l.target.id === d.id) {
                    connected.add(l.source.id);
                    connected.add(l.target.id);
                    return 1;
                }
                return 0.1;
            })
            .style('stroke-width', l =>
                (l.source.id === d.id || l.target.id === d.id)
                    ? Math.sqrt(l.strength || 1) * 3
                    : Math.sqrt(l.strength || 1) * 2
            );

        node.select('circle')
            .style('opacity', n => connected.has(n.id) ? 1 : 0.3);
        node.select('text')
            .style('opacity', n => connected.has(n.id) ? 1 : 0.3);

        tooltip
            .style('visibility', 'visible')
            .html(`
                <strong>${d.title || d.id}</strong><br/>
                Connections: ${d.connections || 0}<br/>
                Created: ${d.created ? new Date(d.created).toLocaleDateString() : 'Unknown'}
            `)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px');
    }

    function handleNodeMouseOut() {
        link
            .style('stroke-opacity', 0.6)
            .style('stroke-width', d => Math.sqrt(d.strength || 1) * 2);

        node.select('circle').style('opacity', 1);
        node.select('text').style('opacity', 1);

        tooltip.style('visibility', 'hidden');
    }

    addGraphLegend(g, width, height);

    setTimeout(() => {
        const bounds = g.node().getBBox();
        const midX = bounds.x + bounds.width / 2;
        const midY = bounds.y + bounds.height / 2;
        const scale = 0.8 / Math.max(bounds.width / width, bounds.height / height);
        const translate = [width / 2 - scale * midX, height / 2 - scale * midY];

        if (bounds.width && bounds.height) {
            svg.transition().duration(750).call(
                zoom.transform,
                d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale)
            );
        }
    }, 500);
}

function addGraphLegend(container, width, height) {
    const legend = container.append('g')
        .attr('class', 'graph-legend')
        .attr('transform', `translate(${width - 150}, 20)`);

    const items = [
        { color: '#dc3545', label: 'Orphan notes', size: 8 },
        { color: '#28a745', label: 'Few connections', size: 10 },
        { color: '#007bff', label: 'Well connected', size: 15 },
        { color: '#6f42c1', label: 'Hub notes', size: 20 }
    ];

    const entry = legend.selectAll('.legend-item')
        .data(items)
        .enter().append('g')
        .attr('class', 'legend-item')
        .attr('transform', (d, i) => `translate(0, ${i * 25})`);

    entry.append('circle')
        .attr('r', d => d.size / 2)
        .attr('fill', d => d.color)
        .attr('stroke', '#fff')
        .attr('stroke-width', 1);

    entry.append('text')
        .attr('x', 15)
        .attr('y', 0)
        .attr('dy', '.35em')
        .attr('font-size', '11px')
        .attr('font-family', 'Arial, sans-serif')
        .attr('fill', '#333')
        .text(d => d.label);
}

// Drag functions
function dragstarted(event, d) {
    if (!event.active) graphSimulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragended(event, d) {
    if (!event.active) graphSimulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

// Responsive resizing
function resizeGraph() {
    if (!graphSvg) return;
    const container = document.getElementById('graph-container');
    const width = container.clientWidth;
    const height = container.clientHeight;

    graphSvg.attr('width', width).attr('height', height);

    if (graphSimulation) {
        graphSimulation
            .force('center', d3.forceCenter(width / 2, height / 2))
            .restart();
    }
}

window.addEventListener('resize', resizeGraph);

export {
    toggleGraph,
    closeGraph,
    renderGraph,
    loadGraphData,
    addGraphLegend,
    dragstarted,
    dragged,
    dragended,
    resizeGraph
};
