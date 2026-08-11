import React, { useEffect, useState } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider, AdminRoute, ProtectedRoute } from './auth';
import { UploadProgressProvider } from './uploadProgress';
import UploadProgressWidget from './UploadProgressWidget';
import { IconDarkMode, IconLightMode } from './components/Icons';

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

function DarkModeToggle() {
  const [isDark, setIsDark] = useState(() => document.body.classList.contains('dark-mode'));

  useEffect(() => {
    document.body.classList.toggle('dark-mode', isDark);
  }, [isDark]);

  return (
    <button
      type="button"
      className="dark-mode-button"
      onClick={() => setIsDark((v) => !v)}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      title={isDark ? 'Light mode' : 'Dark mode'}
    >
      {isDark ? <IconLightMode /> : <IconDarkMode />}
    </button>
  );
}

function Shell() {
  return (
    <>
      <DarkModeToggle />
      <UploadProgressWidget />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/dashboard/my-uploads" element={<MyUploadsPage />} />
          <Route path="/dashboard/upload" element={<UploadFilePage />} />
        </Route>

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
  return (
    <AuthProvider>
      <UploadProgressProvider>
        <Shell />
      </UploadProgressProvider>
    </AuthProvider>
  );
}
