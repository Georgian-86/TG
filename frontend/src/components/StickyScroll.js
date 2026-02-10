import React, { useRef, useState } from "react";
import { useMotionValueEvent, useScroll, useTransform, motion } from "framer-motion";
import "../styles/stickyScroll.css";

export const StickyScroll = ({
    content,
    contentClassName,
}) => {
    const [activeCard, setActiveCard] = React.useState(0);
    const ref = useRef(null);
    const { scrollYProgress } = useScroll({
        container: ref,
    });
    const cardLength = content.length;

    useMotionValueEvent(scrollYProgress, "change", (latest) => {
        const cardsBreakpoints = content.map((_, index) => index / cardLength);
        const closestBreakpointIndex = cardsBreakpoints.reduce(
            (acc, breakpoint, index) => {
                const distance = Math.abs(latest - breakpoint);
                if (distance < Math.abs(latest - cardsBreakpoints[acc])) {
                    return index;
                }
                return acc;
            },
            0
        );
        setActiveCard(closestBreakpointIndex);
    });

    const linearGradients = [
        "linear-gradient(to bottom right, var(--cyan-500, #06b6d4), var(--emerald-500, #10b981))",
        "linear-gradient(to bottom right, var(--pink-500, #ec4899), var(--indigo-500, #6366f1))",
        "linear-gradient(to bottom right, var(--orange-500, #f97316), var(--yellow-500, #eab308))",
        "linear-gradient(to bottom right, var(--cyan-500, #06b6d4), var(--emerald-500, #10b981))",
        "linear-gradient(to bottom right, var(--purple-500, #a855f7), var(--pink-500, #ec4899))",
        "linear-gradient(to bottom right, var(--blue-500, #3b82f6), var(--cyan-500, #06b6d4))",
    ];

    return (
        <div className="sticky-scroll-wrapper">
            <div className="sticky-scroll-progress-bar">
                <motion.div
                    className="sticky-scroll-progress-fill"
                    style={{ scaleY: scrollYProgress, originY: 0 }}
                />
            </div>
            <motion.div
                className="sticky-scroll-container"
                ref={ref}
            >
                <div className="sticky-scroll-content-wrapper">
                    <div className="sticky-scroll-text-col">
                        {content.map((item, index) => (
                            <div key={item.title + index} className="sticky-scroll-item">
                                <motion.h2
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: activeCard === index ? 1 : 0.3 }}
                                    className="sticky-scroll-title"
                                >
                                    {item.title}
                                </motion.h2>
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: activeCard === index ? 1 : 0.3 }}
                                    className="sticky-scroll-description"
                                >
                                    {item.description}
                                </motion.div>
                            </div>
                        ))}
                        <div style={{ height: "10rem" }} />
                    </div>
                </div>
                <motion.div
                    animate={{
                        background: linearGradients[activeCard % linearGradients.length],
                    }}
                    className={`sticky-scroll-card ${contentClassName}`}
                >
                    <div className="sticky-scroll-card-content">
                        {content[activeCard].content ?? null}
                    </div>
                </motion.div>
            </motion.div>
        </div>
    );
};
