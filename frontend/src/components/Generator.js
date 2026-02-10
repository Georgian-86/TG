import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Zap, Download, CheckCircle, AlertCircle, TrendingUp, User, Settings, History, HelpCircle, ArrowUp, Clock, GraduationCap, FileText, ChevronDown, MonitorPlay, Globe, ExternalLink, SlidersHorizontal } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import lessonService from '../lib/api/lessons';
import GenieLoader from './GenieLoader';
import LessonView from './LessonView';
import CognitiveLoadGauge from './CognitiveLoadGauge';
import SessionBlueprintModal from './SessionBlueprintModal';
import '../styles/generator.css';

import FeedbackModal from './FeedbackModal';

import Toast from './Toast';

const Generator = ({ backButton, hideSidebar = false }) => {
  const navigate = useNavigate();
  const { user, refreshUser } = useAuth();
  const textareaRef = useRef(null);

  // Feedback Modal State
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });

  // State
  const [topic, setTopic] = useState('');
  const [level, setLevel] = useState('undergraduate');
  const [duration, setDuration] = useState('30');
  const [contentType, setContentType] = useState('both');
  const [includeQuiz, setIncludeQuiz] = useState(false);
  const [quizDuration, setQuizDuration] = useState('10');
  const [quizMarks, setQuizMarks] = useState('20');

  // Generation State
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [generated, setGenerated] = useState(false);
  const [disclaimerAcked, setDisclaimerAcked] = useState(false);

  // UI State for Popovers
  const [activePopover, setActivePopover] = useState(null); // 'level', 'duration', 'format'
  const [showBlueprintModal, setShowBlueprintModal] = useState(false);
  const [showMobileOptions, setShowMobileOptions] = useState(false);
  const [isMobileView, setIsMobileView] = useState(window.innerWidth < 480);

  // Track mobile view for conditional rendering
  useEffect(() => {
    const handleResize = () => setIsMobileView(window.innerWidth < 480);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Result State
  const [lessonState, setLessonState] = useState({
    lesson_plan: {},
    objectives: [],
    sections: [],
    key_takeaways: [],
    resources: [],
    quiz: null,
    ppt_url: '',
    pdf_url: ''
  });

  const quota = user?.lessons_quota || 5;
  const used = user?.lessons_this_month || 0;
  const freeGenerations = Math.max(0, quota - used);
  const canGenerate = freeGenerations > 0;

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = '54px';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 150) + 'px';
    }
  }, [topic]);

  // Greeting based on time
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  // --- Smart Context Logic (Mirrored from Backend) ---
  const getDurationProfile = (mins) => {
    const m = parseInt(mins);
    if (m <= 30) return { objectives: 3, sections: ["Introduction", "Core Concepts"], takeaways: 3, quiz: 1 };
    if (m <= 45) return { objectives: 4, sections: ["Introduction", "Core Concepts", "Worked Examples"], takeaways: 4, quiz: 1 };
    if (m <= 60) return { objectives: 5, sections: ["Introduction", "Core Concepts", "Worked Examples", "Applications"], takeaways: 5, quiz: 2 };
    return { objectives: 6, sections: ["Introduction", "Core Concepts", "Worked Examples", "Applications", "Discussion"], takeaways: 6, quiz: 3 };
  };

  const getRecommendedDuration = (lvl) => {
    const map = {
      'school': '30–45 minutes',
      'undergraduate': '45–60 minutes',
      'postgraduate': '60–75 minutes',
      'professional': '60 minutes'
    };
    return map[lvl.toLowerCase()] || '60 minutes';
  };

  const getCognitiveMeter = (lvl, mins) => {
    const m = parseInt(mins);
    const l = lvl.toLowerCase();
    if (l === 'school' && m <= 45) return { bars: 2, label: 'Light Load', color: 'bg-green-500' };
    if (l === 'undergraduate' && m <= 60) return { bars: 3, label: 'Standard Load', color: 'bg-blue-500' };
    return { bars: 5, label: 'Deep Dive', color: 'bg-indigo-500' };
  };

  const profile = getDurationProfile(duration);
  const meter = getCognitiveMeter(level, duration);

  const simulateGenerationPipeline = async () => {
    const steps = [
      { progress: 15, message: '✨ Summoning the Teaching Genie...' },
      { progress: 30, message: `🔍 Researching detailed concepts for "${topic}"...` },
      { progress: 45, message: '🧠 Crafting personalized learning pathways...' },
      { progress: 60, message: '📚 Compiling world-class academic resources...' },
      { progress: 80, message: '🎨 Designing visual slides and study notes...' },
    ];

    for (const step of steps) {
      await new Promise(resolve => setTimeout(resolve, 800));
      setProgress(step.progress);
      setProgressMessage(step.message);
    }

    if (includeQuiz) {
      setProgress(90);
      setProgressMessage('🎮 Generating interactive quiz questions...');
      await new Promise(resolve => setTimeout(resolve, 600));
    }

    setProgress(100);
    setProgressMessage('🚀 Finalizing your lesson package...');
  };

  const handleGenerate = async () => {
    if (!topic.trim()) return;

    // Check for Mandatory Feedback (User has used >= 1 lesson & no feedback)
    if (user?.subscription_tier === 'free' && user?.lessons_this_month >= 1 && !user?.feedback_provided) {
      setShowFeedbackModal(true);
      return;
    }

    // Show blueprint modal for confirmation
    setShowBlueprintModal(true);
  };

  // Actual generation after modal confirmation
  const handleConfirmGenerate = async () => {
    // Close modal
    setShowBlueprintModal(false);

    // Trigger Upsell on Button Click (Non-blocking with timeout)
    const userTier = user?.subscription_tier || 'free';

    if (userTier === 'free') {
      // Register listener FIRST, then dispatch (fixes race condition)
      const upgradePromise = new Promise((resolve) => {
        let resolved = false;
        
        const handleClosed = () => {
          if (!resolved) {
            resolved = true;
            window.removeEventListener('upgrade-modal-closed', handleClosed);
            resolve();
          }
        };
        
        // Add listener before dispatching
        window.addEventListener('upgrade-modal-closed', handleClosed);
        
        // Timeout fallback - don't block generation forever (5 seconds max)
        setTimeout(() => {
          if (!resolved) {
            resolved = true;
            window.removeEventListener('upgrade-modal-closed', handleClosed);
            resolve();
          }
        }, 5000);
      });

      // Now dispatch the trigger
      window.dispatchEvent(new Event('trigger-upgrade-modal'));
      
      // Wait for modal close or timeout
      await upgradePromise;
    }

    if (used >= quota) {
      setToast({ show: true, message: 'Monthly quota exceeded. Please upgrade your plan.', type: 'error' });
      return;
    }

    try {
      setLoading(true);
      setProgress(0);

      // Start simulation and API call in parallel-ish
      simulateGenerationPipeline();

      const lessonData = await lessonService.generateLesson({
        topic: topic.trim(),
        level,
        duration: parseInt(duration),
        includeQuiz,
        quizDuration: includeQuiz ? parseInt(quizDuration) : undefined,
        quizMarks: includeQuiz ? parseInt(quizMarks) : undefined,
      });

      setLessonState({
        lesson_plan: {
          title: lessonData.topic || topic,
          level: lessonData.level || level,
          duration: `${lessonData.duration || duration} minutes`,
        },
        objectives: lessonData.learning_objectives || [],
        sections: lessonData.lesson_plan || [],
        key_takeaways: lessonData.key_takeaways || [],
        resources: lessonData.resources || [],
        quiz: lessonData.quiz || null,
        ppt_url: lessonData.ppt_url || '',
        pdf_url: lessonData.pdf_url || '',
        generation_time: lessonData.generation_time || lessonData.processing_time_seconds || 0
      });

      setGenerated(true);
      if (refreshUser) await refreshUser();

      // Trigger Upsell AGAIN after generation
      setTimeout(() => {
        window.dispatchEvent(new Event('trigger-upgrade-modal'));
      }, 2000); // 2s delay to let them see the result first

    } catch (err) {
      console.error('Generation Error:', err);
      setToast({ show: true, message: 'Failed to generate: ' + (err.message || 'Unknown error'), type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // Render Result View - Using LessonView Component
  if (generated && !loading) {
    // Prepare lesson data for LessonView
    const lessonForView = {
      title: lessonState.lesson_plan.title || topic,
      level: lessonState.lesson_plan.level || level,
      duration: lessonState.lesson_plan.duration || `${duration} minutes`,
      learning_objectives: lessonState.objectives,
      sections: lessonState.sections,
      key_takeaways: lessonState.key_takeaways,
      resources: lessonState.resources,
      quiz: lessonState.quiz,
      ppt_url: lessonState.ppt_url,
      pdf_url: lessonState.pdf_url
    };

    return (
      <>
        {/* LessonView Component */}
        <LessonView
          lesson={lessonForView}
          topic={topic}
          onBack={() => setGenerated(false)}
        />

        {toast.show && (
          <Toast
            type={toast.type}
            message={toast.message}
            onClose={() => setToast({ ...toast, show: false })}
          />
        )}
      </>
    );
  }

  // Loading View
  if (loading) {
    return <GenieLoader message={progressMessage} />;
  }

  // === Default: "Copilot" Prompt Interface ===
  return (
    <div className="copilot-container" style={hideSidebar ? { marginLeft: 0 } : {}}>

      {/* Stats Header (Moved from Footer) */}
      <div className="stats-header">
        <div className="stat-pill">
          <Sparkles size={14} className="text-orange-500" />
          <span>{freeGenerations} free generations left</span>
        </div>
        <div className="stat-pill">
          <History size={14} className="text-blue-500" />
          <span>{used} total created</span>
        </div>
      </div>

      {/* Greeting Section */}
      <div className="greeting-section">
        <h1 className="greeting-text">
          {getGreeting()}, {user?.full_name?.split(' ')[0] || 'Teacher'}.
        </h1>
        <p className="greeting-subtext">What would you like to teach today?</p>
      </div>

      {/* Mobile Options - Above prompt bar for Claude-like feel */}
      <div className="mobile-options-wrapper">
        {/* Mobile Options Toggle - ChatGPT/Gemini Style */}
        <button
          className={`mobile-options-toggle ${showMobileOptions ? 'active' : ''}`}
          onClick={() => setShowMobileOptions(!showMobileOptions)}
        >
          <SlidersHorizontal size={16} />
          <span>Options</span>
          <ChevronDown size={14} />
        </button>

        {/* Mobile Options Panel */}
        <div className={`mobile-options-panel ${showMobileOptions ? 'open' : ''}`}>
          <div className="mobile-option-row">
            <label className="mobile-option-label">
              <GraduationCap size={18} />
              Level
            </label>
            <select
              className="mobile-option-select"
              value={level}
              onChange={(e) => setLevel(e.target.value)}
            >
              <option value="school">School</option>
              <option value="undergraduate">Undergraduate</option>
              <option value="postgraduate">Postgraduate</option>
              <option value="professional">Professional</option>
            </select>
          </div>
          <div className="mobile-option-row">
            <label className="mobile-option-label">
              <Clock size={18} />
              Duration
            </label>
            <select
              className="mobile-option-select"
              value={duration}
              onChange={(e) => setDuration(e.target.value)}
            >
              <option value="20">20 min</option>
              <option value="30">30 min</option>
              <option value="60">60 min</option>
              <option value="90">90 min</option>
              <option value="120">120 min</option>
            </select>
          </div>
          <div className="mobile-option-row">
            <label className="mobile-option-label">
              <FileText size={18} />
              Format
            </label>
            <select
              className="mobile-option-select"
              value={contentType}
              onChange={(e) => setContentType(e.target.value)}
            >
              <option value="both">Slides + Notes</option>
              <option value="slides">Slides Only</option>
              <option value="notes">Notes Only</option>
            </select>
          </div>
          <div className="mobile-option-row">
            <label className="mobile-option-label">
              <Zap size={18} />
              Include Quiz
            </label>
            <button
              className={`mobile-quiz-toggle ${includeQuiz ? 'active' : ''}`}
              onClick={() => setIncludeQuiz(!includeQuiz)}
            >
              {includeQuiz ? 'Yes' : 'No'}
            </button>
          </div>
        </div>
      </div>

      {/* The Magic Prompt Bar */}
      <div className="prompt-bar-container">
        <div className="prompt-bar">
          {/* Input */}
          <textarea
            ref={textareaRef}
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Describe your lesson topic..."
            className="prompt-textarea"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleGenerate();
              }
            }}
          />
          {/* Generate Button */}
          <button
            className="btn-generate-copilot"
            onClick={handleGenerate}
            disabled={!topic.trim()}
          >
            <ArrowUp size={24} strokeWidth={3} />
          </button>
        </div>

        {/* Smart Context Pills - Desktop only */}
        <div className="context-pills">
          {/* Level Pill */}
          <div className="relative">
            <button
              className={`context-pill ${activePopover === 'level' ? 'active' : ''}`}
              onClick={() => setActivePopover(activePopover === 'level' ? null : 'level')}
            >
              <GraduationCap size={16} />
              <span className="capitalize">{level}</span>
              <ChevronDown size={14} />
            </button>
            {activePopover === 'level' && (
              <div className="popover-menu">
                {['school', 'undergraduate', 'postgraduate', 'professional'].map(l => (
                  <div
                    key={l}
                    className={`popover-item ${level === l ? 'selected' : ''}`}
                    onClick={() => { setLevel(l); setActivePopover(null); }}
                  >
                    {l.charAt(0).toUpperCase() + l.slice(1)}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Duration Pill */}
          <div className="relative">
            <button
              className={`context-pill ${activePopover === 'duration' ? 'active' : ''}`}
              onClick={() => setActivePopover(activePopover === 'duration' ? null : 'duration')}
            >
              <Clock size={16} />
              <span>{duration} min</span>
              <ChevronDown size={14} />
            </button>
            {activePopover === 'duration' && (
              <div className="popover-menu">
                {['20', '30', '60', '90', '120'].map(d => (
                  <div
                    key={d}
                    className={`popover-item ${duration === d ? 'selected' : ''}`}
                    onClick={() => { setDuration(d); setActivePopover(null); }}
                  >
                    {d} Minutes
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Content Type Pill */}
          <div className="relative">
            <button
              className={`context-pill ${activePopover === 'type' ? 'active' : ''}`}
              onClick={() => setActivePopover(activePopover === 'type' ? null : 'type')}
            >
              <FileText size={16} />
              <span>{contentType === 'both' ? 'Slides + Notes' : contentType}</span>
              <ChevronDown size={14} />
            </button>
            {activePopover === 'type' && (
              <div className="popover-menu">
                {[
                  { id: 'both', label: 'Slides + Notes' },
                  { id: 'slides', label: 'Slides Only' },
                  { id: 'notes', label: 'Notes Only' }
                ].map(t => (
                  <div
                    key={t.id}
                    className={`popover-item ${contentType === t.id ? 'selected' : ''}`}
                    onClick={() => { setContentType(t.id); setActivePopover(null); }}
                  >
                    {t.label}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Quiz Toggle (Simple) */}
          <button
            className={`context-pill ${includeQuiz ? 'active' : ''}`}
            onClick={() => setIncludeQuiz(!includeQuiz)}
            style={{ borderColor: includeQuiz ? '#f59e0b' : '' }}
          >
            <Zap size={16} className={includeQuiz ? 'fill-orange-500 text-orange-500' : ''} />
            <span>Quiz: {includeQuiz ? 'On' : 'Off'}</span>
          </button>
        </div>

        {/* Suggestion Chips (Only if clear) */}
        {!topic && (
          <div className="suggestion-chips">
            {[
              "Photosynthesis for Grade 5",
              "Introduction to Python Programming",
              "Shakespeare's Macbeth Analysis"
            ].map((s, i) => (
              <button key={i} className="suggestion-chip" onClick={() => setTopic(s)}>
                {s}
              </button>
            ))}
          </div>
        )}


        {/* --- Live Preview Cards (When topic entered) - Hidden on Mobile --- */}
        {topic && !isMobileView && (
          <div className="cognitive-load-section mt-6 grid grid-cols-1 md:grid-cols-2 gap-4 animate-in fade-in slide-in-from-top-2 duration-500">

            {/* Cognitive Load Gauge - New Animated Component */}
            <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-lg flex items-center justify-center">
              <CognitiveLoadGauge level={level} duration={duration} />
            </div>
          </div>
        )}
      </div>

      {/* Feedback Enforcement Modal */}
      {showFeedbackModal && (
        <FeedbackModal
          onClose={() => setShowFeedbackModal(false)}
          onUnlock={() => {
            setToast({ show: true, message: "Thank you! Your remaining trials have been unlocked.", type: 'success' });
          }}
        />
      )}

      {/* Session Blueprint Confirmation Modal */}
      <SessionBlueprintModal
        isOpen={showBlueprintModal}
        onClose={() => setShowBlueprintModal(false)}
        onGenerate={handleConfirmGenerate}
        topic={topic}
        level={level}
        duration={duration}
        contentType={contentType}
        includeQuiz={includeQuiz}
        quizDuration={quizDuration}
        quizMarks={quizMarks}
        profile={profile}
      />

      {toast.show && (
        <Toast
          type={toast.type}
          message={toast.message}
          onClose={() => setToast({ ...toast, show: false })}
        />
      )}
    </div>
  );
};

export default Generator;
