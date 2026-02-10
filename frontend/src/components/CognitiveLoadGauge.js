import React from 'react';

/**
 * Beautiful cognitive load indicator with color-coded squares
 */
const CognitiveLoadGauge = ({ level, duration }) => {
    // Calculate load level and get colors
    const getLoadMetrics = (lvl, mins) => {
        const m = parseInt(mins);
        const l = lvl.toLowerCase();

        // Define color schemes for each level
        const levels = {
            1: { label: 'Light Load', color: '#10b981', bgColor: '#d1fae5' },
            2: { label: 'Moderate', color: '#3b82f6', bgColor: '#dbeafe' },
            3: { label: 'Standard', color: '#6366f1', bgColor: '#e0e7ff' },
            4: { label: 'Deep Dive', color: '#8b5cf6', bgColor: '#ede9fe' },
            5: { label: 'Intensive', color: '#f59e0b', bgColor: '#fef3c7' }
        };

        let loadLevel = 3; // default

        // School level
        if (l === 'school') {
            loadLevel = m <= 30 ? 1 : 2;
        }
        // Undergraduate level
        else if (l === 'undergraduate') {
            loadLevel = m <= 45 ? 3 : 4;
        }
        // Postgraduate level
        else if (l === 'postgraduate') {
            loadLevel = m <= 60 ? 4 : 5;
        }
        // Professional level
        else if (l === 'professional') {
            loadLevel = m <= 45 ? 3 : m <= 60 ? 4 : 5;
        }
        // Fallback for any other level
        else {
            loadLevel = 3;
        }

        return { loadLevel, ...levels[loadLevel] };
    };

    const { loadLevel, label, color, bgColor } = getLoadMetrics(level, duration);

    return (
        <div className="cognitive-load-component">
            <div className="cognitive-load-title">COGNITIVE LOAD</div>

            <div className="cognitive-load-squares">
                {[1, 2, 3, 4, 5].map((i) => (
                    <div
                        key={i}
                        className={`load-square ${i <= loadLevel ? 'filled' : ''}`}
                        style={{
                            backgroundColor: i <= loadLevel ? color : 'transparent',
                            borderColor: i <= loadLevel ? color : '#d1d5db',
                            boxShadow: i <= loadLevel ? `0 0 12px ${color}40` : 'none'
                        }}
                    />
                ))}
            </div>

            <div
                className="cognitive-level-badge"
                style={{
                    color: color,
                    backgroundColor: bgColor,
                    borderColor: color
                }}
            >
                {label}
            </div>
        </div>
    );
};

export default CognitiveLoadGauge;
