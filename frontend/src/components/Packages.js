import React from 'react';
import { Check, X } from 'lucide-react';
import { Link } from 'react-router-dom';
import '../styles/packages.css';

export default function Packages() {
  const packages = [
    {
      name: 'Free Trial',
      price: '₹0',
      period: 'Forever Free',
      badge: 'Start Here',
      color: 'free',
      icon: '/free.png',
      features: [
        { name: '1000 Free Credits (10 Generations)', included: true },
        { name: 'AI-Powered Discovery', included: true },
        { name: 'All Academic Levels', included: true },
        { name: 'PDF Downloads', included: true },
        { name: 'PowerPoint Export', included: false },
        { name: 'Priority Support', included: false }
      ]
    },
    {
      name: 'Silver',
      price: '',
      period: 'Coming Soon...',
      badge: 'Popular',
      color: 'silver',
      icon: '/silver.png',
      features: [
        { name: '5000 Additional Credits (50 Generations)', included: true },
        { name: 'PowerPoint & Word Export', included: true },
        { name: 'All Academic Levels', included: true },
        { name: 'Advanced Templates', included: true },
        { name: 'Email Support', included: true },
        { name: 'Priority Support', included: false }
      ]
    },
    {
      name: 'Gold',
      price: '',
      period: 'Coming Soon...',
      badge: 'Best Value',
      color: 'gold',
      icon: '/gold.png',
      featured: true,
      features: [
        { name: '10000 Additional Credits (100 Generations)', included: true },
        { name: 'All Academic Levels', included: true },
        { name: 'Custom Branding', included: true },
        { name: 'Priority Chat & Email', included: true },
        { name: 'Advanced Analytics', included: true }
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
        { name: 'Unlimited Generations', included: true },
        { name: 'API Access', included: true },
        { name: 'All Academic Levels', included: true },
        { name: 'Custom Integrations', included: true },
        { name: 'Dedicated Support Team', included: true },
        { name: 'SLA Guarantee', included: true }
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

              <Link to="/login" className={`btn btn-large ${pkg.featured ? 'btn-accent' : pkg.name === 'Free Trial' ? 'btn-outline' : 'btn-outline'}`}>
                {pkg.name === 'Free Trial' ? 'Sign Up Free' : pkg.name === 'Institutional' ? 'Contact Sales' : `Upgrade to ${pkg.name}`}
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
