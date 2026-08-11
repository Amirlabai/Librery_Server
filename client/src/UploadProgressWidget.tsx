import React from 'react';
import { useUploadProgress } from './uploadProgress';

export default function UploadProgressWidget() {
  const { progress } = useUploadProgress();
  const { isActive, currentFile, type, progress: pct } = progress;

  if (!isActive) return null;

  return (
    <div className="upload-progress-widget" role="status" aria-live="polite">
      <div className="upload-progress-widget__title">
        Uploading {type === 'folder' ? 'folder' : 'files'}: {pct}%
      </div>
      <div className="upload-progress-widget__file">{currentFile || 'Preparing...'}</div>
      <div className="upload-progress-widget__bar" aria-hidden="true">
        <div className="upload-progress-widget__fill" style={{ transform: `scaleX(${Math.max(0, Math.min(100, pct)) / 100})` }} />
      </div>
    </div>
  );
}
