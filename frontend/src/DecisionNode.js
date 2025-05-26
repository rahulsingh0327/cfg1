import React from 'react';
import { Handle, Position } from 'react-flow-renderer';

export default function DecisionNode({ data }) {
  console.log('Rendering DecisionNode with data:', data);
  return (
    <div
      style={{
        width: '100px',
        height: '100px',
        background: '#f0f4c3',
        border: '2px solid #333',
        clipPath: 'polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
      }}
    >
      {/* Incoming edge from top */}
      <Handle type="target" position={Position.Top} style={{ background: '#555',}} />

      {/* YES edge should come from the right edge (which becomes the bottom point after rotation) */}
    <Handle 
      type="source" 
      position={Position.Right} 
      id="no" 
      style={{ background: 'red'}} 
    />

    {/* NO edge should come from the bottom edge (which becomes the right point after rotation) */}
    <Handle 
      type="source" 
      position={Position.Left} 
      id="yes" 
      style={{ background: 'green' }} 
    />

      <div style={{ textAlign: 'center', fontFamily: 'monospace' }}>
        {data.label}
      </div>
    </div>
  );
}
