import React from 'react';
import { Check, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/packages.css';

export default function Packages() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const handleUpgradeClick = (e, packageName) => {
    e.preventDefault();
    
    // For Institutional plan, always go to pricing page to see contact info
    if (packageName === 'Institutional') {
      if (user) {
        navigate('/pricing');
      } else {
        navigate('/login');
      }
      return;
    }
    
    // If user is logged in, go to pricing page
    // If not logged in, go to login/signup page
    if (user) {
      navigate('/pricing');
    } else {
      if (packageName === 'Free Trial') {
        navigate('/signup');
      } else {
        navigate('/login');
      }
    }
  };

  const packages = [
    {
      name: 'Free Trial',
      price: '₹0',
      period: 'Forever Free',
      badge: 'Start Here',
      color: 'free',
      icon: '/free.png',
      features: [
        { name: '10 Free Generations', included: true },
        { name: 'AI-Powered Discovery', included: true },
        { name: 'All Academic Levels', included: true },
        { name: 'PDF Downloads', included: true },
        { name: 'RBT Mapping', included: true },
        { name: 'Scenario based Quizzes', included: false },
        { name: 'PowerPoint Export', included: false },
        { name: 'Priority Support', included: false }
      ]
    },
    {
      name: 'Silver',
      price: '₹399',
      period: '/month',
      badge: 'Popular',
      color: 'silver',
      icon: '/silver.png',
      features: [
        { name: '20 Generations', included: true },
        { name: 'AI-Powered Discovery', included: true },
        { name: 'All Academic Levels', included: true },
        { name: 'PowerPoint Export', included: true },
        { name: 'PDF Export', included: true },
        { name: 'Advanced Templates', included: true },
        { name: 'Email Support', included: true },
        { name: 'RBT Mapping', included: true },
        { name: 'Scenario based Quizzes', included: true },
        { name: 'Priority Support', included: false }
      ]
    },
    {
      name: 'Gold',
      price: '₹999',
      period: '/month',
      badge: 'Best Value',
      color: 'gold',
      icon: '/gold.png',
      featured: true,
      features: [
        { name: '50 Generations', included: true },
        { name: 'AI-Powered Discovery', included: true },
        { name: 'All Academic Levels', included: true },
        { name: 'PowerPoint Export', included: true },
        { name: 'PDF Export', included: true },
        { name: 'Priority Chat & Email', included: true },
        { name: 'Advanced Analytics', included: true },
        { name: 'RBT Mapping', included: true },
        { name: 'Scenario based Quizzes', included: true },
        { name: 'Graphics included', included: true },
      ]
    },
    {
      name: 'Institutional',
      price: 'Custom',
      period: '/month',
      badge: 'Enterprise',
      color: 'institutional',
      icon: '/institution.png',
      features: [
        { name: 'Unlimited or bulk generations', included: true },
        { name: 'Multi-teacher access (faculty dashboard)', included: true },
        { name: 'Admin control panel', included: true },
        { name: 'Custom templates for institution', included: true },
        { name: 'RBT, IKS & LO-PO Mapping', included: true },
        { name: 'Level-based cognitive load control', included: true },
        { name: 'Institution branding on PPT/PDF', included: true },
        { name: 'Custom lesson formats', included: true },
        { name: 'Department-wise access', included: true },
        { name: 'Training & onboarding support', included: true },
        { name: 'Dedicated support', included: true }
      ]
    }
  ];

  return (
    <section id="packages" className="packages">
      <div className="container">
        <div className="section-header">
          <h2>Choose Your Plan</h2>
          <p>Flexible packages designed for educators of all sizes</p>
        </div>

        <div className="packages-grid">
          {packages.map((pkg, index) => (
            <div key={index} className={`package-card ${pkg.color} ${pkg.featured ? 'featured' : ''}`}>
              {pkg.badge && <div className="package-badge">{pkg.badge}</div>}

              <div className="package-header">
                <div className="package-icon">
                  <img src={pkg.icon} alt={`${pkg.name} icon`} />
                </div>
                <h3>{pkg.name}</h3>
                <div className="package-price">{pkg.price}<span>{pkg.period}</span></div>
              </div>

              <ul className="package-features">
                {pkg.features.map((feature, idx) => (
                  <li key={idx} className={feature.included ? 'included' : 'excluded'}>
                    {feature.included ? <Check size={20} /> : <X size={20} />}
                    <span>{feature.name}</span>
                  </li>
                ))}
              </ul>

              <button 
                onClick={(e) => handleUpgradeClick(e, pkg.name)}
                className={`btn btn-large ${pkg.featured ? 'btn-accent' : pkg.name === 'Free Trial' ? 'btn-outline' : 'btn-outline'}`}
              >
                {pkg.name === 'Free Trial' ? 'Sign Up Free' : pkg.name === 'Institutional' ? 'Contact Sales' : `Upgrade to ${pkg.name}`}
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
