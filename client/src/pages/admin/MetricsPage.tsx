import React from 'react';
import AdminLayout from './AdminLayout';

const logs = [
  {
    type: 'session',
    name: 'Session Log (Login/Logout)',
    description: 'Track user login and failure events.',
  },
  {
    type: 'download',
    name: 'Download Log (File/Folder/Delete)',
    description: 'Track all file, folder, and delete events.',
  },
  {
    type: 'suggestion',
    name: 'Suggestion Log (User Feedback)',
    description: 'Records all user suggestions.',
  },
  {
    type: 'upload',
    name: 'Upload Log (Uploads traffic)',
    description: 'Records all uploads.',
  },
  {
    type: 'declined',
    name: 'Declined Log (Declined Files)',
    description: 'Records all declined files.',
  },
];

export default function MetricsPage() {
  return (
    <AdminLayout activeTab="metrics">
      <div className="content-wrapper">
        {logs.map((log) => (
          <div key={log.type} className="log-item">
            <div className="log-details">
              <h2>{log.name}</h2>
              <p>{log.description}</p>
            </div>
            <button
              type="button"
              className="download-btn"
              onClick={() => window.open(`/admin/metrics/download/${log.type}`, '_blank')}
            >
              Download as Excel
            </button>
          </div>
        ))}
      </div>
    </AdminLayout>
  );
}
