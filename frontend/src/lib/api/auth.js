/**
 * Authentication API Service
 * 
 * Handles all authentication-related API calls
 * Production-ready with proper error handling
 */

import apiClient from './client';

/**
 * User registration
 * @param {Object} data - Registration data
 * @param {string} data.email - User email
 * @param {string} data.password - User password
 * @param {string} data.fullName - Full name
 * @param {string} data.organization - Organization/institution
 * @returns {Promise<Object>} User data
 */
export const register = async (data) => {
    try {
        const response = await apiClient.post('/api/v1/auth/register', {
            email: data.email,
            password: data.password,
            full_name: data.fullName || data.full_name,
            organization: data.organization || data.institution?.value || data.otherInstitution,
            country: data.country?.value || data.country,
            phone_number: data.phoneNumber || data.phone_number,
        });

        return response.data;
    } catch (error) {
        // Enhance error message for common registration errors
        if (error.statusCode === 400) {
            throw new Error(error.message || 'Invalid registration data');
        }
        if (error.message?.includes('already exists')) {
            throw new Error('An account with this email already exists');
        }
        throw error;
    }
};

/**
 * User login
 * @param {Object} credentials
 * @param {string} credentials.email - User email
 * @param {string} credentials.password - User password
 * @returns {Promise<Object>} Authentication tokens and user data
 */
export const login = async (credentials) => {
    try {
        const response = await apiClient.post('/api/v1/auth/login', {
            email: credentials.email,
            password: credentials.password,
        });

        const { access_token, refresh_token, user } = response.data;

        // Store tokens securely
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);

        // Store user data (non-sensitive)
        if (user) {
            localStorage.setItem('user', JSON.stringify(user));
        }

        return response.data;
    } catch (error) {
        // Enhance error messages
        if (error.statusCode === 401) {
            throw new Error('Invalid email or password');
        }
        if (error.statusCode === 429) {
            throw new Error('Too many login attempts. Please try again later.');
        }
        throw error;
    }
};

/**
 * Refresh access token
 * @param {string} refreshToken - Refresh token
 * @returns {Promise<Object>} New tokens
 */
export const refreshToken = async (refreshToken) => {
    try {
        const response = await apiClient.post('/api/v1/auth/refresh', {
            refresh_token: refreshToken,
        });

        const { access_token, refresh_token: newRefreshToken } = response.data;

        // Update stored tokens
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', newRefreshToken);

        return response.data;
    } catch (error) {
        // If refresh fails, user needs to re-login
        logout();
        throw new Error('Session expired. Please login again.');
    }
};

/**
 * Get current user profile
 * @returns {Promise<Object>} User profile data
 */
export const getCurrentUser = async () => {
    try {
        const response = await apiClient.get('/api/v1/auth/me');

        // Update cached user data
        localStorage.setItem('user', JSON.stringify(response.data));

        return response.data;
    } catch (error) {
        console.error('Failed to fetch user profile:', error);
        throw error;
    }
};

/**
 * Update user profile
 * @param {Object} updates - Profile updates
 * @returns {Promise<Object>} Updated user data
 */
export const updateProfile = async (updates) => {
    try {
        const response = await apiClient.put('/api/v1/auth/me', updates);

        // Update cached user data
        localStorage.setItem('user', JSON.stringify(response.data));

        return response.data;
    } catch (error) {
        console.error('Failed to update profile:', error);
        throw error;
    }
};

/**
 * Complete profile for Google OAuth users
 * @param {Object} profileData - Profile completion data
 * @returns {Promise<Object>} Updated user data
 */
export const completeProfile = async (profileData) => {
    try {
        const response = await apiClient.post('/api/v1/auth/complete-profile', profileData);
        // Update cached user data
        localStorage.setItem('user', JSON.stringify(response.data));
        return response.data;
    } catch (error) {
        console.error('Failed to complete profile:', error);
        throw error;
    }
};

/**
 * Change password
 * @param {string} currentPassword - Current password
 * @param {string} newPassword - New password
 * @returns {Promise<Object>} Success message
 */
export const changePassword = async (currentPassword, newPassword) => {
    try {
        const response = await apiClient.post('/api/v1/auth/change-password', {
            current_password: currentPassword,
            new_password: newPassword,
        });

        return response.data;
    } catch (error) {
        if (error.statusCode === 400) {
            throw new Error('Current password is incorrect');
        }
        throw error;
    }
};

/**
 * Logout user
 * Clears all stored authentication data
 */
export const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');

    // Redirect to login
    window.location.href = '/login';
};

/**
 * Check if user is authenticated
 * @returns {boolean} Authentication status
 */
export const isAuthenticated = () => {
    const token = localStorage.getItem('access_token');
    return !!token;
};

/**
 * Get cached user data
 * @returns {Object|null} Cached user data or null
 */
export const getCachedUser = () => {
    try {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    } catch (error) {
        console.error('Error parsing cached user:', error);
        return null;
    }
};

// Export all functions as a service object
const authService = {
    register,
    login,
    refreshToken,
    getCurrentUser,
    updateProfile,
    completeProfile,
    changePassword,
    logout,
    isAuthenticated,
    getCachedUser,
};

export default authService;
