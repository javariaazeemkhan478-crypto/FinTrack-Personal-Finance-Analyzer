import { useState, useEffect } from 'react';
import api from '../api/client';

export default function Analytics() {
    const [data, setData] = useState<any>(null);
    useEffect(() => {
        api.get('/api/v1/analytics/overview').then(res => setData(res.data)).catch(console.error);
    }, []);
    return (
        <div className="card">
            <h2>Analytics Overview</h2>
            {!data ? <p>Loading analytics...</p> : (
                <div style={{display: 'flex', gap: '2rem'}}>
                    <div><h3>Income</h3><p className="text-green">${data.total_income || 0}</p></div>
                    <div><h3>Expenses</h3><p className="text-red">${data.total_expenses || 0}</p></div>
                    <div><h3>Net</h3><p>${(data.total_income || 0) - (data.total_expenses || 0)}</p></div>
                </div>
            )}
        </div>
    );
}
