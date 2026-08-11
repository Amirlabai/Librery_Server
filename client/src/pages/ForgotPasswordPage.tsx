import React, { useState } from 'react';
import './auth.css';
import { Link } from 'react-router-dom';
import { toastError, toastSuccess } from '../toast';
import { useDarkMode } from '../useDarkMode';
import { apiHeaders, apiUrl } from '../api';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [busy, setBusy] = useState(false);
  const isDark = useDarkMode();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (busy) return;
    setBusy(true);
    try {
      const res = await fetch(apiUrl('/forgot-password'), {
        method: 'POST',
        credentials: 'include',
        headers: apiHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ email: email.trim() }),
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(body?.error || 'Failed to send reset link');
      toastSuccess('Reset link sent');
    } catch (err: any) {
      toastError(err?.message || 'Failed to send reset link');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page-root">
      <div className="login-container">
        <div className="auth-brand">
          <img
            src={isDark ? '/assets/icons/banner-logo-dark-mode.webp' : '/assets/icons/banner-logo.webp'}
            alt="Merkaz"
          />
        </div>
        <header className="auth-header">
          <h1 className="auth-title">Forgot password</h1>
          <p className="auth-subtitle">We will email you a reset link</p>
        </header>

        <form onSubmit={onSubmit} className="login-form">
          <div>
            <label className="field-label" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              className="full-width"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              type="email"
              required
              autoComplete="email"
            />
          </div>
          <button disabled={busy} type="submit" className="button">
            {busy ? 'Sending...' : 'Send reset link'}
          </button>
        </form>

        <div className="auth-links">
          <Link className="forgot-pass" to="/login">
            Back to sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
