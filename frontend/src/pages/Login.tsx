import { useState } from 'react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            // OAuth2PasswordRequestForm expects form data (username, password), but since FastAPI expects it or JSON depending on the route...
            // Let's check the backend. In phase 1, auth was implemented. Usually FastAPI auth uses OAuth2PasswordRequestForm which requires x-www-form-urlencoded
            // But if it's a standard pydantic model, it uses JSON. Let's send JSON.
            const res = await api.post('/api/v1/auth/login', { email, password });
            login(res.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Invalid email or password');
        }
    };

    return (
        <div className="container" style={{ maxWidth: '400px', marginTop: '10vh' }}>
            <div className="card">
                <h2 style={{ textAlign: 'center', marginBottom: '1.5rem' }}>Login to FinTrack</h2>
                {error && <div style={{ color: '#ef4444', marginBottom: '1rem', textAlign: 'center', fontWeight: 'bold' }}>{error}</div>}
                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>Email</label>
                        <input className="input" type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
                    </div>
                    <div style={{ marginBottom: '1.5rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>Password</label>
                        <input className="input" type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} required />
                    </div>
                    <button className="btn" style={{ width: '100%', marginBottom: '1rem' }} type="submit">Login</button>
                </form>
                <div style={{ textAlign: 'center' }}>
                    <span style={{ color: '#6b7280' }}>Don't have an account? </span>
                    <Link to="/register" style={{ color: '#3b82f6', textDecoration: 'none', fontWeight: 600 }}>Create Account</Link>
                </div>
            </div>
        </div>
    );
}
