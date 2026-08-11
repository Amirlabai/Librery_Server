import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './dashboard.css';
import { toastError, toastSuccess } from '../toast';
import { authGetJson, authPostJson } from '../authFetch';
import { downloadAuthenticated, previewAuthenticated } from '../api';
import { useAuth } from '../auth';
import { IconFile, IconFolder, IconHome, IconLightbulb, IconLink, IconMenu } from '../components/Icons';
import { useDarkMode } from '../useDarkMode';

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
  cooldown_level?: number;
};

type UsefulLink = {
  url: string;
  title: string;
  description: string;
  dir?: string;
};

function normalizePath(p: string): string {
  return (p || '').replace(/^\/+/, '').replace(/\/+$/, '');
}

function isFolderItem(item: BrowseItem): boolean {
  return !!(item.is_folder ?? item.isFolder);
}

function formatSize(bytes?: number): string {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${Math.round((bytes / k ** i) * 100) / 100} ${sizes[i]}`;
}

export default function DashboardPage() {
  const nav = useNavigate();
  const { user, logout } = useAuth();

  const [path, setPath] = useState('');
  const [allItems, setAllItems] = useState<BrowseItem[]>([]);
  const [isAdmin, setIsAdmin] = useState(false);
  const [cooldownLevel, setCooldownLevel] = useState(0);
  const [busy, setBusy] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFile, setSelectedFile] = useState<BrowseItem | null>(null);

  const [showCreateFolderModal, setShowCreateFolderModal] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');

  const [showDownloadWarning, setShowDownloadWarning] = useState(false);
  const [downloadItem, setDownloadItem] = useState<BrowseItem | null>(null);

  const [showEditPathModal, setShowEditPathModal] = useState(false);
  const [editedFilePath, setEditedFilePath] = useState('');
  const [oldPath, setOldPath] = useState('');
  const [editModalPath, setEditModalPath] = useState('');
  const [modalFolders, setModalFolders] = useState<BrowseItem[]>([]);

  const [showSuggestBox, setShowSuggestBox] = useState(false);
  const [suggestionText, setSuggestionText] = useState('');

  const [showUsefulLinksModal, setShowUsefulLinksModal] = useState(false);
  const [usefulLinks, setUsefulLinks] = useState<UsefulLink[]>([]);
  const [openMenuPath, setOpenMenuPath] = useState<string | null>(null);

  const searchTimer = useRef<number | null>(null);
  const isDarkMode = useDarkMode();

  useEffect(() => {
    if (!openMenuPath) return;
    function onDocClick() {
      setOpenMenuPath(null);
    }
    document.addEventListener('click', onDocClick);
    return () => document.removeEventListener('click', onDocClick);
  }, [openMenuPath]);

  const parentPath = useMemo(() => {
    const parts = normalizePath(path).split('/').filter(Boolean);
    parts.pop();
    return parts.join('/');
  }, [path]);

  const applyBrowseResponse = useCallback((res: BrowseResponse, cleanPath: string) => {
    const folders = res.folders || [];
    const files = res.files || [];
    setAllItems([...folders, ...files]);
    setPath(res.current_path || cleanPath);
    setIsAdmin(!!res.is_admin);
    if (res.cooldown_level !== undefined) setCooldownLevel(res.cooldown_level);
  }, []);

  const loadBrowse = useCallback(async (nextPath: string) => {
    const clean = normalizePath(nextPath);
    setBusy(true);
    try {
      const url = clean ? `/browse/${clean}` : '/browse';
      const res = await authGetJson<BrowseResponse>(url);
      applyBrowseResponse(res, clean);
    } catch (err: any) {
      toastError(err?.message || 'Failed to load files');
    } finally {
      setBusy(false);
      setIsSearching(false);
    }
  }, [applyBrowseResponse]);

  const executeSearch = useCallback(
    async (query: string) => {
      const trimmed = query.trim();
      if (!trimmed) {
        await loadBrowse(path);
        return;
      }

      setIsSearching(true);
      try {
        const q = encodeURIComponent(trimmed);
        const fp = encodeURIComponent(normalizePath(path));
        const res = await authGetJson<BrowseResponse>(`/search?q=${q}&folder_path=${fp}`);
        const folders = res.folders || [];
        const files = res.files || [];
        setAllItems([...folders, ...files]);
      } catch (err: any) {
        toastError(err?.message || 'Search failed');
      } finally {
        setIsSearching(false);
      }
    },
    [loadBrowse, path],
  );

  useEffect(() => {
    loadBrowse('');
  }, [loadBrowse]);

  useEffect(() => {
    if (searchTimer.current) window.clearTimeout(searchTimer.current);
    searchTimer.current = window.setTimeout(() => {
      executeSearch(searchQuery);
    }, 100);
    return () => {
      if (searchTimer.current) window.clearTimeout(searchTimer.current);
    };
  }, [searchQuery, executeSearch]);

  function navigateItem(item: BrowseItem) {
    if (isFolderItem(item)) {
      setPath(item.path);
      setSearchQuery('');
      loadBrowse(item.path);
    } else {
      setSelectedFile(item);
    }
  }

  async function onLogout() {
    await logout();
    nav('/login');
  }

  function navAdmin() {
    if (user?.role === 'admin') nav('/metrics');
  }

  function previewItem(item: BrowseItem, event: React.MouseEvent) {
    event.stopPropagation();
    if (isFolderItem(item)) return;
    previewAuthenticated(`/preview/${item.path}`).catch((err: any) => {
      toastError(err?.message || 'Preview failed');
    });
  }

  function openDownloadWarning(item: BrowseItem, event: React.MouseEvent) {
    event.stopPropagation();
    setDownloadItem(item);
    setShowDownloadWarning(true);
  }

  function confirmDownload(event: React.MouseEvent) {
    event.stopPropagation();
    if (!downloadItem) return;
    const kind = isFolderItem(downloadItem) ? 'folder' : 'file';
    const fallback = isFolderItem(downloadItem) ? `${downloadItem.name}.zip` : downloadItem.name;
    downloadAuthenticated(`/download/${kind}/${downloadItem.path}`, fallback).catch((err: any) => {
      toastError(err?.message || 'Download failed');
    });
    setShowDownloadWarning(false);
    setDownloadItem(null);
  }

  async function onDelete(item: BrowseItem, event: React.MouseEvent) {
    event.stopPropagation();
    if (!isAdmin) return;
    if (!confirm(`Delete "${item.name}"?`)) return;

    const current = path;
    try {
      await authPostJson(`/delete/${item.path}`, {});
      toastSuccess('Deleted successfully');
      await loadBrowse(current);
    } catch (err: any) {
      toastError(err?.message || 'Delete failed');
    }
  }

  async function createFolder() {
    const name = newFolderName.trim();
    if (!name) {
      toastError('Folder name cannot be empty.');
      return;
    }

    try {
      await authPostJson('/create_folder', {
        parent_path: normalizePath(path),
        folder_name: name,
      });
      toastSuccess('Folder created');
      setShowCreateFolderModal(false);
      setNewFolderName('');
      await loadBrowse(path);
    } catch (err: any) {
      toastError(err?.message || 'Failed to create folder');
    }
  }

  async function submitSuggestion(e: React.FormEvent) {
    e.preventDefault();
    const text = suggestionText.trim();
    if (!text) {
      toastError('Suggestion cannot be empty');
      return;
    }

    try {
      await authPostJson('/suggest', { suggestion: text });
      toastSuccess('Suggestion submitted');
      setSuggestionText('');
      setShowSuggestBox(false);
    } catch (err: any) {
      toastError(err?.message || 'Failed to submit suggestion');
    }
  }

  async function loadFoldersForModal(folderPath: string) {
    const clean = normalizePath(folderPath);
    try {
      const url = clean ? `/browse/${clean}` : '/browse';
      const res = await authGetJson<BrowseResponse>(url);
      setModalFolders(res.folders || []);
      setEditModalPath(res.current_path || clean);
    } catch (err: any) {
      toastError(err?.message || 'Failed to load folders');
    }
  }

  function openEditPathModal(item: BrowseItem, event: React.MouseEvent) {
    event.stopPropagation();
    setSelectedFile(item);
    setOldPath(item.path);
    setEditedFilePath(item.path);
    setShowEditPathModal(true);
    loadFoldersForModal('');
  }

  async function editFilePath() {
    if (!selectedFile?.upload_id) {
      toastError('No file selected.');
      return;
    }

    try {
      await authPostJson('/admin/edit_upload_path/', {
        upload_id: selectedFile.upload_id,
        new_path: editedFilePath,
        oldPath,
      });
      toastSuccess('Path updated successfully');
      setShowEditPathModal(false);
      await loadBrowse(path);
    } catch (err: any) {
      toastError(err?.message || 'Failed to update path');
    }
  }

  function openFolderInModal(folder: BrowseItem) {
    const next = normalizePath(folder.path);
    loadFoldersForModal(next);
    if (selectedFile?.name) {
      setEditedFilePath(next ? `/${next}/${selectedFile.name}` : `/${selectedFile.name}`);
    }
  }

  function goBackInModal() {
    const parts = editModalPath.split('/').filter(Boolean);
    parts.pop();
    const up = parts.join('/');
    loadFoldersForModal(up);
    if (selectedFile?.name) {
      setEditedFilePath(up ? `/${up}/${selectedFile.name}` : `/${selectedFile.name}`);
    }
  }

  async function loadUsefulLinks() {
    try {
      const links = await authGetJson<UsefulLink[]>('/useful_links');
      setUsefulLinks(Array.isArray(links) ? links : []);
    } catch {
      setUsefulLinks([]);
    }
  }

  function openUsefulLinksModal() {
    setShowUsefulLinksModal(true);
    loadUsefulLinks();
  }

  const loading = busy || isSearching;

  return (
    <div className="page-root">
      <div className="container">
        <div className="intro-header" />

        <header className="header">
          <div className="header-left">
            <div className="logo header-logo">
              <img
                src={isDarkMode ? '/assets/icons/banner-logo-dark-mode.webp' : '/assets/icons/banner-logo.webp'}
                alt="Merkaz"
              />
            </div>
            {user?.fullName && <span className="user-name">Welcome, {user.fullName}</span>}
          </div>

          <div className="header-right">
            <Link to="/dashboard/my-uploads" className="my-uploads-btn">
              My Uploads
            </Link>
            <Link to={`/dashboard/upload?path=${encodeURIComponent(normalizePath(path))}`} className="upload-btn">
              Upload File
            </Link>
            {isAdmin && (
              <button type="button" onClick={navAdmin} className="admin-dashboard-btn">
                Admin Dashboard
              </button>
            )}
            <button type="button" onClick={onLogout} className="logout-btn">
              Logout
            </button>
          </div>
        </header>

        <div className="path-bar">
          <button type="button" className="home-link" onClick={() => { setSearchQuery(''); loadBrowse(''); }} aria-label="Home">
            <IconHome className="shell-icon" />
          </button>

          {isAdmin && (
            <>
              <div className="create-folder-wrapper">
                <button type="button" onClick={() => setShowCreateFolderModal(true)} className="create-folder-btn">
                  Create Folder
                </button>
              </div>
              <input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search files"
                className="search-items"
                aria-label="Search files"
              />
            </>
          )}

          {normalizePath(path) && (
            <div className="back-btn-wrapper">
              <button
                type="button"
                className="backPathButton"
                onClick={() => {
                  setSearchQuery('');
                  setPath(parentPath);
                  loadBrowse(parentPath);
                }}
              >
                Back
              </button>
              <span className="pathFolders">{normalizePath(path) || '/'}</span>
            </div>
          )}
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th style={{ width: 70, textAlign: 'center' }}>Size</th>
                <th style={{ width: 168, textAlign: 'center' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr>
                  <td colSpan={3} style={{ textAlign: 'center', padding: 20 }}>
                    Loading...
                  </td>
                </tr>
              )}

              {!loading &&
                allItems.map((item) => (
                  <tr
                    key={item.path}
                    className={selectedFile?.path === item.path ? 'selected-row' : undefined}
                    onClick={() => navigateItem(item)}
                  >
                    <td data-label="Name">
                      <div className="item-name">
                        {isFolderItem(item) ? <IconFolder /> : <IconFile />}
                        <span>{isFolderItem(item) ? `${item.name}/` : item.name}</span>
                      </div>
                    </td>
                    <td data-label="Size" style={{ textAlign: 'center' }}>
                      <span>{formatSize(item.size)}</span>
                    </td>
                    <td data-label="Actions" style={{ textAlign: 'center' }}>
                      <div className="action-cell" onClick={(e) => e.stopPropagation()}>
                        {!isFolderItem(item) && (
                          <button type="button" onClick={(e) => previewItem(item, e)} className="action-btn preview-btn">
                            Preview
                          </button>
                        )}
                        <button
                          type="button"
                          onClick={(e) => openDownloadWarning(item, e)}
                          className="action-btn download-btn"
                        >
                          Download
                        </button>
                        {isAdmin && (
                          <div className={`row-menu${openMenuPath === item.path ? ' is-open' : ''}`}>
                            <button
                              type="button"
                              className="row-menu-trigger"
                              aria-label={`More actions for ${item.name}`}
                              aria-expanded={openMenuPath === item.path}
                              onClick={(e) => {
                                e.stopPropagation();
                                setOpenMenuPath((current) => (current === item.path ? null : item.path));
                              }}
                            >
                              <IconMenu size={18} />
                            </button>
                            {openMenuPath === item.path && (
                              <div className="row-menu-panel" role="menu">
                                {!isFolderItem(item) && (
                                  <button
                                    type="button"
                                    role="menuitem"
                                    className="row-menu-item"
                                    onClick={(e) => {
                                      setOpenMenuPath(null);
                                      openEditPathModal(item, e);
                                    }}
                                  >
                                    Edit path
                                  </button>
                                )}
                                <button
                                  type="button"
                                  role="menuitem"
                                  className="row-menu-item row-menu-item--danger"
                                  onClick={(e) => {
                                    setOpenMenuPath(null);
                                    onDelete(item, e);
                                  }}
                                >
                                  Delete
                                </button>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}

              {!loading && allItems.length === 0 && (
                <tr>
                  <td colSpan={3} style={{ textAlign: 'center', color: 'var(--placeholder-color)', padding: 30 }}>
                    This folder is empty.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {showCreateFolderModal && (
          <div className="modal-overlay" onClick={() => setShowCreateFolderModal(false)} role="presentation">
            <div className="modal-content" onClick={(e) => e.stopPropagation()} role="dialog" aria-labelledby="create-folder-title">
              <div className="modal-header">
                <h2 id="create-folder-title">Create New Folder</h2>
                <button type="button" className="modal-close" onClick={() => setShowCreateFolderModal(false)} aria-label="Close">
                  ×
                </button>
              </div>
              <div className="modal-body">
                <label htmlFor="folderName">Folder Name:</label>
                <input
                  type="text"
                  id="folderName"
                  value={newFolderName}
                  onChange={(e) => setNewFolderName(e.target.value)}
                  placeholder="Enter folder name..."
                  onKeyDown={(e) => e.key === 'Enter' && createFolder()}
                  autoFocus
                />
                <div className="modal-actions">
                  <button type="button" onClick={createFolder} className="create-btn">
                    Create
                  </button>
                  <button type="button" onClick={() => setShowCreateFolderModal(false)} className="cancel-btn">
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {showEditPathModal && (
          <div className="edit-modal-overlay" onClick={() => setShowEditPathModal(false)} role="presentation">
            <div className="edit-modal-content" onClick={(e) => e.stopPropagation()} role="dialog" aria-labelledby="edit-path-title">
              <div className="edit-modal-header">
                <h2 id="edit-path-title">Edit file path</h2>
                <button type="button" className="edit-modal-close" onClick={() => setShowEditPathModal(false)} aria-label="Close">
                  ×
                </button>
              </div>
              <div className="edit-modal-body">
                <label htmlFor="newFilePath">New File Path:</label>
                <input
                  type="text"
                  id="newFilePath"
                  value={editedFilePath}
                  onChange={(e) => setEditedFilePath(e.target.value)}
                  readOnly
                  onKeyDown={(e) => e.key === 'Enter' && editFilePath()}
                />
                <div className="edit-modal-actions">
                  <button type="button" onClick={editFilePath} className="edit-update-btn">
                    Update
                  </button>
                  <button type="button" onClick={() => setShowEditPathModal(false)} className="edit-cancel-btn">
                    Cancel
                  </button>
                </div>

                <div className="edit-left-side">
                  <h3>Your folders</h3>
                  <p className="path-display">{editModalPath || '/'}</p>
                  <div className="folders-content">
                    <ul>
                      {modalFolders.map((folder) => (
                        <li key={folder.path} className="folder-item">
                          <button type="button" className="openFolderInModalBtn" onClick={() => openFolderInModal(folder)}>
                            {folder.name}
                          </button>
                        </li>
                      ))}
                      {modalFolders.length === 0 && <li className="no-folders">This folder is empty.</li>}
                    </ul>
                  </div>
                  <button type="button" className="edit-back-btn" onClick={goBackInModal}>
                    Back
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {showDownloadWarning && (
          <div className="modal-overlay" onClick={() => setShowDownloadWarning(false)} role="presentation">
            <div className="modal-content" onClick={(e) => e.stopPropagation()} role="dialog" aria-labelledby="download-warning-title">
              <div className="modal-header">
                <h2 id="download-warning-title">Warning</h2>
                <button type="button" className="modal-close" onClick={() => setShowDownloadWarning(false)} aria-label="Close">
                  ×
                </button>
              </div>
              <div className="modal-body">
                <p>
                  This file may pose security risks. Make sure it comes from a trusted source before downloading.
                  <br />
                  <br />
                  Proceed?
                </p>
                <div className="modal-actions">
                  <button type="button" onClick={confirmDownload} className="create-btn">
                    Continue
                  </button>
                  <button type="button" onClick={() => setShowDownloadWarning(false)} className="cancel-btn">
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {showSuggestBox && (
          <div className="suggestion-box-modal-overlay" onClick={() => setShowSuggestBox(false)} role="presentation">
            <div className="suggestion-box-content" onClick={(e) => e.stopPropagation()} role="dialog">
              <div className="suggestion-box-header">
                <h2>Write to us</h2>
                <p className="cooldownLevel">(Cooldown: Level {cooldownLevel})</p>
                <form onSubmit={submitSuggestion}>
                  <textarea
                    value={suggestionText}
                    onChange={(e) => setSuggestionText(e.target.value)}
                    className="suggestion-text-area"
                    rows={4}
                    placeholder="Type your suggestion here..."
                    required
                  />
                  <button type="submit">Submit Suggestion</button>
                </form>
              </div>
            </div>
          </div>
        )}

        {showUsefulLinksModal && (
          <div className="suggestion-box-modal-overlay" onClick={() => setShowUsefulLinksModal(false)} role="presentation">
            <div
              className="suggestion-box-content useful-links-content useful-links-modal"
              onClick={(e) => e.stopPropagation()}
              role="dialog"
            >
              <div className="suggestion-box-header">
                <h2>Useful Links</h2>
                <div className="useful-links-list">
                  {usefulLinks.map((link) => (
                    <div key={link.url} className="useful-link-item">
                      <a href={link.url} target="_blank" rel="noopener noreferrer" className="useful-link">
                        <span className="link-title" dir={link.dir || undefined}>
                          {link.title}
                        </span>
                        <span className="link-description" dir={link.dir || undefined}>
                          {link.description}
                        </span>
                      </a>
                    </div>
                  ))}
                  {usefulLinks.length === 0 && (
                    <div style={{ textAlign: 'center', padding: 20, color: 'var(--placeholder-color)' }}>
                      Loading links...
                    </div>
                  )}
                </div>
                <button type="button" onClick={() => setShowUsefulLinksModal(false)} className="close-links-btn">
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        <footer>
          <button
            type="button"
            className={`suggestion-group useful-links-group${showUsefulLinksModal ? ' lightbulb-active' : ''}`}
            onClick={openUsefulLinksModal}
          >
            <span className="lightbulb-wrapper">
              <IconLink className="shell-icon" />
            </span>
            <span className="suggest-text">Useful links</span>
          </button>

          <button
            type="button"
            className={`suggestion-group report-bug-group${showSuggestBox ? ' lightbulb-active' : ''}`}
            onClick={() => setShowSuggestBox(true)}
          >
            <span className="suggest-text">Report Bug/Help</span>
            <span className="lightbulb-wrapper">
              <IconLightbulb className="shell-icon" />
            </span>
          </button>
        </footer>
      </div>
    </div>
  );
}
