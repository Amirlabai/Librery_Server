import React, { useMemo, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import * as api from '../api';
import { toastError, toastSuccess } from '../toast';

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = useMemo(() => searchParams.get('token'), [searchParams]);
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const nav = useNavigate();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (busy) return;
    if (!token) {
      toastError('Invalid reset link');
      return;
    }

    setBusy(true);
    try {
      await api.resetPass(token, password);
      toastSuccess('Password updated successfully');
      nav('/login');
    } catch (err: any) {
      toastError(err?.message || 'Failed to reset password');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ maxWidth: 520, margin: '40px auto', padding: 16 }}>
      <h2>Reset password</h2>
      <form onSubmit={onSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <input
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="New password"
          type="password"
          required
        />
        <button disabled={busy} type="submit">
          {busy ? 'Saving...' : 'Save new password'}
        </button>
      </form>
    </div>
  );
}

