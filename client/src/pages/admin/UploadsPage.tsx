import React, { useEffect, useState } from 'react';
import AdminLayout from './AdminLayout';
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
  }, []);

  function updatePath(index: number, path: string) {
    setUploads((prev) => prev.map((item, i) => (i === index ? { ...item, path } : item)));
  }

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
    <AdminLayout activeTab="uploads">
      <div className="content-wrapper">
        <div className="scrollable-content">
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>User Email</th>
                  <th>Uploaded Item</th>
                  <th style={{ width: '40%' }}>Approve Location</th>
                  <th style={{ width: '15%', textAlign: 'center' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {busy && (
                  <tr>
                    <td colSpan={5} className="empty-cell">
                      Loading...
                    </td>
                  </tr>
                )}

                {!busy &&
                  uploads.map((upload, index) => (
                    <tr key={`${upload.timestamp}-${upload.filename}`}>
                      <td data-label="Timestamp">{upload.timestamp}</td>
                      <td data-label="User Email">{upload.email}</td>
                      <td data-label="Uploaded Item">{upload.filename}</td>
                      <td data-label="Approve Location">
                        <input
                          type="text"
                          value={upload.path}
                          onChange={(e) => updatePath(index, e.target.value)}
                          placeholder="Enter destination path"
                          className="path-input"
                        />
                      </td>
                      <td data-label="Actions" style={{ textAlign: 'center' }}>
                        <div className="actions-cell">
                          <button type="button" className="action-btn approve-btn" onClick={() => approve(upload)}>
                            Approve
                          </button>
                          <button type="button" className="action-btn decline-btn" onClick={() => decline(upload)}>
                            Decline
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}

                {!busy && uploads.length === 0 && (
                  <tr>
                    <td colSpan={5} className="empty-cell">
                      No files are pending review.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AdminLayout>
  );
}
