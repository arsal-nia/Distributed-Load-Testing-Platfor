import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';

export default function CreateTest() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    target_url: 'http://target-service:8000/fast',
    requests: 100,
    concurrency: 10,
    workers: 1,
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const update = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const payload = {
        target_url: form.target_url,
        requests: parseInt(form.requests, 10),
        concurrency: parseInt(form.concurrency, 10),
        workers: parseInt(form.workers, 10),
      };
      const created = await api.createTest(payload);
      await api.startTest(created.test_id);
      navigate(`/tests/${created.test_id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <h1>Create Load Test</h1>
      {error && <div className="error">{error}</div>}
      <form onSubmit={submit} className="card" style={{ maxWidth: 500 }}>
        <label>Target URL</label>
        <input value={form.target_url} onChange={update('target_url')} required />

        <label>Number of Requests</label>
        <input type="number" min="1" value={form.requests} onChange={update('requests')} required />

        <label>Concurrency</label>
        <input type="number" min="1" value={form.concurrency} onChange={update('concurrency')} required />

        <label>Workers</label>
        <input type="number" min="1" value={form.workers} onChange={update('workers')} required />

        <button type="submit" disabled={submitting}>
          {submitting ? 'Starting...' : 'Create & Start'}
        </button>
      </form>
    </>
  );
}