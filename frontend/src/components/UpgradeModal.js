import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Crown, Check, Zap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import '../styles/coming-soon-modal.css'; // Reusing backdrop styles

const UpgradeModal = ({ isOpen, onClose }) => {
    const navigate = useNavigate();

    const handleUpgrade = () => {
        onClose();
        navigate('/pricing');
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        className="modal-backdrop"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        style={{
                            position: 'fixed',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            background: 'rgba(0,0,0,0.7)',
                            backdropFilter: 'blur(5px)',
                            zIndex: 9998
                        }}
                    />

                    {/* Modal */}
                    <motion.div
                        style={{
                            position: 'fixed',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            pointerEvents: 'none',
                            zIndex: 9999,
                        }}
                        initial={{ opacity: 0, scale: 0.9, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.9, y: 20 }}
                        transition={{ type: "spring", duration: 0.5 }}
                    >
                        <div
                            className="upgrade-modal"
                            style={{
                                pointerEvents: 'auto',
                                background: 'linear-gradient(145deg, #1a1a1a, #2d2d2d)',
                                border: '1px solid rgba(255, 215, 0, 0.2)',
                                borderRadius: '20px',
                                padding: '30px',
                                maxWidth: '500px',
                                width: '90%',
                                boxShadow: '0 20px 50px rgba(0,0,0,0.5), 0 0 30px rgba(255, 215, 0, 0.1)',
                                position: 'relative',
                                overflow: 'hidden'
                            }}
                        >
                            {/* Decorative Background Elements */}
                            <div style={{ position: 'absolute', top: -50, right: -50, width: 150, height: 150, background: 'linear-gradient(to bottom left, #FFD700, transparent)', opacity: 0.1, borderRadius: '50%' }} />

                            {/* Close Button */}
                            <button
                                onClick={onClose}
                                style={{
                                    position: 'absolute',
                                    top: '15px',
                                    right: '15px',
                                    background: 'transparent',
                                    border: 'none',
                                    color: '#888',
                                    cursor: 'pointer',
                                    transition: 'color 0.2s'
                                }}
                                onMouseEnter={(e) => e.target.style.color = '#fff'}
                                onMouseLeave={(e) => e.target.style.color = '#888'}
                            >
                                <X size={24} />
                            </button>

                            {/* Content */}
                            <div style={{ textAlign: 'center', position: 'relative', zIndex: 1 }}>
                                <motion.div
                                    initial={{ scale: 0, rotate: -20 }}
                                    animate={{ scale: 1, rotate: 0 }}
                                    transition={{ type: "spring", stiffness: 200, delay: 0.2 }}
                                    style={{
                                        width: '80px',
                                        height: '80px',
                                        background: 'linear-gradient(135deg, #FFD700, #FFA500)',
                                        borderRadius: '50%',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        margin: '0 auto 20px',
                                        boxShadow: '0 10px 20px rgba(255, 215, 0, 0.3)'
                                    }}
                                >
                                    <Crown size={40} color="#fff" />
                                </motion.div>

                                <motion.h2
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.3 }}
                                    style={{
                                        color: '#fff',
                                        fontSize: '28px',
                                        marginBottom: '10px',
                                        fontFamily: '"Outfit", sans-serif'
                                    }}
                                >
                                    Unlock Your Potential
                                </motion.h2>

                                <motion.p
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.4 }}
                                    style={{
                                        color: '#ccc',
                                        fontSize: '16px',
                                        lineHeight: '1.6',
                                        marginBottom: '25px'
                                    }}
                                >
                                    You're currently on the <strong>Free Tier</strong>. Upgrade to Pro to unlock advanced AI models, unlimited generations, and premium features!
                                </motion.p>

                                {/* Features List */}
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    transition={{ delay: 0.5 }}
                                    style={{
                                        textAlign: 'left',
                                        background: '#ffffff',
                                        padding: '20px',
                                        borderRadius: '16px',
                                        marginBottom: '25px',
                                        border: '1px solid #FFD700',
                                        boxShadow: '0 4px 15px rgba(0,0,0,0.2)'
                                    }}
                                >
                                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px', color: '#000000', fontWeight: '700', fontSize: '16px' }}>
                                        <div style={{ background: '#FFF4E5', padding: '4px', borderRadius: '50%', marginRight: '12px', display: 'flex' }}>
                                            <Check size={16} color="#FF9900" strokeWidth={4} />
                                        </div>
                                        <span>Access to GPT-4 & Premium Models</span>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px', color: '#000000', fontWeight: '700', fontSize: '16px' }}>
                                        <div style={{ background: '#FFF4E5', padding: '4px', borderRadius: '50%', marginRight: '12px', display: 'flex' }}>
                                            <Check size={16} color="#FF9900" strokeWidth={4} />
                                        </div>
                                        <span>Unlimited Lesson Planning</span>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', color: '#000000', fontWeight: '700', fontSize: '16px' }}>
                                        <div style={{ background: '#FFF4E5', padding: '4px', borderRadius: '50%', marginRight: '12px', display: 'flex' }}>
                                            <Check size={16} color="#FF9900" strokeWidth={4} />
                                        </div>
                                        <span>Priority Support</span>
                                    </div>
                                </motion.div>

                                {/* Buttons */}
                                <div style={{ display: 'flex', gap: '15px', justifyContent: 'center' }}>
                                    <motion.button
                                        onClick={onClose}
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                        style={{
                                            padding: '12px 24px',
                                            borderRadius: '50px',
                                            background: 'transparent',
                                            border: '1px solid #777',
                                            color: '#e0e0e0',
                                            fontSize: '16px',
                                            cursor: 'pointer',
                                            fontWeight: '600'
                                        }}
                                    >
                                        Maybe Later
                                    </motion.button>

                                    <motion.button
                                        onClick={handleUpgrade}
                                        whileHover={{ scale: 1.05, boxShadow: '0 0 20px rgba(255, 215, 0, 0.4)' }}
                                        whileTap={{ scale: 0.95 }}
                                        style={{
                                            padding: '12px 30px',
                                            borderRadius: '50px',
                                            background: 'linear-gradient(90deg, #FFD700, #FFA500)',
                                            border: 'none',
                                            color: '#000',
                                            fontSize: '16px',
                                            cursor: 'pointer',
                                            fontWeight: '700',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '8px'
                                        }}
                                    >
                                        <Zap size={18} fill="black" />
                                        Upgrade Now
                                    </motion.button>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};

export default UpgradeModal;
