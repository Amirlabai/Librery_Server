import React, { useState } from 'react';
import './auth.css';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth';
import { toastError } from '../toast';
import { useDarkMode } from '../useDarkMode';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [busy, setBusy] = useState(false);
  const nav = useNavigate();
  const { login } = useAuth();
  const isDark = useDarkMode();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (busy) return;
    setBusy(true);
    try {
      await login(email, password);
      nav('/dashboard');
    } catch (err: any) {
      toastError(err?.message || 'Login failed');
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
          <h1 className="auth-title">Sign in</h1>
          <p className="auth-subtitle">Access your Merkaz files</p>
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

          <div>
            <label className="field-label" htmlFor="password">
              Password
            </label>
            <div className="password-field">
              <input
                id="password"
                className="full-width"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                type={showPassword ? 'text' : 'password'}
                required
                autoComplete="current-password"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword((v) => !v)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>

          <button disabled={busy} type="submit" className="button">
            {busy ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        <div className="auth-links">
          <Link className="forgot-pass" to="/forgot-password">
            Forgot password?
          </Link>
          <p className="have-account">
            Don&apos;t have an account?
            <Link className="create" to="/register">
              Create one
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
