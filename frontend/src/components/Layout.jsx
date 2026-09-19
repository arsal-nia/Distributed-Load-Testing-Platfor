import { Link, Outlet } from 'react-router-dom';

export default function Layout() {
  return (
    <>
      <nav>
        <span className="brand">Load Testing Platform</span>
        <Link to="/">Dashboard</Link>
        <Link to="/create">Create Test</Link>
        <a href="http://localhost:3001" target="_blank" rel="noreferrer">Grafana</a>
      </nav>
      <div className="container">
        <Outlet />
      </div>
    </>
  );
}