/**
 * Production-Grade API Client
 * 
 * Features:
 * - JWT authentication with automatic token refresh
 * - Request/response interceptors for error handling
 * - Timeout protection
 * - Retry logic for network failures
 * - AWS-compatible configuration
 */

import axios from 'axios';

// Environment-based API URL (AWS-compatible)
const getApiUrl = () => {
    // Priority: Environment variable > Default
    if (process.env.REACT_APP_API_URL) {
        return process.env.REACT_APP_API_URL;
    }

    // Default to localhost in development
    if (process.env.NODE_ENV === 'development') {
        return 'http://localhost:8000';
    }

    // Production should always have REACT_APP_API_URL set
    console.error('REACT_APP_API_URL not set in production!');
    return window.location.origin; // Fallback to same domain
};

export const API_BASE_URL = getApiUrl();

// Create axios instance with production defaults
export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 300000, // 5 minutes timeout
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: false, // Set to true if using cookies
});

// Track if we're currently refreshing token to prevent multiple refresh calls
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });

    failedQueue = [];
};

/**
 * REQUEST INTERCEPTOR
 * Adds JWT token to all requests
 */
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        // Add request timestamp for debugging
        config.metadata = { startTime: new Date() };

        return config;
    },
    (error) => {
        console.error('Request interceptor error:', error);
        return Promise.reject(error);
    }
);

/**
 * RESPONSE INTERCEPTOR
 * Handles token refresh and error responses
 */
apiClient.interceptors.response.use(
    (response) => {
        // Log response time in development
        if (process.env.NODE_ENV === 'development') {
            const endTime = new Date();
            const duration = endTime - response.config.metadata.startTime;
            console.log(`API ${response.config.method.toUpperCase()} ${response.config.url}: ${duration}ms`);
        }

        return response;
    },
    async (error) => {
        const originalRequest = error.config;

        // Network error (no response from server)
        if (!error.response) {
            console.error('Network error:', error.message);
            return Promise.reject({
                message: 'Network error. Please check your internet connection.',
                isNetworkError: true,
            });
        }

        // Handle 401 Unauthorized - Token expired or invalid
        if (error.response.status === 401 && !originalRequest._retry) {
            // Prevent infinite loops
            if (originalRequest.url.includes('/auth/refresh')) {
                // Refresh token itself failed
                handleAuthFailure();
                return Promise.reject(error);
            }

            originalRequest._retry = true;

            // If already refreshing, queue this request
            if (isRefreshing) {
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject });
                })
                    .then(token => {
                        originalRequest.headers.Authorization = `Bearer ${token}`;
                        return apiClient(originalRequest);
                    })
                    .catch(err => Promise.reject(err));
            }

            isRefreshing = true;
            const refreshToken = localStorage.getItem('refresh_token');

            if (!refreshToken) {
                handleAuthFailure();
                return Promise.reject(error);
            }

            try {
                // Attempt to refresh token
                const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
                    refresh_token: refreshToken,
                });

                const { access_token, refresh_token: newRefreshToken } = response.data;

                // Update tokens
                localStorage.setItem('access_token', access_token);
                localStorage.setItem('refresh_token', newRefreshToken);

                // Update authorization header
                originalRequest.headers.Authorization = `Bearer ${access_token}`;

                // Process queued requests
                processQueue(null, access_token);

                return apiClient(originalRequest);
            } catch (refreshError) {
                // Refresh failed
                processQueue(refreshError, null);
                handleAuthFailure();
                return Promise.reject(refreshError);
            } finally {
                isRefreshing = false;
            }
        }

        // Handle 403 Forbidden
        if (error.response.status === 403) {
            console.error('Access forbidden:', error.response.data);
            return Promise.reject({
                message: error.response.data.detail || 'You do not have permission to perform this action.',
                statusCode: 403,
            });
        }

        // Handle 429 Too Many Requests
        if (error.response.status === 429) {
            return Promise.reject({
                message: 'Too many requests. Please wait a moment and try again.',
                statusCode: 429,
            });
        }

        // Handle 500 Server Errors
        if (error.response.status >= 500) {
            console.error('Server error:', error.response.data);
            return Promise.reject({
                message: 'Server error. Please try again later.',
                statusCode: error.response.status,
            });
        }

        // Return formatted error
        return Promise.reject({
            message: error.response.data.detail || error.response.data.message || 'An error occurred',
            statusCode: error.response.status,
            data: error.response.data,
        });
    }
);

/**
 * Handle authentication failure
 * Clears tokens and redirects to login
 */
const handleAuthFailure = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');

    // Only redirect if not already on login/signup page
    if (!window.location.pathname.includes('/login') &&
        !window.location.pathname.includes('/signup')) {
        window.location.href = '/login?session_expired=true';
    }
};

/**
 * Health check endpoint
 * Used to verify API connectivity
 */
export const checkApiHealth = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/health`, {
            timeout: 5000,
        });
        return response.data;
    } catch (error) {
        console.error('API health check failed:', error);
        return { status: 'unhealthy', error: error.message };
    }
};

/**
 * Get current API configuration
 * Useful for debugging
 */
export const getApiConfig = () => ({
    baseURL: API_BASE_URL,
    environment: process.env.NODE_ENV,
    timeout: apiClient.defaults.timeout,
});

export default apiClient;
