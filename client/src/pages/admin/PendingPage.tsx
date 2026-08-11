import React, { useEffect, useState } from 'react';
import AdminLayout from './AdminLayout';
import { toastError, toastSuccess } from '../../toast';
import { authGetJson, authPostJson } from '../../authFetch';

type PendingUser = {
  email: string;
  status?: string;
};

export default function PendingPage() {
  const [users, setUsers] = useState<PendingUser[]>([]);
  const [busy, setBusy] = useState(false);

  async function load() {
    setBusy(true);
    try {
      const res = await authGetJson<PendingUser[]>('/admin/pending');
      setUsers(Array.isArray(res) ? res : []);
    } catch (err: any) {
      toastError(err?.message || 'Failed to load pending users');
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function approve(email: string) {
    try {
      await authPostJson(`/admin/approve/${email}`, {});
      toastSuccess('User approved');
      await load();
    } catch (err: any) {
      toastError(err?.message || 'Approve failed');
    }
  }

  async function deny(email: string) {
    try {
      await authPostJson(`/admin/deny/${email}`, {});
      toastSuccess('User denied');
      await load();
    } catch (err: any) {
      toastError(err?.message || 'Deny failed');
    }
  }

  return (
    <AdminLayout activeTab="pending">
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
                      <button type="button" className="action-btn approve-btn" onClick={() => approve(u.email)}>
                        Approve
                      </button>
                      <button type="button" className="action-btn deny-btn" onClick={() => deny(u.email)}>
                        Deny
                      </button>
                    </td>
                  </tr>
                ))}

              {!busy && users.length === 0 && (
                <tr>
                  <td colSpan={2} className="empty-cell">
                    No users are pending approval.
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
