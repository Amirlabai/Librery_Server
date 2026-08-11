import React, { useEffect, useState } from 'react';
import './admin.css';
import { toastError, toastSuccess } from '../../toast';
import { authGetJson, authPostJson } from '../../authFetch';

type AdminUser = {
  email: string;
  role: string;
  status: string;
  online_status?: boolean;
};

export default function UsersPage() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [busy, setBusy] = useState(false);

  async function load() {
    setBusy(true);
    try {
      const res = await authGetJson<{ users: AdminUser[]; current_admin?: string }>('/admin/users');
      setUsers(Array.isArray(res?.users) ? res.users : []);
    } catch (err: any) {
      toastError(err?.message || 'Failed to load users');
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function toggleRole(email: string) {
    try {
      await authPostJson(`/admin/toggle-role/${email}`, {});
      toastSuccess('Role updated');
      await load();
    } catch (err: any) {
      toastError(err?.message || 'Failed to update role');
    }
  }

  async function toggleStatus(email: string) {
    try {
      await authPostJson(`/admin/toggle-status/${email}`, {});
      toastSuccess('Status updated');
      await load();
    } catch (err: any) {
      toastError(err?.message || 'Failed to update status');
    }
  }

  return (
    <div style={{ padding: 16 }}>
      <h2>Admin users</h2>
      {busy && <div>Loading...</div>}
      {!busy && (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ textAlign: 'left', borderBottom: '1px solid #ddd' }}>Email</th>
              <th style={{ textAlign: 'left', borderBottom: '1px solid #ddd' }}>Role</th>
              <th style={{ textAlign: 'left', borderBottom: '1px solid #ddd' }}>Status</th>
              <th style={{ textAlign: 'left', borderBottom: '1px solid #ddd' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.email}>
                <td style={{ padding: '8px 0' }}>{u.email}</td>
                <td style={{ padding: '8px 0' }}>{u.role}</td>
                <td style={{ padding: '8px 0' }}>{u.status}</td>
                <td style={{ padding: '8px 0' }}>
                  <button onClick={() => toggleRole(u.email)}>Toggle role</button>{' '}
                  <button onClick={() => toggleStatus(u.email)}>Toggle status</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

