import React from 'react';
import '../styles/marquee.css';

const Marquee = ({ children, reverse = false, pauseOnHover = true, duration = 20 }) => {
    return (
        <div
            className={`marquee-container ${pauseOnHover ? 'pause-on-hover' : ''}`}
            style={{ '--duration': `${duration}s` }}
        >
            <div className={`marquee-content ${reverse ? 'reverse' : ''}`}>
                <div className="marquee-set">
                    {children}
                </div>
                <div className="marquee-set">
                    {children}
                </div>
            </div>
        </div>
    );
};

export default Marquee;
