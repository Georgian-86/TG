import React, { useState, useEffect } from 'react';
import { Clock, Zap, FileText, Target, Lightbulb, CheckCircle, Loader, Brain, BookOpen } from 'lucide-react';
import GenieLampSVG from './GenieLampSVG';
import '../styles/genie-loader.css';

export default function GenieLoader({ message = '' }) {
  const [elapsedTime, setElapsedTime] = useState(0); // in milliseconds
  const [currentStage, setCurrentStage] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  // Agent stages with faster progression to show all agents
  const stages = [
    { name: 'Initializing System', agent: 'System', icon: Loader, duration: 2000 },
    { name: 'Analyzing Structure', agent: 'Structure Agent', icon: FileText, duration: 4000 },
    { name: 'Crafting Objectives', agent: 'Objectives Agent', icon: Target, duration: 5000 },
    { name: 'Generating Content', agent: 'Content Agent', icon: Brain, duration: 8000 },
    { name: 'Creating Assessments', agent: 'Assessment Agent', icon: Lightbulb, duration: 6000 },
    { name: 'Building Quiz', agent: 'Quiz Agent', icon: BookOpen, duration: 5000 },
    { name: 'Finalizing Lesson', agent: 'System', icon: CheckCircle, duration: 100000 }
  ];

  // Timer effect - counts in ms
  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedTime(prev => prev + 10);
    }, 10);

    return () => clearInterval(timer);
  }, []);

  // Stage progression effect
  useEffect(() => {
    let cumulativeTime = 0;
    for (let i = 0; i < stages.length; i++) {
      cumulativeTime += stages[i].duration;
      if (elapsedTime < cumulativeTime) {
        setCurrentStage(i);
        break;
      }
    }
  }, [elapsedTime]);

  // Format time as seconds.milliseconds (e.g., 42.35)
  const formatTime = (ms) => {
    const seconds = Math.floor(ms / 1000);
    const milliseconds = Math.floor((ms % 1000) / 10);
    return `${seconds}.${String(milliseconds).padStart(2, '0')}`;
  };

  // Get agent-specific color scheme
  const getAgentColors = (agentName) => {
    const colorSchemes = {
      'System': {
        bg: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
        icon: '#8b5cf6',
        glow: 'rgba(139, 92, 246, 0.3)'
      },
      'Structure Agent': {
        bg: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
        icon: '#3b82f6',
        glow: 'rgba(59, 130, 246, 0.3)'
      },
      'Objectives Agent': {
        bg: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
        icon: '#10b981',
        glow: 'rgba(16, 185, 129, 0.3)'
      },
      'Content Agent': {
        bg: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
        icon: '#f59e0b',
        glow: 'rgba(245, 158, 11, 0.3)'
      },
      'Assessment Agent': {
        bg: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
        icon: '#8b5cf6',
        glow: 'rgba(139, 92, 246, 0.3)'
      },
      'Quiz Agent': {
        bg: 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)',
        icon: '#ec4899',
        glow: 'rgba(236, 72, 153, 0.3)'
      }
    };

    return colorSchemes[agentName] || colorSchemes['System'];
  };

  // Check if we've reached the final stage (detecting completion)
  useEffect(() => {
    if (currentStage === stages.length - 1 && elapsedTime > 30000) {
      setIsComplete(true);
    }
  }, [currentStage, elapsedTime]);

  const CurrentIcon = stages[currentStage]?.icon || Loader;
  const currentAgent = stages[currentStage];
  const agentColors = getAgentColors(currentAgent?.agent);

  return (
    <div className="genie-loader-container">
      <div className="genie-loading-wrapper">
        {/* Background Effects */}
        <div className="magical-background">
          <div className="magic-particle particle-1"></div>
          <div className="magic-particle particle-2"></div>
          <div className="magic-particle particle-3"></div>
          <div className="magic-particle particle-4"></div>
          <div className="magic-particle particle-5"></div>
        </div>

        {/* Main Content Grid */}
        <div className="loader-content-grid">
          {/* Left: Lamp & Text */}
          <div className="lamp-section">
            <div className="lamp-svg-container">
              <GenieLampSVG />

              {/* Magic Smoke */}
              <div className="magic-smoke">
                <div className="smoke-cloud smoke-1"></div>
                <div className="smoke-cloud smoke-2"></div>
                <div className="smoke-cloud smoke-3"></div>
              </div>

              <div className="lamp-glow"></div>
            </div>

            <div className="loading-text-container">
              <h2 className="loading-title-new">Crafting Your</h2>
              <h1 className="loading-title-main">Perfect Lesson</h1>
              <p className="loading-subtitle">
                Powered by Advanced AI Agents
              </p>
            </div>
          </div>

          {/* Right: Progress Info */}
          <div className="progress-section">
            {/* Timer Card */}
            <div className="timer-card-new">
              <div className="timer-header">
                <Clock size={20} />
                <span className="timer-label-new">Generation Time</span>
              </div>
              <div className="timer-display-new">
                {formatTime(elapsedTime)}<span className="timer-unit">s</span>
              </div>
              {!isComplete && elapsedTime < 60000 && (
                <div className="timer-message">⚡ Lightning Fast Generation</div>
              )}
            </div>

            {/* Current Agent Card - ONLY COLOR THE AGENT NAME */}
            <div className="agent-spotlight-card">
              <div className="agent-icon-large">
                <CurrentIcon size={32} className="pulsing-icon" />
              </div>
              <div className="agent-details-large">
                <div className="agent-status-text">Currently Working</div>
                <div className="agent-name-large" style={{ color: agentColors.icon }}>
                  {currentAgent?.agent}
                </div>
                <div className="agent-task-text">{currentAgent?.name}</div>
              </div>
              <div className="agent-loading-bar">
                <div className="loading-bar-fill"></div>
              </div>
            </div>

            {/* Completion Message */}
            {isComplete && (
              <div className="completion-card">
                <CheckCircle size={32} />
                <div className="completion-text">
                  <div className="completion-title">Lesson Ready!</div>
                  <div className="completion-time">
                    Generated in just {formatTime(elapsedTime)} seconds
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
