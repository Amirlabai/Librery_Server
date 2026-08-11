import React, { useState } from 'react';
import './auth.css';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth';
import { toastError, toastSuccess } from '../toast';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const nav = useNavigate();

  const { login } = useAuth();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (busy) return;
    setBusy(true);
    try {
      await login(email, password);
      toastSuccess('Redirecting...');
      nav('/dashboard');
    } catch (err: any) {
      toastError(err?.message || 'Login failed');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ maxWidth: 520, margin: '40px auto', padding: 16 }}>
      <h2>Login</h2>
      <form onSubmit={onSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <input
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          type="email"
          required
        />
        <input
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          type="password"
          required
        />
        <button disabled={busy} type="submit">
          {busy ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  );
}

