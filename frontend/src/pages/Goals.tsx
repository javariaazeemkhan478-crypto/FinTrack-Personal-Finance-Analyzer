import { useState, useEffect } from 'react';
import api from '../api/client';

export default function Goals() {
    const [goals, setGoals] = useState<any[]>([]);
    
    useEffect(() => {
        api.get('/api/v1/goals').then(res => setGoals(res.data)).catch(console.error);
    }, []);

    return (
        <div className="card">
            <h2>Goals</h2>
            {goals.length === 0 ? <p>No goals set. Create one to start tracking!</p> : (
                <ul>
                    {goals.map(g => (
                        <li key={g.id}>{g.name}: ${g.current_amount} / ${g.target_amount}</li>
                    ))}
                </ul>
            )}
        </div>
    );
}
