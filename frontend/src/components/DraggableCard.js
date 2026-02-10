import React, { useRef, useState, useEffect } from "react";
import {
    motion,
    useMotionValue,
    useSpring,
    useTransform,
    useAnimationControls,
    useInView,
} from "framer-motion";
import '../styles/draggable-gallery.css';

export const DraggableCardBody = ({
    className,
    children,
    style,
    containerRef // Add prop to receive container ref
}) => {
    const mouseX = useMotionValue(0);
    const mouseY = useMotionValue(0);
    const cardRef = useRef(null);
    const controls = useAnimationControls();
    const [isDragging, setIsDragging] = useState(false);
    const [rotation, setRotation] = useState(style?.rotate || 0);
    const [hasBeenDragged, setHasBeenDragged] = useState(false);
    const [constraints, setConstraints] = useState({
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
    });

    // Check if the gallery container is in view
    const isInView = useInView(containerRef || cardRef, {
        amount: 0.3, // Trigger when 30% visible
        once: false // Keep checking
    });

    const springConfig = {
        stiffness: 100,
        damping: 20,
        mass: 0.5,
    };

    // 3D tilt based on mouse position
    const rotateX = useSpring(useTransform(mouseY, [-300, 300], [25, -25]), springConfig);
    const rotateY = useSpring(useTransform(mouseX, [-300, 300], [-25, 25]), springConfig);
    const opacity = useSpring(useTransform(mouseX, [-300, 0, 300], [0.9, 1, 0.9]), springConfig);
    const glareOpacity = useSpring(useTransform(mouseX, [-300, 0, 300], [0.15, 0, 0.15]), springConfig);

    useEffect(() => {
        const updateConstraints = () => {
            if (typeof window !== "undefined") {
                setConstraints({
                    top: -window.innerHeight,
                    left: -window.innerWidth,
                    right: window.innerWidth,
                    bottom: window.innerHeight,
                });
            }
        };

        updateConstraints();
        window.addEventListener("resize", updateConstraints);
        return () => {
            window.removeEventListener("resize", updateConstraints);
        };
    }, []);

    // Auto-stack when scrolling away from the section
    useEffect(() => {
        if (!isInView && hasBeenDragged) {
            // Return cards to stack when section is out of view
            controls.start({
                x: 0,
                y: 0,
                rotate: style?.rotate || 0,
                scale: 1,
                transition: {
                    duration: 0.8,
                    type: "spring",
                    bounce: 0.2
                }
            });
            setRotation(style?.rotate || 0);
            setHasBeenDragged(false);
        }

        // Reshuffle animation when section comes into view
        if (isInView && !hasBeenDragged) {
            const reshuffleSequence = async () => {
                // Generate random position for spread effect
                const randomX = (Math.random() - 0.5) * 300; // Random X between -150 and 150
                const randomY = (Math.random() - 0.5) * 200; // Random Y between -100 and 100
                const randomRotate = (Math.random() - 0.5) * 30; // Random rotation between -15 and 15

                // Step 1: Spread cards out
                await controls.start({
                    x: randomX,
                    y: randomY,
                    rotate: randomRotate,
                    transition: {
                        duration: 0.8,
                        ease: "easeOut"
                    }
                });

                // Step 2: Bring cards back to stack
                await controls.start({
                    x: 0,
                    y: 0,
                    rotate: style?.rotate || 0,
                    transition: {
                        duration: 0.6,
                        type: "spring",
                        bounce: 0.3
                    }
                });
            };
            reshuffleSequence();
        }
    }, [isInView, hasBeenDragged, controls, style?.rotate]);

    const handleMouseMove = (e) => {
        if (isDragging) return; // Don't update tilt while dragging

        const { clientX, clientY } = e;
        const { width, height, left, top } =
            cardRef.current?.getBoundingClientRect() ?? {
                width: 0,
                height: 0,
                left: 0,
                top: 0,
            };
        const centerX = left + width / 2;
        const centerY = top + height / 2;
        const deltaX = clientX - centerX;
        const deltaY = clientY - centerY;
        mouseX.set(deltaX);
        mouseY.set(deltaY);
    };

    const handleMouseLeave = () => {
        mouseX.set(0);
        mouseY.set(0);
    };

    // Handle rotation via shift+drag
    const handleDrag = (event, info) => {
        setHasBeenDragged(true);
        // If shift is held, rotate the card instead of moving
        if (event.shiftKey) {
            const newRotation = rotation + info.delta.x * 0.5;
            setRotation(newRotation);
            controls.set({ rotate: newRotation });
        }
    };

    return (
        <motion.div
            ref={cardRef}
            drag
            dragMomentum={false}
            dragConstraints={constraints}
            onDragStart={() => {
                setIsDragging(true);
                setHasBeenDragged(true);
                document.body.style.cursor = "grabbing";
            }}
            onDrag={handleDrag}
            onDragEnd={() => {
                setIsDragging(false);
                document.body.style.cursor = "default";
                // Reset tilt but keep position and rotation
                // The auto-stacking useEffect will handle full reset if out of view
                controls.start({
                    rotateX: 0,
                    rotateY: 0,
                    transition: {
                        type: "spring",
                        ...springConfig,
                    },
                });
            }}
            style={{
                rotateX,
                rotateY,
                opacity,
                rotate: rotation,
                willChange: "transform",
                ...style,
                rotate: style?.rotate || 0, // Initial rotation from style
            }}
            initial={{
                x: 0,
                y: 0,
                rotate: style?.rotate || 0,
                scale: 1
            }}
            animate={controls}
            whileHover={{ scale: 1.03, zIndex: 50 }}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
            className={`draggable-card ${className || ''}`}
        >
            {children}
            <motion.div
                style={{
                    opacity: glareOpacity,
                }}
                className="draggable-card-glare"
            />
        </motion.div>
    );
};

export const DraggableCardContainer = ({
    className,
    children
}) => {
    const containerRef = useRef(null);

    // Clone children and pass containerRef to each DraggableCardBody
    const childrenWithProps = React.Children.map(children, child => {
        if (child && child.type === DraggableCardBody) {
            return React.cloneElement(child, { containerRef });
        }
        return child;
    });

    return (
        <div ref={containerRef} className={`draggable-card-container ${className || ''}`}>
            {childrenWithProps}
        </div>
    );
};
