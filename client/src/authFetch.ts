import { apiHeaders, apiUrl } from './api';

export async function authGetJson<T>(path: string): Promise<T> {
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
      // ignore
    }
    throw new Error(body?.error || `Request failed (${res.status})`);
  }

  return (await res.json()) as T;
}

export async function authPostJson<T>(path: string, body: any): Promise<T> {
  const res = await fetch(apiUrl(path), {
    method: 'POST',
    credentials: 'include',
    headers: apiHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(body ?? {}),
  });

  if (!res.ok) {
    let err: any = null;
    try {
      err = await res.json();
    } catch {
      // ignore
    }
    throw new Error(err?.error || `Request failed (${res.status})`);
  }

  return (await res.json()) as T;
}
