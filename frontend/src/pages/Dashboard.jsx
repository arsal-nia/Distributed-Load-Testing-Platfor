import { Link } from 'react-router-dom';
import { useTests } from '../hooks/useTests';
import TestCard from '../components/TestCard';

export default function Dashboard() {
  const { tests, loading, error } = useTests();

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Tests</h1>
        <Link to="/create"><button>+ New Test</button></Link>
      </div>

      {error && <div className="error">{error}</div>}
      {loading && <div className="empty">Loading...</div>}
      {!loading && tests.length === 0 && <div className="empty">No tests yet. Create one to get started.</div>}

      <div style={{ marginTop: 20 }}>
        {tests.map((t) => <TestCard key={t.test_id} test={t} />)}
      </div>
    </>
  );
}