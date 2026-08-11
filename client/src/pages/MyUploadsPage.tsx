import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import './dashboard.css';
import { toastError } from '../toast';
import { authGetJson } from '../authFetch';

type UploadHistory = {
  timestamp: string;
  filename: string;
  path: string | null;
  status: string;
};

function statusClass(status: string): string {
  if (status === 'Pending Review') return 'status-pending';
  if (status === 'Declined') return 'status-declined';
  if (status === 'Approved') return 'status-approved';
  return '';
}

export default function MyUploadsPage() {
  const [uploads, setUploads] = useState<UploadHistory[]>([]);
  const [busy, setBusy] = useState(false);

  async function load() {
    setBusy(true);
    try {
      const res = await authGetJson<UploadHistory[]>('/my_uploads');
      setUploads(Array.isArray(res) ? res : []);
    } catch (err: any) {
      toastError(err?.message || 'Failed to load uploads');
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="page-root">
      <div className="container">
        <header className="header">
          <h1>My Upload History</h1>
          <Link to="/dashboard" className="my-uploads-btn">
            Back to Files
          </Link>
        </header>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Filename</th>
                <th>Suggested Path</th>
                <th style={{ width: '20%' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {busy && (
                <tr>
                  <td colSpan={4} style={{ textAlign: 'center', padding: 20 }}>
                    Loading...
                  </td>
                </tr>
              )}

              {!busy &&
                uploads.map((upload) => (
                  <tr key={`${upload.timestamp}-${upload.filename}`}>
                    <td data-label="Timestamp">{upload.timestamp}</td>
                    <td data-label="Filename">{upload.filename}</td>
                    <td data-label="Suggested Path">/{upload.path || 'Home'}</td>
                    <td data-label="Status">
                      <span className={statusClass(upload.status)}>{upload.status}</span>
                    </td>
                  </tr>
                ))}

              {!busy && uploads.length === 0 && (
                <tr>
                  <td colSpan={4} style={{ textAlign: 'center', color: 'var(--placeholder-color)', padding: 30 }}>
                    You have not uploaded any files.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
