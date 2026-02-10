import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import LoadingScreen from '../components/LoadingScreen';

export default function AuthCallback() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const { refreshUser } = useAuth();

    useEffect(() => {
        const processCallback = async () => {
            const token = searchParams.get('token');
            const error = searchParams.get('error');

            if (error) {
                navigate('/login?error=' + error);
                return;
            }

            if (token) {
                localStorage.setItem('access_token', token);
                try {
                    // Initialize session with new token
                    await refreshUser();
                    navigate('/generator');
                } catch (err) {
                    console.error('Callback error:', err);
                    navigate('/login?error=auth_failed');
                }
            } else {
                navigate('/login');
            }
        };

        processCallback();
    }, [searchParams, navigate, refreshUser]);

    return <LoadingScreen />;
}
