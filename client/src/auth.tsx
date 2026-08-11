import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import * as api from './api';
import { toastError, toastSuccess } from './toast';

export interface AuthUser {
  token: string;
  role: string | null;
  email: string | null;
  fullName: string | null;
  challenge?: string;
}

const TOKEN_KEY = 'token';

function readToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

function clearAuthStorage(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem('role');
  localStorage.removeItem('email');
  localStorage.removeItem('fullName');
}

interface AuthContextValue {
  user: AuthUser | null;
  isLoggedIn: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<AuthUser | null>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);

  const hydrateFromStorage = useCallback(() => {
    const token = readToken();
    if (!token) {
      setUser(null);
      return;
    }

    setUser({
      token,
      role: localStorage.getItem('role'),
      email: localStorage.getItem('email'),
      fullName: localStorage.getItem('fullName'),
    });
  }, []);

  useEffect(() => {
    hydrateFromStorage();
  }, [hydrateFromStorage]);

  const login = useCallback(async (email: string, password: string) => {
    const res = await api.login(email, password);
    if (!res?.token) throw new Error('Login failed: no token received');

    localStorage.setItem(TOKEN_KEY, res.token);
    if (res.role) localStorage.setItem('role', res.role);
    localStorage.setItem('email', email.trim());
    if (res.full_name) localStorage.setItem('fullName', res.full_name);

    setUser({
      token: res.token,
      role: res.role ?? null,
      email: email.trim(),
      fullName: res.full_name ?? null,
    });
    toastSuccess('Login successful');
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.logout();
    } catch {
      // Logout should not fail the UI.
    }
    clearAuthStorage();
    setUser(null);
  }, []);

  const refresh = useCallback(async (): Promise<AuthUser | null> => {
    try {
      const res: any = await api.refreshSession();
      if (res?.token) {
        localStorage.setItem(TOKEN_KEY, res.token);
      } else if (!res?.token) {
        clearAuthStorage();
        setUser(null);
        return null;
      }

      const nextUser: AuthUser = {
        token: res?.token,
        role: res?.role ?? localStorage.getItem('role'),
        email: res?.email ?? localStorage.getItem('email'),
        fullName: res?.full_name ?? localStorage.getItem('fullName'),
        challenge: res?.challenge,
      };

      if (nextUser.role) localStorage.setItem('role', nextUser.role);
      if (nextUser.email) localStorage.setItem('email', nextUser.email);
      if (nextUser.fullName) localStorage.setItem('fullName', nextUser.fullName);
      setUser(nextUser);
      return nextUser;
    } catch (err) {
      clearAuthStorage();
      setUser(null);
      return null;
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isLoggedIn: !!user?.token,
      login,
      logout,
      refresh,
    }),
    [login, logout, refresh, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export function ProtectedRoute() {
  const { refresh } = useAuth();
  const location = useLocation();

  const [allowed, setAllowed] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;
    setAllowed(null);

    refresh().then((u) => {
      if (!mounted) return;
      setAllowed(!!u?.token);
    });

    return () => {
      mounted = false;
    };
  }, [location.pathname, refresh]);

  if (allowed === null) return <div />;
  if (!allowed) return <Navigate to="/login" replace />;

  return <Outlet />;
}

export function AdminRoute() {
  const { refresh } = useAuth();
  const location = useLocation();
  const [allowed, setAllowed] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;
    setAllowed(null);

    refresh().then((u) => {
      if (!mounted) return;
      setAllowed(u?.role === 'admin');
    });

    return () => {
      mounted = false;
    };
  }, [location.pathname, refresh]);

  if (allowed === null) return <div />;
  if (!allowed) return <Navigate to="/dashboard" replace />;

  return <Outlet />;
}

