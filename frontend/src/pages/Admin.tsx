import { useState, useEffect } from 'react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';

export default function Admin() {
    const { user } = useAuth();
    const [users, setUsers] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                // If there's an exact endpoint /api/v1/users (often typical) or admin
                const res = await api.get('/api/v1/users'); 
                setUsers(res.data);
            } catch (err: any) {
                setError(err.response?.data?.detail || 'Failed to load users');
            } finally {
                setLoading(false);
            }
        };
        if (user && (user.role === 'SUPER_ADMIN' || user.role === 'ADMIN')) {
            fetchUsers();
        }
    }, [user]);

    if (!user) return null;
    if (user.role !== 'SUPER_ADMIN' && user.role !== 'ADMIN') {
        return <Navigate to="/dashboard" replace />;
    }

    if (loading) return <div>Loading Admin Data...</div>;

    return (
        <div>
            <h2>Admin Dashboard</h2>
            {error && <div style={{ color: 'red' }}>{error}</div>}
            
            <div className="card" style={{ marginTop: '2rem' }}>
                <h3>User Management</h3>
                {users.length === 0 ? <p>No users found.</p> : (
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Role</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(u => (
                                <tr key={u.id}>
                                    <td>{u.name}</td>
                                    <td>{u.email}</td>
                                    <td><span className="badge badge-income">{u.role}</span></td>
                                    <td>{u.is_active ? 'Active' : 'Disabled'}</td>
                                    <td>
                                        <button className="btn" style={{ marginRight: '0.5rem', padding: '0.2rem 0.5rem' }}>Edit Role</button>
                                        <button className="btn btn-danger" style={{ padding: '0.2rem 0.5rem' }}>{u.is_active ? 'Disable' : 'Enable'}</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}
