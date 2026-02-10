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
            name: "Free",
            price: "$0",
            period: "forever",
            description: "Essential tools for casual users.",
            features: [
                "5 Basic Lesson Plans / Month",
                "Standard Response Speed",
                "Access to Community Templates",
                "Export to PDF"
            ],
            notIncluded: [
                "GPT-4 Model Access",
                "Interactive Quiz Generation",
                "Priority Support",
                "Custom Branding"
            ],
            cta: "Current Plan",
            highlight: false,
            action: () => { }
        },
        {
            name: "Silver",
            price: billingCycle === 'monthly' ? "$10" : "$100",
            period: billingCycle === 'monthly' ? "/ month" : "/ year",
            description: "Essential power for everyday teaching.",
            features: [
                "Unlimited Lesson Generation",
                "Standard AI Models",
                "One-Click Quiz & Slide Generation",
                "Export to Editable PPT/Docx",
                "Standard Email Support"
            ],
            notIncluded: [
                "GPT-4o & Advanced Models",
                "Priority Support",
                "Bulk Generation"
            ],
            cta: "Upgrade to Silver",
            highlight: false,
            recommended: false,
            action: () => alert("Redirecting to specific payment gateway...")
        },
        {
            name: "Gold",
            price: billingCycle === 'monthly' ? "$15" : "$150",
            period: billingCycle === 'monthly' ? "/ month" : "/ year",
            description: "The ultimate toolkit for power users.",
            features: [
                "Everything in Silver",
                "Access to GPT-4o & Claude 3.5",
                "Priority 24/7 Support",
                "Bulk Lesson Generation (10x faster)",
                "Personalized AI Style Tuning"
            ],
            notIncluded: [],
            cta: "Get Gold Access",
            highlight: true,
            recommended: true,
            action: () => alert("Redirecting to Gold Payment...")
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
                            whileHover={{ y: -10, boxShadow: tier.highlight ? '0 20px 40px -10px rgba(255, 215, 0, 0.15)' : '0 20px 40px -10px rgba(0,0,0,0.5)' }}
                            style={{
                                background: tier.highlight ? '#111' : '#0e0e0e',
                                border: tier.highlight ? '1px solid #FFD700' : '1px solid #222',
                                borderRadius: '24px',
                                padding: '40px',
                                position: 'relative',
                                display: 'flex',
                                flexDirection: 'column',
                                height: '100%'
                            }}
                        >
                            {tier.recommended && (
                                <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', overflow: 'hidden', height: '150px', pointerEvents: 'none', borderRadius: '24px 24px 0 0' }}>
                                    <div style={{ position: 'absolute', top: -80, left: 0, width: '100%', height: '100%', background: 'linear-gradient(to bottom, rgba(255,215,0,0.1), transparent)' }} />
                                    <div style={{ position: 'absolute', top: 20, right: 20, background: '#FFD700', color: '#000', padding: '6px 12px', borderRadius: '20px', fontWeight: 'bold', fontSize: '12px', letterSpacing: '0.5px' }}>
                                        POPULAR
                                    </div>
                                </div>
                            )}

                            <h3 style={{ fontSize: '28px', marginBottom: '15px', color: '#fff', fontWeight: '700' }}>{tier.name}</h3>
                            <p style={{ color: '#888', marginBottom: '30px', minHeight: '40px', fontSize: '16px', lineHeight: '1.5' }}>{tier.description}</p>

                            <div style={{ display: 'flex', alignItems: 'baseline', marginBottom: '30px' }}>
                                <span style={{ fontSize: '56px', fontWeight: '800', color: tier.highlight ? '#FFD700' : '#fff', letterSpacing: '-2px' }}>{tier.price}</span>
                                <span style={{ color: '#666', marginLeft: '8px', fontSize: '18px' }}>{tier.period}</span>
                            </div>

                            <button
                                onClick={tier.action}
                                style={{
                                    width: '100%',
                                    padding: '18px',
                                    borderRadius: '16px',
                                    border: 'none',
                                    background: tier.highlight ? 'linear-gradient(90deg, #FFD700, #FDB931)' : 'rgba(255,255,255,0.05)',
                                    color: tier.highlight ? '#000' : '#fff',
                                    fontWeight: '700',
                                    fontSize: '16px',
                                    cursor: 'pointer',
                                    marginBottom: '40px',
                                    transition: 'all 0.3s',
                                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px',
                                    boxShadow: tier.highlight ? '0 10px 20px rgba(255, 215, 0, 0.2)' : 'none'
                                }}
                                onMouseEnter={(e) => {
                                    if (tier.highlight) e.currentTarget.style.transform = 'translateY(-2px)';
                                    else e.currentTarget.style.background = 'rgba(255,255,255,0.1)';
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.transform = 'translateY(0)';
                                    if (!tier.highlight) e.currentTarget.style.background = 'rgba(255,255,255,0.05)';
                                }}
                            >
                                {tier.highlight ? 'Get Started Now' : tier.cta}
                                {tier.highlight && <Zap size={20} fill="black" />}
                            </button>

                            <div style={{ flex: 1, borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '30px' }}>
                                {tier.features.map((feature, i) => (
                                    <div key={i} style={{ display: 'flex', alignItems: 'start', marginBottom: '18px' }}>
                                        <div style={{ background: tier.highlight ? 'rgba(255, 215, 0, 0.1)' : 'rgba(255,255,255,0.05)', padding: '4px', borderRadius: '50%', marginRight: '16px', marginTop: '2px' }}>
                                            <Check size={14} color={tier.highlight ? '#FFD700' : '#888'} strokeWidth={3} />
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
