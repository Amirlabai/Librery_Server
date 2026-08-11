import React, { useEffect, useState } from 'react';
import './admin.css';
import { toastError, toastSuccess } from '../../toast';
import { authGetJson, authPostJson } from '../../authFetch';

type UploadItem = {
  timestamp: string;
  email: string;
  filename: string;
  path: string;
};

export default function UploadsPage() {
  const [uploads, setUploads] = useState<UploadItem[]>([]);
  const [busy, setBusy] = useState(false);

  async function load() {
    setBusy(true);
    try {
      const res = await authGetJson<UploadItem[]>('/admin/uploads');
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

  async function approve(item: UploadItem) {
    try {
      await authPostJson(`/admin/move_upload/${item.filename}`, { target_path: item.path });
      toastSuccess(`Approved ${item.filename}`);
      await load();
    } catch (err: any) {
      toastError(err?.message || 'Approve failed');
    }
  }

  async function decline(item: UploadItem) {
    if (!confirm('Are you sure you want to decline and delete this item?')) return;
    try {
      await authPostJson(`/admin/decline_upload/${item.filename}`, { target_path: item.path });
      toastSuccess(`Declined ${item.filename}`);
      await load();
    } catch (err: any) {
      toastError(err?.message || 'Decline failed');
    }
  }

  return (
    <div style={{ padding: 16 }}>
      <h2>Admin uploads</h2>
      {busy && <div>Loading...</div>}
      {!busy && uploads.length === 0 && <div>No pending uploads.</div>}
      {!busy && uploads.length > 0 && (
        <div style={{ display: 'grid', gap: 10 }}>
          {uploads.map((u) => (
            <div
              key={u.filename + u.timestamp}
              style={{
                display: 'grid',
                gap: 6,
                padding: 12,
                borderRadius: 12,
                background: 'rgba(0,0,0,0.03)',
              }}
            >
              <div style={{ fontWeight: 600 }}>{u.filename}</div>
              <div style={{ fontSize: 12, opacity: 0.8 }}>Uploader: {u.email}</div>
              <div style={{ fontSize: 12, opacity: 0.8 }}>Target: {u.path}</div>
              <div style={{ fontSize: 12, opacity: 0.8 }}>Time: {u.timestamp}</div>
              <div style={{ display: 'flex', gap: 8 }}>
                <button onClick={() => approve(u)}>Approve</button>
                <button onClick={() => decline(u)}>Decline</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

