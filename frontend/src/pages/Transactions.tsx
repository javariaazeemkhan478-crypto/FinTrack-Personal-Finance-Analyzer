import { useEffect, useState } from 'react';
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
