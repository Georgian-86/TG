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

const mascotImage = '/TechGenieMascot.png';

const Generator = ({ backButton, hideSidebar = false }) => {
  const navigate = useNavigate();
  const { user, refreshUser } = useAuth();
  const textareaRef = useRef(null);

  const clearSession = () => {
    localStorage.removeItem('current_lesson_session');
    setGenerated(false);
    setTopic('');
    setLessonState({
      lesson_plan: {},
      objectives: [],
      sections: [],
      key_takeaways: [],
      resources: [],
      quiz: null,
      ppt_url: '',
      pdf_url: ''
    });
  };

  // Feedback Modal State
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });

  // State
  const [topic, setTopic] = useState('');
  const [level, setLevel] = useState('');
  const [duration, setDuration] = useState('');
  const [contentType, setContentType] = useState('');
  const [includeQuiz, setIncludeQuiz] = useState(false);
  const [quizDuration, setQuizDuration] = useState('10');
  const [quizMarks, setQuizMarks] = useState('20');

  // Advanced Options
  const [includeRBT, setIncludeRBT] = useState(true);
  const [loPoMapping, setLoPoMapping] = useState(false);
  const [iksIntegration, setIksIntegration] = useState(false);

  // Generation State
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [generated, setGenerated] = useState(false);
  const [showSuccessScreen, setShowSuccessScreen] = useState(false);
  const [finalGenerationTime, setFinalGenerationTime] = useState(0);
  const [disclaimerAcked, setDisclaimerAcked] = useState(false);
  const [feedbackUnlocked, setFeedbackUnlocked] = useState(false);

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

  // Persistence Logic: Save state on change
  useEffect(() => {
    if (generated && lessonState.lesson_plan) {
      const sessionData = {
        lessonState,
        generated,
        topic,
        level,
        duration,
        showSuccessScreen: false, // Don't show success screen on reload
        finalGenerationTime,
        timestamp: Date.now()
      };
      localStorage.setItem('current_lesson_session', JSON.stringify(sessionData));
    }
  }, [generated, lessonState, topic, level, duration, finalGenerationTime]);

  // Persistence Logic: Restore state on mount
  useEffect(() => {
    const savedSession = localStorage.getItem('current_lesson_session');
    if (savedSession) {
      try {
        const parsed = JSON.parse(savedSession);
        // Only restore if less than 24 hours old
        if (Date.now() - parsed.timestamp < 24 * 60 * 60 * 1000) {
          setLessonState(parsed.lessonState);
          setGenerated(parsed.generated);
          setTopic(parsed.topic);
          setLevel(parsed.level);
          setDuration(parsed.duration);
          setFinalGenerationTime(parsed.finalGenerationTime);
          // We don't restore showSuccessScreen to avoid re-triggering animations
        } else {
          localStorage.removeItem('current_lesson_session');
        }
      } catch (e) {
        console.error('Failed to restore session', e);
      }
    }
  }, []);

  // Dynamic Placeholder Logic
  const [placeholderText, setPlaceholderText] = useState('');
  useEffect(() => {
    const phases = [
      { text: "Enter the topic", delay: 1000 },
      { text: "", delay: 500 },
      { text: "Machine Learning Fundamentals", delay: 2000 },
      { text: "", delay: 500 },
      { text: "Strategic Management & Leadership", delay: 2000 },
      { text: "", delay: 500 },
      { text: "Enter the topic", delay: 1000 },
      { text: "", delay: 500 },
      { text: "Human Anatomy & Physiology", delay: 2000 },
      { text: "", delay: 500 },
      { text: "Cloud Computing Architecture", delay: 2000 },
      { text: "", delay: 500 },
      { text: "Enter the topic", delay: 1000 },
      { text: "", delay: 500 },
      { text: "Financial Accounting Basics", delay: 2000 },
      { text: "", delay: 500 },
      { text: "Pharmacology & Drug Interactions", delay: 2000 },
      { text: "", delay: 500 }
    ];

    let currentPhase = 0;
    let currentChar = 0;
    let isDeleting = false;
    let timeoutId;

    const type = () => {
      const phase = phases[currentPhase % phases.length];
      const fullText = phase.text;
      const speed = isDeleting ? 50 : 100;

      if (!isDeleting && currentChar < fullText.length) {
        setPlaceholderText(fullText.substring(0, currentChar + 1));
        currentChar++;
        timeoutId = setTimeout(type, speed);
      } else if (isDeleting && currentChar > 0) {
        setPlaceholderText(fullText.substring(0, currentChar - 1));
        currentChar--;
        timeoutId = setTimeout(type, speed);
      } else {
        // Finished typing or deleting
        if (!isDeleting) {
          // Pause before deleting
          timeoutId = setTimeout(() => {
            isDeleting = true;
            type();
          }, phase.delay);
        } else {
          // Move to next phase
          isDeleting = false;
          currentPhase++;
          timeoutId = setTimeout(type, 500);
        }
      }
    };

    timeoutId = setTimeout(type, 1000);

    return () => clearTimeout(timeoutId);
  }, []);

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
      setProgressMessage('🎮 Generating interactive scenarios...');
      await new Promise(resolve => setTimeout(resolve, 600));
    }

    setProgress(100);
    setProgressMessage('🚀 Finalizing your lesson package...');
  };

  const handleGenerate = async () => {
    console.log("Generate button clicked");
    console.log("Topic:", topic);
    console.log("User:", user);

    if (!topic.trim()) {
      console.log("Topic is empty");
      return;
    }

    // Check for Mandatory Feedback (User has used >= 2 lessons & no feedback)
    console.log("Checking feedback lock:", {
      feedbackUnlocked,
      tier: user?.subscription_tier,
      used: user?.lessons_this_month,
      provided: user?.feedback_provided
    });

    if (!feedbackUnlocked && user?.subscription_tier === 'free' && user?.lessons_this_month >= 2 && !user?.feedback_provided) {
      console.log("Feedback lock active - showing modal");
      setShowFeedbackModal(true);
      return;
    }

    console.log("Opening blueprint modal");
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
      const startTime = Date.now();
      simulateGenerationPipeline();

      const lessonData = await lessonService.generateLesson({
        topic: topic.trim(),
        level: level || 'undergraduate',
        duration: parseInt(duration || '30'),
        includeQuiz,
        quizDuration: includeQuiz ? parseInt(quizDuration) : undefined,
        quizMarks: includeQuiz ? parseInt(quizMarks) : undefined,
        includeRBT,
        loPoMapping,
        iksIntegration
      });


      const endTime = Date.now();
      const totalTime = (endTime - startTime) / 1000;
      setFinalGenerationTime(totalTime);

      setLessonState({
        lesson_plan: {
          title: lessonData.topic || topic,
          level: lessonData.level || level || 'Undergraduate',
          duration: `${lessonData.duration || duration || '30'} minutes`,
        },
        objectives: lessonData.learning_objectives || [],
        sections: lessonData.lesson_plan || [],
        key_takeaways: lessonData.key_takeaways || [],
        resources: lessonData.resources || [],
        quiz: lessonData.quiz || null,
        ppt_url: lessonData.ppt_url || '',
        pdf_url: lessonData.pdf_url || '',
        generation_time: totalTime
      });

      setGenerated(true);
      setShowSuccessScreen(true);

      if (refreshUser) await refreshUser();

      // Trigger Upsell AGAIN after generation
      setTimeout(() => {
        window.dispatchEvent(new Event('trigger-upgrade-modal'));
      }, 5000);

      // Auto-hide success screen after 3 seconds
      setTimeout(() => {
        setShowSuccessScreen(false);
      }, 3000);

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
      level: lessonState.lesson_plan.level || level || 'Undergraduate',
      duration: lessonState.lesson_plan.duration || `${duration || 30} minutes`,
      learning_objectives: lessonState.objectives,
      sections: lessonState.lesson_plan.sections || lessonState.sections,
      key_takeaways: lessonState.key_takeaways,
      resources: lessonState.resources,
      quiz: lessonState.quiz,
      ppt_url: lessonState.ppt_url,
      pdf_url: lessonState.pdf_url,
      include_rbt: includeRBT,
      generation_time: finalGenerationTime
    };

    return (
      <>
        <LessonView
          lesson={lessonForView}
          topic={topic}
          onBack={clearSession}
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

  // Success Screen
  if (showSuccessScreen) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-white">
        <div className="text-center p-8 bg-white rounded-2xl shadow-xl border border-gray-100 max-w-md w-full animate-in fade-in zoom-in duration-500">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle size={40} className="text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Lesson Generated!</h2>
          <p className="text-gray-500 mb-6">Your personalized lesson plan is ready.</p>
          <div className="inline-flex items-center px-4 py-2 bg-blue-50 text-blue-700 rounded-full font-medium">
            <Clock size={16} className="mr-2" />
            Generated in {finalGenerationTime.toFixed(2)} seconds
          </div>
        </div>
      </div>
    );
  }

  // Loading View
  if (loading) {
    return <GenieLoader message={progressMessage} />;
  }

  const handleDurationSelect = (d) => {
    setDuration(d);
    setActivePopover(null);
  };

  const handleFormatSelect = (f) => {
    setContentType(f);
    setActivePopover(null);
  };

  const handleLevelSelect = (l) => {
    setLevel(l.toLowerCase());
    setActivePopover(null);
  };

  // Mobile option handlers
  const handleMobileOptionSelect = (type, value) => {
    switch (type) {
      case 'level': setLevel(value.toLowerCase()); break;
      case 'time': setDuration(value.replace(' mins', '')); break;
      case 'resources': setContentType(value.toLowerCase()); break; // Mapping needs adjustment if values differ
      default: break;
    }
  };

  // === Default: "Copilot" Prompt Interface ===
  return (
    <div className="copilot-container" style={hideSidebar ? { marginLeft: 0 } : {}}>

      {/* Back Button for Mobile/Tablet */}
      {backButton && (
        <button
          onClick={backButton}
          className="btn-back-floating"
          style={{ position: 'absolute', top: '20px', left: '20px', zIndex: 50, background: 'white', padding: '8px 16px', borderRadius: '20px', border: '1px solid #eee', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}
        >
          <User size={16} /> Dashboard
        </button>
      )}

      {/* Mascot - Moved above stats */}
      <img src={mascotImage} alt="TeachGenie Mascot" className="mascot-image" />

      {/* Stats Header */}
      <div className="stats-header">
        <div className="stat-pill">
          <Sparkles size={14} className="text-yellow-500" />
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

      {/* Mobile Options Logic (Hidden on Desktop) */}
      <div className="mobile-options-wrapper">
        <button
          className="mobile-options-toggle"
          onClick={() => setShowMobileOptions(!showMobileOptions)}
        >
          <SlidersHorizontal size={16} />
          {showMobileOptions ? 'Hide Lesson Options' : 'Customize Lesson Options'}
        </button>

        {showMobileOptions && (
          <div className="mobile-options-panel" style={{ marginTop: '16px', background: 'white', padding: '16px', borderRadius: '16px', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
            <div className="mobile-option-row" style={{ marginBottom: '12px' }}>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: '500', color: '#6b7280', marginBottom: '8px' }}>Education Level</label>
              <select
                value={level ? level.charAt(0).toUpperCase() + level.slice(1) : ''}
                onChange={(e) => handleMobileOptionSelect('level', e.target.value)}
                style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
              >
                <option value="">Select Level</option>
                <option value="School">School</option>
                <option value="Undergraduate">Undergraduate</option>
                <option value="Postgraduate">Postgraduate</option>
                <option value="Professional">Professional</option>
              </select>
            </div>

            <div className="mobile-option-row">
              <label style={{ display: 'block', fontSize: '13px', fontWeight: '500', color: '#6b7280', marginBottom: '8px' }}>Duration</label>
              <select
                value={duration ? `${duration} mins` : ''}
                onChange={(e) => handleMobileOptionSelect('time', e.target.value)}
                style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
              >
                <option value="">Select Duration</option>
                <option value="30 mins">30 mins</option>
                <option value="45 mins">45 mins</option>
                <option value="60 mins">60 mins</option>
                <option value="90 mins">90 mins</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Prompt Bar */}
      <div className={`prompt-bar-container ${loading ? 'loading-active' : ''}`}>
        <div className="prompt-bar">
          <textarea
            ref={textareaRef}
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder={placeholderText}
            className="prompt-textarea"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleGenerate();
              }
            }}
          />

          <button
            className="btn-generate-copilot"
            disabled={!topic.trim() || loading}
            onClick={handleGenerate}
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <ArrowUp size={24} />
            )}
          </button>
        </div>
      </div>

      {/* Context Pills Row */}
      <div className="context-pills">

        {/* Level Pill */}
        <div className="relative">
          <button
            className={`context-pill ${activePopover === 'level' ? 'active' : ''}`}
            onClick={() => setActivePopover(activePopover === 'level' ? null : 'level')}
          >
            <GraduationCap size={16} />
            <span className="capitalize">{level || 'Level'}</span>
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

        {/* Time Pill */}
        <div className="relative">
          <button
            className={`context-pill ${activePopover === 'duration' ? 'active' : ''}`}
            onClick={() => setActivePopover(activePopover === 'duration' ? null : 'duration')}
          >
            <Clock size={16} />
            <span>{duration ? `${duration} min` : 'Time'}</span>
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

        {/* Resources Pill */}
        <div className="relative">
          <button
            className={`context-pill ${activePopover === 'type' ? 'active' : ''}`}
            onClick={() => setActivePopover(activePopover === 'type' ? null : 'type')}
          >
            <FileText size={16} />
            <span>{contentType === 'both' ? 'Slides + Notes' : contentType === 'slides' ? 'Slides Only' : contentType === 'notes' ? 'Notes Only' : 'Resources'}</span>
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

        {/* Scenario Quiz Dropdown */}
        <div className="relative">
          <button
            className={`context-pill ${activePopover === 'quiz' ? 'active' : ''}`}
            onClick={() => setActivePopover(activePopover === 'quiz' ? null : 'quiz')}
          >
            <Zap size={16} className={includeQuiz ? 'fill-orange-500 text-orange-500' : ''} />
            <span>Scenarios: {includeQuiz ? 'Include' : 'Exclude'}</span>
            <ChevronDown size={14} />
          </button>
          {activePopover === 'quiz' && (
            <div className="popover-menu">
              <div
                className={`popover-item ${includeQuiz ? 'selected' : ''}`}
                onClick={() => { setIncludeQuiz(true); setActivePopover(null); }}
              >
                Include
              </div>
              <div
                className={`popover-item ${!includeQuiz ? 'selected' : ''}`}
                onClick={() => { setIncludeQuiz(false); setActivePopover(null); }}
              >
                Exclude
              </div>
            </div>
          )}
        </div>

        {/* RBT Dropdown */}
        <div className="relative">
          <button
            className={`context-pill ${activePopover === 'rbt' ? 'active' : ''}`}
            onClick={() => setActivePopover(activePopover === 'rbt' ? null : 'rbt')}
          >
            <span>{includeRBT ? 'RBT: Include' : 'RBT: Exclude'}</span>
            <ChevronDown size={14} />
          </button>
          {activePopover === 'rbt' && (
            <div className="popover-menu">
              <div
                className={`popover-item ${includeRBT ? 'selected' : ''}`}
                onClick={() => { setIncludeRBT(true); setActivePopover(null); }}
              >
                Include
              </div>
              <div
                className={`popover-item ${!includeRBT ? 'selected' : ''}`}
                onClick={() => { setIncludeRBT(false); setActivePopover(null); }}
              >
                Exclude
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Suggestion Chips */}
      {topic && !isMobileView && (
        <div className="cognitive-load-section mt-6 grid grid-cols-1 md:grid-cols-2 gap-4 animate-in fade-in slide-in-from-top-2 duration-500">
          <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-lg flex items-center justify-center">
            <CognitiveLoadGauge level={level} duration={duration} />
          </div>
        </div>
      )}

      {/* Feedback Enforcement Modal */}
      {showFeedbackModal && (
        <FeedbackModal
          onClose={() => setShowFeedbackModal(false)}
          onUnlock={() => {
            setFeedbackUnlocked(true);
            setToast({ show: true, message: "Thank you! Your remaining trials have been unlocked.", type: 'success' });
          }}
        />
      )}

      {/* Session Blueprint Confirmation Modal */}
      {showBlueprintModal && (
        <SessionBlueprintModal
          isOpen={showBlueprintModal}
          onClose={() => setShowBlueprintModal(false)}
          onGenerate={handleConfirmGenerate}
          topic={topic}
          level={level}
          duration={duration}
          contentType={contentType}
          profile={profile}
          includeQuiz={includeQuiz}
          quizDuration={quizDuration}
          quizMarks={quizMarks}
          includeRBT={includeRBT}
          loPoMapping={loPoMapping}
          iksIntegration={iksIntegration}
        />
      )}

      {toast.show && (
        <Toast
          type={toast.type}
          message={toast.message}
          onClose={() => setToast({ ...toast, show: false })}
        />
      )}
    </div >
  );
};

export default Generator;
