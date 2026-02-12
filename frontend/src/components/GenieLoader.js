import React, { useState, useEffect } from 'react';
import { Clock, Zap, FileText, Target, Lightbulb, CheckCircle, Loader, Brain, BookOpen } from 'lucide-react';
import GenieLampSVG from './GenieLampSVG';
import '../styles/genie-loader.css';

export default function GenieLoader({ message = '' }) {
  const [elapsedTime, setElapsedTime] = useState(0); // in milliseconds
  const [currentStage, setCurrentStage] = useState(0);


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
        cardBg: 'linear-gradient(135deg, rgba(30, 58, 138, 0.9) 0%, rgba(30, 64, 175, 0.9) 100%)',
        iconBg: 'rgba(255, 255, 255, 0.2)',
        iconColor: '#ffffff',
        textColor: '#ffffff',
        subTextColor: 'rgba(255, 255, 255, 0.8)',
        borderColor: 'rgba(59, 130, 246, 0.5)'
      },
      'Structure Agent': {
        cardBg: 'linear-gradient(135deg, rgba(37, 99, 235, 0.9) 0%, rgba(59, 130, 246, 0.9) 100%)', // Blue
        iconBg: 'rgba(255, 255, 255, 0.2)',
        iconColor: '#ffffff',
        textColor: '#ffffff',
        subTextColor: 'rgba(255, 255, 255, 0.9)',
        borderColor: 'rgba(147, 197, 253, 0.5)'
      },
      'Objectives Agent': {
        cardBg: 'linear-gradient(135deg, rgba(5, 150, 105, 0.9) 0%, rgba(16, 185, 129, 0.9) 100%)', // Green
        iconBg: 'rgba(255, 255, 255, 0.2)',
        iconColor: '#ffffff',
        textColor: '#ffffff',
        subTextColor: 'rgba(255, 255, 255, 0.9)',
        borderColor: 'rgba(110, 231, 183, 0.5)'
      },
      'Content Agent': {
        cardBg: 'linear-gradient(135deg, rgba(217, 119, 6, 0.9) 0%, rgba(245, 158, 11, 0.9) 100%)', // Orange
        iconBg: 'rgba(255, 255, 255, 0.2)',
        iconColor: '#ffffff',
        textColor: '#ffffff',
        subTextColor: 'rgba(255, 255, 255, 0.9)',
        borderColor: 'rgba(253, 186, 116, 0.5)'
      },
      'Assessment Agent': {
        cardBg: 'linear-gradient(135deg, rgba(124, 58, 237, 0.9) 0%, rgba(139, 92, 246, 0.9) 100%)', // Purple
        iconBg: 'rgba(255, 255, 255, 0.2)',
        iconColor: '#ffffff',
        textColor: '#ffffff',
        subTextColor: 'rgba(255, 255, 255, 0.9)',
        borderColor: 'rgba(196, 181, 253, 0.5)'
      },
      'Quiz Agent': {
        cardBg: 'linear-gradient(135deg, rgba(219, 39, 119, 0.9) 0%, rgba(236, 72, 153, 0.9) 100%)', // Pink
        iconBg: 'rgba(255, 255, 255, 0.2)',
        iconColor: '#ffffff',
        textColor: '#ffffff',
        subTextColor: 'rgba(255, 255, 255, 0.9)',
        borderColor: 'rgba(249, 168, 212, 0.5)'
      }
    };

    return colorSchemes[agentName] || colorSchemes['System'];
  };



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
                TeachGenie agents on the GO....
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
              {elapsedTime < 60000 && (
                <div className="timer-message">⚡ Lightning Fast Generation</div>
              )}
            </div>

            {/* Current Agent Card - DYNAMIC FLASHCARD STYLE */}
            <div
              className="agent-spotlight-card"
              style={{
                background: agentColors.cardBg,
                borderColor: agentColors.borderColor,
                boxShadow: `0 20px 40px ${agentColors.borderColor}`
              }}
            >
              <div
                className="agent-icon-large"
                style={{
                  background: agentColors.iconBg,
                  color: agentColors.iconColor,
                  boxShadow: 'none' // Remove specific shadow to blend
                }}
              >
                <CurrentIcon size={32} className="pulsing-icon" />
              </div>
              <div className="agent-details-large">
                <div className="agent-status-text" style={{ color: agentColors.subTextColor }}>Currently Working</div>
                <div className="agent-name-large" style={{ color: agentColors.textColor }}>
                  {currentAgent?.agent}
                </div>
                <div className="agent-task-text" style={{ color: agentColors.subTextColor }}>{currentAgent?.name}</div>
              </div>
              <div className="agent-loading-bar" style={{ background: 'rgba(255,255,255,0.2)' }}>
                <div className="loading-bar-fill" style={{ background: '#ffffff' }}></div>
              </div>
            </div>


          </div>
        </div>
      </div>
    </div>
  );
}
