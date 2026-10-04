import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Transactions from './pages/Transactions';
import Admin from './pages/Admin';
import Auditor from './pages/Auditor';
import Analytics from './pages/Analytics';
import Budgets from './pages/Budgets';
import Goals from './pages/Goals';
import Notifications from './pages/Notifications';
import Reports from './pages/Reports';
import Profile from './pages/Profile';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    const { user, loading } = useAuth();
    if (loading) return <div>Loading...</div>;
    if (!user) return <Navigate to="/login" replace />;
    return <>{children}</>;
};

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
                    <Route path="/admin" element={<Admin />} />
                    <Route path="/auditor" element={<Auditor />} />
                    <Route path="/budgets" element={<Budgets />} />
                    <Route path="/goals" element={<Goals />} />
                    <Route path="/analytics" element={<Analytics />} />
                    <Route path="/notifications" element={<Notifications />} />
                    <Route path="/reports" element={<Reports />} />
                    <Route path="/profile" element={<Profile />} />
                </Route>
            </Routes>
        </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
