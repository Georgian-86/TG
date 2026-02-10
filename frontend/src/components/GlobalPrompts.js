import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import UpgradeModal from './UpgradeModal';

const GlobalPrompts = () => {
    const { user, isAuthenticated } = useAuth();
    const location = useLocation();
    const [showUpgradeModal, setShowUpgradeModal] = useState(false);

    useEffect(() => {
        // Exclude Home Page from prompts
        if (location.pathname === '/') return;

        // Logic to triggering the Upgrade Modal
        // 1. User must be logged in
        // 2. User must be on 'free' tier 
        // 3. Trigger on EVERY mount (refresh/navigation that remounts app)
        // 4. Trigger Randomly (Periodic)
        // 5. Manual triggers via event

        let randomTimer;

        const checkAndShow = () => {
            if (isAuthenticated && user) {
                // Check subscription_tier (matches backend model)
                const userTier = user.subscription_tier || 'free';

                if (userTier === 'free') {
                    // Show modal immediately upon login/refresh (with slight delay for UX)
                    // REMOVED SESSION CHECK: Now shows on every refresh/mount
                    const timer = setTimeout(() => {
                        setShowUpgradeModal(true);
                    }, 1500);

                    // Setup Random Interval (Recursive)
                    const scheduleNextRandom = () => {
                        // Random time between 45 seconds and 3 minutes (45000 - 180000 ms)
                        const minTime = 45000;
                        const maxTime = 180000;
                        const randomTime = Math.floor(Math.random() * (maxTime - minTime + 1) + minTime);

                        console.log(`[GlobalPrompts] Next random upgrade prompt in ${randomTime / 1000}s`);

                        randomTimer = setTimeout(() => {
                            if (isAuthenticated) {
                                setShowUpgradeModal(true);
                                scheduleNextRandom(); // Schedule the next one entirely
                            }
                        }, randomTime);
                    };
                    scheduleNextRandom();

                    return () => {
                        clearTimeout(timer);
                        if (randomTimer) clearTimeout(randomTimer);
                    };
                }
            }
        };

        const cleanup = checkAndShow();

        // Listen for manual triggers (e.g. from Generator button)
        const handleManualTrigger = () => {
            if (isAuthenticated && user) {
                const userTier = user.subscription_tier || 'free';
                if (userTier === 'free') {
                    setShowUpgradeModal(true);
                }
            }
        };

        window.addEventListener('trigger-upgrade-modal', handleManualTrigger);

        return () => {
            if (cleanup && typeof cleanup === 'function') cleanup();
            if (randomTimer) clearTimeout(randomTimer);
            window.removeEventListener('trigger-upgrade-modal', handleManualTrigger);
        };

    }, [isAuthenticated, user]);

    const handleClose = () => {
        setShowUpgradeModal(false);
        // Dispatch event so listeners know the user has responded/closed it
        window.dispatchEvent(new Event('upgrade-modal-closed'));
    };

    return (
        <>
            <UpgradeModal
                isOpen={showUpgradeModal}
                onClose={handleClose}
            />
        </>
    );
};

export default GlobalPrompts;
