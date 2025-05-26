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
      padding: '10px 12px',
      borderRadius: 6,
      background: '#e0f7fa',
      textAlign: 'center',
      fontFamily: 'monospace',
      position: 'relative',
      minWidth: 140,
      boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
      userSelect: 'none',
    }}>
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: '#555', width: 10, height: 10, borderRadius: '50%' }}
      />
      {data.label}
      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: '#555', width: 10, height: 10, borderRadius: '50%' }}
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
  const [astString, setAstString] = useState('');

  const handleSubmit = async () => {
    const response = await fetch("http://localhost:8000/parse/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code }),
    });
    const data = await response.json();

    const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(data.nodes, data.edges);

    setNodes(layoutedNodes);
    setEdges(layoutedEdges);
    setAstString(data.ast || "");
  };

  return (
    <div style={{
      padding: '1.5rem 2rem',
      fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
      backgroundColor: '#fafafa',
      minHeight: '100vh',
      boxSizing: 'border-box',
      color: '#333',
    }}>
      <h1 style={{ marginBottom: '1.5rem', fontWeight: 600, color: '#00796b' }}>
        Python AST Flowchart Visualizer
      </h1>

      <div style={{
        display: 'flex',
        gap: '1.5rem',
        height: '65vh',
        marginBottom: '1.5rem',
      }}>
        <textarea
          rows={20}
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="Paste your Python code here..."
          style={{
            width: '50%',
            fontFamily: 'monospace',
            fontSize: '1rem',
            padding: '12px',
            borderRadius: 8,
            border: '1.5px solid #ccc',
            boxShadow: 'inset 0 2px 5px rgba(0,0,0,0.05)',
            resize: 'none',
            height: '100%',
            boxSizing: 'border-box',
            transition: 'border-color 0.3s ease',
          }}
          onFocus={e => e.target.style.borderColor = '#00796b'}
          onBlur={e => e.target.style.borderColor = '#ccc'}
        />

        <div style={{
          width: '50%',
          height: '100%',
          borderRadius: 8,
          border: '1.5px solid #ccc',
          backgroundColor: '#fff',
          boxShadow: '0 3px 8px rgba(0,0,0,0.1)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
        }}>
          <ReactFlow
            nodes={nodes}
            edges={edges.map(e => ({
              debug: true,
              ...e,
              type: 'step',
              markerEnd: { type: 'arrowclosed', color: '#00796b' },
              animated: e.animated || false,
              label: e.label || '',
              style: { stroke: '#00796b', strokeWidth: 2, zIndex: 2000 }
            }))}
            nodeTypes={nodeTypes}
            fitView
            panOnDrag
            zoomOnScroll
            zoomOnPinch
            snapToGrid
            snapGrid={[15, 15]}
            elevateEdgesOnSelect={true}
            style={{ flexGrow: 1 }}
          />
        </div>
      </div>

      <button
        onClick={handleSubmit}
        style={{
          backgroundColor: '#00796b',
          color: 'white',
          border: 'none',
          padding: '0.75rem 1.5rem',
          fontSize: '1rem',
          fontWeight: '600',
          borderRadius: 8,
          cursor: 'pointer',
          boxShadow: '0 4px 8px rgba(0, 121, 107, 0.4)',
          transition: 'background-color 0.3s ease',
          marginBottom: '1.5rem',
          display: 'block',
          marginLeft: 'auto',
          marginRight: 'auto',
          width: 'max-content',
        }}
        onMouseEnter={e => e.currentTarget.style.backgroundColor = '#004d40'}
        onMouseLeave={e => e.currentTarget.style.backgroundColor = '#00796b'}
      >
        Visualize
      </button>

      <div style={{
        maxHeight: '25vh',
        overflowY: 'auto',
        backgroundColor: '#ffffff',
        border: '1.5px solid #ccc',
        borderRadius: 8,
        padding: '1rem',
        fontFamily: 'monospace',
        fontSize: '0.9rem',
        color: '#555',
        boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.05)',
        whiteSpace: 'pre-wrap',
        lineHeight: 1.4,
      }}>
        {astString || "AST will appear here after visualization."}
      </div>
    </div>
  );
}
