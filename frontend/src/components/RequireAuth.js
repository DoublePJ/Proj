import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function RequireAuth({ children }) {
    const { isAuthenticated } = useAuth();
    if (!isAuthenticated) {
        return <Navigate to="/auth" replace />;
    }
    return children || null;
}

export default RequireAuth;
