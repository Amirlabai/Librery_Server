const BACKEND_URL_KEY = 'api_backend_url';
const TOKEN_KEY = 'token';

function hasWindow(): boolean {
  return typeof window !== 'undefined';
}

export function getBackendUrl(): string {
  const fromEnv = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim();
  if (fromEnv) return fromEnv.replace(/\/+$/, '');

  if (!hasWindow()) return 'http://localhost:8000';

  const storedUrl = localStorage.getItem(BACKEND_URL_KEY);
  if (storedUrl) return storedUrl.replace(/\/+$/, '');

  // Relative URLs: Vite proxy (dev) or Flask serving client/dist.
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

/** Build absolute or relative API URL from a path. */
export function apiUrl(path: string): string {
  const base = getBackendUrl();
  const p = path.startsWith('/') ? path : `/${path}`;
  return base ? `${base}${p}` : p;
}

export function apiHeaders(extra?: HeadersInit): Record<string, string> {
  const headers: Record<string, string> = {
    'ngrok-skip-browser-warning': 'true',
  };
  if (extra) {
    const h = new Headers(extra);
    h.forEach((v, k) => {
      headers[k] = v;
    });
  }
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

async function requestJson<T>(path: string, init: RequestInit): Promise<T> {
  const res = await fetch(apiUrl(path), {
    credentials: 'include',
    ...init,
    headers: apiHeaders(init.headers),
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
    xhr.open('POST', apiUrl('/upload'), true);
    xhr.withCredentials = true;

    const headers = apiHeaders();
    Object.entries(headers).forEach(([k, v]) => xhr.setRequestHeader(k, v));

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

function filenameFromDisposition(header: string | null, fallback: string): string {
  if (!header) return fallback;
  const utf = /filename\*=UTF-8''([^;]+)/i.exec(header);
  if (utf?.[1]) {
    try {
      return decodeURIComponent(utf[1]);
    } catch {
      /* ignore */
    }
  }
  const plain = /filename="?([^";]+)"?/i.exec(header);
  return plain?.[1]?.trim() || fallback;
}

/** Authenticated GET → trigger browser download (Vercel → ngrok safe). */
export async function downloadAuthenticated(path: string, fallbackName: string): Promise<void> {
  const res = await fetch(apiUrl(path), {
    method: 'GET',
    credentials: 'include',
    headers: apiHeaders(),
  });
  if (!res.ok) {
    let body: any = null;
    try {
      body = await res.json();
    } catch {
      /* ignore */
    }
    throw new Error(body?.error || `Download failed (${res.status})`);
  }
  const blob = await res.blob();
  const name = filenameFromDisposition(res.headers.get('Content-Disposition'), fallbackName);
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

/** Authenticated GET → open blob in a new tab for preview. */
export async function previewAuthenticated(path: string): Promise<void> {
  const res = await fetch(apiUrl(path), {
    method: 'GET',
    credentials: 'include',
    headers: apiHeaders(),
  });
  if (!res.ok) {
    let body: any = null;
    try {
      body = await res.json();
    } catch {
      /* ignore */
    }
    throw new Error(body?.error || `Preview failed (${res.status})`);
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  window.open(url, '_blank');
  window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
}

