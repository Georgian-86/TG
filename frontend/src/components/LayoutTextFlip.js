import React, { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import "../styles/layoutTextFlip.css";

export const LayoutTextFlip = ({
    words,
    duration = 2000,
    className = "",
    startDelay = 0
}) => {
    const [currentWord, setCurrentWord] = useState(words[0]);

    useEffect(() => {
        let interval;
        const startTimeout = setTimeout(() => {
            interval = setInterval(() => {
                setCurrentWord((prev) => {
                    const currentIndex = words.indexOf(prev);
                    const nextIndex = (currentIndex + 1) % words.length;
                    return words[nextIndex];
                });
            }, duration);
        }, startDelay);

        return () => {
            clearTimeout(startTimeout);
            clearInterval(interval);
        };
    }, [words, duration, startDelay]);

    return (
        <div className={`layout-text-flip ${className}`}>
            <AnimatePresence mode="popLayout">
                <motion.span
                    key={currentWord}
                    initial={{ y: 30, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: -30, opacity: 0 }}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                >
                    {currentWord}
                </motion.span>
            </AnimatePresence>
        </div>
    );
};
