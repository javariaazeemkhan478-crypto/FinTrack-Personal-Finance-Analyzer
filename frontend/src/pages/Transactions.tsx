import { useEffect, useState } from 'react';
import api from '../api/client';

export default function Transactions() {
    const [txs, setTxs] = useState<any[]>([]);
    const [amount, setAmount] = useState('');
    const [type, setType] = useState('EXPENSE');
    const [cat, setCat] = useState('Food');
    const [desc, setDesc] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [submitting, setSubmitting] = useState(false);

    const fetchTxs = async () => {
        try {
            const res = await api.get('/api/v1/transactions');
            setTxs(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchTxs(); }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(''); setSuccess(''); setSubmitting(true);
        try {
            await api.post('/api/v1/transactions/', { 
                amount: parseFloat(amount), 
                transaction_type: type, 
                category: cat, 
                description: desc 
            });
            setSuccess('Transaction added successfully!');
            fetchTxs();
            setAmount(''); setDesc('');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to add transaction.');
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading transactions...</div>;

    return (
        <div style={{ padding: '1rem', maxWidth: '1200px', margin: '0 auto' }}>
            <h1 style={{ marginBottom: '0.5rem' }}>Transactions</h1>
            <p style={{ color: '#6b7280', marginBottom: '2rem' }}>Manage and track your income and expenses.</p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
                {/* ADD TX FORM */}
                <div className="card" style={{ height: 'fit-content' }}>
                    <h3>Add Transaction</h3>
                    {error && <div style={{ color: 'red', marginBottom: '1rem' }}>{error}</div>}
                    {success && <div style={{ color: 'green', marginBottom: '1rem' }}>{success}</div>}
                    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Type *</label>
                            <select className="input" value={type} onChange={e=>setType(e.target.value)} style={{ width: '100%', padding: '0.5rem' }}>
                                <option value="EXPENSE">Expense</option>
                                <option value="INCOME">Income</option>
                            </select>
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Amount ($) *</label>
                            <input className="input" type="number" step="0.01" min="0.01" placeholder="Amount" value={amount} onChange={e=>setAmount(e.target.value)} required style={{ width: '100%', padding: '0.5rem' }} />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Category *</label>
                            <input className="input" type="text" placeholder="e.g. Food, Salary, Rent" value={cat} onChange={e=>setCat(e.target.value)} required style={{ width: '100%', padding: '0.5rem' }} />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Description</label>
                            <input className="input" type="text" placeholder="Optional notes" value={desc} onChange={e=>setDesc(e.target.value)} style={{ width: '100%', padding: '0.5rem' }} />
                        </div>
                        <button className="btn" type="submit" disabled={submitting} style={{ background: '#3b82f6', color: 'white', marginTop: '1rem' }}>
                            {submitting ? 'Adding...' : 'Add Transaction'}
                        </button>
                    </form>
                </div>

                {/* TX LIST */}
                <div className="card" style={{ overflowX: 'auto' }}>
                    <h3>Transaction History</h3>
                    {txs.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '3rem 1rem' }}>
                            <p style={{ color: '#6b7280' }}>No transactions recorded yet. Add one to see it here.</p>
                        </div>
                    ) : (
                        <table className="table" style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse', marginTop: '1rem' }}>
                            <thead>
                                <tr style={{ borderBottom: '2px solid #f3f4f6' }}>
                                    <th style={{ padding: '0.75rem' }}>Date</th>
                                    <th style={{ padding: '0.75rem' }}>Type</th>
                                    <th style={{ padding: '0.75rem' }}>Category</th>
                                    <th style={{ padding: '0.75rem' }}>Description</th>
                                    <th style={{ padding: '0.75rem' }}>Amount</th>
                                </tr>
                            </thead>
                            <tbody>
                                {txs.map(t => {
                                    const isIncome = t.transaction_type === 'INCOME';
                                    return (
                                        <tr key={t.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                                            <td style={{ padding: '0.75rem', whiteSpace: 'nowrap' }}>{new Date(t.created_at || t.date).toLocaleDateString()}</td>
                                            <td style={{ padding: '0.75rem' }}>
                                                <span style={{ 
                                                    padding: '0.2rem 0.5rem', 
                                                    borderRadius: '4px', 
                                                    fontSize: '0.8rem',
                                                    background: isIncome ? '#d1fae5' : '#fee2e2',
                                                    color: isIncome ? '#065f46' : '#991b1b'
                                                }}>
                                                    {t.transaction_type}
                                                </span>
                                            </td>
                                            <td style={{ padding: '0.75rem' }}>{t.category}</td>
                                            <td style={{ padding: '0.75rem' }}>{t.description}</td>
                                            <td style={{ padding: '0.75rem', fontWeight: 'bold', color: isIncome ? '#10b981' : '#ef4444' }}>
                                                {isIncome ? '+' : '-'}${t.amount.toFixed(2)}
                                            </td>
                                        </tr>
                                    )
                                })}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
}
