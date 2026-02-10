import React from 'react';
import { ArrowRight } from 'lucide-react';
import '../styles/how-it-works.css';

export default function HowItWorks() {
  const steps = [
    {
      number: '1',
      title: 'Enter Your Topic',
      description: 'Tell the Genie what you want to teach - be as specific as you want'
    },
    {
      number: '2',
      title: 'Watch the Magic',
      description: 'The Genie emerges and transforms your topic into amazing content in 60 seconds'
    },
    {
      number: '3',
      title: 'Download & Teach',
      description: 'Get presentation slides, lesson plans, quizzes, and resources - ready to use immediately'
    }
  ];

  return (
    <section id="how-it-works" className="how-it-works">
      <div className="container">
        <div className="section-header">
          <h2>How It Works</h2>
          <p>Three simple steps to generate your lecture materials</p>
        </div>

        <div className="hiw-steps-container">
          {steps.map((step, index) => (
            <div key={index}>
              <div className="step-card">
                <div className="step-number">{step.number}</div>
                <h3>{step.title}</h3>
                <p>{step.description}</p>
              </div>
              {index < steps.length - 1 && (
                <div className="step-connector">
                  <svg width="120" height="80" viewBox="0 0 120 80" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                      <linearGradient id={`gradient-${index}`} x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#1e3a8a" />
                        <stop offset="50%" stopColor="#3b82f6" />
                        <stop offset="100%" stopColor="#f59e0b" />
                      </linearGradient>
                    </defs>
                    <path
                      d="M 10 40 Q 40 20, 70 40 T 110 40"
                      stroke={`url(#gradient-${index})`}
                      strokeWidth="3"
                      strokeDasharray="8 4"
                      strokeLinecap="round"
                      fill="none"
                      className="connector-path"
                    />
                    <circle cx="110" cy="40" r="5" fill="#f59e0b" className="connector-dot" />
                  </svg>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
