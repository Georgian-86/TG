import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import ComingSoonModal from './ComingSoonModal';
import '../styles/footer.css';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  const [showComingSoonModal, setShowComingSoonModal] = useState(false);

  return (
    <>
      <footer className="footer">
        <div className="footer-wrapper">
          {/* Logo */}
          <div className="footer-logo-section">
            <img src="/TechGenieMascot.png" alt="TeachGenie" className="footer-logo-img" />
            <h2 className="footer-logo-text">TeachGenie</h2>
          </div>

          <nav className="footer-nav">
            <Link to="/#features">FEATURES</Link>
            <Link to="/#packages">PRICING</Link>
            <Link to="/#how-it-works">HOW IT WORKS</Link>
            <button onClick={() => setShowComingSoonModal(true)}>
              GENERATOR
            </button>
            <Link to="/team">TEAM</Link>
            <Link to="/learn-more">ABOUT</Link>
            <Link to="/login">LOGIN</Link>
          </nav>

          {/* Copyright Badge */}
          <div className="footer-copyright">
            © {currentYear} TeachGenie. All Rights Reserved
          </div>

          {/* Credits */}
          <div className="footer-credits">
            <span className="credit-item">
              <span className="credit-label">Developer:</span>
              <span className="credit-name">
                <a href="https://www.linkedin.com/in/loviraj">Lovi Raj Gupta</a>
              </span>
            </span>
            <span className="divider">•</span>
            <span className="credit-item">
              <span className="credit-label">Contributors:</span>
              <span className="credit-name">
                <a href="https://www.linkedin.com/in/medha-jha810">Medha Jha</a> & <a href="https://www.linkedin.com/in/golukumar15">Golu Kumar</a>
              </span>
            </span>
            <span className="divider">•</span>
            <span className="credit-item">
              <a href="mailto:info@teachgenie.ai" className="credit-email">info@teachgenie.ai</a>
            </span>
          </div>
        </div>
      </footer>

      {/* Coming Soon Modal */}
      <ComingSoonModal
        isOpen={showComingSoonModal}
        onClose={() => setShowComingSoonModal(false)}
        featureName="Dashboard"
      />
    </>
  );
};

export default Footer;
