import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, X, Shield, Zap, CreditCard, Lock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar'; // Corrected import

const PricingPage = () => {
    const navigate = useNavigate();
    const [billingCycle, setBillingCycle] = useState('monthly'); // 'monthly' or 'yearly'

    const tiers = [
        {
            name: "🟢 Free Plan",
            subtitle: "Starter for Individual Teachers",
            price: "₹0",
            period: "forever",
            description: "Best for trying TeachGenie",
            features: [
                "10 content generations/month",
                "PDF download only",
                "Key Learning Objectives",
                "Structured Content",
                "Key Takeaways",
                "RBT (Revised Bloom's Taxonomy) Mapping",
                "Standard quality generation"
            ],
            notIncluded: [
                "PPT downloads",
                "Scenario-based quizzes",
                "Premium graphics",
                "Priority support"
            ],
            badge: "",
            perfectFor: "Teachers exploring AI-assisted teaching for the first time",
            cta: "Get Started Free",
            highlight: false,
            action: () => { }
        },
        {
            name: "🥈 Silver Plan",
            subtitle: "For Active Teachers",
            price: billingCycle === 'monthly' ? "₹399" : "₹3,999",
            period: billingCycle === 'monthly' ? "/ month" : "/ year",
            description: "Best for regular classroom usage",
            features: [
                "Everything in Free +",
                "20 generations/month",
                "PPT + PDF downloads",
                "Scenario-based quizzes",
                "Key takeaways & structured notes",
                "RBT mapping",
                "Faster generation speed",
                "Better content depth"
            ],
            notIncluded: [
                "Premium graphics",
                "Advanced quizzes",
                "Priority generation",
                "High-depth academic content"
            ],
            badge: "",
            perfectFor: "Teachers who create lessons & presentations weekly",
            cta: "Upgrade to Silver",
            highlight: false,
            recommended: false,
            action: () => alert("Redirecting to Silver payment gateway...")
        },
        {
            name: "🥇 Gold Plan",
            subtitle: "Power Teachers & Content Creators",
            price: billingCycle === 'monthly' ? "₹999" : "₹9,999",
            period: billingCycle === 'monthly' ? "/ month" : "/ year",
            description: "Best for advanced teaching & premium content",
            features: [
                "Everything in Silver +",
                "50 generations/month",
                "Premium graphics & visual slides",
                "Enhanced PPT designs",
                "Advanced scenario-based quizzes",
                "Smart structured explanations",
                "Priority generation speed",
                "High-depth academic content"
            ],
            notIncluded: [],
            badge: "POPULAR",
            perfectFor: "Educators, trainers, coaching institutes, content creators",
            cta: "Get Gold Access",
            highlight: true,
            recommended: true,
            action: () => alert("Redirecting to Gold Payment...")
        },
        {
            name: "🏫 Institutional Plan",
            subtitle: "For Schools, Colleges & Universities",
            price: "Custom",
            period: "pricing",
            description: "Fully customizable based on your institution's needs",
            features: [
                "Unlimited or bulk generations accordingly",
                "Multi-teacher access (faculty dashboard)",
                "Admin control panel",
                "Custom templates for institution",
                "RBT, IKS & LO-PO Mapping",
                "Level-based cognitive load control",
                "Custom lesson formats",
                "Department-wise access",
                "Training & onboarding support",
                "Dedicated support"
            ],
            notIncluded: [],
            badge: "ENTERPRISE",
            perfectFor: "Schools • Colleges • Universities • Coaching Institutes • EdTech organizations",
            cta: "Contact for Demo",
            highlight: false,
            recommended: false,
            institutional: true,
            action: () => alert("Redirecting to contact form...")
        }
    ];

    return (
        <div style={{ minHeight: '100vh', background: '#050505', color: '#fff', fontFamily: '"Outfit", sans-serif', overflow: 'hidden', position: 'relative' }}>

            {/* Back Arrow */}
            <div
                onClick={() => navigate('/generator')}
                style={{ position: 'absolute', top: '40px', left: '40px', cursor: 'pointer', zIndex: 10, background: 'rgba(255,255,255,0.1)', padding: '10px', borderRadius: '50%', color: '#fff', transition: 'background 0.3s' }}
                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.2)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
            >
                <X size={24} />
            </div>

            {/* Ambient Background Glow */}
            <div style={{ position: 'absolute', top: 0, left: '50%', transform: 'translateX(-50%)', width: '100%', height: '600px', background: 'radial-gradient(ellipse at top, rgba(255, 215, 0, 0.15), transparent 70%)', pointerEvents: 'none', zIndex: 0 }} />

            <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '120px 20px 60px', position: 'relative', zIndex: 1 }}>

                {/* Header Section */}
                <div style={{ textAlign: 'center', marginBottom: '80px' }}>
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.5 }}
                        style={{ display: 'inline-block', padding: '8px 16px', borderRadius: '30px', background: 'rgba(255, 215, 0, 0.1)', border: '1px solid rgba(255, 215, 0, 0.3)', color: '#FFD700', fontSize: '14px', fontWeight: '600', marginBottom: '20px' }}
                    >
                        PRICING PLANS
                    </motion.div>
                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        style={{ fontSize: '56px', fontWeight: '800', marginBottom: '24px', letterSpacing: '-1px', color: '#ffffff' }}
                    >
                        Invest in your <span style={{ background: 'linear-gradient(to right, #FFD700, #FFA500)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Teaching Superpowers</span>
                    </motion.h1>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        style={{ fontSize: '20px', color: '#888', maxWidth: '600px', margin: '0 auto', lineHeight: '1.6' }}
                    >
                        Choose the perfect plan to save hours of planning time and engage your students like never before.
                    </motion.p>

                    {/* Billing Toggle */}
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: '50px', gap: '20px', background: 'rgba(255,255,255,0.03)', width: 'fit-content', margin: '50px auto 0', padding: '8px', borderRadius: '50px', border: '1px solid rgba(255,255,255,0.05)' }}>
                        <div
                            onClick={() => setBillingCycle('monthly')}
                            style={{ padding: '10px 24px', borderRadius: '24px', background: billingCycle === 'monthly' ? '#333' : 'transparent', color: billingCycle === 'monthly' ? '#fff' : '#888', cursor: 'pointer', transition: 'all 0.3s', fontWeight: '600' }}
                        >
                            Monthly
                        </div>
                        <div
                            onClick={() => setBillingCycle('yearly')}
                            style={{ padding: '10px 24px', borderRadius: '24px', background: billingCycle === 'yearly' ? '#333' : 'transparent', color: billingCycle === 'yearly' ? '#fff' : '#888', cursor: 'pointer', transition: 'all 0.3s', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px' }}
                        >
                            Yearly
                            <span style={{ fontSize: '10px', background: '#FFD700', color: '#000', padding: '2px 6px', borderRadius: '4px', fontWeight: 'bold' }}>-20%</span>
                        </div>
                    </div>
                </div>

                {/* Pricing Cards */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '40px', marginBottom: '100px' }}>
                    {tiers.map((tier, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 + 0.2 }}
                            whileHover={{ y: -10, boxShadow: tier.highlight ? '0 20px 40px -10px rgba(255, 215, 0, 0.15)' : tier.institutional ? '0 20px 40px -10px rgba(138, 43, 226, 0.15)' : '0 20px 40px -10px rgba(0,0,0,0.5)' }}
                            style={{
                                background: tier.highlight ? '#111' : tier.institutional ? 'linear-gradient(135deg, #1a0a2e 0%, #0f0518 100%)' : '#0e0e0e',
                                border: tier.highlight ? '1px solid #FFD700' : tier.institutional ? '1px solid #8A2BE2' : '1px solid #222',
                                borderRadius: '24px',
                                padding: '40px',
                                position: 'relative',
                                display: 'flex',
                                flexDirection: 'column',
                                height: '100%'
                            }}
                        >
                            {(tier.recommended || tier.badge) && (
                                <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', overflow: 'hidden', height: '150px', pointerEvents: 'none', borderRadius: '24px 24px 0 0' }}>
                                    <div style={{ position: 'absolute', top: -80, left: 0, width: '100%', height: '100%', background: tier.institutional ? 'linear-gradient(to bottom, rgba(138,43,226,0.1), transparent)' : 'linear-gradient(to bottom, rgba(255,215,0,0.1), transparent)' }} />
                                    <div style={{ position: 'absolute', top: 20, right: 20, background: tier.institutional ? '#8A2BE2' : '#FFD700', color: tier.institutional ? '#fff' : '#000', padding: '6px 12px', borderRadius: '20px', fontWeight: 'bold', fontSize: '12px', letterSpacing: '0.5px' }}>
                                        {tier.badge || 'POPULAR'}
                                    </div>
                                </div>
                            )}

                            <h3 style={{ fontSize: '28px', marginBottom: '8px', color: '#fff', fontWeight: '700' }}>{tier.name}</h3>
                            {tier.subtitle && (
                                <p style={{ color: tier.institutional ? '#c792ea' : '#999', marginBottom: '15px', fontSize: '14px', fontWeight: '600' }}>{tier.subtitle}</p>
                            )}
                            <p style={{ color: '#888', marginBottom: '30px', minHeight: '40px', fontSize: '16px', lineHeight: '1.5' }}>{tier.description}</p>

                            <div style={{ display: 'flex', alignItems: 'baseline', marginBottom: '30px' }}>
                                <span style={{ fontSize: '56px', fontWeight: '800', color: tier.highlight ? '#FFD700' : tier.institutional ? '#8A2BE2' : '#fff', letterSpacing: '-2px' }}>{tier.price}</span>
                                <span style={{ color: '#666', marginLeft: '8px', fontSize: '18px' }}>{tier.period}</span>
                            </div>

                            <button
                                onClick={tier.action}
                                style={{
                                    width: '100%',
                                    padding: '18px',
                                    borderRadius: '16px',
                                    border: 'none',
                                    background: tier.highlight ? 'linear-gradient(90deg, #FFD700, #FDB931)' : tier.institutional ? 'linear-gradient(90deg, #8A2BE2, #9D4EDD)' : 'rgba(255,255,255,0.05)',
                                    color: tier.highlight || tier.institutional ? '#fff' : '#fff',
                                    fontWeight: '700',
                                    fontSize: '16px',
                                    cursor: 'pointer',
                                    marginBottom: '40px',
                                    transition: 'all 0.3s',
                                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px',
                                    boxShadow: tier.highlight ? '0 10px 20px rgba(255, 215, 0, 0.2)' : tier.institutional ? '0 10px 20px rgba(138, 43, 226, 0.2)' : 'none'
                                }}
                                onMouseEnter={(e) => {
                                    if (tier.highlight || tier.institutional) e.currentTarget.style.transform = 'translateY(-2px)';
                                    else e.currentTarget.style.background = 'rgba(255,255,255,0.1)';
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.transform = 'translateY(0)';
                                    if (!tier.highlight && !tier.institutional) e.currentTarget.style.background = 'rgba(255,255,255,0.05)';
                                }}
                            >
                                {tier.cta}
                                {tier.highlight && <Zap size={20} fill="#000" />}
                            </button>

                            <div style={{ flex: 1, borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '30px' }}>
                                {tier.features.map((feature, i) => (
                                    <div key={i} style={{ display: 'flex', alignItems: 'start', marginBottom: '18px' }}>
                                        <div style={{ background: tier.highlight ? 'rgba(255, 215, 0, 0.1)' : tier.institutional ? 'rgba(138, 43, 226, 0.1)' : 'rgba(255,255,255,0.05)', padding: '4px', borderRadius: '50%', marginRight: '16px', marginTop: '2px' }}>
                                            <Check size={14} color={tier.highlight ? '#FFD700' : tier.institutional ? '#8A2BE2' : '#888'} strokeWidth={3} />
                                        </div>
                                        <span style={{ color: '#ddd', fontSize: '16px', fontWeight: '500' }}>{feature}</span>
                                    </div>
                                ))}
                                {tier.notIncluded.map((feature, i) => (
                                    <div key={i} style={{ display: 'flex', alignItems: 'center', marginBottom: '18px', opacity: 0.4 }}>
                                        <div style={{ padding: '4px', borderRadius: '50%', marginRight: '16px' }}>
                                            <X size={14} color="#666" />
                                        </div>
                                        <span style={{ color: '#666', fontSize: '16px' }}>{feature}</span>
                                    </div>
                                ))}
                            </div>

                            {tier.perfectFor && (
                                <div style={{ marginTop: '24px', padding: '16px', background: 'rgba(255,255,255,0.02)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
                                    <p style={{ color: '#999', fontSize: '13px', marginBottom: '6px', fontWeight: '600' }}>Perfect for:</p>
                                    <p style={{ color: '#ddd', fontSize: '14px', lineHeight: '1.6' }}>{tier.perfectFor}</p>
                                </div>
                            )}
                        </motion.div>
                    ))}
                </div>

                {/* Secure Payment Section */}
                <div style={{
                    background: 'rgba(25, 25, 25, 0.95)',
                    borderRadius: '24px',
                    padding: '60px',
                    border: '1px solid rgba(255, 255, 255, 0.15)',
                    textAlign: 'center',
                    maxWidth: '800px',
                    margin: '0 auto',
                    position: 'relative',
                    overflow: 'hidden',
                    boxShadow: '0 20px 50px rgba(0,0,0,0.5), inset 0 0 20px rgba(255,255,255,0.02)'
                }}>
                    <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '2px', background: 'linear-gradient(90deg, transparent, #333, transparent)' }} />

                    <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '30px' }}>
                        <div style={{ background: 'rgba(255, 215, 0, 0.08)', padding: '20px', borderRadius: '50%', border: '1px solid rgba(255, 215, 0, 0.4)', boxShadow: '0 0 40px rgba(255, 215, 0, 0.15)' }}>
                            <Lock size={40} color="#FFD700" />
                        </div>
                    </div>
                    <h2 style={{ fontSize: '32px', marginBottom: '16px', fontWeight: '800', color: '#ffffff', letterSpacing: '-0.5px' }}>Secure SSL Payment</h2>
                    <p style={{ color: '#ccc', marginBottom: '40px', fontSize: '18px' }}>
                        Transform your classroom with peace of mind. Your transaction is encrypted and secured.
                    </p>

                    <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', flexWrap: 'wrap', alignItems: 'center' }}>
                        {/* Styled Credit Cards */}
                        <div style={{ background: '#222', borderRadius: '8px', padding: '10px 15px', color: '#fff', fontSize: '14px', fontWeight: 'bold', letterSpacing: '1px', border: '1px solid #333' }}>VISA</div>
                        <div style={{ background: '#222', borderRadius: '8px', padding: '10px 15px', color: '#fff', fontSize: '14px', fontWeight: 'bold', letterSpacing: '1px', border: '1px solid #333' }}>Mastercard</div>
                        <div style={{ background: '#222', borderRadius: '8px', padding: '10px 15px', color: '#fff', fontSize: '14px', fontWeight: 'bold', letterSpacing: '1px', border: '1px solid #333' }}>AMEX</div>
                        <div style={{ background: '#0070BA', borderRadius: '8px', padding: '10px 15px', color: '#fff', fontSize: '14px', fontWeight: 'bold', letterSpacing: '1px', border: '1px solid #005ea6' }}>PayPal</div>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default PricingPage;
