import { useEffect, useState } from 'react';
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
