import { Routes, Route } from 'react-router-dom';
import Layout from 'src/components/Layout';
import Dashboard from './pages/Dashboard';
import CreateTest from './pages/CreateTest';
import TestDetail from './pages/TestDetail';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="create" element={<CreateTest />} />
        <Route path="tests/:id" element={<TestDetail />} />
      </Route>
    </Routes>
  );
}