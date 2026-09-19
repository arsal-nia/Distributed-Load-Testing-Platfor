import { Link } from 'react-router-dom';
import StatusBadge from './StatusBadge';

export default function TestCard({ test }) {
  return (
    <div className="card">
      <h3>
        <Link to={`/tests/${test.test_id}`}>{test.test_id}</Link>
      </h3>
      <StatusBadge status={test.status} />
    </div>
  );
}