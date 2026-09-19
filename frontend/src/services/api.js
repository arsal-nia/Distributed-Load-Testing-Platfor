const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001';
const API_TOKEN = import.meta.env.VITE_API_TOKEN || '';

async function request(path, options = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (API_TOKEN) {
    headers['Authorization'] = `Bearer ${API_TOKEN}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { ...headers, ...(options.headers || {}) },
  });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      if (body.detail) detail = body.detail;
    } catch { /* ignore */ }
    throw new Error(detail);
  }
  return res.json();
}

export const api = {
  listTests:     ()          => request('/api/tests'),
  getTest:       (id)        => request(`/api/tests/${id}`),
  getResults:    (id)        => request(`/api/tests/${id}/results`),
  createTest:    (payload)   => request('/api/tests',      { method: 'POST', body: JSON.stringify(payload) }),
  startTest:     (id)        => request(`/api/tests/${id}/start`, { method: 'POST' }),
  stopTest:      (id)        => request(`/api/tests/${id}/stop`,  { method: 'POST' }),
};
