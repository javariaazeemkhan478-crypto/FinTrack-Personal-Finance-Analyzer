import { useState } from 'react';
import api from '../api/client';
import { useNavigate, Link } from 'react-router-dom';

export default function Register() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        try {
            await api.post('/api/v1/auth/register', { name, email, password });
            setSuccess('Account created successfully. Please log in.');
            setTimeout(() => {
                navigate('/login');
            }, 1500);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Registration failed');
        }
    };

    return (
        <div className="container" style={{ maxWidth: '400px', marginTop: '10vh' }}>
            <div className="card">
                <h2 style={{ textAlign: 'center', marginBottom: '1.5rem' }}>Create your account</h2>
                {error && <div style={{ color: '#ef4444', marginBottom: '1rem', textAlign: 'center', fontWeight: 'bold' }}>{error}</div>}
                {success && <div style={{ color: '#10b981', marginBottom: '1rem', textAlign: 'center', fontWeight: 'bold' }}>{success}</div>}
                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>Name</label>
                        <input className="input" type="text" placeholder="Name" value={name} onChange={e => setName(e.target.value)} required />
                    </div>
                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>Email</label>
                        <input className="input" type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
                    </div>
                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>Password</label>
                        <input className="input" type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} required />
                    </div>
                    <div style={{ marginBottom: '1.5rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>Confirm Password</label>
                        <input className="input" type="password" placeholder="Confirm Password" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} required />
                    </div>
                    <button className="btn" style={{ width: '100%', marginBottom: '1rem' }} type="submit">Create Account</button>
                </form>
                <div style={{ textAlign: 'center' }}>
                    <span style={{ color: '#6b7280' }}>Already have an account? </span>
                    <Link to="/login" style={{ color: '#3b82f6', textDecoration: 'none', fontWeight: 600 }}>Login</Link>
                </div>
            </div>
        </div>
    );
}
