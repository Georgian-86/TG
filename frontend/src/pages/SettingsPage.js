import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
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
    X
} from 'lucide-react';
import '../styles/dashboard.css';

export default function SettingsPage() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    // Layout State
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

    // Settings State
    const [darkMode, setDarkMode] = useState(false);
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
        // Navigate to generator with lesson state (handled if GeneratorPage supports it)
        navigate('/generator', { state: { lessonId: lesson.id } });
    };
    const handleProfileSelect = () => {
        // Since Profile is currently a view within GeneratorPage, we navigate there for now
        // Or if you separate ProfilePage later, change this.
        navigate('/generator'); // Temporary until Profile route is formalized
    };

    const SettingsSection = ({ title, children, className = "" }) => (
        <div className={`modern-card h-full ${className}`}>
            <h3 className="text-xl font-bold text-white mb-6 pb-4 border-b border-white/10 flex items-center gap-2">
                {title}
            </h3>
            <div className="space-y-3">
                {children}
            </div>
        </div>
    );

    const SettingsItem = ({ icon: Icon, title, description, action }) => (
        <div className="setting-item flex items-center justify-between group cursor-pointer hover:bg-white/5">
            <div className="flex items-center gap-4">
                <div className="setting-icon-box transform group-hover:scale-110 transition-transform duration-300">
                    <Icon size={22} strokeWidth={2} />
                </div>
                <div>
                    <strong className="text-white block mb-1 text-base">{title}</strong>
                    <p className="text-gray-400 text-sm leading-relaxed">{description}</p>
                </div>
            </div>
            <div className="pl-4">
                {action}
            </div>
        </div>
    );

    const Toggle = ({ checked, onChange }) => (
        <div
            onClick={() => onChange(!checked)}
            className={`w-14 h-8 rounded-full transition-all duration-300 relative cursor-pointer ${checked ? 'bg-gradient-to-r from-orange-500 to-orange-600 shadow-lg shadow-orange-500/30' : 'bg-gray-700'}`}
        >
            <div className={`w-6 h-6 bg-white rounded-full absolute top-1 transition-all duration-300 shadow-md ${checked ? 'left-7' : 'left-1'}`} />
        </div>
    );

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
                    navigate('/generator'); // Navigate back to dashboard when closing
                }}
            />

            {/* Main Content Area */}
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

                <div className="h-full overflow-y-auto p-4 md:p-6 custom-scrollbar" style={{ paddingTop: isMobile ? '70px' : undefined }}>
                    {/* Mobile Header Toggle */}
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

                    <div className="modern-page p-4 md:p-8">
                        <div className="max-w-6xl mx-auto">
                            <div className="mb-10 text-center md:text-left">
                                <h1 className="modern-title text-4xl mb-3">Settings & Preferences</h1>
                                <p className="modern-subtitle text-lg">Manage your workspace, appearance, and account security</p>
                            </div>

                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                                {/* Appearance Column */}
                                <div className="space-y-8">
                                    <SettingsSection title={<><Moon size={24} className="text-orange-500" /> Appearance</>}>
                                        <SettingsItem
                                            icon={darkMode ? Moon : Sun}
                                            title="Dark Mode"
                                            description="Switch between light and dark themes for better visibility"
                                            action={<Toggle checked={darkMode} onChange={setDarkMode} />}
                                        />
                                    </SettingsSection>

                                    <SettingsSection title={<><Bell size={24} className="text-orange-500" /> Notifications</>}>
                                        <SettingsItem
                                            icon={Bell}
                                            title="Email Notifications"
                                            description="Receive daily summaries and alerts about your lesson plans"
                                            action={<Toggle checked={notifications} onChange={setNotifications} />}
                                        />
                                    </SettingsSection>
                                </div>

                                {/* Account & Security Column */}
                                <div className="space-y-8">
                                    <SettingsSection title={<><Shield size={24} className="text-orange-500" /> Security & Privacy</>}>
                                        <SettingsItem
                                            icon={Shield}
                                            title="Change Password"
                                            description="Update your password periodically to keep your account secure"
                                            action={
                                                <button className="modern-btn-ghost text-sm py-2 px-4 hover:border-orange-500 hover:text-orange-500">
                                                    Update
                                                </button>
                                            }
                                        />
                                        <SettingsItem
                                            icon={Trash2}
                                            title="Delete Account"
                                            description="Permanently remove your account and all associated data"
                                            action={
                                                <button className="text-red-500 hover:text-red-400 text-sm font-medium px-4 py-2 hover:bg-red-500/10 rounded-lg transition-colors">
                                                    Delete
                                                </button>
                                            }
                                        />
                                    </SettingsSection>

                                    <SettingsSection title={<><HelpCircle size={24} className="text-orange-500" /> Support</>}>
                                        <SettingsItem
                                            icon={HelpCircle}
                                            title="Help Center"
                                            description="Guides, FAQs, and support for using TeachGenie"
                                            action={
                                                <button className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-white/10 text-gray-400 hover:text-white transition-all">
                                                    <ChevronRight size={24} />
                                                </button>
                                            }
                                        />
                                    </SettingsSection>
                                </div>
                            </div>

                            <div className="mt-12 text-center text-gray-500 text-sm">
                                TeachGenie v1.0.0 • © 2026 All Rights Reserved
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
