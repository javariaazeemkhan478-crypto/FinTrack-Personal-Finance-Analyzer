import { Outlet, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Layout() {
    const { user, logout } = useAuth();

    return (
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            <nav className="nav">
                <div>
                    <Link to="/dashboard" style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#1f2937' }}>FinTrack</Link>
                    
                    {/* Role-based navigation */}
                    <Link to="/dashboard" style={{ marginLeft: '2rem' }}>Dashboard</Link>
                    
                    {/* Only show these if NOT an auditor */}
                    {user?.role !== 'AUDITOR' && (
                        <>
                            <Link to="/transactions">Transactions</Link>
                            <Link to="/budgets">Budgets</Link>
                            <Link to="/goals">Goals</Link>
                        </>
                    )}

                    {/* Show analytics for non-auditors, or let auditors use their specific dash */}
                    {user?.role !== 'AUDITOR' && <Link to="/analytics">Analytics</Link>}

                    {/* Show Admin tools only for admins */}
                    {(user?.role === 'SUPER_ADMIN' || user?.role === 'ADMIN') && (
                        <Link to="/admin" style={{ color: '#ef4444' }}>Admin Panel</Link>
                    )}

                    {/* Show Auditor tools only for auditors */}
                    {(user?.role === 'AUDITOR' || user?.role === 'SUPER_ADMIN') && (
                        <Link to="/auditor" style={{ color: '#8b5cf6' }}>Audit Panel</Link>
                    )}
                </div>
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <span style={{ fontWeight: 500 }}>{user?.name}</span>
                    
                    {/* Role Badge */}
                    <span className={`badge ${user?.role === 'SUPER_ADMIN' ? 'badge-expense' : 'badge-income'}`}>
                        {user?.role.replace('_', ' ')}
                    </span>
                    
                    <button onClick={logout} className="btn" style={{ marginLeft: '1rem', background: '#e5e7eb', color: '#374151' }}>Logout</button>
                </div>
            </nav>
            <main className="container" style={{ flexGrow: 1, width: '100%' }}>
                <Outlet />
            </main>
        </div>
    );
}
