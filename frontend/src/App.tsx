import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Transactions from './pages/Transactions';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    const { user, loading } = useAuth();
    if (loading) return <div>Loading...</div>;
    if (!user) return <Navigate to="/login" replace />;
    return <>{children}</>;
};

// Add a route to redirect authenticated users away from public pages
const PublicRoute = ({ children }: { children: React.ReactNode }) => {
    const { user, loading } = useAuth();
    if (loading) return <div>Loading...</div>;
    if (user) return <Navigate to="/dashboard" replace />;
    return <>{children}</>;
};

function App() {
  return (
    <AuthProvider>
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
                <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
                
                <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/transactions" element={<Transactions />} />
                    <Route path="/budgets" element={<div><div className="card"><h2>Budgets</h2><p>Under Construction</p></div></div>} />
                    <Route path="/goals" element={<div><div className="card"><h2>Goals</h2><p>Under Construction</p></div></div>} />
                    <Route path="/analytics" element={<div><div className="card"><h2>Analytics</h2><p>Under Construction</p></div></div>} />
                    <Route path="/notifications" element={<div><div className="card"><h2>Notifications</h2><p>Under Construction</p></div></div>} />
                    <Route path="/reports" element={<div><div className="card"><h2>Reports</h2><p>Under Construction</p></div></div>} />
                    <Route path="/profile" element={<div><div className="card"><h2>Profile</h2><p>Under Construction</p></div></div>} />
                    <Route path="/admin" element={<div><div className="card"><h2>Admin</h2><p>Under Construction</p></div></div>} />
                </Route>
            </Routes>
        </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
