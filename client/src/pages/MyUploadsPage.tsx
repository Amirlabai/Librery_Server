import React, { useEffect, useState } from 'react';
import { toastError } from '../toast';
import { authGetJson } from '../authFetch';

type UploadHistory = {
  timestamp: string;
  filename: string;
  path: string | null;
  status: string;
};

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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div style={{ padding: 16 }}>
      <h2>My uploads</h2>
      {busy && <div>Loading...</div>}
      {!busy && uploads.length === 0 && <div>No uploads.</div>}
      {!busy && uploads.length > 0 && (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ textAlign: 'left', borderBottom: '1px solid #ddd' }}>File</th>
              <th style={{ textAlign: 'left', borderBottom: '1px solid #ddd' }}>Status</th>
              <th style={{ textAlign: 'left', borderBottom: '1px solid #ddd' }}>Time</th>
            </tr>
          </thead>
          <tbody>
            {uploads.map((u, idx) => (
              <tr key={u.filename + idx}>
                <td style={{ padding: '8px 0' }}>{u.filename}</td>
                <td style={{ padding: '8px 0' }}>{u.status}</td>
                <td style={{ padding: '8px 0' }}>{u.timestamp}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

