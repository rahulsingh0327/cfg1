import React, { useState } from 'react';
import ReactFlow, { Handle, Position } from 'react-flow-renderer';
import 'react-flow-renderer/dist/style.css';
import IoNode from './IoNode';
import DecisionNode from './DecisionNode';
import getLayoutedElements from './layout';


export function AssignmentNode({ data }) {
  return (
    <div style={{
      border: '2px solid #555',
      padding: '8px',
      borderRadius: 4,
      background: '#e0f7fa',
      textAlign: 'center',
      fontFamily: 'monospace',
      position: 'relative',
      minWidth: 120
    }}>
      {/* Incoming arrow handle (top) */}
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: '#555', width: 8, height: 8 }}
      />

      {/* Label content */}
      {data.label}

      {/* Outgoing arrow handle (bottom) */}
      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: '#555', width: 8, height: 8 }}
      />
    </div>
  );
}

const nodeTypes = {
  assignment: AssignmentNode,
  io: IoNode,
  decision: DecisionNode,
};

export default function App() {
  const [code, setCode] = useState('');
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  const handleSubmit = async () => {
    const response = await fetch("http://localhost:8000/parse/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code }),
    });
    const data = await response.json();
  
   

    // 🧠 Layout nodes and edges using Dagre
    const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(data.nodes, data.edges);
  
    setNodes(layoutedNodes);
    setEdges(layoutedEdges);
  };

  return (
    <div style={{ padding: '1rem' }}>
      <h1>Python AST Flowchart Visualizer</h1>
      <textarea
        rows={10}
        cols={80}
        value={code}
        onChange={(e) => setCode(e.target.value)}
        placeholder="Paste Python code..."
        style={{ width: '100%', fontFamily: 'monospace' }}
      />
      <br />
      <button onClick={handleSubmit}>Visualize</button>

      <div style={{ height: '80vh', border: '1px solid #ccc', marginTop: '1rem', overflow: 'auto' }}>
      <ReactFlow
          nodes={nodes}
          edges={edges.map(e => ({
            ...e,
            type: 'step',
            markerEnd: {
              type: 'arrowclosed',
              color: '#000'
            },
            animated: e.animated || false,
            label: e.label || '',
            style: { stroke: '#000', strokeWidth: 2 }
          }))}
          nodeTypes={nodeTypes}
          fitView
          panOnDrag
          zoomOnScroll
          zoomOnPinch
        />
      </div>
    </div>
  );
}
