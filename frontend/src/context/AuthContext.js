/**
 * Authentication Context
 * 
 * Provides global authentication state and methods
 * Production-ready with proper error handling and persistence
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import authService from '../lib/api/auth';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    /**
     * Load user from cache or API
     */
    const loadUser = useCallback(async () => {
        try {
            const token = localStorage.getItem('access_token');

            if (!token) {
                setLoading(false);
                return;
            }

            // Try to load from cache first for instant UI
            const cachedUser = authService.getCachedUser();
            if (cachedUser) {
                setUser(cachedUser);
            }

            // Fetch fresh user data
            const userData = await authService.getCurrentUser();
            setUser(userData);
            setError(null);
        } catch (err) {
            console.error('Failed to load user:', err);

            // If token is invalid, clear everything
            if (err.statusCode === 401) {
                authService.logout();
                setUser(null);
            }

            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    /**
     * Initialize auth state on mount
     */
    useEffect(() => {
        loadUser();
    }, [loadUser]);

    /**
     * Login user
     * @param {string} email - User email
     * @param {string} password - User password
     * @returns {Promise<Object>} User data
     */
    const login = async (email, password) => {
        try {
            setError(null);
            const data = await authService.login({ email, password });
            setUser(data.user);
            return data;
        } catch (err) {
            setError(err.message);
            throw err;
        }
    };

    /**
     * Register new user
     * @param {Object} userData - Registration data
     * @returns {Promise<Object>} User data
     */
    const register = async (userData) => {
        try {
            setError(null);
            await authService.register(userData);

            // Auto-login after registration
            const loginData = await login(userData.email, userData.password);
            return loginData;
        } catch (err) {
            setError(err.message);
            throw err;
        }
    };

    /**
     * Logout user
     */
    const logout = useCallback(() => {
        authService.logout();
        setUser(null);
        setError(null);
    }, []);

    /**
     * Update user profile
     * @param {Object} updates - Profile updates
     * @returns {Promise<Object>} Updated user data
     */
    const updateUser = async (updates) => {
        try {
            setError(null);
            const updatedUser = await authService.updateProfile(updates);
            setUser(updatedUser);
            return updatedUser;
        } catch (err) {
            setError(err.message);
            throw err;
        }
    };

    /**
     * Refresh user data
     * Useful after user performs actions that might change their quota
     */
    const refreshUser = async () => {
        try {
            const userData = await authService.getCurrentUser();
            setUser(userData);
            return userData;
        } catch (err) {
            console.error('Failed to refresh user:', err);
            throw err;
        }
    };

    const value = {
        user,
        loading,
        error,
        login,
        register,
        logout,
        updateUser,
        refreshUser,
        isAuthenticated: !!user,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

/**
 * Hook to use auth context
 * @returns {Object} Auth context value
 */
export function useAuth() {
    const context = useContext(AuthContext);

    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }

    return context;
}

export default AuthContext;
