import React, { useEffect, useMemo, useState } from 'react';
import { Navigate, Route, Routes, useNavigate } from 'react-router-dom';
import { AuthProvider, AdminRoute, ProtectedRoute, useAuth } from './auth';
import { UploadProgressProvider } from './uploadProgress';
import UploadProgressWidget from './UploadProgressWidget';
import { toastError, toastSuccess } from './toast';

import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import DashboardPage from './pages/DashboardPage';
import MyUploadsPage from './pages/MyUploadsPage';
import UploadFilePage from './pages/UploadFilePage';

import MetricsPage from './pages/admin/MetricsPage';
import UsersPage from './pages/admin/UsersPage';
import PendingPage from './pages/admin/PendingPage';
import DeniedPage from './pages/admin/DeniedPage';
import UploadsPage from './pages/admin/UploadsPage';

function Placeholder() {
  return <div />;
}

function Shell() {
  const { logout } = useAuth();
  const nav = useNavigate();

  const [isDark, setIsDark] = useState(false);
  const [showChallenge, setShowChallenge] = useState(false);
  const [challengeActivated, setChallengeActivated] = useState(false);
  const [leaderboard, setLeaderboard] = useState<any[] | null>(null);
  const [answer, setAnswer] = useState('');
  const [puzzleNum, setPuzzleNum] = useState(0);

  useEffect(() => {
    document.body.classList.toggle('dark-mode', isDark);
  }, [isDark]);

  const onLogout = async () => {
    await logout();
    nav('/login');
  };

  useEffect(() => {
    let buffer = '';
    const secret = '753951';

    async function activate() {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch('/api/activate-challenge', {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({ code: secret }),
        });

        if (!res.ok) throw new Error('Challenge activation failed');
        setChallengeActivated(true);
        setShowChallenge(true);
      } catch (e: any) {
        // Endpoints might not exist in this backend build. Keep UI fail-soft.
        toastError(e?.message || 'Challenge activation failed');
      }
    }

    const onKeyUp = (e: KeyboardEvent) => {
      if (e.key < '0' || e.key > '9') {
        buffer = '';
        return;
      }

      buffer += e.key;
      buffer = buffer.slice(-secret.length);
      if (buffer === secret) activate();
    };

    document.addEventListener('keyup', onKeyUp);
    return () => document.removeEventListener('keyup', onKeyUp);
  }, []);

  useEffect(() => {
    async function loadLeaderboard() {
      if (!challengeActivated) return;
      try {
        const token = localStorage.getItem('token');
        const res = await fetch('/api/leaderboard-data', {
          method: 'GET',
          credentials: 'include',
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        if (!res.ok) throw new Error('Failed to load leaderboard');
        const body = await res.json();
        setLeaderboard(body?.leaderboard ?? body?.members ?? []);
      } catch {
        setLeaderboard([]);
      }
    }

    loadLeaderboard();
  }, [challengeActivated]);

  return (
    <>
      <UploadProgressWidget />
      <div style={{ position: 'sticky', top: 0, background: 'rgba(255,255,255,0.9)', zIndex: 10 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', padding: 12 }}>
          <div style={{ fontWeight: 700 }}>Merkaz</div>
          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <button onClick={() => setIsDark((v) => !v)}>Dark mode</button>
            <button onClick={() => setShowChallenge((v) => !v)}>
              {showChallenge ? 'Hide challenge' : 'Show challenge'}
            </button>
            <button onClick={onLogout}>Logout</button>
          </div>
        </div>
        {showChallenge && (
          <div style={{ padding: '0 12px 12px 12px', maxWidth: 980, margin: '0 auto' }}>
            <div style={{ fontWeight: 700, marginBottom: 8 }}>Challenge</div>
            <div style={{ fontSize: 12, opacity: 0.85, marginBottom: 12 }}>
              Enter the numpad code 753951 (keyboard digits only). This is a client-only shortcut.
            </div>
            {challengeActivated ? (
              <>
                <div style={{ fontSize: 13, marginBottom: 8 }}>Leaderboard</div>
                {leaderboard ? (
                  <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontSize: 12 }}>
                    {JSON.stringify(leaderboard, null, 2)}
                  </pre>
                ) : (
                  <div>Loading...</div>
                )}

                <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginTop: 14 }}>
                  <input
                    value={puzzleNum}
                    type="number"
                    min={1}
                    max={5}
                    onChange={(e) => setPuzzleNum(Number(e.target.value))}
                    style={{ width: 80 }}
                  />
                  <input
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    placeholder="Your answer"
                    style={{ flex: 1 }}
                  />
                  <button
                    onClick={async () => {
                      try {
                        const token = localStorage.getItem('token');
                        const res = await fetch('/api/submit-answer', {
                          method: 'POST',
                          credentials: 'include',
                          headers: {
                            'Content-Type': 'application/json',
                            ...(token ? { Authorization: `Bearer ${token}` } : {}),
                          },
                          body: JSON.stringify({ puzzle_name: `puzzle${puzzleNum}`, answer }),
                        });
                        if (!res.ok) throw new Error('Submit failed');
                        toastSuccess('Answer submitted');
                        setAnswer('');
                      } catch (e: any) {
                        toastError(e?.message || 'Submit failed');
                      }
                    }}
                  >
                    Submit
                  </button>
                </div>
              </>
            ) : (
              <div style={{ fontSize: 12, opacity: 0.85 }}>Not activated yet.</div>
            )}
          </div>
        )}
      </div>

      <Routes>
        {/* Public */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />

        {/* User */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/dashboard/my-uploads" element={<MyUploadsPage />} />
          <Route path="/dashboard/upload" element={<UploadFilePage />} />
        </Route>

        {/* Admin */}
        <Route element={<AdminRoute />}>
          <Route path="/metrics" element={<MetricsPage />} />
          <Route path="/users" element={<UsersPage />} />
          <Route path="/pending" element={<PendingPage />} />
          <Route path="/denied" element={<DeniedPage />} />
          <Route path="/uploads" element={<UploadsPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </>
  );
}

export default function App() {
  // Keep this component tiny; providers live here so hooks in Shell work.
  return (
    <AuthProvider>
      <UploadProgressProvider>
        <Shell />
      </UploadProgressProvider>
    </AuthProvider>
  );
}

