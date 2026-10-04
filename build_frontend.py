import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# 1. API Client
create_file('frontend/src/api/client.ts', '''import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
});

api.interceptors.request.use(config => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

api.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            try {
                const refreshToken = localStorage.getItem('refresh_token');
                const res = await axios.post(`${api.defaults.baseURL}/api/v1/auth/refresh?refresh_token=${refreshToken}`);
                localStorage.setItem('access_token', res.data.access_token);
                localStorage.setItem('refresh_token', res.data.refresh_token);
                return api(originalRequest);
            } catch (err) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);
export default api;
''')

# 2. Auth Context
create_file('frontend/src/context/AuthContext.tsx', '''import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

interface User {
    id: string;
    email: string;
    name: string;
    role: string;
}

interface AuthContextType {
    user: User | null;
    login: (tokens: any) => void;
    logout: () => void;
    loading: boolean;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const AuthProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkAuth = async () => {
            const token = localStorage.getItem('access_token');
            if (token) {
                try {
                    const res = await api.get('/api/v1/auth/me');
                    setUser(res.data);
                } catch (e) {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                }
            }
            setLoading(false);
        };
        checkAuth();
    }, []);

    const login = (tokens: any) => {
        localStorage.setItem('access_token', tokens.access_token);
        localStorage.setItem('refresh_token', tokens.refresh_token);
        window.location.href = '/dashboard';
    };

    const logout = async () => {
        const refresh = localStorage.getItem('refresh_token');
        if (refresh) {
            try { await api.post(`/api/v1/auth/logout?refresh_token=${refresh}`); } catch (e) {}
        }
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
        window.location.href = '/login';
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
''')

# 3. App.tsx with Router
create_file('frontend/src/App.tsx', '''import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';

// Simple placeholders for pages
const Login = () => {
    const { login } = useAuth();
    const handleLogin = async () => {
        // Mocking login for the skeleton
        login({ access_token: 'fake', refresh_token: 'fake' });
    };
    return <div><h1>Login</h1><button onClick={handleLogin}>Log In</button></div>;
};

const Dashboard = () => {
    const { user, logout } = useAuth();
    if (!user) return <Navigate to="/login" />;
    return <div><h1>Dashboard</h1><p>Welcome {user.name}</p><button onClick={logout}>Logout</button></div>;
};

function App() {
  return (
    <AuthProvider>
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Navigate to="/dashboard" />} />
                <Route path="/login" element={<Login />} />
                <Route path="/dashboard" element={<Dashboard />} />
            </Routes>
        </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
''')

# 4. Environment config
create_file('frontend/.env', '''VITE_API_BASE_URL=http://localhost:8000
''')

print("Frontend scaffold scripts generated.")
