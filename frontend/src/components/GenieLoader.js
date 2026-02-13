import React, { useState, useEffect } from 'react';
import { Clock, Zap, FileText, Target, Lightbulb, CheckCircle, Loader, Brain, BookOpen } from 'lucide-react';
import GenieLampSVG from './GenieLampSVG';
import '../styles/genie-loader.css';

export default function GenieLoader({ message = '' }) {
  const [elapsedTime, setElapsedTime] = useState(0); // in milliseconds
  const [currentStage, setCurrentStage] = useState(0);


  // Agent stages - each takes approximately 10 seconds
  const stages = [
    { name: 'Analyzing Structure', agent: 'Structure Agent', icon: FileText, duration: 10000, startTime: 0 },
    { name: 'Crafting Objectives', agent: 'Objectives Agent', icon: Target, duration: 10000, startTime: 10000 },
    { name: 'Generating Content', agent: 'Content Agent', icon: Brain, duration: 10000, startTime: 20000 },
    { name: 'Creating Assessments', agent: 'Assessment Agent', icon: Lightbulb, duration: 10000, startTime: 30000 },
    { name: 'Building Quiz', agent: 'Quiz Agent', icon: BookOpen, duration: 10000, startTime: 40000 },
    { name: 'Finalizing Lesson', agent: 'System Complete', icon: CheckCircle, duration: 100000, startTime: 50000 }
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

  // Calculate progress for each agent
  const getAgentProgress = (stage) => {
    const endTime = stage.startTime + stage.duration;
    
    if (elapsedTime < stage.startTime) {
      return 0; // Not started yet
    } else if (elapsedTime >= endTime) {
      return 100; // Completed
    } else {
      // In progress
      const progress = ((elapsedTime - stage.startTime) / stage.duration) * 100;
      return Math.min(100, Math.max(0, progress));
    }
  };

  // Check if agent is currently active
  const isAgentActive = (index) => {
    return index === currentStage;
  };

  // Check if agent is completed
  const isAgentCompleted = (index) => {
    return elapsedTime >= (stages[index].startTime + stages[index].duration);
  };

  // Format time as seconds.milliseconds (e.g., 42.35)
  const formatTime = (ms) => {
    const seconds = Math.floor(ms / 1000);
    const milliseconds = Math.floor((ms % 1000) / 10);
    return `${seconds}.${String(milliseconds).padStart(2, '0')}`;
  };

  // Get completed state colors for each agent (dimmed version of active colors)
  const getCompletedColors = (agentName) => {
    const completedSchemes = {
      'System': {
        bg: 'rgba(30, 58, 138, 0.25)',
        border: 'rgba(59, 130, 246, 0.4)',
        icon: 'rgba(59, 130, 246, 0.4)',
        text: '#3b82f6',
        check: '#3b82f6'
      },
      'Structure Agent': {
        bg: 'rgba(37, 99, 235, 0.25)',
        border: 'rgba(59, 130, 246, 0.4)',
        icon: 'rgba(59, 130, 246, 0.4)',
        text: '#3b82f6',
        check: '#3b82f6'
      },
      'Objectives Agent': {
        bg: 'rgba(5, 150, 105, 0.25)',
        border: 'rgba(16, 185, 129, 0.4)',
        icon: 'rgba(16, 185, 129, 0.4)',
        text: '#10b981',
        check: '#10b981'
      },
      'Content Agent': {
        bg: 'rgba(217, 119, 6, 0.25)',
        border: 'rgba(245, 158, 11, 0.4)',
        icon: 'rgba(245, 158, 11, 0.4)',
        text: '#f59e0b',
        check: '#f59e0b'
      },
      'Assessment Agent': {
        bg: 'rgba(124, 58, 237, 0.25)',
        border: 'rgba(139, 92, 246, 0.4)',
        icon: 'rgba(139, 92, 246, 0.4)',
        text: '#8b5cf6',
        check: '#8b5cf6'
      },
      'Quiz Agent': {
        bg: 'rgba(219, 39, 119, 0.25)',
        border: 'rgba(236, 72, 153, 0.4)',
        icon: 'rgba(236, 72, 153, 0.4)',
        text: '#ec4899',
        check: '#ec4899'
      },
      'System Complete': {
        bg: 'rgba(16, 185, 129, 0.25)',
        border: 'rgba(16, 185, 129, 0.4)',
        icon: 'rgba(16, 185, 129, 0.4)',
        text: '#10b981',
        check: '#10b981'
      }
    };
    return completedSchemes[agentName] || completedSchemes['System'];
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
      },
      'System Complete': {
        cardBg: 'linear-gradient(135deg, rgba(16, 185, 129, 0.9) 0%, rgba(5, 150, 105, 0.9) 100%)', // Emerald Green
        iconBg: 'rgba(255, 255, 255, 0.2)',
        iconColor: '#ffffff',
        textColor: '#ffffff',
        subTextColor: 'rgba(255, 255, 255, 0.9)',
        borderColor: 'rgba(110, 231, 183, 0.5)'
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
                <Clock size={24} />
                <span className="timer-label-new">Generation Time</span>
              </div>
              <div className="timer-display-new">{formatTime(elapsedTime)}<span className="timer-unit">s</span>
              </div>
              {elapsedTime < 60000 && (
                <div className="timer-message">⚡ Lightning Fast Generation</div>
              )}
            </div>

            {/* Single Active Agent Card - Show only current agent */}
            <div className="agents-grid-single">
              {stages.map((stage, index) => {
                const AgentIcon = stage.icon;
                const colors = getAgentColors(stage.agent);
                const progress = getAgentProgress(stage);
                const isActive = isAgentActive(index);
                
                // Only show the currently active agent
                if (!isActive) return null;

                return (
                  <div
                    key={index}
                    className="agent-card-large active"
                    style={{
                      background: colors.cardBg,
                      borderColor: colors.borderColor,
                      animation: 'fadeInScale 0.5s ease-out'
                    }}
                  >
                    <div className="agent-card-header">
                      <div
                        className="agent-icon-large"
                        style={{
                          background: colors.iconBg,
                          color: colors.iconColor
                        }}
                      >
                        <AgentIcon size={32} className="pulsing-icon" />
                      </div>
                    </div>
                    <div className="agent-card-body">
                      <div 
                        className="agent-name-large" 
                        style={{ 
                          color: colors.textColor
                        }}
                      >
                        {stage.agent}
                      </div>
                      <div 
                        className="agent-task-large" 
                        style={{ 
                          color: colors.subTextColor
                        }}
                      >
                        {stage.name}
                      </div>
                    </div>
                    {/* Progress Bar */}
                    <div className="agent-progress-bar-large" style={{ background: 'rgba(0, 0, 0, 0.3)' }}>
                      <div 
                        className="agent-progress-fill-golden" 
                        style={{ 
                          width: `${progress}%`,
                          transition: 'width 0.3s ease-out'
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>


          </div>
        </div>
      </div>
    </div>
  );
}
