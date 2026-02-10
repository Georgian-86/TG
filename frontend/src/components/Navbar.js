import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import { Home, Package, Lightbulb, Sparkles, Sun, Moon, Wand2, Droplets, Gem, Menu, X, Users } from 'lucide-react';
import ComingSoonModal from './ComingSoonModal';
import '../styles/navbar.css';

export default function Navbar() {
  const { theme, toggleTheme, themes } = useTheme();
  const { user } = useAuth();  // Get auth state
  const [visible, setVisible] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [showComingSoonModal, setShowComingSoonModal] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;

      if (currentScrollY < 100) {
        setVisible(true);
      } else if (currentScrollY > lastScrollY) {
        setVisible(false);
      } else {
        setVisible(true);
      }

      setLastScrollY(currentScrollY);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [lastScrollY]);

  // Close mobile menu on resize
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 768) {
        setMobileMenuOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Navigation items - removed Dashboard to avoid duplication with button
  const navItems = [
    { name: 'Home', link: '/', icon: <Home size={20} />, isRoute: true },
    { name: 'Features', link: '/#features', icon: <Sparkles size={20} />, isRoute: true },
    { name: 'Packages', link: '/#packages', icon: <Package size={20} />, isRoute: true },
    { name: 'How It Works', link: '/#how-it-works', icon: <Lightbulb size={20} />, isRoute: true },
  ];

  const handleNavClick = () => {
    setMobileMenuOpen(false);
  };

  return (
    <>
      <nav className={`floating-navbar ${visible ? 'visible' : 'hidden'}`}>
        <div className="floating-navbar-container">
          <Link to="/" className="navbar-logo">
            <img src="/TechGenieMascot.png" alt="TeachGenie" className="navbar-logo-img" />
            <span className="navbar-logo-text">TeachGenie</span>
          </Link>

          {/* Desktop Menu */}
          <ul className="floating-nav-menu">
            {navItems.map((item, index) => (
              <li key={index}>
                {item.isComingSoon ? (
                  <button
                    onClick={() => setShowComingSoonModal(true)}
                    className="nav-item"
                    style={{ background: 'none', border: 'none', cursor: 'pointer' }}
                  >
                    <span className="nav-icon">{item.icon}</span>
                    <span className="nav-text">{item.name}</span>
                  </button>
                ) : item.isRoute ? (
                  <Link to={item.link} className="nav-item">
                    <span className="nav-icon">{item.icon}</span>
                    <span className="nav-text">{item.name}</span>
                  </Link>
                ) : (
                  <a href={item.link} className="nav-item">
                    <span className="nav-icon">{item.icon}</span>
                    <span className="nav-text">{item.name}</span>
                  </a>
                )}
              </li>
            ))}
          </ul>

          <div className="nav-actions">
            <button
              className="theme-toggle-btn"
              onClick={toggleTheme}
              title="Toggle theme"
              aria-label="Toggle theme"
            >
              {theme === 'light' && <Sun size={20} />}
              {theme === 'dark' && <Moon size={20} />}
              {theme === 'ocean' && <Droplets size={20} />}
              {theme === 'elegant' && <Gem size={20} />}
            </button>
            <Link to={user ? '/generator' : '/signup'} className="nav-cta-btn">
              {user ? 'Dashboard' : 'Get Started'}
            </Link>

            {/* Mobile Hamburger */}
            <button
              className="mobile-menu-btn"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile Drawer */}
      <div className={`mobile-drawer ${mobileMenuOpen ? 'open' : ''}`}>
        <div className="mobile-drawer-content">
          <ul className="mobile-nav-list">
            {navItems.map((item, index) => (
              <li key={index}>
                {item.isComingSoon ? (
                  <button
                    onClick={() => {
                      setShowComingSoonModal(true);
                      handleNavClick();
                    }}
                    className="mobile-nav-item"
                    style={{ background: 'none', border: 'none', cursor: 'pointer', width: '100%', textAlign: 'left' }}
                  >
                    <span className="mobile-nav-icon">{item.icon}</span>
                    <span className="mobile-nav-text">{item.name}</span>
                  </button>
                ) : item.isRoute ? (
                  <Link to={item.link} className="mobile-nav-item" onClick={handleNavClick}>
                    <span className="mobile-nav-icon">{item.icon}</span>
                    <span className="mobile-nav-text">{item.name}</span>
                  </Link>
                ) : (
                  <a href={item.link} className="mobile-nav-item" onClick={handleNavClick}>
                    <span className="mobile-nav-icon">{item.icon}</span>
                    <span className="mobile-nav-text">{item.name}</span>
                  </a>
                )}
              </li>
            ))}
          </ul>
          <Link to={user ? '/generator' : '/signup'} className="mobile-cta-btn" onClick={handleNavClick}>
            {user ? 'Dashboard' : 'Get Started'}
          </Link>
        </div>
      </div>

      {/* Overlay */}
      {mobileMenuOpen && (
        <div className="mobile-overlay" onClick={() => setMobileMenuOpen(false)} />
      )}

      {/* Coming Soon Modal */}
      <ComingSoonModal
        isOpen={showComingSoonModal}
        onClose={() => setShowComingSoonModal(false)}
        featureName="Dashboard"
      />
    </>
  );
}

