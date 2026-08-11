import React from 'react';
import { useUploadProgress } from './uploadProgress';

export default function UploadProgressWidget() {
  const { progress } = useUploadProgress();
  const { isActive, currentFile, type, progress: pct } = progress;

  if (!isActive) return null;

  return (
    <div
      style={{
        position: 'fixed',
        right: 16,
        bottom: 16,
        width: 360,
        background: 'rgba(17, 24, 39, 0.92)',
        color: '#fff',
        borderRadius: 12,
        padding: 14,
        boxShadow: '0 12px 30px rgba(0,0,0,0.2)',
      }}
    >
      <div style={{ fontWeight: 600, marginBottom: 8 }}>
        Upload {type === 'folder' ? 'folder' : 'files'}: {pct}%
      </div>
      <div style={{ fontSize: 12, opacity: 0.85, wordBreak: 'break-word' }}>{currentFile}</div>
    </div>
  );
}

