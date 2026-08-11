import React, { useEffect, useState } from 'react';
import './admin.css';
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function rePend(email: string) {
    try {
      await authPostJson(`/admin/re-pend/${email}`, {});
      toastSuccess('Moved back to pending');
      await load();
    } catch (err: any) {
      toastError(err?.message || 'Failed to re-pen user');
    }
  }

  return (
    <div style={{ padding: 16 }}>
      <h2>Denied users</h2>
      {busy && <div>Loading...</div>}
      {!busy && users.length === 0 && <div>No denied users.</div>}
      {!busy && users.length > 0 && (
        <div style={{ display: 'grid', gap: 10 }}>
          {users.map((u) => (
            <div key={u.email} style={{ display: 'flex', justifyContent: 'space-between', gap: 12, padding: 12, background: 'rgba(0,0,0,0.03)', borderRadius: 12 }}>
              <div style={{ fontWeight: 600 }}>{u.email}</div>
              <button onClick={() => rePend(u.email)}>Re-pend</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

