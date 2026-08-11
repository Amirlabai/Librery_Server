import React, { useState } from 'react';
import './auth.css';
import { Link, useNavigate } from 'react-router-dom';
import * as api from '../api';
import { toastError, toastSuccess } from '../toast';
import { useDarkMode } from '../useDarkMode';

export default function RegisterPage() {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const nav = useNavigate();
  const isDark = useDarkMode();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (busy) return;
    setBusy(true);
    try {
      await api.register(firstName, lastName, email, password);
      toastSuccess('Registered successfully');
      nav('/login');
    } catch (err: any) {
      toastError(err?.message || 'Registration failed');
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
          <h1 className="auth-title">Create account</h1>
          <p className="auth-subtitle">Join the Merkaz file library</p>
        </header>

        <form onSubmit={onSubmit} className="login-form">
          <div>
            <label className="field-label" htmlFor="firstName">
              First name
            </label>
            <input
              id="firstName"
              className="full-width"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              required
              autoComplete="given-name"
            />
          </div>

          <div>
            <label className="field-label" htmlFor="lastName">
              Last name
            </label>
            <input
              id="lastName"
              className="full-width"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              required
              autoComplete="family-name"
            />
          </div>

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

          <button disabled={busy} type="submit" className="button">
            {busy ? 'Creating account...' : 'Create account'}
          </button>
        </form>

        <div className="auth-links">
          <p className="have-account">
            Already have an account?
            <Link className="create" to="/login">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
