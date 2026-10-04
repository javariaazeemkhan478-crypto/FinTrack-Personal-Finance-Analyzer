// import React from 'react';
import { Link, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Layout() {
    const { user, logout } = useAuth();
    return (
        <div>
            <nav className="nav">
                <div>
                    <Link to="/dashboard" style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#3b82f6' }}>FinTrack</Link>
                    <Link to="/transactions">Transactions</Link>
                    <Link to="/budgets">Budgets</Link>
                    <Link to="/goals">Goals</Link>
                    <Link to="/analytics">Analytics</Link>
                </div>
                <div>
                    <span style={{ marginRight: '1rem' }}>{user?.name} ({user?.role})</span>
                    <button className="btn btn-danger" onClick={logout}>Logout</button>
                </div>
            </nav>
            <main className="container">
                <Outlet />
            </main>
        </div>
    );
}
