import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import api from '../api/client';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export default function Dashboard() {
    const { user } = useAuth();
    const [overview, setOverview] = useState<any>(null);
    const [monthly, setMonthly] = useState<any[]>([]);
    const [categories, setCategories] = useState<any[]>([]);
    const [budgets, setBudgets] = useState<any[]>([]);
    const [goals, setGoals] = useState<any[]>([]);
    const [transactions, setTransactions] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#a855f7', '#ec4899'];

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                const [ovRes, monRes, catRes, budRes, goalRes, txRes] = await Promise.allSettled([
                    api.get('/api/v1/analytics/overview'),
                    api.get('/api/v1/analytics/monthly'),
                    api.get('/api/v1/analytics/categories'),
                    api.get('/api/v1/budgets'),
                    api.get('/api/v1/goals'),
                    api.get('/api/v1/transactions?limit=5')
                ]);

                if (ovRes.status === 'fulfilled') setOverview(ovRes.value.data);
                if (monRes.status === 'fulfilled') setMonthly(monRes.value.data);
                if (catRes.status === 'fulfilled') setCategories(catRes.value.data);
                if (budRes.status === 'fulfilled') setBudgets(budRes.value.data.slice(0, 3));
                if (goalRes.status === 'fulfilled') setGoals(goalRes.value.data.slice(0, 3));
                if (txRes.status === 'fulfilled') setTransactions(txRes.value.data);
            } catch (err) {
                console.error("Dashboard fetch error", err);
            } finally {
                setLoading(false);
            }
        };
        fetchDashboardData();
    }, []);

    if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading your financial overview...</div>;

    const noData = !overview || (overview.total_income === 0 && overview.total_expenses === 0);

    return (
        <div style={{ padding: '1rem' }}>
            <div style={{ marginBottom: '2rem' }}>
                <h1 style={{ margin: 0 }}>Welcome back, {user?.name} 👋</h1>
                <p style={{ color: '#6b7280', margin: '0.5rem 0' }}>Here's your financial overview.</p>
            </div>

            {/* QUICK ACTIONS */}
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', flexWrap: 'wrap' }}>
                <Link to="/transactions" className="btn" style={{ background: '#3b82f6', color: 'white' }}>+ Add Transaction</Link>
                <Link to="/budgets" className="btn" style={{ background: '#10b981', color: 'white' }}>+ Create Budget</Link>
                <Link to="/goals" className="btn" style={{ background: '#8b5cf6', color: 'white' }}>+ Set Goal</Link>
                <Link to="/analytics" className="btn" style={{ background: '#f59e0b', color: 'white' }}>View Analytics</Link>
            </div>

            {noData ? (
                <div className="card" style={{ textAlign: 'center', padding: '4rem 1rem' }}>
                    <h2>No financial data yet</h2>
                    <p style={{ color: '#6b7280', marginBottom: '1rem' }}>Add your first income or expense transaction to unlock insights.</p>
                    <Link to="/transactions" className="btn">Add Transaction</Link>
                </div>
            ) : (
                <>
                    {/* TOP SUMMARY */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
                        <div className="card" style={{ borderLeft: '4px solid #3b82f6' }}>
                            <p style={{ color: '#6b7280', margin: 0 }}>Total Balance</p>
                            <h2 style={{ margin: '0.5rem 0' }}>${overview?.current_balance?.toFixed(2) || '0.00'}</h2>
                        </div>
                        <div className="card" style={{ borderLeft: '4px solid #10b981' }}>
                            <p style={{ color: '#6b7280', margin: 0 }}>Total Income</p>
                            <h2 style={{ margin: '0.5rem 0', color: '#10b981' }}>+${overview?.total_income?.toFixed(2) || '0.00'}</h2>
                        </div>
                        <div className="card" style={{ borderLeft: '4px solid #ef4444' }}>
                            <p style={{ color: '#6b7280', margin: 0 }}>Total Expenses</p>
                            <h2 style={{ margin: '0.5rem 0', color: '#ef4444' }}>-${overview?.total_expenses?.toFixed(2) || '0.00'}</h2>
                        </div>
                        <div className="card" style={{ borderLeft: '4px solid #f59e0b' }}>
                            <p style={{ color: '#6b7280', margin: 0 }}>Net Savings</p>
                            <h2 style={{ margin: '0.5rem 0' }}>${((overview?.total_income || 0) - (overview?.total_expenses || 0)).toFixed(2)}</h2>
                        </div>
                    </div>

                    {/* CHARTS ROW */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
                        <div className="card">
                            <h3>Income vs Expenses (Monthly)</h3>
                            {monthly.length === 0 ? <p style={{ color: '#6b7280' }}>Not enough data for monthly trends.</p> : (
                                <div style={{ height: 300, marginTop: '1rem' }}>
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart data={monthly}>
                                            <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                            <XAxis dataKey="month" />
                                            <YAxis />
                                            <Tooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
                                            <Bar dataKey="income" fill="#10b981" name="Income" />
                                            <Bar dataKey="expenses" fill="#ef4444" name="Expenses" />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            )}
                        </div>

                        <div className="card">
                            <h3>Spending by Category</h3>
                            {categories.length === 0 ? <p style={{ color: '#6b7280' }}>Add expenses to see categorization.</p> : (
                                <div style={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                    <ResponsiveContainer width="100%" height="100%">
                                        <PieChart>
                                            <Pie data={categories} dataKey="amount" nameKey="category" cx="50%" cy="50%" outerRadius={100} label>
                                                {categories.map((_, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                                            </Pie>
                                            <Tooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
                                        </PieChart>
                                    </ResponsiveContainer>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* BUDGETS & GOALS ROW */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
                        <div className="card">
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <h3>Budget Overview</h3>
                                <Link to="/budgets" style={{ fontSize: '0.9rem', color: '#3b82f6' }}>View All</Link>
                            </div>
                            {budgets.length === 0 ? (
                                <p style={{ color: '#6b7280' }}>No active budgets. <Link to="/budgets">Create one.</Link></p>
                            ) : (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginTop: '1rem' }}>
                                    {budgets.map(b => {
                                        const percent = Math.min((b.spent / b.amount) * 100, 100);
                                        const color = percent > 90 ? '#ef4444' : percent > 75 ? '#f59e0b' : '#10b981';
                                        return (
                                            <div key={b.id}>
                                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                                    <strong>{b.category}</strong>
                                                    <span>${b.spent} / ${b.amount}</span>
                                                </div>
                                                <div style={{ height: '8px', background: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
                                                    <div style={{ width: `${percent}%`, height: '100%', background: color, transition: 'width 0.3s' }}></div>
                                                </div>
                                                <small style={{ color, fontWeight: 500 }}>{percent.toFixed(1)}% Used</small>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </div>

                        <div className="card">
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <h3>Financial Goals</h3>
                                <Link to="/goals" style={{ fontSize: '0.9rem', color: '#3b82f6' }}>View All</Link>
                            </div>
                            {goals.length === 0 ? (
                                <p style={{ color: '#6b7280' }}>No financial goals set. <Link to="/goals">Set a target.</Link></p>
                            ) : (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginTop: '1rem' }}>
                                    {goals.map(g => {
                                        const percent = Math.min((g.current_amount / g.target_amount) * 100, 100);
                                        return (
                                            <div key={g.id}>
                                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                                    <strong>{g.name}</strong>
                                                    <span>${g.current_amount} / ${g.target_amount}</span>
                                                </div>
                                                <div style={{ height: '8px', background: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
                                                    <div style={{ width: `${percent}%`, height: '100%', background: '#8b5cf6', transition: 'width 0.3s' }}></div>
                                                </div>
                                                <small style={{ color: '#6b7280' }}>{percent.toFixed(1)}% Complete • ${(g.target_amount - g.current_amount).toFixed(2)} remaining</small>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* RECENT TRANSACTIONS */}
                    <div className="card">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                            <h3>Recent Transactions</h3>
                            <Link to="/transactions" style={{ fontSize: '0.9rem', color: '#3b82f6' }}>View All</Link>
                        </div>
                        {transactions.length === 0 ? (
                            <p style={{ color: '#6b7280' }}>No transactions recorded yet.</p>
                        ) : (
                            <div style={{ overflowX: 'auto' }}>
                                <table className="table" style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
                                    <thead>
                                        <tr style={{ borderBottom: '2px solid #f3f4f6' }}>
                                            <th style={{ padding: '0.75rem' }}>Date</th>
                                            <th style={{ padding: '0.75rem' }}>Description</th>
                                            <th style={{ padding: '0.75rem' }}>Category</th>
                                            <th style={{ padding: '0.75rem' }}>Amount</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {transactions.map(tx => (
                                            <tr key={tx.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                                                <td style={{ padding: '0.75rem' }}>{new Date(tx.date).toLocaleDateString()}</td>
                                                <td style={{ padding: '0.75rem' }}>{tx.description}</td>
                                                <td style={{ padding: '0.75rem' }}>{tx.category}</td>
                                                <td style={{ padding: '0.75rem', fontWeight: 'bold', color: tx.type === 'INCOME' ? '#10b981' : '#ef4444' }}>
                                                    {tx.type === 'INCOME' ? '+' : '-'}${tx.amount.toFixed(2)}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                </>
            )}
        </div>
    );
}
