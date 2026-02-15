import React, { useState, useEffect } from 'react';
import {
    Camera, User, Mail, MapPin, Briefcase, Building, Save,
    CheckCircle, AlertCircle, Phone, Award, BookOpen, Clock,
    Shield, Plus, X, GraduationCap, Building2, Calendar
} from 'lucide-react';
import { getProfile, updateProfile, uploadAvatar } from '../../services/dashboardApi';
import { useAuth } from '../../context/AuthContext';
import '../../styles/profile-page.css';

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
        <div className="profile-page-wrapper">
            {/* Header */}
            <div className="profile-page-header">
                <h1 className="profile-page-title">My Profile</h1>
                <p className="profile-page-subtitle">
                    Manage your personal information and preferences
                </p>
            </div>

            {/* Status Messages */}
            {error && (
                <div className="profile-status-message error">
                    <AlertCircle size={20} />
                    {error}
                </div>
            )}
            {success && (
                <div className="profile-status-message success">
                    <CheckCircle size={20} />
                    {success}
                </div>
            )}

            {/* Main Layout */}
            <div className="profile-content-layout">
                {/* Sidebar Card */}
                <div className="profile-sidebar-card">
                    {/* Avatar Section */}
                    <div className="profile-avatar-section">
                        <div className="profile-avatar-wrapper">
                            {avatarPreview ? (
                                <img src={avatarPreview} alt="Profile" className="profile-avatar-image" />
                            ) : (
                                <div className="profile-avatar-image" style={{
                                    background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    fontSize: '3rem',
                                    fontWeight: '700',
                                    color: 'white'
                                }}>
                                    {formData.full_name?.charAt(0)?.toUpperCase() || 'U'}
                                </div>
                            )}
                            <label className="profile-avatar-upload">
                                <Camera size={20} />
                                <input
                                    type="file"
                                    accept="image/*"
                                    className="profile-avatar-input"
                                    onChange={handleAvatarChange}
                                />
                            </label>
                        </div>
                        <h2 className="profile-user-name">{formData.full_name || 'User Name'}</h2>
                        <p className="profile-user-email">{formData.email}</p>
                    </div>

                    {/* Status Items */}
                    <div className="profile-status-items">
                        <div className="profile-status-item">
                            <div className="profile-status-icon">
                                <Briefcase size={18} />
                            </div>
                            <div className="profile-status-text">
                                <p className="profile-status-label">Role</p>
                                <p className="profile-status-value">{formData.job_title || 'Not specified'}</p>
                            </div>
                        </div>

                        <div className="profile-status-item">
                            <div className="profile-status-icon">
                                <Building2 size={18} />
                            </div>
                            <div className="profile-status-text">
                                <p className="profile-status-label">Organization</p>
                                <p className="profile-status-value">{formData.organization || 'Not specified'}</p>
                            </div>
                        </div>

                        <div className="profile-status-item">
                            <div className="profile-status-icon">
                                <MapPin size={18} />
                            </div>
                            <div className="profile-status-text">
                                <p className="profile-status-label">Location</p>
                                <p className="profile-status-value">{formData.country || 'Not specified'}</p>
                            </div>
                        </div>

                        <div className="profile-status-item">
                            <div className="profile-status-icon">
                                <Shield size={18} />
                            </div>
                            <div className="profile-status-text">
                                <p className="profile-status-label">Status</p>
                                <p className="profile-status-value">Active Account</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Main Content */}
                <div className="profile-main-content">
                    {/* Professional Snapshot */}
                    <div className="profile-info-card">
                        <div className="profile-card-header">
                            <h2 className="profile-card-title">
                                <div className="profile-card-icon">
                                    <BookOpen size={22} />
                                </div>
                                Professional Snapshot
                            </h2>
                        </div>

                        <div className="profile-snapshot-grid">
                            {/* Subjects */}
                            <div className="profile-snapshot-item">
                                <div className="profile-snapshot-header">
                                    <h3 className="profile-snapshot-title">Subjects</h3>
                                    <button className="profile-add-button">
                                        <Plus size={14} />
                                        Add
                                    </button>
                                </div>
                                {formData.subjects ? (
                                    <div className="profile-items-list">
                                        {formData.subjects.split(',').map((subject, idx) => (
                                            <span key={idx} className="profile-item-tag">{subject.trim()}</span>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="profile-empty-state">No subjects added yet</p>
                                )}
                            </div>

                            {/* Certifications */}
                            <div className="profile-snapshot-item">
                                <div className="profile-snapshot-header">
                                    <h3 className="profile-snapshot-title">Certifications</h3>
                                    <button className="profile-add-button">
                                        <Plus size={14} />
                                        Add
                                    </button>
                                </div>
                                {formData.certifications ? (
                                    <div className="profile-items-list">
                                        {formData.certifications.split(',').map((cert, idx) => (
                                            <span key={idx} className="profile-item-tag">{cert.trim()}</span>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="profile-empty-state">No certifications added yet</p>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Bio Section */}
                    <div className="profile-info-card">
                        <div className="profile-card-header">
                            <h2 className="profile-card-title">
                                <div className="profile-card-icon">
                                    <GraduationCap size={22} />
                                </div>
                                Teaching Philosophy
                            </h2>
                        </div>
                        <p className="profile-bio-text">
                            {formData.bio || 'Share your teaching philosophy and educational approach...'}
                        </p>
                    </div>

                    {/* Edit Profile Form */}
                    <div className="profile-info-card">
                        <div className="profile-card-header">
                            <h2 className="profile-card-title">
                                <div className="profile-card-icon">
                                    <User size={22} />
                                </div>
                                Edit Profile Details
                            </h2>
                        </div>

                        <div className="profile-form-grid">
                            <div className="profile-form-field">
                                <label className="profile-form-label">Full Name</label>
                                <input
                                    type="text"
                                    name="full_name"
                                    value={formData.full_name}
                                    onChange={handleChange}
                                    className="profile-form-input"
                                    placeholder="Enter your full name"
                                />
                            </div>

                            <div className="profile-form-field">
                                <label className="profile-form-label">Phone Number</label>
                                <input
                                    type="text"
                                    name="phone_number"
                                    value={formData.phone_number}
                                    onChange={handleChange}
                                    className="profile-form-input"
                                    placeholder="+1 (555) 123-4567"
                                />
                            </div>

                            <div className="profile-form-field">
                                <label className="profile-form-label">Email Address</label>
                                <input
                                    type="email"
                                    value={formData.email}
                                    disabled
                                    className="profile-form-input"
                                />
                            </div>

                            <div className="profile-form-field">
                                <label className="profile-form-label">Country / Location</label>
                                <input
                                    type="text"
                                    name="country"
                                    value={formData.country}
                                    onChange={handleChange}
                                    className="profile-form-input"
                                    placeholder="United States"
                                />
                            </div>

                            <div className="profile-form-field">
                                <label className="profile-form-label">Current Role</label>
                                <input
                                    type="text"
                                    name="job_title"
                                    value={formData.job_title}
                                    onChange={handleChange}
                                    className="profile-form-input"
                                    placeholder="Teacher, Professor, etc."
                                />
                            </div>

                            <div className="profile-form-field">
                                <label className="profile-form-label">Organization</label>
                                <input
                                    type="text"
                                    name="organization"
                                    value={formData.organization}
                                    onChange={handleChange}
                                    className="profile-form-input"
                                    placeholder="School or Institution"
                                />
                            </div>

                            <div className="profile-form-field full-width">
                                <label className="profile-form-label">Teaching Philosophy / Bio</label>
                                <input
                                    type="text"
                                    name="bio"
                                    value={formData.bio}
                                    onChange={handleChange}
                                    className="profile-form-input"
                                    placeholder="Share your teaching philosophy..."
                                />
                            </div>

                            <div className="profile-form-field full-width">
                                <label className="profile-form-label">Subjects (comma-separated)</label>
                                <input
                                    type="text"
                                    name="subjects"
                                    value={formData.subjects}
                                    onChange={handleChange}
                                    className="profile-form-input"
                                    placeholder="Mathematics, Science, English"
                                />
                            </div>

                            <div className="profile-form-field full-width">
                                <label className="profile-form-label">Certifications (comma-separated)</label>
                                <input
                                    type="text"
                                    name="certifications"
                                    value={formData.certifications}
                                    onChange={handleChange}
                                    className="profile-form-input"
                                    placeholder="Teaching License, Master's Degree"
                                />
                            </div>
                        </div>

                        <div className="profile-form-actions">
                            <button 
                                type="button" 
                                className="profile-btn profile-btn-cancel"
                                onClick={() => loadProfile()}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleSubmit}
                                className="profile-btn profile-btn-save"
                                disabled={saving}
                            >
                                {saving ? (
                                    <>
                                        <Clock size={18} className="animate-spin" />
                                        Saving...
                                    </>
                                ) : (
                                    <>
                                        <Save size={18} />
                                        Save Changes
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProfileEditor;
