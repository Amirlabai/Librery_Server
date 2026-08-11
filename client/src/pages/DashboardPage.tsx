import React, { useEffect, useMemo, useState } from 'react';
import './dashboard.css';
import { toastError, toastSuccess } from '../toast';
import { authGetJson, authPostJson } from '../authFetch';

type BrowseItem = {
  upload_id?: string;
  name: string;
  path: string;
  has_files?: boolean;
  size?: number;
  is_folder?: boolean;
  isFolder?: boolean;
};

type BrowseResponse = {
  files: BrowseItem[];
  folders: BrowseItem[];
  current_path: string;
  is_admin: boolean;
};

function normalizePath(p: string): string {
  return (p || '').replace(/^\/+/, '').replace(/\/+$/, '');
}

export default function DashboardPage() {
  const [path, setPath] = useState('');
  const [data, setData] = useState<BrowseResponse>({
    files: [],
    folders: [],
    current_path: '',
    is_admin: false,
  });
  const [busy, setBusy] = useState(false);

  const [createFolderName, setCreateFolderName] = useState('');
  const [suggestion, setSuggestion] = useState('');

  const parentPath = useMemo(() => {
    const parts = normalizePath(path).split('/').filter(Boolean);
    parts.pop();
    return parts.join('/');
  }, [path]);

  async function loadBrowse(nextPath: string) {
    const clean = normalizePath(nextPath);
    setBusy(true);
    try {
      const url = clean ? `/browse/${clean}` : '/browse';
      const res = await authGetJson<BrowseResponse>(url);
      setData({
        files: res.files || [],
        folders: res.folders || [],
        current_path: res.current_path || clean,
        is_admin: !!res.is_admin,
      });
    } catch (err: any) {
      toastError(err?.message || 'Failed to load files');
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    loadBrowse(path);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function onDelete(itemPath: string) {
    if (!data.is_admin) return;
    if (!confirm(`Delete "${itemPath}" ?`)) return;

    try {
      await authPostJson(`/delete/${itemPath}`, {});
      toastSuccess('Deleted');
      await loadBrowse(path);
    } catch (err: any) {
      toastError(err?.message || 'Delete failed');
    }
  }

  async function onCreateFolder() {
    if (!data.is_admin) return;
    const name = createFolderName.trim();
    if (!name) return;

    try {
      await authPostJson('/create_folder', { parent_path: normalizePath(path), folder_name: name });
      toastSuccess('Folder created');
      setCreateFolderName('');
      await loadBrowse(path);
    } catch (err: any) {
      toastError(err?.message || 'Failed to create folder');
    }
  }

  async function onSubmitSuggestion() {
    if (!data.is_admin) {
      // backend doesn't require admin, but keeping UX consistent for now.
    }
    const s = suggestion.trim();
    if (!s) return;
    try {
      await authPostJson('/suggest', { suggestion: s });
      toastSuccess('Suggestion submitted');
      setSuggestion('');
    } catch (err: any) {
      toastError(err?.message || 'Failed to submit suggestion');
    }
  }

  function downloadItem(item: BrowseItem) {
    const isFolder = item.is_folder ?? item.isFolder ?? false;
    const kind = isFolder ? 'folder' : 'file';
    window.open(`/download/${kind}/${item.path}`, '_blank');
  }

  function previewItem(item: BrowseItem) {
    const isFolder = item.is_folder ?? item.isFolder ?? false;
    if (isFolder) return;
    window.open(`/preview/${item.path}`, '_blank');
  }

  return (
    <div style={{ padding: 16 }}>
      <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 14 }}>
        <h2 style={{ margin: 0 }}>Dashboard</h2>
        <div style={{ flex: 1, opacity: 0.85, fontSize: 12 }}>
          Path: <span>{normalizePath(path) || '/'}</span>
        </div>
        {normalizePath(path) && (
          <button
            disabled={busy}
            onClick={() => {
              const next = parentPath;
              setPath(next);
              loadBrowse(next);
            }}
          >
            Back
          </button>
        )}
        <button disabled={busy} onClick={() => loadBrowse(path)}>
          Refresh
        </button>
      </div>

      {data.is_admin && (
        <div
          style={{
            display: 'flex',
            gap: 10,
            flexWrap: 'wrap',
            marginBottom: 18,
            padding: 12,
            borderRadius: 12,
            background: 'rgba(0,0,0,0.03)',
          }}
        >
          <input
            value={createFolderName}
            onChange={(e) => setCreateFolderName(e.target.value)}
            placeholder="New folder name"
          />
          <button disabled={busy} onClick={onCreateFolder}>
            Create folder
          </button>
        </div>
      )}

      {!data.is_admin && (
        <div style={{ marginBottom: 18, opacity: 0.9 }}>
          <h3 style={{ margin: '0 0 8px' }}>Suggestion</h3>
          <div style={{ display: 'flex', gap: 10 }}>
            <input value={suggestion} onChange={(e) => setSuggestion(e.target.value)} placeholder="Write a suggestion" />
            <button disabled={busy} onClick={onSubmitSuggestion}>
              Send
            </button>
          </div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 10 }}>
        {busy && <div>Loading...</div>}

        {!busy && data.folders.length === 0 && data.files.length === 0 && <div>No items.</div>}

        {data.folders.map((f) => (
          <div
            key={f.path}
            style={{
              display: 'flex',
              gap: 12,
              justifyContent: 'space-between',
              padding: 12,
              borderRadius: 12,
              background: 'rgba(0,0,0,0.03)',
            }}
          >
            <div>
              <div style={{ fontWeight: 600 }}>{f.name}</div>
              <div style={{ fontSize: 12, opacity: 0.75 }}>{normalizePath(f.path) || ''}</div>
            </div>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <button
                disabled={busy}
                onClick={() => {
                  setPath(f.path);
                  loadBrowse(f.path);
                }}
              >
                Open
              </button>
              <button disabled={busy} onClick={() => downloadItem(f)}>
                Download
              </button>
              {data.is_admin && (
                <button disabled={busy} onClick={() => onDelete(f.path)}>
                  Delete
                </button>
              )}
            </div>
          </div>
        ))}

        {data.files.map((f) => (
          <div
            key={f.path}
            style={{
              display: 'flex',
              gap: 12,
              justifyContent: 'space-between',
              padding: 12,
              borderRadius: 12,
              background: 'rgba(0,0,0,0.03)',
            }}
          >
            <div>
              <div style={{ fontWeight: 600 }}>{f.name}</div>
              <div style={{ fontSize: 12, opacity: 0.75 }}>{normalizePath(f.path) || ''}</div>
            </div>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <button disabled={busy} onClick={() => previewItem(f)}>
                Preview
              </button>
              <button disabled={busy} onClick={() => downloadItem(f)}>
                Download
              </button>
              {data.is_admin && (
                <button disabled={busy} onClick={() => onDelete(f.path)}>
                  Delete
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

