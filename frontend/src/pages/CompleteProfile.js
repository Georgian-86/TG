import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import Select from 'react-select';
import { Building2, Phone, MapPin, CheckCircle, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { completeProfile } from '../lib/api/auth';
import '../styles/auth.css';

const countryOptions = [
    { value: 'US', label: 'United States' },
    { value: 'UK', label: 'United Kingdom' },
    { value: 'CA', label: 'Canada' },
    { value: 'AU', label: 'Australia' },
    { value: 'IN', label: 'India' },
    { value: 'OTHER', label: 'Other' }
];

export default function CompleteProfile() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const { login } = useAuth(); // We might need to manually update auth state

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [formData, setFormData] = useState({
        organization: '',
        country: null,
        phoneNumber: ''
    });

    useEffect(() => {
        // Extract token from URL if present (redirected from Google callback)
        const token = searchParams.get('token');
        if (token) {
            localStorage.setItem('access_token', token);
            // Ideally we should also fetch user info here to populate name/email if possible,
            // but for now we just assume we need to complete profile.
        } else {
            // If no token and not logged in, redirect to login
            const storedToken = localStorage.getItem('access_token');
            if (!storedToken) {
                navigate('/login');
            }
        }
    }, [searchParams, navigate]);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSelectChange = (name, value) => {
        setFormData({
            ...formData,
            [name]: value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!formData.organization || !formData.country || !formData.phoneNumber) {
            setError('Please fill in all required fields');
            return;
        }

        setLoading(true);

        try {
            const profileData = {
                organization: formData.organization,
                country: formData.country.value,
                phone_number: formData.phoneNumber
            };

            await completeProfile(profileData);

            // Force reload user context or redirect
            // Since completeProfile updates cached user, we can just navigate.
            // But we might want to refresh the AuthContext.
            window.location.href = '/generator'; // Hard reload to ensure context picks up new data

        } catch (err) {
            console.error('Profile completion error:', err);
            setError(err.message || 'Failed to update profile. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-background"><div className="gradient-1"></div><div className="gradient-2"></div></div>
            <div className="auth-wrapper">
                <div className="auth-card">
                    <div className="auth-header">
                        <div className="auth-logo">
                            <img src="/TechGenieMascot.png" alt="TeachGenie" className="auth-logo-image" style={{ width: '50px', height: '50px', borderRadius: '50%' }} />
                            <h1 className="animated-title">TeachGenie</h1>
                        </div>
                        <p className="auth-subtitle">Complete Your Profile</p>
                        <p className="text-sm text-slate-500 mt-2">
                            Please provide a few more details to finish setting up your account.
                        </p>
                    </div>

                    <div className="auth-form-container">
                        {error && (
                            <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm flex items-center gap-2 border border-red-200">
                                <AlertCircle size={16} /> {error}
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="auth-form space-y-4">

                            <div className="form-group">
                                <label><Building2 size={20} /> Organization / Institution</label>
                                <input
                                    type="text"
                                    name="organization"
                                    value={formData.organization}
                                    onChange={handleChange}
                                    placeholder="e.g. University of Design"
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label><MapPin size={20} /> Country</label>
                                <Select
                                    options={countryOptions}
                                    value={formData.country}
                                    onChange={(option) => handleSelectChange('country', option)}
                                    placeholder="Select Country"
                                    className="react-select-container"
                                    classNamePrefix="react-select"
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label><Phone size={20} /> Phone Number</label>
                                <input
                                    type="tel"
                                    name="phoneNumber"
                                    value={formData.phoneNumber}
                                    onChange={handleChange}
                                    placeholder="+1 234 567 8900"
                                    required
                                />
                            </div>

                            <button
                                type="submit"
                                className="btn btn-accent btn-large w-full mt-6"
                                disabled={loading}
                            >
                                {loading ? (
                                    <span className="flex items-center justify-center gap-2">
                                        <span className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></span>
                                        Saving...
                                    </span>
                                ) : (
                                    <span className="flex items-center justify-center gap-2">
                                        Complete Setup <CheckCircle size={18} />
                                    </span>
                                )}
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
}
