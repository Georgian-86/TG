import React from 'react';
import '../styles/generator.css'; // Ensure styles are imported

/**
 * Beautiful cognitive load indicator with gradient bars
 * Redesigned for Mobile & Research Level Support
 */
const CognitiveLoadGauge = ({ level, duration }) => {
    // Calculate load level and get colors
    const getLoadMetrics = (lvl, mins) => {
        const m = parseInt(mins);
        const l = lvl ? lvl.toLowerCase() : 'undergraduate';

        // 5-Level Gradient Color Scheme: Green -> Golden -> Blue -> Orange -> Red
        const levels = {
            1: {
                label: 'Light Load',
                color: '#10b981',
                gradient: 'linear-gradient(135deg, #34d399 0%, #10b981 100%)',
                bgColor: '#ecfdf5'
            },
            2: {
                label: 'Moderate',
                color: '#f59e0b',
                gradient: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
                bgColor: '#fffbeb'
            },
            3: {
                label: 'Standard',
                color: '#3b82f6',
                gradient: 'linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%)',
                bgColor: '#eff6ff'
            },
            4: {
                label: 'Deep Dive',
                color: '#f97316',
                gradient: 'linear-gradient(135deg, #fb923c 0%, #f97316 100%)',
                bgColor: '#fff7ed'
            },
            5: {
                label: 'Intensive/Research',
                color: '#ef4444',
                gradient: 'linear-gradient(135deg, #f87171 0%, #ef4444 100%)',
                bgColor: '#fef2f2'
            }
        };

        let loadLevel = 3; // default

        // School level
        if (l === 'school') {
            if (m <= 15) loadLevel = 1;
            else if (m <= 25) loadLevel = 2;
            else if (m <= 30) loadLevel = 3;
            else if (m <= 60) loadLevel = 4;
            else loadLevel = 5;
        }
        // Undergraduate level
        else if (l === 'undergraduate') {
            if (m <= 30) loadLevel = 1;
            else if (m <= 45) loadLevel = 2;
            else if (m <= 60) loadLevel = 3;
            else if (m <= 90) loadLevel = 4;
            else loadLevel = 5;
        }
        // Postgraduate level
        else if (l === 'postgraduate') {
            if (m <= 45) loadLevel = 1;
            else if (m <= 60) loadLevel = 2;
            else if (m <= 90) loadLevel = 3;
            else if (m <= 120) loadLevel = 4;
            else loadLevel = 5;
        }
        // Research level
        else if (l === 'research') {
            if (m <= 60) loadLevel = 1;
            else if (m <= 90) loadLevel = 2;
            else if (m <= 120) loadLevel = 3;
            else if (m <= 150) loadLevel = 4;
            else loadLevel = 5;
        }
        // Fallback
        else {
            if (m <= 60) loadLevel = 1;
            else if (m <= 90) loadLevel = 2;
            else if (m <= 120) loadLevel = 3;
            else if (m <= 150) loadLevel = 4;
            else loadLevel = 5;
        }

        return { loadLevel, ...levels[loadLevel] };
    };

    const { loadLevel, label, color, gradient } = getLoadMetrics(level, duration);

    return (
        <div className="cognitive-load-component" style={{ width: '100%' }}>
            {/* Title */}
            <div className="cognitive-load-title" style={{
                fontSize: '11px',
                fontWeight: '700',
                color: '#64748b',
                letterSpacing: '0.5px',
                marginBottom: '8px',
                textTransform: 'uppercase'
            }}>
                COGNITIVE LOAD
            </div>

            {/* Gradient Bars */}
            <div className="cognitive-load-squares" style={{ display: 'flex', gap: '4px', height: '10px', marginBottom: '8px' }}>
                {[1, 2, 3, 4, 5].map((i) => (
                    <div
                        key={i}
                        className={`load-square`}
                        style={{
                            flex: 1,
                            background: i <= loadLevel ? gradient : '#e2e8f0',
                            borderRadius: '3px',
                            transition: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
                            opacity: i <= loadLevel ? 1 : 0.5,
                            boxShadow: i <= loadLevel ? `0 2px 4px ${color}30` : 'none',
                            transform: i <= loadLevel ? 'scaleY(1)' : 'scaleY(0.8)'
                        }}
                    />
                ))}
            </div>

            {/* Label Below Bars */}
            <div
                className="cognitive-level-label"
                style={{
                    color: color,
                    fontSize: '13px',
                    fontWeight: '600',
                    textAlign: 'right'
                }}
            >
                {label}
            </div>
        </div>
    );
};

export default CognitiveLoadGauge;
