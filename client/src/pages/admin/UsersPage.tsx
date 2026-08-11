import React, { useEffect, useState } from 'react';
import AdminLayout from './AdminLayout';
import { toastError, toastSuccess } from '../../toast';
import { authGetJson, authPostJson } from '../../authFetch';
import { useAuth } from '../../auth';

type AdminUser = {
  email: string;
  role?: string;
  status?: string;
  is_admin?: boolean;
  is_active?: boolean;
  online_status?: boolean;
};

export default function UsersPage() {
  const { user } = useAuth();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [busy, setBusy] = useState(false);

  async function load() {
    setBusy(true);
    try {
      const res = await authGetJson<{ users: AdminUser[]; current_admin?: string }>('/admin/users');
      setUsers(Array.isArray(res?.users) ? res.users : []);
    } catch (err: any) {
      toastError(err?.message || 'Failed to load users');
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function toggleRole(email: string) {
    try {
      await authPostJson(`/admin/toggle-role/${email}`, {});
      toastSuccess('Role updated');
      await load();
    } catch (err: any) {
      toastError(err?.message || 'Failed to update role');
    }
  }

  async function toggleStatus(email: string) {
    try {
      await authPostJson(`/admin/toggle-status/${email}`, {});
      toastSuccess('Status updated');
      await load();
    } catch (err: any) {
      toastError(err?.message || 'Failed to update status');
    }
  }

  const currentEmail = user?.email || '';

  return (
    <AdminLayout activeTab="users">
      <div className="content-wrapper">
        <div className="scrollable-content">
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Email</th>
                  <th style={{ width: '15%', textAlign: 'center' }}>Role</th>
                  <th style={{ width: '15%', textAlign: 'center' }}>Status</th>
                  <th style={{ width: '15%', textAlign: 'center' }}>Online Status</th>
                  <th style={{ width: '30%', textAlign: 'center' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {busy && (
                  <tr>
                    <td colSpan={5} className="empty-cell">
                      Loading...
                    </td>
                  </tr>
                )}

                {!busy &&
                  users.map((u) => {
                    const isAdmin = u.is_admin ?? u.role === 'admin';
                    const isActive = u.is_active ?? u.status === 'active';
                    const isOnline = !!u.online_status;

                    return (
                      <tr key={u.email}>
                        <td data-label="Email">{u.email}</td>
                        <td data-label="Role" style={{ textAlign: 'center' }}>
                          <span className={`badge ${isAdmin ? 'role-admin' : 'role-user'}`}>
                            {isAdmin ? 'Admin' : 'User'}
                          </span>
                        </td>
                        <td data-label="Status" style={{ textAlign: 'center' }}>
                          <span className={`badge ${isActive ? 'status-active' : 'status-inactive'}`}>
                            {isActive ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td data-label="Online Status" style={{ textAlign: 'center' }}>
                          <span className={`online-status ${isOnline ? 'online' : 'offline'}`} />
                          {isOnline ? 'Online' : 'Offline'}
                        </td>
                        <td className="actions-cell" data-label="Actions">
                          {u.email !== currentEmail ? (
                            <>
                              <button
                                type="button"
                                className={`action-btn ${isAdmin ? 'remove-admin' : 'make-admin'}`}
                                onClick={() => toggleRole(u.email)}
                              >
                                {isAdmin ? 'Remove Admin' : 'Make Admin'}
                              </button>
                              <button
                                type="button"
                                className={`action-btn ${isActive ? 'deactivate-user' : 'activate-user'}`}
                                onClick={() => toggleStatus(u.email)}
                              >
                                {isActive ? 'Deactivate' : 'Activate'}
                              </button>
                            </>
                          ) : (
                            <span>(You)</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}

                {!busy && users.length === 0 && (
                  <tr>
                    <td colSpan={5} className="empty-cell">
                      No users found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AdminLayout>
  );
}
