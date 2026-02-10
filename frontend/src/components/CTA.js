import React from 'react';
import { Sparkles, ArrowRight, Users } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/cta.css';

const CTA = () => {
  const { user } = useAuth();  // Get auth state

  return (
    <section className="cta">
      <div className="cta-background">
        <div className="cta-shape cta-shape-1"></div>
        <div className="cta-shape cta-shape-2"></div>
        <div className="cta-shape cta-shape-3"></div>
      </div>

      <div className="container cta-content">
        <div className="cta-header">
          <h2>Ready to Transform Your Teaching?</h2>
          <p>Join thousands of educators who are saving hours every week with Teach Genie</p>
        </div>

        <div className="cta-features">
          <div className="cta-feature">
            <span className="feature-icon">✨</span>
            <span className="feature-text">No credit card required</span>
          </div>
          <div className="cta-feature">
            <span className="feature-icon">⚡</span>
            <span className="feature-text">Get 1000 free tokens</span>
          </div>
          <div className="cta-feature">
            <span className="feature-icon">🚀</span>
            <span className="feature-text">Start generating in seconds</span>
          </div>
        </div>

        <div className="cta-buttons">
          <Link to={user ? '/generator' : '/login'} className="btn btn-accent cta-btn">
            <Sparkles size={20} />
            {user ? 'Go to Dashboard' : 'Start Your Free Trial Now'}
            <ArrowRight size={20} />
          </Link>
          <Link to="/team" className="btn btn-secondary cta-btn">
            <Users size={20} />
            Meet Our Team
          </Link>
        </div>
      </div>
    </section>
  );
};

export default CTA;
