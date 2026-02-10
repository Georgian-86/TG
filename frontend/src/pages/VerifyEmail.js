import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import OTPInput from '../components/OTPInput';
import { API_BASE_URL } from '../lib/api/client';
import '../styles/auth.css';
import '../styles/otp.css';

export default function VerifyEmail() {
    const navigate = useNavigate();
    const location = useLocation();
    const email = location.state?.email || sessionStorage.getItem('verificationEmail');

    const [otp, setOtp] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const [canResend, setCanResend] = useState(false);
    const [resendCountdown, setResendCountdown] = useState(60);

    useEffect(() => {
        if (!email) {
            navigate('/signup');
            return;
        }

        // Start countdown timer
        const timer = setInterval(() => {
            setResendCountdown((prev) => {
                if (prev <= 1) {
                    setCanResend(true);
                    clearInterval(timer);
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        return () => clearInterval(timer);
    }, [email, navigate]);

    const maskEmail = (email) => {
        if (!email) return '';
        const [username, domain] = email.split('@');
        const maskedUsername = username.substring(0, 2) + '***';
        return `${maskedUsername}@${domain}`;
    };

    const handleVerify = async (otpCode) => {
        setLoading(true);
        setError('');

        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/auth/verify-email`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    otp: otpCode
                })
            });

            const data = await response.json();

            if (response.ok && data.verified) {
                setSuccess(true);
                sessionStorage.removeItem('verificationEmail');

                // Redirect to login after 2 seconds
                setTimeout(() => {
                    navigate('/login', {
                        state: { message: 'Email verified successfully! Please login.' }
                    });
                }, 2000);
            } else {
                setError(data.detail || data.error || 'Invalid verification code');
                setOtp('');
            }
        } catch (err) {
            setError('Network error. Please try again.');
            setOtp('');
        } finally {
            setLoading(false);
        }
    };

    const handleResend = async () => {
        if (!canResend) return;

        setLoading(true);
        setError('');

        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/auth/resend-verification-email`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: email })
            });

            const data = await response.json();

            if (response.ok) {
                setCanResend(false);
                setResendCountdown(60);

                // Restart countdown
                const timer = setInterval(() => {
                    setResendCountdown((prev) => {
                        if (prev <= 1) {
                            setCanResend(true);
                            clearInterval(timer);
                            return 0;
                        }
                        return prev - 1;
                    });
                }, 1000);

                setError('');
                alert('New verification code sent!');
            } else {
                setError(data.detail || 'Failed to resend code');
            }
        } catch (err) {
            setError('Network error. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    if (success) {
        return (
            <div className="auth-container">
                <div className="auth-card" style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '64px', marginBottom: '20px' }}>✅</div>
                    <h2 style={{ color: '#10b981', marginBottom: '10px' }}>Email Verified!</h2>
                    <p style={{ color: '#6b7280' }}>Redirecting to login...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="auth-container">
            <div className="auth-card">
                <div className="auth-header">
                    <h1>Verify Your Email</h1>
                    <p>We sent a 6-digit code to <strong>{maskEmail(email)}</strong></p>
                </div>

                <div style={{ marginTop: '30px' }}>
                    <OTPInput
                        value={otp}
                        onChange={setOtp}
                        onComplete={handleVerify}
                        error={error}
                        disabled={loading}
                    />
                </div>

                {error && (
                    <div style={{
                        background: '#fee2e2',
                        border: '1px solid #ef4444',
                        borderRadius: '8px',
                        padding: '12px',
                        marginTop: '20px',
                        color: '#991b1b',
                        fontSize: '14px',
                        textAlign: 'center'
                    }}>
                        {error}
                    </div>
                )}

                <div style={{ marginTop: '30px', textAlign: 'center' }}>
                    <p style={{ color: '#6b7280', fontSize: '14px', marginBottom: '15px' }}>
                        Didn't receive the code?
                    </p>

                    {canResend ? (
                        <button
                            onClick={handleResend}
                            disabled={loading}
                            style={{
                                background: 'transparent',
                                border: 'none',
                                color: '#f97316',
                                fontSize: '14px',
                                fontWeight: '600',
                                cursor: 'pointer',
                                textDecoration: 'underline'
                            }}
                        >
                            Resend Code
                        </button>
                    ) : (
                        <p style={{ color: '#9ca3af', fontSize: '14px' }}>
                            Resend available in {resendCountdown}s
                        </p>
                    )}
                </div>

                <div style={{
                    marginTop: '30px',
                    padding: '15px',
                    background: '#fff7ed',
                    borderRadius: '8px',
                    borderLeft: '4px solid #f97316'
                }}>
                    <p style={{ fontSize: '13px', color: '#78350f', margin: 0 }}>
                        <strong>⏱️ Code expires in 10 minutes</strong><br />
                        For your security, never share this code with anyone.
                    </p>
                </div>

                <button
                    onClick={() => navigate('/signup')}
                    style={{
                        marginTop: '20px',
                        width: '100%',
                        background: 'transparent',
                        border: '1px solid #e5e7eb',
                        color: '#6b7280',
                        padding: '12px',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: '14px'
                    }}
                >
                    ← Back to Signup
                </button>
            </div>
        </div>
    );
}
