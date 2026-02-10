import React, { useState, useEffect } from 'react';
import {
    Camera, User, Mail, MapPin, Briefcase, Building, Save,
    CheckCircle, AlertCircle, Phone, Award, BookOpen, Clock,
    Shield, Plus, X, GraduationCap
} from 'lucide-react';
import { getProfile, updateProfile, uploadAvatar } from '../../services/dashboardApi';
import { useAuth } from '../../context/AuthContext';
import '../../styles/ModernTheme.css'; // Explicit Import for Plain CSS styles

const ProfileEditor = () => {
    const { user, refreshUser } = useAuth();
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [avatarPreview, setAvatarPreview] = useState(null);

    const [formData, setFormData] = useState({
        full_name: '',
        email: '',
        phone_number: '',
        country: '',
        organization: '',
        job_title: '',
        department: '',
        bio: '',
        subjects: '',
        certifications: '',
    });

    useEffect(() => {
        loadProfile();
    }, []);

    const loadProfile = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('access_token');
            const profile = await getProfile(token);

            setFormData(prev => ({
                ...prev,
                full_name: profile.full_name || user?.full_name || '',
                email: profile.email || user?.email || '',
                phone_number: profile.phone_number || user?.phone_number || '',
                country: profile.country || user?.country || '',
                organization: profile.organization || user?.organization || '',
                job_title: profile.job_title || user?.job_title || '',
                department: profile.department || user?.department || '',
                bio: profile.bio || user?.bio || ''
            }));

            if (profile.profile_picture_url || user?.profile_picture_url) {
                setAvatarPreview(profile.profile_picture_url || user?.profile_picture_url);
            }
        } catch (err) {
            console.error('Failed to load profile:', err);
            setError(err.response?.data?.detail || 'Failed to load profile data');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleAvatarChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        if (file.size > 5 * 1024 * 1024) {
            setError('Image size must be less than 5MB');
            return;
        }
        try {
            const reader = new FileReader();
            reader.onloadend = () => setAvatarPreview(reader.result);
            reader.readAsDataURL(file);
            const token = localStorage.getItem('access_token');
            await uploadAvatar(token, file);
            await refreshUser();
            setSuccess('Profile picture updated');
            setTimeout(() => setSuccess(null), 3000);
        } catch (err) {
            setError('Failed to upload picture');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            setSaving(true);
            setError(null);
            setSuccess(null);
            const token = localStorage.getItem('access_token');
            const payload = {
                full_name: formData.full_name,
                phone_number: formData.phone_number,
                country: formData.country,
                organization: formData.organization,
                job_title: formData.job_title,
                department: formData.department,
                bio: formData.bio
            };
            await updateProfile(token, payload);
            await refreshUser();
            setSuccess('Profile updated successfully');
            setTimeout(() => setSuccess(null), 3000);
        } catch (err) {
            console.error(err);
            setError('Failed to update profile');
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading Profile...</div>;

    return (
        <div className="profile-page-container">
            {/* Header */}
            <div className="profile-header">
                <h1>Profile Settings</h1>
                <button
                    onClick={() => window.location.href = '/dashboard'}
                    className="auth-btn"
                >
                    Back to Dashboard
                </button>
            </div>

            {/* Main Layout Grid */}
            <div className="profile-layout-grid">

                {/* --- Left Sidebar --- */}
                <div className="profile-sidebar">
                    <div className="sidebar-card">
                        <div className="avatar-wrapper">
                            {avatarPreview ? (
                                <img src={avatarPreview} alt="Profile" className="avatar-image" />
                            ) : (
                                <div className="avatar-placeholder">
                                    {formData.full_name?.charAt(0) || 'U'}
                                </div>
                            )}
                            <label className="upload-circle">
                                <Camera size={16} />
                                <input
                                    type="file"
                                    accept="image/*"
                                    style={{ display: 'none' }}
                                    onChange={handleAvatarChange}
                                />
                            </label>
                        </div>

                        <h2 className="user-name">{formData.full_name || 'User Name'}</h2>
                        <p className="user-email">{formData.email}</p>

                        <div className="status-item">
                            <div className="status-label"><Briefcase size={12} /> Role</div>
                            <div className="status-value">{formData.job_title || 'Not specified'}</div>
                        </div>

                        <div className="status-item">
                            <div className="status-label"><Shield size={12} /> Status</div>
                            <div className="status-value status-active">
                                <span className="status-dot"></span> Active Account
                            </div>
                        </div>
                    </div>
                </div>

                {/* --- Right Content Area --- */}
                <div className="profile-content">

                    {/* Upper Section: Info Cards */}
                    <div className="section-title">
                        <BookOpen size={20} /> Professional Snapshot
                    </div>

                    <div className="info-cards-grid">
                        {/* Subjects Card */}
                        <div className="info-card">
                            <div className="card-header">
                                <div className="icon-box"><BookOpen size={18} /></div>
                                <span>Subjects of Interest</span>
                            </div>
                            <div className="card-body">
                                {formData.subjects ? formData.subjects : "No subjects recorded yet."}
                            </div>
                            <div className="add-field-row">
                                <input
                                    type="text"
                                    name="subjects"
                                    value={formData.subjects}
                                    onChange={handleChange}
                                    placeholder="Add subject..."
                                    className="input-styled"
                                />
                                <button className="btn-icon"><Plus size={18} /></button>
                            </div>
                        </div>

                        {/* Certifications Card */}
                        <div className="info-card">
                            <div className="card-header">
                                <div className="icon-box"><Award size={18} /></div>
                                <span>Certifications</span>
                            </div>
                            <div className="card-body">
                                {formData.certifications ? formData.certifications : "No certifications recorded yet."}
                            </div>
                            <div className="add-field-row">
                                <input
                                    type="text"
                                    name="certifications"
                                    value={formData.certifications}
                                    onChange={handleChange}
                                    placeholder="Add new..."
                                    className="input-styled"
                                />
                                <button className="btn-icon"><Plus size={18} /></button>
                            </div>
                        </div>
                    </div>

                    {/* Middle Section: Bio Card */}
                    <div className="info-card" style={{ marginBottom: '1.5rem' }}>
                        <div className="card-header">
                            <div className="icon-box"><GraduationCap size={18} /></div>
                            <span>Teaching Philosophy / Bio</span>
                        </div>
                        <div className="card-body">
                            {formData.bio ? formData.bio : "No bio recorded."}
                        </div>
                        <div className="add-field-row">
                            <input
                                type="text"
                                name="bio"
                                value={formData.bio}
                                onChange={handleChange}
                                placeholder="Write a short bio..."
                                className="input-styled"
                            />
                            <button className="btn-icon"><Plus size={18} /></button>
                        </div>
                    </div>

                    {/* Lower Section: Edit Form */}
                    <div className="section-title">
                        <User size={20} /> Edit Profile Details
                    </div>

                    <div className="edit-form-card">
                        <div className="form-grid-2">
                            <div className="form-field">
                                <label>Full Name</label>
                                <input
                                    type="text"
                                    name="full_name"
                                    value={formData.full_name}
                                    onChange={handleChange}
                                    className="input-styled"
                                />
                            </div>
                            <div className="form-field">
                                <label>Phone Number</label>
                                <input
                                    type="text"
                                    name="phone_number"
                                    value={formData.phone_number}
                                    onChange={handleChange}
                                    placeholder="+1..."
                                    className="input-styled"
                                />
                            </div>
                            <div className="form-field">
                                <label>Email Address</label>
                                <input
                                    type="email"
                                    value={formData.email}
                                    disabled
                                    className="input-styled"
                                    style={{ background: '#f3f4f6', cursor: 'not-allowed' }}
                                />
                            </div>
                            <div className="form-field">
                                <label>Country / Location</label>
                                <input
                                    type="text"
                                    name="country"
                                    value={formData.country}
                                    onChange={handleChange}
                                    className="input-styled"
                                />
                            </div>
                            <div className="form-field">
                                <label>Current Role</label>
                                <input
                                    type="text"
                                    name="job_title"
                                    value={formData.job_title}
                                    onChange={handleChange}
                                    className="input-styled"
                                />
                            </div>
                            <div className="form-field">
                                <label>Organization</label>
                                <input
                                    type="text"
                                    name="organization"
                                    value={formData.organization}
                                    onChange={handleChange}
                                    className="input-styled"
                                />
                            </div>
                        </div>

                        <div className="form-actions">
                            <button type="button" className="btn-cancel">Cancel</button>
                            <button
                                onClick={handleSubmit}
                                className="btn-save"
                                disabled={saving}
                            >
                                {saving ? "Saving..." : "Save Changes"}
                            </button>
                        </div>
                    </div>

                    {/* Status Messages */}
                    {(error || success) && (
                        <div style={{
                            position: 'fixed', bottom: '2rem', right: '2rem',
                            padding: '1rem', borderRadius: '0.5rem',
                            backgroundColor: error ? '#fef2f2' : '#f0fdf4',
                            border: `1px solid ${error ? '#fecaca' : '#bbf7d0'}`,
                            color: error ? '#b91c1c' : '#15803d',
                            display: 'flex', alignItems: 'center', gap: '0.5rem',
                            boxShadow: '0 4px 6px rgba(0,0,0,0.1)', zIndex: 100
                        }}>
                            {error ? <AlertCircle size={20} /> : <CheckCircle size={20} />}
                            {error || success}
                        </div>
                    )}

                </div>
            </div>
        </div>
    );
};

export default ProfileEditor;
