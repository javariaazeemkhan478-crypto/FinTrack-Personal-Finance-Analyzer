import { useState, useEffect } from 'react';
import api from '../api/client';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';

export default function Analytics() {
    const [overview, setOverview] = useState<any>(null);
    const [monthly, setMonthly] = useState<any[]>([]);
    const [categories, setCategories] = useState<any[]>([]);
    const [trends, setTrends] = useState<any[]>([]);
    const [savings, setSavings] = useState<any[]>([]);
    const [topExpenses, setTopExpenses] = useState<any[]>([]);
    const [anomalies, setAnomalies] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#a855f7', '#ec4899'];

    useEffect(() => {
        const fetchAnalytics = async () => {
            try {
                const [ovRes, monRes, catRes, trRes, savRes, topRes, anomRes] = await Promise.allSettled([
                    api.get('/api/v1/analytics/overview'),
                    api.get('/api/v1/analytics/monthly'),
                    api.get('/api/v1/analytics/categories'),
                    api.get('/api/v1/analytics/trends'),
                    api.get('/api/v1/analytics/savings'),
                    api.get('/api/v1/analytics/top-expenses'),
                    api.get('/api/v1/analytics/anomalies')
                ]);

                if (ovRes.status === 'fulfilled') setOverview(ovRes.value.data);
                if (monRes.status === 'fulfilled') setMonthly(monRes.value.data);
                if (catRes.status === 'fulfilled') setCategories(catRes.value.data);
                if (trRes.status === 'fulfilled') setTrends(trRes.value.data);
                if (savRes.status === 'fulfilled') setSavings(savRes.value.data);
                if (topRes.status === 'fulfilled') setTopExpenses(topRes.value.data);
                if (anomRes.status === 'fulfilled') setAnomalies(anomRes.value.data);
            } catch (err) {
                console.error("Analytics fetch error", err);
            } finally {
                setLoading(false);
            }
        };
        fetchAnalytics();
    }, []);

    if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Crunching numbers...</div>;

    const noData = !overview || (overview.total_income === 0 && overview.total_expenses === 0);

    if (noData) {
        return (
            <div className="card" style={{ textAlign: 'center', padding: '4rem 1rem', marginTop: '2rem' }}>
                <h2>Not Enough Data Yet</h2>
                <p style={{ color: '#6b7280', marginBottom: '1rem' }}>Add a few income and expense transactions and FinTrack will start analyzing your financial patterns.</p>
            </div>
        );
    }

    return (
        <div style={{ padding: '1rem' }}>
            <div style={{ marginBottom: '2rem' }}>
                <h1 style={{ margin: 0 }}>Financial Analytics</h1>
                <p style={{ color: '#6b7280', margin: '0.5rem 0' }}>Understand your spending, savings, and financial trends.</p>
            </div>

            {/* ANOMALIES ALERT */}
            {anomalies.length > 0 && (
                <div style={{ background: '#fef2f2', border: '1px solid #f87171', color: '#b91c1c', padding: '1rem', borderRadius: '8px', marginBottom: '2rem' }}>
                    <strong>Warning: Unusually high expense detected!</strong>
                    <ul style={{ margin: '0.5rem 0 0 1rem' }}>
                        {anomalies.map((a, i) => <li key={i}>{a.description} - ${a.amount} (Avg: ${a.average})</li>)}
                    </ul>
                </div>
            )}

            {/* SUMMARY CARDS */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
                <div className="card">
                    <p style={{ color: '#6b7280', margin: 0 }}>Total Income</p>
                    <h2 style={{ margin: '0.5rem 0', color: '#10b981' }}>${overview?.total_income?.toFixed(2) || '0.00'}</h2>
                </div>
                <div className="card">
                    <p style={{ color: '#6b7280', margin: 0 }}>Total Expenses</p>
                    <h2 style={{ margin: '0.5rem 0', color: '#ef4444' }}>${overview?.total_expenses?.toFixed(2) || '0.00'}</h2>
                </div>
                <div className="card">
                    <p style={{ color: '#6b7280', margin: 0 }}>Net Savings</p>
                    <h2 style={{ margin: '0.5rem 0' }}>${((overview?.total_income || 0) - (overview?.total_expenses || 0)).toFixed(2)}</h2>
                </div>
                <div className="card">
                    <p style={{ color: '#6b7280', margin: 0 }}>Savings Rate</p>
                    <h2 style={{ margin: '0.5rem 0', color: '#3b82f6' }}>{overview?.total_income > 0 ? (((overview?.total_income - overview?.total_expenses) / overview?.total_income) * 100).toFixed(1) : '0'}%</h2>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', gap: '1.5rem' }}>
                
                {/* MONTHLY I/E */}
                <div className="card">
                    <h3>Monthly Income vs Expenses</h3>
                    <div style={{ height: 350, marginTop: '1rem' }}>
                        {monthly.length === 0 ? <p>No monthly data available.</p> : (
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={monthly}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                    <XAxis dataKey="month" />
                                    <YAxis />
                                    <Tooltip formatter={(val: any) => `$${Number(val).toFixed(2)}`} />
                                    <Legend />
                                    <Bar dataKey="income" fill="#10b981" name="Income" />
                                    <Bar dataKey="expenses" fill="#ef4444" name="Expenses" />
                                </BarChart>
                            </ResponsiveContainer>
                        )}
                    </div>
                </div>

                {/* CATEGORIES */}
                <div className="card">
                    <h3>Spending by Category</h3>
                    <div style={{ height: 350, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        {categories.length === 0 ? <p>No category data available.</p> : (
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie data={categories} dataKey="amount" nameKey="category" cx="50%" cy="50%" outerRadius={120} label>
                                        {categories.map((_, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                                    </Pie>
                                    <Tooltip formatter={(val: any) => `$${Number(val).toFixed(2)}`} />
                                    <Legend />
                                </PieChart>
                            </ResponsiveContainer>
                        )}
                    </div>
                </div>

                {/* EXPENSE TRENDS */}
                <div className="card">
                    <h3>Expense Trend Over Time</h3>
                    <div style={{ height: 300, marginTop: '1rem' }}>
                        {trends.length === 0 ? <p>No trend data available.</p> : (
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={trends}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                    <XAxis dataKey="date" />
                                    <YAxis />
                                    <Tooltip formatter={(val: any) => `$${Number(val).toFixed(2)}`} />
                                    <Line type="monotone" dataKey="amount" stroke="#ef4444" strokeWidth={2} dot={{ r: 4 }} name="Daily Expense" />
                                </LineChart>
                            </ResponsiveContainer>
                        )}
                    </div>
                </div>

                {/* SAVINGS TRENDS */}
                <div className="card">
                    <h3>Savings Trend</h3>
                    <div style={{ height: 300, marginTop: '1rem' }}>
                        {savings.length === 0 ? <p>No savings data available.</p> : (
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={savings}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                    <XAxis dataKey="month" />
                                    <YAxis />
                                    <Tooltip formatter={(val: any) => `$${Number(val).toFixed(2)}`} />
                                    <Line type="monotone" dataKey="savings" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} name="Net Savings" />
                                </LineChart>
                            </ResponsiveContainer>
                        )}
                    </div>
                </div>

                {/* TOP EXPENSES */}
                <div className="card">
                    <h3>Top Expenses (All Time)</h3>
                    {topExpenses.length === 0 ? <p>No top expenses available.</p> : (
                        <div style={{ marginTop: '1rem' }}>
                            {topExpenses.map((tx, i) => (
                                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem 0', borderBottom: '1px solid #f3f4f6' }}>
                                    <div>
                                        <strong>{tx.description}</strong>
                                        <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>{tx.category} • {tx.date}</div>
                                    </div>
                                    <div style={{ fontWeight: 'bold', color: '#ef4444' }}>${tx.amount.toFixed(2)}</div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
}
