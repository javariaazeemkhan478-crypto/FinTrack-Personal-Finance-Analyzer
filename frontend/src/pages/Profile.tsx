import { useAuth } from '../context/AuthContext';

export default function Profile() {
    const { user } = useAuth();
    return (
        <div className="card">
            <h2>User Profile</h2>
            {user ? (
                <div>
                    <p><strong>Name:</strong> {user.name}</p>
                    <p><strong>Email:</strong> {user.email}</p>
                    <p><strong>Role:</strong> <span className="badge badge-income">{user.role}</span></p>
                </div>
            ) : <p>Please log in.</p>}
        </div>
    );
}
