import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# STYLES (Simple CSS for a SaaS look)
create_file('frontend/src/index.css', '''
body { margin: 0; font-family: 'Inter', sans-serif; background-color: #f3f4f6; color: #1f2937; }
.container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
.card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1rem; }
.btn { padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; background: #3b82f6; color: white; }
.btn:hover { background: #2563eb; }
.btn-danger { background: #ef4444; }
.input { width: 100%; padding: 0.5rem; margin-bottom: 1rem; border: 1px solid #d1d5db; border-radius: 4px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }
.nav { background: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.nav a { margin-right: 1rem; text-decoration: none; color: #4b5563; font-weight: 500; }
.nav a:hover { color: #111827; }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { padding: 0.75rem; border-bottom: 1px solid #e5e7eb; text-align: left; }
.table th { background: #f9fafb; font-weight: 600; }
.badge { padding: 0.25rem 0.5rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
.badge-income { background: #d1fae5; color: #065f46; }
.badge-expense { background: #fee2e2; color: #991b1b; }
.progress-bar { width: 100%; height: 8px; background: #e5e7eb; border-radius: 4px; overflow: hidden; }
.progress-fill { height: 100%; background: #3b82f6; }
.progress-fill.warning { background: #f59e0b; }
.progress-fill.danger { background: #ef4444; }
''')

# BATCH 1: Auth & Public
create_file('frontend/src/pages/Login.tsx', '''import React, { useState } from 'react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const res = await api.post('/api/v1/auth/login', { email, password });
            login(res.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Login failed');
        }
    };

    return (
        <div className="container" style={{ maxWidth: '400px', marginTop: '10vh' }}>
            <div className="card">
                <h2>Login to FinTrack</h2>
                {error && <div style={{ color: 'red', marginBottom: '1rem' }}>{error}</div>}
                <form onSubmit={handleSubmit}>
                    <input className="input" type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
                    <input className="input" type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} required />
                    <button className="btn" style={{ width: '100%' }} type="submit">Login</button>
                </form>
            </div>
        </div>
    );
}
''')

create_file('frontend/src/pages/Register.tsx', '''import React, { useState } from 'react';
import api from '../api/client';
import { useNavigate } from 'react-router-dom';

export default function Register() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await api.post('/api/v1/auth/register', { name, email, password });
            navigate('/login');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Registration failed');
        }
    };

    return (
        <div className="container" style={{ maxWidth: '400px', marginTop: '10vh' }}>
            <div className="card">
                <h2>Create Account</h2>
                {error && <div style={{ color: 'red', marginBottom: '1rem' }}>{error}</div>}
                <form onSubmit={handleSubmit}>
                    <input className="input" type="text" placeholder="Name" value={name} onChange={e => setName(e.target.value)} required />
                    <input className="input" type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
                    <input className="input" type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} required />
                    <button className="btn" style={{ width: '100%' }} type="submit">Register</button>
                </form>
            </div>
        </div>
    );
}
''')

create_file('frontend/src/components/Layout.tsx', '''import React from 'react';
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
''')

# BATCH 2 & 3 & 5 & 6 (Combined simplified dashboard and features)
create_file('frontend/src/pages/Dashboard.tsx', '''import React, { useEffect, useState } from 'react';
import api from '../api/client';

export default function Dashboard() {
    const [overview, setOverview] = useState<any>(null);

    useEffect(() => {
        api.get('/api/v1/analytics/overview').then(res => setOverview(res.data)).catch(console.error);
    }, []);

    if (!overview) return <div className="container">Loading dashboard...</div>;

    return (
        <div>
            <h1>Dashboard</h1>
            <div className="grid">
                <div className="card">
                    <h3>Balance</h3>
                    <h2>${overview.current_balance}</h2>
                </div>
                <div className="card">
                    <h3>Income</h3>
                    <h2 style={{ color: 'green' }}>${overview.total_income}</h2>
                </div>
                <div className="card">
                    <h3>Expenses</h3>
                    <h2 style={{ color: 'red' }}>${overview.total_expenses}</h2>
                </div>
                <div className="card">
                    <h3>Savings Rate</h3>
                    <h2>{overview.savings_rate.toFixed(1)}%</h2>
                </div>
            </div>
        </div>
    );
}
''')

create_file('frontend/src/pages/Transactions.tsx', '''import React, { useEffect, useState } from 'react';
import api from '../api/client';

export default function Transactions() {
    const [txs, setTxs] = useState<any[]>([]);
    const [amount, setAmount] = useState('');
    const [type, setType] = useState('EXPENSE');
    const [cat, setCat] = useState('Food');
    const [desc, setDesc] = useState('');

    const fetchTxs = () => api.get('/api/v1/transactions').then(res => setTxs(res.data)).catch(console.error);
    useEffect(() => { fetchTxs(); }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        await api.post('/api/v1/transactions/', { amount: parseFloat(amount), transaction_type: type, category: cat, description: desc });
        fetchTxs();
        setAmount(''); setDesc('');
    };

    return (
        <div>
            <h1>Transactions</h1>
            <div className="card">
                <h3>Add Transaction</h3>
                <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '1rem' }}>
                    <input className="input" type="number" placeholder="Amount" value={amount} onChange={e=>setAmount(e.target.value)} required />
                    <select className="input" value={type} onChange={e=>setType(e.target.value)}>
                        <option value="EXPENSE">Expense</option><option value="INCOME">Income</option>
                    </select>
                    <input className="input" type="text" placeholder="Category" value={cat} onChange={e=>setCat(e.target.value)} required />
                    <input className="input" type="text" placeholder="Description" value={desc} onChange={e=>setDesc(e.target.value)} />
                    <button className="btn" type="submit">Add</button>
                </form>
            </div>
            <div className="card">
                <table className="table">
                    <thead><tr><th>Date</th><th>Type</th><th>Category</th><th>Description</th><th>Amount</th></tr></thead>
                    <tbody>
                        {txs.map(t => (
                            <tr key={t.id}>
                                <td>{new Date(t.created_at).toLocaleDateString()}</td>
                                <td><span className={`badge badge-${t.transaction_type.toLowerCase()}`}>{t.transaction_type}</span></td>
                                <td>{t.category}</td>
                                <td>{t.description}</td>
                                <td>${t.amount}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
''')

# UPDATE App.tsx
create_file('frontend/src/App.tsx', '''import React from 'react';
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
    if (!user) return <Navigate to="/login" />;
    return <>{children}</>;
};

function App() {
  return (
    <AuthProvider>
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                
                <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
                    <Route path="/" element={<Navigate to="/dashboard" />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/transactions" element={<Transactions />} />
                    <Route path="/budgets" element={<div><h1>Budgets</h1><p>Under Construction</p></div>} />
                    <Route path="/goals" element={<div><h1>Goals</h1><p>Under Construction</p></div>} />
                    <Route path="/analytics" element={<div><h1>Analytics</h1><p>Under Construction</p></div>} />
                </Route>
            </Routes>
        </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
''')

print("React UI batches generated.")
