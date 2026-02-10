/**
 * Protected Route Component
 * 
 * Wraps routes that require authentication
 * Redirects to login if user is not authenticated
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * Loading spinner component
 */
const LoadingSpinner = () => (
    <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        backgroundColor: 'var(--bg-white, #fff)',
    }}>
        <div style={{
            textAlign: 'center',
        }}>
            <div className="spinner" style={{
                width: '48px',
                height: '48px',
                border: '4px solid rgba(99, 102, 241, 0.1)',
                borderTopColor: '#6366f1',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
                margin: '0 auto 16px',
            }}></div>
            <p style={{
                fontSize: '16px',
                color: 'var(--text-muted, #666)',
            }}>
                Loading...
            </p>
        </div>
    </div>
);

/**
 * ProtectedRoute component
 * @param {Object} props
 * @param {React.ReactNode} props.children - Child components to render if authenticated
 * @returns {React.ReactNode}
 */
export default function ProtectedRoute({ children }) {
    const { user, loading } = useAuth();
    const location = useLocation();

    // Show loading spinner while checking authentication
    if (loading) {
        return <LoadingSpinner />;
    }

    // Redirect to login if not authenticated
    if (!user) {
        // Save the attempted location for redirect after login
        return (
            <Navigate
                to="/login"
                state={{ from: location.pathname }}
                replace
            />
        );
    }

    // Redirect to profile completion if needed
    // Note: We check if it is explicitly false (to avoid issues with legacy users where it might be undefined/null initially)
    if (user.profile_completed === false) {
        return <Navigate to="/complete-profile" replace />;
    }

    // User is authenticated, render children
    return children;
}
