import React, { useEffect, useState } from 'react';
import AdminLayout from './AdminLayout';
import { toastError, toastSuccess } from '../../toast';
import { authGetJson, authPostJson } from '../../authFetch';

type DeniedUser = {
  email: string;
};

export default function DeniedPage() {
  const [users, setUsers] = useState<DeniedUser[]>([]);
  const [busy, setBusy] = useState(false);

  async function load() {
    setBusy(true);
    try {
      const res = await authGetJson<DeniedUser[]>('/admin/denied');
      setUsers(Array.isArray(res) ? res : []);
    } catch (err: any) {
      toastError(err?.message || 'Failed to load denied users');
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function rePend(email: string) {
    try {
      await authPostJson(`/admin/re-pend/${email}`, {});
      toastSuccess('Moved back to pending');
      await load();
    } catch (err: any) {
      toastError(err?.message || 'Failed to re-pend user');
    }
  }

  return (
    <AdminLayout activeTab="denied">
      <div className="content-wrapper">
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Email</th>
                <th style={{ width: '25%', textAlign: 'center' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {busy && (
                <tr>
                  <td colSpan={2} className="empty-cell">
                    Loading...
                  </td>
                </tr>
              )}

              {!busy &&
                users.map((u) => (
                  <tr key={u.email}>
                    <td data-label="Email">{u.email}</td>
                    <td data-label="Action" style={{ textAlign: 'center' }}>
                      <button type="button" className="action-btn" onClick={() => rePend(u.email)}>
                        Move to Pending
                      </button>
                    </td>
                  </tr>
                ))}

              {!busy && users.length === 0 && (
                <tr>
                  <td colSpan={2} className="empty-cell">
                    No users have been denied.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </AdminLayout>
  );
}
