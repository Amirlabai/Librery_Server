import React, { useState } from 'react';
import AdminLayout from './AdminLayout';
import { downloadAuthenticated } from '../../api';
import { toastError } from '../../toast';

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
  const [busyType, setBusyType] = useState<string | null>(null);

  async function onDownload(type: string) {
    if (busyType) return;
    setBusyType(type);
    try {
      await downloadAuthenticated(`/admin/metrics/download/${type}`, `${type}_log.xlsx`);
    } catch (err: any) {
      toastError(err?.message || 'Download failed');
    } finally {
      setBusyType(null);
    }
  }

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
              disabled={busyType === log.type}
              onClick={() => onDownload(log.type)}
            >
              {busyType === log.type ? 'Downloading…' : 'Download as Excel'}
            </button>
          </div>
        ))}
      </div>
    </AdminLayout>
  );
}
