import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { TypingAnimation } from './TypingAnimation';
import '../styles/hero.css';

const TYPING_WORDS = ["Revolutionize Teaching."];

export default function Hero() {
  const { user } = useAuth();  // Get auth state
  const [visibleWords, setVisibleWords] = useState([]);
  const staticWords = [
    { text: 'One Minute.', class: 'navy-text', delay: 5500 },
    { text: 'Infinite Impact.', class: 'gold-text', delay: 5900 }
  ];

  useEffect(() => {
    staticWords.forEach((word, index) => {
      setTimeout(() => {
        setVisibleWords(prev => [...prev, index]);
      }, word.delay);
    });
  }, []);

  return (
    <section className="hero" id="hero">
      <div className="hero-background">
        <div className="gradient-1"></div>
        <div className="gradient-2"></div>
      </div>

      <div className="container hero-content">
        <div className="hero-text">
          <h1 className="hero-title">
            <span className="title-block typing-line">
              <TypingAnimation
                words={TYPING_WORDS}
                blinkCursor={true}
                duration={220}
                className="navy-text"
              />
            </span>
            {staticWords.map((word, index) => (
              <span key={index} className="title-block">
                <span
                  className={`animated-word ${word.class} ${visibleWords.includes(index) ? 'visible' : ''}`}
                >
                  {word.text}
                </span>
              </span>
            ))}
          </h1>

          <p className="hero-subtitle">
            Your AI Teaching Co-Instructor - Pack your lecture <br className="desktop-break" />
            in about a minute, and let the magic happen.
          </p>

          <div className="hero-buttons">
            <Link to={user ? '/generator' : '/login'} className="btn btn-accent btn-large">
              {user ? 'Go to Dashboard' : 'Start Free Trial'}
            </Link>
            <Link to="/learn-more" className="btn btn-outline btn-large">
              Learn More
            </Link>
          </div>
          <div className="trust-logos">
            <span>Of the teachers</span> • <span>For the teachers</span> • <span>By the teachers</span>
          </div>
        </div>


        <div className="hero-visual">
          <div className="hero-card-wrapper">
            {/* The Character Popping Out */}
            <div className="pop-out-character">
              <img src="/TechGenieMascot.png" alt="TeachGenie Mascot" className="hero-mascot-image" />
            </div>

            {/* The Card Base with Sparkles */}
            <div className="hero-card-base">
              <div className="sparkles-container">
                <div className="sparkle"></div>
                <div className="sparkle"></div>
                <div className="sparkle"></div>
                <div className="sparkle"></div>
                <div className="sparkle"></div>
                <div className="sparkle"></div>
                <div className="sparkle"></div>
                <div className="sparkle"></div>
                <div className="sparkle"></div>
                <div className="sparkle"></div>
                <div className="sparkle"></div>
                <div className="sparkle"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
