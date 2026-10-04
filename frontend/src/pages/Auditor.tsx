import { useState, useEffect } from 'react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';

export default function Auditor() {
    const { user } = useAuth();
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchAuditData = async () => {
            try {
                const res = await api.get('/api/v1/analytics/overview');
                setStats(res.data);
            } catch (err: any) {
                setError(err.response?.data?.detail || 'Failed to load audit data');
            } finally {
                setLoading(false);
            }
        };
        
        if (user && user.role === 'AUDITOR') {
            fetchAuditData();
        }
    }, [user]);

    if (!user) return null;
    if (user.role !== 'AUDITOR' && user.role !== 'SUPER_ADMIN') {
        return <Navigate to="/dashboard" replace />;
    }

    if (loading) return <div>Loading Audit Data...</div>;

    return (
        <div>
            <h2><span style={{ color: '#ef4444', border: '1px solid #ef4444', padding: '0.2rem 0.5rem', fontSize: '0.8rem', borderRadius: '4px', verticalAlign: 'middle', marginRight: '0.5rem' }}>READ ONLY</span> Auditor Dashboard</h2>
            {error && <div style={{ color: 'red' }}>{error}</div>}
            
            {!error && stats && (
                <div className="grid" style={{ marginTop: '2rem' }}>
                    <div className="card">
                        <h3>Global Balance</h3>
                        <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>${stats.current_balance || 0}</p>
                    </div>
                    <div className="card">
                        <h3>Total Processed Income</h3>
                        <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'green' }}>${stats.total_income || 0}</p>
                    </div>
                    <div className="card">
                        <h3>Total Processed Expenses</h3>
                        <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'red' }}>${stats.total_expenses || 0}</p>
                    </div>
                </div>
            )}
            
            <div className="card" style={{ marginTop: '2rem' }}>
                <h3>Compliance Overview</h3>
                <p>This view guarantees data immutability. You cannot edit, delete, or modify any financial records. If irregularities are detected in the macro balances above, please contact a System Administrator.</p>
            </div>
        </div>
    );
}
