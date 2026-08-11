const TOKEN_KEY = 'token';

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem(TOKEN_KEY);
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function authGetJson<T>(path: string): Promise<T> {
  const res = await fetch(path, {
    method: 'GET',
    credentials: 'include',
    headers: { ...authHeaders() },
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
  const res = await fetch(path, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(),
    },
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

