import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import StatusBadge from '../components/StatusBadge';

export default function TestDetail() {
  const { id } = useParams();
  const [status, setStatus] = useState(null);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const s = await api.getTest(id);
        if (cancelled) return;
        setStatus(s);

        if (s.status === 'COMPLETED' || s.status === 'STOPPED' || s.status === 'FAILED') {
          try {
            const r = await api.getResults(id);
            if (!cancelled) setResults(r);
          } catch { /* results not yet persisted */ }
        }
      } catch (e) {
        if (!cancelled) setError(e.message);
      }
    }
    load();
    const t = setInterval(load, 2000);
    return () => { cancelled = true; clearInterval(t); };
  }, [id]);

  async function stop() {
    try { await api.stopTest(id); } catch (e) { alert(e.message); }
  }

  if (error) return <div className="error">{error}</div>;
  if (!status) return <div className="empty">Loading...</div>;

  const maxLatency = results
    ? Math.max(results.p99_latency_ms || 1, 1)
    : 1;

  return (
    <>
      <Link to="/">&larr; Back to Dashboard</Link>
      <h1 style={{ marginTop: 12 }}>{id}</h1>
      <p style={{ margin: '8px 0 16px' }}><StatusBadge status={status.status} /></p>

      {status.status === 'RUNNING' && (
        <button className="danger" onClick={stop}>Stop Test</button>
      )}

      {results && (
        <>
          <div className="stats">
            <div className="stat"><div className="value">{results.total_requests}</div><div className="label">Total</div></div>
            <div className="stat"><div className="value" style={{ color: '#059669' }}>{results.successful_requests}</div><div className="label">Successful</div></div>
            <div className="stat"><div className="value" style={{ color: '#dc2626' }}>{results.failed_requests}</div><div className="label">Failed</div></div>
            <div className="stat"><div className="value">{results.requests_per_second.toFixed(1)}</div><div className="label">Req/s</div></div>
          </div>

          <div className="card">
            <h3>Latency (ms)</h3>
            <div className="latency-bar">
              <div className="bar-label">Min: {results.average_latency_ms.toFixed(1)} | Avg: {results.average_latency_ms.toFixed(1)}</div>
            </div>
            {[
              ['P50', results.p50_latency_ms],
              ['P95', results.p95_latency_ms],
              ['P99', results.p99_latency_ms],
            ].map(([label, value]) => (
              <div key={label} className="latency-bar">
                <div className="bar-label">{label}: {value.toFixed(2)} ms</div>
                <div className="bar-bg">
                  <div className="bar-fill" style={{ width: `${(value / maxLatency) * 100}%` }} />
                </div>
              </div>
            ))}
          </div>

          <div className="card">
            <h3>Summary</h3>
            <p>Error rate: <strong>{(results.error_rate * 100).toFixed(2)}%</strong></p>
          </div>
        </>
      )}
    </>
  );
}