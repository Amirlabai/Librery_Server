const BACKEND_URL_KEY = 'api_backend_url';
const TOKEN_KEY = 'token';

function hasWindow(): boolean {
  return typeof window !== 'undefined';
}

export function getBackendUrl(): string {
  if (!hasWindow()) return 'http://localhost:8000';

  const storedUrl = localStorage.getItem(BACKEND_URL_KEY);
  if (storedUrl) return storedUrl;

  // When running in dev (Vite) we rely on the dev-server proxy for same-origin calls.
  // So we prefer relative URLs (base URL = "") unless explicitly configured.
  const hostname = window.location.hostname;
  const port = window.location.port;

  // If we are directly on Flask (port 8000), keep relative URLs.
  if (port === '8000' || (hostname === 'localhost' && port === '')) return '';

  // Default: use relative URLs and let Vite proxy forward to Flask.
  return '';
}

export function setBackendUrl(url: string): void {
  localStorage.setItem(BACKEND_URL_KEY, url);
}

export function clearBackendUrl(): void {
  localStorage.removeItem(BACKEND_URL_KEY);
}

function getToken(): string | null {
  if (!hasWindow()) return null;
  return localStorage.getItem(TOKEN_KEY);
}

function buildUrl(path: string): string {
  const base = getBackendUrl();
  if (!base) return path.startsWith('/') ? path : `/${path}`;
  return `${base}${path.startsWith('/') ? '' : '/'}${path}`;
}

async function requestJson<T>(path: string, init: RequestInit): Promise<T> {
  const res = await fetch(buildUrl(path), {
    credentials: 'include',
    ...init,
    headers: {
      ...(init.headers || {}),
      ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {}),
    },
  });

  if (!res.ok) {
    // Best-effort JSON extraction (backend returns {error: "..."}).
    let body: any = null;
    try {
      body = await res.json();
    } catch {
      body = null;
    }
    const err = new Error(body?.error || `Request failed with ${res.status}`);
    (err as any).status = res.status;
    (err as any).body = body;
    throw err;
  }

  return (await res.json()) as T;
}

export interface LoginResponse {
  token?: string;
  role?: string;
  full_name?: string;
  message?: string;
  error?: string;
}

export interface RegisterResponse {
  message?: string;
  error?: string;
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  return requestJson<LoginResponse>('/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: email.trim(), password: password.trim() }),
  });
}

export async function register(first_name: string, last_name: string, email: string, password: string) {
  return requestJson<RegisterResponse>('/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ first_name, last_name, email: email.trim(), password: password.trim() }),
  });
}

export async function resetPass(token: string, password: string): Promise<{ message?: string; error?: string }> {
  return requestJson('/reset-password/' + encodeURIComponent(token), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  });
}

export async function refreshSession(): Promise<any> {
  return requestJson('/refresh-session', { method: 'GET' });
}

export async function logout(): Promise<any> {
  return requestJson('/logout', { method: 'POST' });
}

export interface UploadProgressEvent {
  currentFile: string;
  currentFileIndex: number; // 1-based
  totalFiles: number;
  completedFiles: number;
  successfulFiles: number;
  failedFiles: number;
  progress: number; // 0..100
  bytesUploaded: number;
  totalBytes: number;
  currentFileProgress: number;
  isUploading: boolean;
}

export interface UploadFilesResult {
  successful: string[];
  failed: Array<{ fileName: string; error: any }>;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function uploadSingleFileXHR(
  file: File,
  subpath: string,
  onFileProgress: (loaded: number, total: number) => void,
): Promise<any> {
  return new Promise((resolve, reject) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('subpath', subpath);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', buildUrl('/upload'), true);
    xhr.withCredentials = true;

    const token = getToken();
    if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`);

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        onFileProgress(e.loaded, e.total);
      } else {
        onFileProgress(e.loaded, 0);
      }
    };

    xhr.onload = () => {
      const raw = xhr.responseText;
      let body: any = null;
      try {
        body = raw ? JSON.parse(raw) : null;
      } catch {
        body = raw;
      }

      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(body);
        return;
      }

      const err: any = new Error(body?.error || `Upload failed (${xhr.status})`);
      err.status = xhr.status;
      err.body = body;
      reject(err);
    };

    xhr.onerror = () => {
      const err: any = new Error('Network error during upload');
      err.status = 0;
      reject(err);
    };

    xhr.send(formData);
  });
}

export async function uploadFiles(
  files: File[],
  subpath: string,
  onProgress: (event: UploadProgressEvent) => void,
  retryCount: number = 3,
): Promise<UploadFilesResult> {
  const totalFiles = files.length;
  const totalBytes = files.reduce((sum, f) => sum + f.size, 0);

  let completedFiles = 0;
  let successfulCount = 0;
  let failedCount = 0;
  const successfulFiles: string[] = [];
  const failedFiles: Array<{ fileName: string; error: any }> = [];

  let bytesUploadedCompleted = 0; // completed files contribute full size

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    let currentFileBytesUploaded = 0;

    const pushProgress = (loaded: number, total: number, isUploading: boolean) => {
      currentFileBytesUploaded = loaded;

      const overallBytes = bytesUploadedCompleted + loaded;
      const overallProgress =
        totalBytes > 0
          ? Math.round((overallBytes / totalBytes) * 100)
          : Math.round((completedFiles / Math.max(totalFiles, 1)) * 100);

      const currentFileProgress = total > 0 ? Math.round((loaded / total) * 100) : 0;

      onProgress({
        currentFile: file.name,
        currentFileIndex: i + 1,
        totalFiles,
        completedFiles,
        successfulFiles: successfulCount,
        failedFiles: failedCount,
        progress: overallProgress,
        bytesUploaded: overallBytes,
        totalBytes,
        currentFileProgress,
        isUploading,
      });
    };

    // Emit an initial snapshot for this file.
    pushProgress(0, file.size, true);

    let attempt = 0;
    let lastErr: any = null;

    while (attempt < retryCount) {
      try {
        const resp = await uploadSingleFileXHR(file, subpath, (loaded, total) => {
          pushProgress(loaded, total, true);
        });

        const ok = !!resp?.successful_uploads && Array.isArray(resp.successful_uploads) && resp.successful_uploads.length > 0;
        if (ok) {
          successfulFiles.push(...resp.successful_uploads);
          successfulCount = successfulFiles.length;
        } else {
          failedFiles.push({
            fileName: file.name,
            error: resp?.error || 'Upload failed',
          });
          failedCount = failedFiles.length;
        }

        // XHR finished, so the backend consumed the request body.
        bytesUploadedCompleted += file.size;
        completedFiles++;

        pushProgress(file.size, file.size, false);
        break;
      } catch (err: any) {
        lastErr = err;

        const status: number = typeof err?.status === 'number' ? err.status : 0;
        const isRetryable = !status || status === 0 || status >= 500;

        attempt++;
        if (!isRetryable || attempt >= retryCount) {
          // Treat as final failure (no bytes added, since we consider request incomplete).
          failedFiles.push({
            fileName: file.name,
            error: err?.body?.error || err?.message || err,
          });
          failedCount = failedFiles.length;
          completedFiles++;
          onProgress({
            currentFile: file.name,
            currentFileIndex: i + 1,
            totalFiles,
            completedFiles,
            successfulFiles: successfulCount,
            failedFiles: failedCount,
            progress: totalBytes > 0 ? Math.round((bytesUploadedCompleted / totalBytes) * 100) : 0,
            bytesUploaded: bytesUploadedCompleted,
            totalBytes,
            currentFileProgress: Math.round((currentFileBytesUploaded / Math.max(file.size, 1)) * 100),
            isUploading: false,
          });
          break;
        }

        // Exponential-ish backoff (matches Angular's "1000 * ..." feel).
        await sleep(1000 * attempt);
      }
    }

    if (lastErr && attempt >= retryCount) {
      // Already pushed failure state above; continue to next file.
    }
  }

  return { successful: successfulFiles, failed: failedFiles };
}

