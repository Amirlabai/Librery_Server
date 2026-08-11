import React from 'react';
import './admin.css';

const logs = [
  { type: 'session', name: 'Session Log (Login/Logout)' },
  { type: 'download', name: 'Download Log (File/Folder/Delete)' },
  { type: 'suggestion', name: 'Suggestion Log (User Feedback)' },
  { type: 'upload', name: 'Upload Log (Uploads traffic)' },
  { type: 'declined', name: 'Declined Log (Declined Files)' },
];

export default function MetricsPage() {
  return (
    <div style={{ padding: 16 }}>
      <h2>Admin metrics</h2>
      <div style={{ display: 'grid', gap: 10, maxWidth: 720 }}>
        {logs.map((l) => (
          <button key={l.type} onClick={() => window.open(`/admin/metrics/download/${l.type}`, '_blank')}>
            Download {l.name}
          </button>
        ))}
      </div>
    </div>
  );
}

