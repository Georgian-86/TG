import React, { useEffect } from 'react';
import GenieLoader from './GenieLoader';
import '../styles/splash-screen.css';

const SplashScreen = ({ onComplete }) => {
  useEffect(() => {
    // Show splash screen for 3.5 seconds, then transition
    const timer = setTimeout(() => {
      const splashContainer = document.querySelector('.splash-screen-container');
      if (splashContainer) {
        splashContainer.classList.add('fade-out');
      }
      
      // Call onComplete after fade animation completes
      const fadeTimer = setTimeout(() => {
        onComplete();
      }, 500);
      
      return () => clearTimeout(fadeTimer);
    }, 3000);

    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <div className="splash-screen-container">
      <div className="splash-screen-overlay">
        <GenieLoader message="✨ Welcome to Teach Genie - Your AI Teaching Assistant ✨" />
      </div>
    </div>
  );
};

export default SplashScreen;
