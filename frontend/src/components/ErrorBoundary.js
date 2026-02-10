/**
 * Error Boundary Component
 * 
 * Catches JavaScript errors anywhere in the child component tree
 * Production-ready with logging and user-friendly error display
 */

import React from 'react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null,
        };
    }

    static getDerivedStateFromError(error) {
        // Update state so the next render will show the fallback UI
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        // Log error to console in development
        if (process.env.NODE_ENV === 'development') {
            console.error('Error caught by boundary:', error, errorInfo);
        }

        // Store error details
        this.setState({
            error,
            errorInfo,
        });

        // In production, you would send this to an error reporting service
        // Example: Sentry, LogRocket, etc.
        if (process.env.NODE_ENV === 'production') {
            // logErrorToService(error, errorInfo);
        }
    }

    handleReset = () => {
        this.setState({
            hasError: false,
            error: null,
            errorInfo: null,
        });
    };

    render() {
        if (this.state.hasError) {
            return (
                <div className="error-boundary-container" style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minHeight: '100vh',
                    padding: '20px',
                    backgroundColor: 'var(--bg-white, #fff)',
                }}>
                    <div className="error-boundary-content" style={{
                        maxWidth: '600px',
                        textAlign: 'center',
                    }}>
                        <div className="error-icon" style={{
                            fontSize: '64px',
                            marginBottom: '20px',
                        }}>
                            ⚠️
                        </div>

                        <h1 style={{
                            fontSize: '32px',
                            marginBottom: '16px',
                            color: 'var(--text-dark, #1a1a1a)',
                        }}>
                            Oops! Something went wrong
                        </h1>

                        <p style={{
                            fontSize: '16px',
                            color: 'var(--text-muted, #666)',
                            marginBottom: '24px',
                            lineHeight: '1.6',
                        }}>
                            We're sorry for the inconvenience. An unexpected error has occurred.
                            Please try refreshing the page or contact support if the problem persists.
                        </p>

                        {process.env.NODE_ENV === 'development' && this.state.error && (
                            <details style={{
                                marginTop: '20px',
                                padding: '16px',
                                backgroundColor: '#f5f5f5',
                                borderRadius: '8px',
                                textAlign: 'left',
                                fontSize: '14px',
                                maxHeight: '300px',
                                overflow: 'auto',
                            }}>
                                <summary style={{ cursor: 'pointer', fontWeight: 'bold', marginBottom: '10px' }}>
                                    Error Details (Development Only)
                                </summary>
                                <div style={{ fontFamily: 'monospace', fontSize: '12px' }}>
                                    <strong>Error:</strong> {this.state.error.toString()}
                                    <br /><br />
                                    <strong>Component Stack:</strong>
                                    <pre style={{ whiteSpace: 'pre-wrap' }}>
                                        {this.state.errorInfo?.componentStack}
                                    </pre>
                                </div>
                            </details>
                        )}

                        <div className="error-actions" style={{
                            display: 'flex',
                            gap: '12px',
                            justifyContent: 'center',
                            marginTop: '32px',
                        }}>
                            <button
                                onClick={this.handleReset}
                                style={{
                                    padding: '12px 24px',
                                    borderRadius: '8px',
                                    border: '1px solid var(--border-color, #ddd)',
                                    backgroundColor: 'var(--bg-white, #fff)',
                                    color: 'var(--text-dark, #1a1a1a)',
                                    fontSize: '16px',
                                    fontWeight: '600',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s',
                                }}
                            >
                                Try Again
                            </button>

                            <button
                                onClick={() => window.location.href = '/'}
                                style={{
                                    padding: '12px 24px',
                                    borderRadius: '8px',
                                    border: 'none',
                                    backgroundColor: 'var(--primary, #6366f1)',
                                    color: '#fff',
                                    fontSize: '16px',
                                    fontWeight: '600',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s',
                                }}
                            >
                                Go to Home
                            </button>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
