import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";

export const Boxes = () => {
    const [isMobile, setIsMobile] = useState(false);
    const [isTouchDevice, setIsTouchDevice] = useState(false);

    useEffect(() => {
        const checkDevice = () => {
            setIsMobile(window.innerWidth <= 768);
            setIsTouchDevice('ontouchstart' in window || navigator.maxTouchPoints > 0);
        };
        checkDevice();
        window.addEventListener('resize', checkDevice);
        return () => window.removeEventListener('resize', checkDevice);
    }, []);

    // Reduce grid on mobile for performance
    const rows = new Array(isMobile ? 15 : 30).fill(1);
    const cols = new Array(isMobile ? 10 : 20).fill(1);

    const colors = [
        "--sky-300",
        "--pink-300",
        "--green-300",
        "--yellow-300",
        "--red-300",
        "--purple-300",
        "--blue-300",
        "--indigo-300",
        "--violet-300",
    ];

    const getRandomColor = () => {
        return colors[Math.floor(Math.random() * colors.length)];
    };

    // Don't render on very small screens for performance
    if (isMobile && window.innerWidth < 480) {
        return null;
    }

    return (
        <div
            style={{
                transform: isMobile
                    ? "translate(-40%,-60%) skewX(-48deg) skewY(14deg) scale(0.5) translateZ(0)"
                    : "translate(-40%,-60%) skewX(-48deg) skewY(14deg) scale(0.675) translateZ(0)",
                position: "fixed",
                top: 0,
                left: 0,
                zIndex: 0,
                display: "flex",
                width: "100%",
                height: "100%",
                pointerEvents: "none",
                opacity: isMobile ? 0.5 : 1, // Reduce opacity on mobile
            }}
            className="boxes-container"
        >
            <div style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                height: "100%",
                zIndex: 1,
                pointerEvents: "none",
                background: "radial-gradient(transparent, transparent, #111)",
            }} />

            <div style={{
                display: "grid",
                gridTemplateColumns: `repeat(${cols.length}, 1fr)`,
                width: "150vw",
                height: "150vh",
                pointerEvents: isTouchDevice ? "none" : "auto", // Disable hover on touch
            }}>
                {rows.map((_, i) => (
                    cols.map((_, j) => (
                        <motion.div
                            key={`cell-${i}-${j}`}
                            whileHover={isTouchDevice ? undefined : {
                                backgroundColor: `var(${getRandomColor()})`,
                                transition: { duration: 0 },
                            }}
                            style={{
                                width: "100%",
                                height: isMobile ? "3rem" : "4rem",
                                borderRight: "1px solid rgba(255, 255, 255, 0.1)",
                                borderBottom: "1px solid rgba(255, 255, 255, 0.1)",
                                position: "relative",
                            }}
                        >
                            {/* Reduce plus icons on mobile */}
                            {!isMobile && j % 2 === 0 && i % 2 === 0 ? (
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    strokeWidth="1.5"
                                    stroke="currentColor"
                                    style={{
                                        position: "absolute",
                                        top: "-10px",
                                        left: "-10px",
                                        width: "20px",
                                        height: "20px",
                                        color: "rgba(255,255,255,0.1)",
                                        pointerEvents: "none"
                                    }}
                                >
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v12m6-6H6" />
                                </svg>
                            ) : null}
                        </motion.div>
                    ))
                ))}
            </div>
        </div>
    );
};

export default Boxes;

