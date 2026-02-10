import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Plus,
    Search,
    FileText,
    Star,
    Trash2,
    Settings,
    ChevronLeft,
    ChevronRight,
    LogOut,
    User,
    X
} from 'lucide-react';
import './ModernSidebar.css';
import { getLessonHistory, toggleFavorite, deleteLesson } from '../../services/dashboardApi';
import { useAuth } from '../../context/AuthContext';

const ModernSidebar = ({ collapsed, onSetCollapsed, onNewLesson, onLessonSelect, onProfileSelect, currentLessonId, showCloseButton, onClose }) => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);
    const [hovered, setHovered] = useState(false);

    useEffect(() => {
        loadHistory();
    }, [searchQuery, showFavoritesOnly]);

    const handleMouseEnter = () => {
        setHovered(true);
        if (collapsed) {
            onSetCollapsed(false);
        }
    };

    const handleMouseLeave = () => {
        setHovered(false);
        // Only auto-collapse if we are not on mobile
        if (window.innerWidth >= 768) {
            onSetCollapsed(true);
        }
    };

    const loadHistory = async () => {
        try {
            setLoading(true);
            const data = await getLessonHistory({
                search: searchQuery,
                favoritesOnly: showFavoritesOnly,
                pageSize: 50
            });
            setHistory(data.items || []);
        } catch (error) {
            console.error('Failed to load history:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleToggleFavorite = async (lessonId, e) => {
        e.stopPropagation();
        try {
            await toggleFavorite(lessonId);
            loadHistory();
        } catch (error) {
            console.error('Failed to toggle favorite:', error);
        }
    };

    const handleDeleteLesson = async (lessonId, e) => {
        e.stopPropagation();
        if (window.confirm('Delete this lesson from history?')) {
            try {
                await deleteLesson(lessonId);
                loadHistory();
            } catch (error) {
                console.error('Failed to delete lesson:', error);
            }
        };
    };

    const handleLessonClick = (lesson) => {
        if (onLessonSelect) {
            onLessonSelect(lesson);
        } else {
            console.log('Lesson selected:', lesson);
        }
    };

    const handleProfileClick = () => {
        if (onProfileSelect) {
            onProfileSelect();
        } else {
            navigate('/profile');
        }
    };

    const groupByDate = (items) => {
        const groups = {
            Today: [],
            Yesterday: [],
            'Last 7 Days': [],
            'Last 30 Days': [],
            Older: []
        };

        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        const lastWeek = new Date(today);
        lastWeek.setDate(lastWeek.getDate() - 7);
        const lastMonth = new Date(today);
        lastMonth.setDate(lastMonth.getDate() - 30);

        items.forEach(item => {
            const itemDate = new Date(item.created_at);
            if (itemDate >= today) {
                groups.Today.push(item);
            } else if (itemDate >= yesterday) {
                groups.Yesterday.push(item);
            } else if (itemDate >= lastWeek) {
                groups['Last 7 Days'].push(item);
            } else if (itemDate >= lastMonth) {
                groups['Last 30 Days'].push(item);
            } else {
                groups.Older.push(item);
            }
        });

        return groups;
    };

    const formatTime = (dateString) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        return date.toLocaleDateString();
    };

    const getInitials = (name) => {
        if (!name) return 'U';
        return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    };

    const groupedHistory = groupByDate(history);

    return (
        <div
            className={`modern-sidebar ${collapsed ? 'collapsed' : ''}`}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
        >
            {/* Mobile Close Button */}
            {showCloseButton && (
                <button className="sidebar-close-btn" onClick={onClose}>
                    <X size={20} />
                </button>
            )}

            {/* Profile Section */}
            <div className="sidebar-profile" onClick={handleProfileClick}>
                <div className="sidebar-profile-avatar">
                    {user?.profile_picture_url ? (
                        <img src={user.profile_picture_url} alt={user.full_name} style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '50%' }} />
                    ) : (
                        getInitials(user?.full_name || user?.email)
                    )}
                </div>
                {!collapsed && (
                    <div className="sidebar-profile-info">
                        <p className="sidebar-profile-name">{user?.full_name || 'User'}</p>
                        <p className="sidebar-profile-role">{user?.job_title || 'Educator'}</p>
                    </div>
                )}
            </div>

            {/* New Lesson Button */}
            <button className="sidebar-new-btn" onClick={onNewLesson}>
                <Plus size={18} />
                {!collapsed && <span className="sidebar-new-btn-text">New Lesson</span>}
            </button>

            {/* Search */}
            {!collapsed && (
                <div className="sidebar-search">
                    <Search className="sidebar-search-icon" size={16} />
                    <input
                        type="text"
                        className="sidebar-search-input"
                        placeholder="Search lessons..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </div>
            )}

            {/* History */}
            <div className="sidebar-history">
                {loading ? (
                    !collapsed && (
                        <>
                            {[1, 2, 3, 4, 5].map(i => (
                                <div key={i} className="sidebar-skeleton">
                                    <div className="skeleton-line"></div>
                                    <div className="skeleton-line"></div>
                                </div>
                            ))}
                        </>
                    )
                ) : history.length === 0 ? (
                    !collapsed && (
                        <div className="sidebar-empty">
                            <FileText className="sidebar-empty-icon" />
                            <p className="sidebar-empty-text">
                                {searchQuery ? 'No lessons found' : 'No lessons yet. Create your first one!'}
                            </p>
                        </div>
                    )
                ) : (
                    Object.entries(groupedHistory).map(([group, items]) =>
                        items.length > 0 && !collapsed && (
                            <div key={group} className="sidebar-date-group">
                                <div className="sidebar-date-label">{group}</div>
                                {items.map(item => (
                                    <div
                                        key={item.id}
                                        className={`sidebar-history-item ${item.id === currentLessonId ? 'active' : ''}`}
                                        onClick={() => handleLessonClick(item)}
                                    >
                                        <FileText className="sidebar-history-item-icon" size={16} />
                                        <div className="sidebar-history-item-content">
                                            <p className="sidebar-history-item-title">
                                                {item.title || item.topic}
                                            </p>
                                            <div className="sidebar-history-item-meta">
                                                <span>{formatTime(item.created_at)}</span>
                                                <span>•</span>
                                                <span>{item.duration}min</span>
                                            </div>
                                        </div>
                                        <div className="sidebar-history-item-actions">
                                            <button
                                                className={`sidebar-history-item-action favorite ${item.is_favorite ? 'active' : ''}`}
                                                onClick={(e) => handleToggleFavorite(item.id, e)}
                                                title="Favorite"
                                            >
                                                <Star size={14} fill={item.is_favorite ? 'currentColor' : 'none'} />
                                            </button>
                                            <button
                                                className="sidebar-history-item-action"
                                                onClick={(e) => handleDeleteLesson(item.id, e)}
                                                title="Delete"
                                            >
                                                <Trash2 size={14} />
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )
                    )
                )}
            </div>

            {/* Settings */}
            <div className="sidebar-settings">
                <button className="sidebar-settings-item" onClick={handleProfileClick}>
                    <User size={18} />
                    {!collapsed && <span className="sidebar-settings-item-text">Profile</span>}
                </button>
                <button className="sidebar-settings-item" onClick={() => navigate('/settings')}>
                    <Settings size={18} />
                    {!collapsed && <span className="sidebar-settings-item-text">Settings</span>}
                </button>
                <button className="sidebar-settings-item" onClick={logout}>
                    <LogOut size={18} />
                    {!collapsed && <span className="sidebar-settings-item-text">Logout</span>}
                </button>
            </div>
        </div>
    );
};

export default ModernSidebar;
