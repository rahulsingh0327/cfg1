import React from 'react';
import { Handle, Position } from 'react-flow-renderer';

export default function AssignmentNode({ data }) {
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
      <Handle type="target" position={Position.Top} style={{ background: '#555' }} />
      {data.label}
      <Handle type="source" position={Position.Bottom} style={{ background: '#555' }} />
    </div>
  );
}