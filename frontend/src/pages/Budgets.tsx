import { useState, useEffect } from 'react';
import api from '../api/client';

export default function Budgets() {
    const [budgets, setBudgets] = useState<any[]>([]);
    
    useEffect(() => {
        api.get('/api/v1/budgets').then(res => setBudgets(res.data)).catch(console.error);
    }, []);

    return (
        <div className="card">
            <h2>Budgets</h2>
            {budgets.length === 0 ? <p>No budgets active. You are within safe limits.</p> : (
                <ul>
                    {budgets.map(b => (
                        <li key={b.id}>{b.category}: ${b.spent} / ${b.amount}</li>
                    ))}
                </ul>
            )}
        </div>
    );
}
