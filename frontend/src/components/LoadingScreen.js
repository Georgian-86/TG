import React, { useEffect, useState } from 'react';
import '../styles/loading-screen.css';

const LoadingScreen = ({ onComplete }) => {
  const [visibleWords, setVisibleWords] = useState([]);
  const words = [
    { text: 'Teach', delay: 500 },
    { text: 'Genie', delay: 800 }
  ];

  useEffect(() => {
    words.forEach((word, index) => {
      setTimeout(() => {
        setVisibleWords(prev => [...prev, index]);
      }, word.delay);
    });

    const timer = setTimeout(() => {
      if (onComplete) {
        onComplete();
      }
    }, 3500);

    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <div className="loading-screen">
      <div className="loading-container">
        {/* Floating Genie Logo */}
        <div className="floating-genie">
          <img src="/TechGenieMascot.png" alt="TeachGenie" className="genie-image" />
          <div className="genie-glow"></div>
        </div>

        {/* Word by Word Title */}
        <div className="loading-title">
          {words.map((word, index) => (
            <span
              key={index}
              className={`word ${index === 0 ? 'blue-text' : 'orange-text'} ${visibleWords.includes(index) ? 'visible' : ''
                }`}
            >
              {word.text}
            </span>
          ))}
        </div>

        {/* Subtitle */}
        <div className="loading-subtitle">
          Are you ready for agentic magic ?
        </div>

        {/* Loading Bar */}
        <div className="loading-bar">
          <div className="loading-progress"></div>
        </div>
      </div>
    </div>
  );
};

export default LoadingScreen;