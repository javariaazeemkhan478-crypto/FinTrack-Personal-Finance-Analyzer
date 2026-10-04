import { useState, useEffect } from 'react';
import api from '../api/client';
import { formatCurrency } from '../utils/currency';

export default function Goals() {
    const [goals, setGoals] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    
    const [name, setName] = useState('');
    const [targetAmount, setTargetAmount] = useState('');
    const [targetDate, setTargetDate] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [contribAmts, setContribAmts] = useState<Record<string, string>>({});

    const fetchGoals = async () => {
        try {
            const res = await api.get('/api/v1/goals');
            setGoals(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchGoals();
    }, []);

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(''); setSuccess('');
        try {
            await api.post('/api/v1/goals/', {
                name,
                target_amount: parseFloat(targetAmount),
                current_amount: 0,
                target_date: targetDate + "T00:00:00Z"
            });
            setSuccess('Goal created successfully!');
            fetchGoals();
            setName(''); setTargetAmount(''); setTargetDate('');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to create goal.');
        }
    };

    const handleContribute = async (id: string) => {
        const amt = parseFloat(contribAmts[id]);
        if (isNaN(amt) || amt <= 0) return;
        try {
            await api.post(`/api/v1/goals/${id}/contribute`, { amount: amt });
            setContribAmts({ ...contribAmts, [id]: '' });
            fetchGoals();
        } catch (err) {
            alert('Failed to contribute.');
        }
    };

    if (loading) return <div style={{ padding: '2rem' }}>Loading goals...</div>;

    return (
        <div style={{ padding: '1rem', maxWidth: '1200px', margin: '0 auto' }}>
            <h1 style={{ marginBottom: '0.5rem' }}>Financial Goals</h1>
            <p style={{ color: '#6b7280', marginBottom: '2rem' }}>Track your savings targets and milestones.</p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '2rem' }}>
                
                {/* CREATE GOAL */}
                <div className="card" style={{ height: 'fit-content' }}>
                    <h3>Create New Goal</h3>
                    {error && <div style={{ color: 'red', marginBottom: '1rem' }}>{error}</div>}
                    {success && <div style={{ color: 'green', marginBottom: '1rem' }}>{success}</div>}
                    <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Goal Name *</label>
                            <input required type="text" value={name} onChange={e => setName(e.target.value)} style={{ width: '100%', padding: '0.5rem' }} placeholder="e.g. Emergency Fund, New Laptop" />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Target Amount *</label>
                            <input required type="number" step="0.01" min="1" value={targetAmount} onChange={e => setTargetAmount(e.target.value)} style={{ width: '100%', padding: '0.5rem' }} placeholder="5000.00" />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Target Date *</label>
                            <input required type="date" value={targetDate} onChange={e => setTargetDate(e.target.value)} style={{ width: '100%', padding: '0.5rem' }} />
                        </div>
                        <button type="submit" className="btn" style={{ background: '#8b5cf6', color: 'white', marginTop: '1rem' }}>Set Goal</button>
                    </form>
                </div>

                {/* GOAL LIST */}
                <div>
                    {goals.length === 0 ? (
                        <div className="card" style={{ textAlign: 'center', padding: '3rem 1rem' }}>
                            <h3>No Goals Yet</h3>
                            <p style={{ color: '#6b7280' }}>Start planning for something important—an emergency fund, new laptop, education, travel, or any financial target.</p>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {goals.map(g => {
                                const percent = Math.min((g.current_amount / g.target_amount) * 100, 100);
                                const isComplete = percent >= 100;
                                
                                return (
                                    <div key={g.id} className="card">
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <h3 style={{ margin: 0 }}>{g.name}</h3>
                                            {isComplete && <span style={{ fontWeight: 'bold', color: '#10b981' }}>Completed 🎉</span>}
                                        </div>
                                        <div style={{ margin: '1rem 0' }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                                <span>Saved: {formatCurrency(g.current_amount)}</span>
                                                <span>Target: {formatCurrency(g.target_amount)}</span>
                                            </div>
                                            <div style={{ height: '12px', background: '#e5e7eb', borderRadius: '6px', overflow: 'hidden' }}>
                                                <div style={{ width: `${percent}%`, height: '100%', background: '#8b5cf6', transition: 'width 0.3s' }}></div>
                                            </div>
                                        </div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', color: '#6b7280', fontSize: '0.9rem', marginBottom: '1rem' }}>
                                            <span>{percent.toFixed(1)}% Complete</span>
                                            <span>{formatCurrency(Math.max(0, g.target_amount - g.current_amount))} Remaining</span>
                                        </div>

                                        {!isComplete && (
                                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                                <input 
                                                    type="number" 
                                                    step="0.01"
                                                    placeholder="Amount to add" 
                                                    value={contribAmts[g.id] || ''} 
                                                    onChange={e => setContribAmts({...contribAmts, [g.id]: e.target.value})}
                                                    style={{ padding: '0.4rem', flex: 1 }}
                                                />
                                                <button onClick={() => handleContribute(g.id)} className="btn" style={{ background: '#3b82f6', color: 'white', padding: '0.4rem 1rem' }}>Add Contribution</button>
                                            </div>
                                        )}
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
