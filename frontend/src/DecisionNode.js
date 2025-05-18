import React from 'react';
import { Handle, Position } from 'react-flow-renderer';

export default function DecisionNode({ data }) {
  return (
    <div style={{
      width: '100px',
      height: '100px',
      transform: 'rotate(45deg)',
      background: '#f0f4c3',
      border: '2px solid #333',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative',
    }}>
      {/* Incoming edge from top */}
      <Handle type="target" position={Position.Top} style={{ background: '#555' }} />

      {/* YES edge should come from the right edge (which becomes the bottom point after rotation) */}
    <Handle 
      type="source" 
      position={Position.Right} 
      id="no" 
      style={{ background: 'green', top: '50%', left: '100%', transform: 'translateY(-730%)' }} 
    />

    {/* NO edge should come from the bottom edge (which becomes the right point after rotation) */}
    <Handle 
      type="source" 
      position={Position.Bottom} 
      id="yes" 
      style={{ background: 'red', top: '100%', left: '50%', transform: 'translateX(620%)' }} 
    />

      <div style={{ transform: 'rotate(-45deg)', textAlign: 'center', fontFamily: 'monospace' }}>
        {data.label}
      </div>
    </div>
  );
}
