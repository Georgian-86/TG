import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Rocket, Clock } from 'lucide-react';
import '../styles/coming-soon-modal.css';

const ComingSoonModal = ({ isOpen, onClose, featureName = "Dashboard" }) => {
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
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.8 }}
                        transition={{ type: "spring", duration: 0.5 }}
                    >
                        <div className="coming-soon-modal" style={{ pointerEvents: 'auto' }}>
                            {/* Close Button */}
                            <button className="modal-close-btn" onClick={onClose} aria-label="Close modal">
                                <X size={24} />
                            </button>

                            {/* Icon */}
                            <motion.div
                                className="modal-icon"
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                            >
                                <Rocket size={64} />
                            </motion.div>

                            {/* Content */}
                            <motion.h2
                                className="modal-title"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.3 }}
                            >
                                {featureName} Coming Soon! 🚀
                            </motion.h2>

                            <motion.p
                                className="modal-description"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.4 }}
                            >
                                We're working hard to bring you an amazing {featureName.toLowerCase()} experience.
                                This feature will be available very soon!
                            </motion.p>

                            <motion.div
                                className="modal-features"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.5 }}
                            >
                                <div className="feature-item">
                                    <Clock size={20} />
                                    <span>Launching Soon</span>
                                </div>
                                <div className="feature-item">
                                    <Rocket size={20} />
                                    <span>Exciting Features Ahead</span>
                                </div>
                            </motion.div>

                            <motion.button
                                className="modal-cta-btn"
                                onClick={onClose}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.6 }}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                            >
                                Got It!
                            </motion.button>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};

export default ComingSoonModal;
