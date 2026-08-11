import React, { useMemo, useState } from 'react';
import './auth.css';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import * as api from '../api';
import { toastError, toastSuccess } from '../toast';
import { useDarkMode } from '../useDarkMode';

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = useMemo(() => searchParams.get('token'), [searchParams]);
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const nav = useNavigate();
  const isDark = useDarkMode();

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
    <div className="page-root">
      <div className="login-container">
        <div className="auth-brand">
          <img
            src={isDark ? '/assets/icons/banner-logo-dark-mode.webp' : '/assets/icons/banner-logo.webp'}
            alt="Merkaz"
          />
        </div>
        <header className="auth-header">
          <h1 className="auth-title">Reset password</h1>
          <p className="auth-subtitle">Choose a new password for your account</p>
        </header>

        <form onSubmit={onSubmit} className="login-form">
          <div>
            <label className="field-label" htmlFor="password">
              New password
            </label>
            <input
              id="password"
              className="full-width"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              required
              autoComplete="new-password"
            />
          </div>
          <button disabled={busy || !token} type="submit" className="button">
            {busy ? 'Saving...' : 'Save new password'}
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
