import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import ModernSidebar from '../components/Sidebar/ModernSidebar';
import Generator from '../components/Generator';
import ProfileEditor from '../components/Profile/ProfileEditor';
import LessonView from '../components/LessonView';
import { getLessonDetail } from '../services/dashboardApi';
import { useAuth } from '../context/AuthContext';
import { Menu, X } from 'lucide-react';

export default function GeneratorPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { lessonId } = useParams();  // Get lesson ID from URL
  const { user } = useAuth();

  // State for layout and view
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const [currentView, setCurrentView] = useState('generator'); // 'generator', 'profile', 'lesson-detail'
  const [selectedLesson, setSelectedLesson] = useState(null);
  const [loading, setLoading] = useState(false);

  // Load lesson from URL parameter on mount/change
  useEffect(() => {
    const loadLessonFromUrl = async () => {
      if (lessonId) {
        try {
          setLoading(true);
          const detail = await getLessonDetail(lessonId);  // apiClient handles auth
          setSelectedLesson(detail);
          setCurrentView('lesson-detail');
        } catch (error) {
          console.error('Failed to load lesson from URL:', error);
          // If lesson not found, redirect to generator
          navigate('/generator');
        } finally {
          setLoading(false);
        }
      } else {
        // No lessonId in URL, show generator
        setSelectedLesson(null);
        setCurrentView('generator');
      }
    };

    loadLessonFromUrl();
  }, [lessonId, navigate]);

  // Check URL params or route for initial view
  useEffect(() => {
    if (location.pathname === '/profile') {
      setCurrentView('profile');
    }
  }, [location]);

  // Handle window resize
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

  const handleSidebarToggle = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const handleNewLesson = () => {
    navigate('/generator');  // Navigate to base URL
    setSelectedLesson(null);
    setCurrentView('generator');
    if (isMobile) setSidebarCollapsed(true);
  };

  const handleHistoryItemClick = async (lesson) => {
    // Navigate to lesson URL - this will trigger the useEffect to load the lesson
    navigate(`/generator/${lesson.id}`);
    if (isMobile) setSidebarCollapsed(true);
  };

  const renderContent = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
        </div>
      );
    }

    switch (currentView) {
      case 'profile':
        return <ProfileEditor />;
      case 'lesson-detail':
        return selectedLesson ? (
          <LessonView
            lesson={selectedLesson}
            topic={selectedLesson.topic}
            onBack={handleNewLesson}
          />
        ) : (
          <div className="text-center p-8">Select a lesson to view</div>
        );
      case 'generator':
      default:
        // Pass hideSidebar=true to hide the internal sidebar of Generator component
        // Pass a wrapper around toggle to act as "back button" if needed, or simple hamburger for mobile
        return (
          <div className="h-full overflow-y-auto">
            <Generator
              hideSidebar={true}
              backButton={null}
            />
          </div>
        );
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900 overflow-hidden">
      {/* Mobile Hamburger Button - Only show when sidebar is closed */}
      {isMobile && sidebarCollapsed && (
        <button
          onClick={handleSidebarToggle}
          className="mobile-hamburger"
          aria-label="Toggle sidebar"
          style={{
            display: 'flex',
            position: 'fixed',
            top: '16px',
            left: '16px',
            zIndex: 1100,
            width: '48px',
            height: '48px',
            background: 'linear-gradient(135deg, #1a1d2e 0%, #16213e 100%)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '12px',
            cursor: 'pointer',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
            transition: 'all 0.3s ease',
          }}
        >
          <Menu size={24} color="white" />
        </button>
      )}

      {/* Sidebar */}
      <ModernSidebar
        collapsed={sidebarCollapsed}
        onSetCollapsed={setSidebarCollapsed}
        onNewLesson={handleNewLesson}
        onLessonSelect={handleHistoryItemClick}
        currentLessonId={selectedLesson?.id || lessonId}  // Highlight active lesson
        onProfileSelect={() => {
          setCurrentView('profile');
          if (isMobile) setSidebarCollapsed(true);
        }}
        showCloseButton={isMobile && !sidebarCollapsed}
        onClose={() => setSidebarCollapsed(true)}
      />

      {/* Main Content Area */}
      <div
        className="flex-1 overflow-hidden transition-all duration-300 relative"
        style={{
          marginLeft: isMobile ? 0 : (sidebarCollapsed ? '70px' : '280px'),
          paddingTop: isMobile ? '70px' : 0
        }}
      >
        {/* Mobile sidebar overlay */}
        {isMobile && !sidebarCollapsed && (
          <div
            className="fixed inset-0 bg-black/60 z-40 backdrop-blur-sm"
            onClick={() => setSidebarCollapsed(true)}
            style={{ animation: 'fadeIn 0.2s ease' }}
          />
        )}

        <div className="h-full overflow-y-auto p-4 md:p-6 custom-scrollbar">
          {renderContent()}
        </div>
      </div>
    </div>
  );
}
