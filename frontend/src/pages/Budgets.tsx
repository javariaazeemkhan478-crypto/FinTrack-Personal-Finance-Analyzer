import { useState, useEffect } from 'react';
import api from '../api/client';
import { formatCurrency } from '../utils/currency';

export default function Budgets() {
    const [budgets, setBudgets] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [category, setCategory] = useState('');
    const [amount, setAmount] = useState('');
    const [month, setMonth] = useState('');
    const [year, setYear] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const fetchBudgets = async () => {
        try {
            const res = await api.get('/api/v1/budgets');
            setBudgets(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchBudgets();
    }, []);

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        try {
            await api.post('/api/v1/budgets/', {
                category,
                amount: parseFloat(amount),
                month: parseInt(month),
                year: parseInt(year)
            });
            setSuccess('Budget created successfully!');
            fetchBudgets();
            setCategory(''); setAmount(''); setMonth(''); setYear('');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to create budget. Check inputs.');
        }
    };

    if (loading) return <div style={{ padding: '2rem' }}>Loading budgets...</div>;

    return (
        <div style={{ padding: '1rem', maxWidth: '1200px', margin: '0 auto' }}>
            <h1 style={{ marginBottom: '0.5rem' }}>Budgets</h1>
            <p style={{ color: '#6b7280', marginBottom: '2rem' }}>Set spending limits and track your pacing.</p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '2rem' }}>
                
                {/* CREATE BUDGET */}
                <div className="card" style={{ height: 'fit-content' }}>
                    <h3>Create New Budget</h3>
                    {error && <div style={{ color: 'red', marginBottom: '1rem' }}>{error}</div>}
                    {success && <div style={{ color: 'green', marginBottom: '1rem' }}>{success}</div>}
                    <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Category *</label>
                            <input required type="text" value={category} onChange={e => setCategory(e.target.value)} style={{ width: '100%', padding: '0.5rem' }} placeholder="e.g. Food, Rent, Entertainment" />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Amount *</label>
                            <input required type="number" step="0.01" min="0.01" value={amount} onChange={e => setAmount(e.target.value)} style={{ width: '100%', padding: '0.5rem' }} placeholder="1000.00" />
                        </div>
                        <div style={{ display: 'flex', gap: '1rem' }}>
                            <div style={{ flex: 1 }}>
                                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Month *</label>
                                <input required type="number" min="1" max="12" value={month} onChange={e => setMonth(e.target.value)} style={{ width: '100%', padding: '0.5rem' }} placeholder="1-12" />
                            </div>
                            <div style={{ flex: 1 }}>
                                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Year *</label>
                                <input required type="number" min="2000" value={year} onChange={e => setYear(e.target.value)} style={{ width: '100%', padding: '0.5rem' }} placeholder="2026" />
                            </div>
                        </div>
                        <button type="submit" className="btn" style={{ background: '#3b82f6', color: 'white', marginTop: '1rem' }}>Create Budget</button>
                    </form>
                </div>

                {/* BUDGET LIST */}
                <div>
                    {budgets.length === 0 ? (
                        <div className="card" style={{ textAlign: 'center', padding: '3rem 1rem' }}>
                            <h3>No Active Budgets</h3>
                            <p style={{ color: '#6b7280' }}>Set spending limits for categories like Food, Transport, Shopping, and Entertainment.</p>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {budgets.map(b => {
                                const percent = Math.min((b.spent / b.amount) * 100, 100);
                                let color = '#10b981';
                                let status = 'Healthy';
                                if (percent > 90) { color = '#ef4444'; status = 'Exceeded / Critical'; }
                                else if (percent > 75) { color = '#f59e0b'; status = 'Warning'; }

                                return (
                                    <div key={b.id} className="card">
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <h3 style={{ margin: 0 }}>{b.category}</h3>
                                            <span style={{ fontWeight: 'bold', color }}>{status}</span>
                                        </div>
                                        <div style={{ margin: '1rem 0' }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                                <span>Spent: {formatCurrency(b.spent)}</span>
                                                <span>Limit: {formatCurrency(b.amount)}</span>
                                            </div>
                                            <div style={{ height: '12px', background: '#e5e7eb', borderRadius: '6px', overflow: 'hidden' }}>
                                                <div style={{ width: `${percent}%`, height: '100%', background: color, transition: 'width 0.3s' }}></div>
                                            </div>
                                        </div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', color: '#6b7280', fontSize: '0.9rem' }}>
                                            <span>{percent.toFixed(1)}% Used</span>
                                            <span>{formatCurrency(b.amount - b.spent)} Remaining</span>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
}
