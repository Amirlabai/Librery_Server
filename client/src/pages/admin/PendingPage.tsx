import React, { useEffect, useState } from 'react';
import './admin.css';
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
    <div style={{ padding: 16 }}>
      <h2>Pending users</h2>
      {busy && <div>Loading...</div>}
      {!busy && users.length === 0 && <div>No pending users.</div>}
      {!busy && users.length > 0 && (
        <div style={{ display: 'grid', gap: 10 }}>
          {users.map((u) => (
            <div
              key={u.email}
              style={{ display: 'flex', justifyContent: 'space-between', gap: 12, padding: 12, background: 'rgba(0,0,0,0.03)', borderRadius: 12 }}
            >
              <div>
                <div style={{ fontWeight: 600 }}>{u.email}</div>
                <div style={{ fontSize: 12, opacity: 0.75 }}>{u.status || ''}</div>
              </div>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <button onClick={() => approve(u.email)}>Approve</button>
                <button onClick={() => deny(u.email)}>Deny</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

