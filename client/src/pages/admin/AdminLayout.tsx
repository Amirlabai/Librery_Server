import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './admin.css';

type AdminTab = 'metrics' | 'users' | 'pending' | 'denied' | 'uploads';

const TABS: { id: AdminTab; label: string; path: string }[] = [
  { id: 'metrics', label: 'Metrics', path: '/metrics' },
  { id: 'users', label: 'Users', path: '/users' },
  { id: 'pending', label: 'Pending', path: '/pending' },
  { id: 'denied', label: 'Denied', path: '/denied' },
  { id: 'uploads', label: 'Uploads', path: '/uploads' },
];

export default function AdminLayout({
  activeTab,
  children,
}: {
  activeTab: AdminTab;
  children: React.ReactNode;
}) {
  const location = useLocation();

  return (
    <div className="page-root admin-page-root">
      <div className="container admin-container">
        <header className="header">
          <h1>Admin Dashboard</h1>
          <Link to="/dashboard" className="back-link">
            Back to Files
          </Link>
        </header>

        <nav className="admin-nav" aria-label="Admin sections">
          {TABS.map((tab) => (
            <Link
              key={tab.id}
              to={tab.path}
              className={`nav-tab${location.pathname === tab.path || activeTab === tab.id ? ' active' : ''}`}
            >
              {tab.label}
            </Link>
          ))}
        </nav>

        {children}
      </div>
    </div>
  );
}
