import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import ModernSidebar from '../components/Sidebar/ModernSidebar';
import {
    Moon,
    Sun,
    Bell,
    Shield,
    Trash2,
    HelpCircle,
    ChevronRight,
    Menu,
    X,
    Palette,
    Mail,
    Key,
    Users
} from 'lucide-react';
import '../styles/dashboard.css';
import '../styles/settings-page.css';

export default function SettingsPage() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const { theme, toggleTheme } = useTheme();

    // Layout State
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

    // Settings State
    const [notifications, setNotifications] = useState(true);

    // Initial Resize Check
    useEffect(() => {
        const handleResize = () => {
            setIsMobile(window.innerWidth < 768);
            if (window.innerWidth < 768) {
                setSidebarCollapsed(true);
            }
        };
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    // Handlers
    const handleNewLesson = () => navigate('/generator');
    const handleLessonSelect = (lesson) => {
        navigate('/generator', { state: { lessonId: lesson.id } });
    };
    const handleProfileSelect = () => {
        navigate('/generator');
    };

    return (
        <div className="flex h-screen bg-gray-50 dark:bg-gray-900 overflow-hidden">
            {/* Sidebar */}
            <ModernSidebar
                collapsed={sidebarCollapsed}
                onSetCollapsed={setSidebarCollapsed}
                onNewLesson={handleNewLesson}
                onLessonSelect={handleLessonSelect}
                onProfileSelect={handleProfileSelect}
                showCloseButton={isMobile && !sidebarCollapsed}
                onClose={() => {
                    setSidebarCollapsed(true);
                    navigate('/generator');
                }}
            />

            {/* Main Content */}
            <div
                className="flex-1 overflow-hidden transition-all duration-300 relative"
                style={{ marginLeft: isMobile ? 0 : (sidebarCollapsed ? '70px' : '280px') }}
            >
                {isMobile && !sidebarCollapsed && (
                    <div
                        className="absolute inset-0 bg-black/50 z-40"
                        onClick={() => setSidebarCollapsed(true)}
                        style={{
                            backdropFilter: 'blur(4px)',
                            WebkitBackdropFilter: 'blur(4px)'
                        }}
                    />
                )}

                <div className="h-full overflow-y-auto custom-scrollbar">
                    {/* Mobile Menu Toggle */}
                    {isMobile && sidebarCollapsed && (
                        <button 
                            onClick={() => setSidebarCollapsed(false)} 
                            style={{
                                position: 'fixed',
                                top: '16px',
                                left: '16px',
                                zIndex: 50,
                                width: '44px',
                                height: '44px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                borderRadius: '12px',
                                background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                                border: 'none',
                                cursor: 'pointer',
                                boxShadow: '0 4px 15px rgba(245, 158, 11, 0.4)',
                                transition: 'all 0.3s ease'
                            }}
                        >
                            <Menu size={24} color="white" />
                        </button>
                    )}

                    <div className="settings-page-wrapper">
                        {/* Header */}
                        <div className="settings-page-header">
                            <h1 className="settings-page-title">Settings & Preferences</h1>
                            <p className="settings-page-subtitle">
                                Customize your experience with TeachGenie
                            </p>
                        </div>

                        {/* Settings Grid */}
                        <div className="settings-content-grid">
                            {/* Appearance Card */}
                            <div className="settings-card">
                                <div className="settings-card-header">
                                    <div className="settings-card-icon">
                                        <Palette size={24} />
                                    </div>
                                    <h2 className="settings-card-title">Appearance</h2>
                                </div>
                                
                                <div className="settings-item">
                                    <div className="settings-item-content">
                                        <div className="settings-item-left">
                                            <div className="settings-item-icon-box">
                                                {theme === 'dark' ? <Moon size={20} /> : <Sun size={20} />}
                                            </div>
                                            <div className="settings-item-info">
                                                <h3 className="settings-item-title">Dark Mode</h3>
                                                <p className="settings-item-description">
                                                    Switch between light and dark themes for comfortable viewing
                                                </p>
                                            </div>
                                        </div>
                                        <div 
                                            className={`settings-toggle ${theme === 'dark' ? 'active' : ''}`}
                                            onClick={toggleTheme}
                                        >
                                            <div className="settings-toggle-handle"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Notifications Card */}
                            <div className="settings-card">
                                <div className="settings-card-header">
                                    <div className="settings-card-icon">
                                        <Bell size={24} />
                                    </div>
                                    <h2 className="settings-card-title">Notifications</h2>
                                </div>
                                
                                <div className="settings-item">
                                    <div className="settings-item-content">
                                        <div className="settings-item-left">
                                            <div className="settings-item-icon-box">
                                                <Mail size={20} />
                                            </div>
                                            <div className="settings-item-info">
                                                <h3 className="settings-item-title">Email Notifications</h3>
                                                <p className="settings-item-description">
                                                    Receive updates, tips, and lesson summaries via email
                                                </p>
                                            </div>
                                        </div>
                                        <div 
                                            className={`settings-toggle ${notifications ? 'active' : ''}`}
                                            onClick={() => setNotifications(!notifications)}
                                        >
                                            <div className="settings-toggle-handle"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Security Card */}
                            <div className="settings-card">
                                <div className="settings-card-header">
                                    <div className="settings-card-icon">
                                        <Shield size={24} />
                                    </div>
                                    <h2 className="settings-card-title">Security & Privacy</h2>
                                </div>
                                
                                <div className="settings-item">
                                    <div className="settings-item-content">
                                        <div className="settings-item-left">
                                            <div className="settings-item-icon-box">
                                                <Key size={20} />
                                            </div>
                                            <div className="settings-item-info">
                                                <h3 className="settings-item-title">Change Password</h3>
                                                <p className="settings-item-description">
                                                    Update your password to keep your account secure
                                                </p>
                                            </div>
                                        </div>
                                        <button className="settings-action-btn">
                                            Update
                                            <ChevronRight size={16} />
                                        </button>
                                    </div>
                                </div>

                                <div className="settings-item">
                                    <div className="settings-item-content">
                                        <div className="settings-item-left">
                                            <div className="settings-item-icon-box">
                                                <Trash2 size={20} />
                                            </div>
                                            <div className="settings-item-info">
                                                <h3 className="settings-item-title">Delete Account</h3>
                                                <p className="settings-item-description">
                                                    Permanently remove your account and all data
                                                </p>
                                            </div>
                                        </div>
                                        <button className="settings-action-btn danger">
                                            Delete
                                            <Trash2 size={16} />
                                        </button>
                                    </div>
                                </div>
                            </div>

                            {/* Support Card */}
                            <div className="settings-card">
                                <div className="settings-card-header">
                                    <div className="settings-card-icon">
                                        <HelpCircle size={24} />
                                    </div>
                                    <h2 className="settings-card-title">Support & Resources</h2>
                                </div>
                                
                                <div className="settings-item">
                                    <div className="settings-item-content">
                                        <div className="settings-item-left">
                                            <div className="settings-item-icon-box">
                                                <HelpCircle size={20} />
                                            </div>
                                            <div className="settings-item-info">
                                                <h3 className="settings-item-title">Help Center</h3>
                                                <p className="settings-item-description">
                                                    Browse guides, FAQs, and tutorials
                                                </p>
                                            </div>
                                        </div>
                                        <button className="settings-action-btn">
                                            Visit
                                            <ChevronRight size={16} />
                                        </button>
                                    </div>
                                </div>

                                <div className="settings-item">
                                    <div className="settings-item-content">
                                        <div className="settings-item-left">
                                            <div className="settings-item-icon-box">
                                                <Users size={20} />
                                            </div>
                                            <div className="settings-item-info">
                                                <h3 className="settings-item-title">Community</h3>
                                                <p className="settings-item-description">
                                                    Join our educator community and share ideas
                                                </p>
                                            </div>
                                        </div>
                                        <button className="settings-action-btn">
                                            Explore
                                            <ChevronRight size={16} />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Footer */}
                        <div className="settings-footer">
                            <p className="settings-footer-text">
                                TeachGenie v1.0.0 • © 2026 All Rights Reserved
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
