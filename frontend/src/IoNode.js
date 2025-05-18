import React from 'react';
import { Handle, Position } from 'react-flow-renderer';

export default function IoNode({ data }) {
  return (
    <div style={{
      transform: 'skewX(-20deg)',
      background: '#fff3e0',
      padding: '8px',
      border: '2px solid #555',
      fontFamily: 'monospace',
      position: 'relative'
    }}>
      <Handle type="target" position={Position.Top} style={{ background: '#555' }} />
      <div style={{ transform: 'skewX(20deg)' }}>{data.label}</div>
      <Handle type="source" position={Position.Bottom} style={{ background: '#555' }} />
    </div>
  );
}