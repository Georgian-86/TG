import React, { useState, useRef, useEffect } from 'react';
import '../styles/auth.css';

export default function OTPInput({ value, onChange, onComplete, error, disabled }) {
    const [otp, setOtp] = useState(value || ['', '', '', '', '', '']);
    const inputRefs = useRef([]);

    useEffect(() => {
        if (value && value.length === 6) {
            setOtp(value.split(''));
        }
    }, [value]);

    const handleChange = (index, val) => {
        if (disabled) return;

        // Only allow numeric input
        if (val && !/^\d$/.test(val)) return;

        const newOtp = [...otp];
        newOtp[index] = val;
        setOtp(newOtp);

        // Notify parent
        const otpString = newOtp.join('');
        onChange(otpString);

        // Auto-advance to next input
        if (val && index < 5) {
            inputRefs.current[index + 1].focus();
        }

        // Call onComplete if all digits entered
        if (otpString.length === 6 && onComplete) {
            onComplete(otpString);
        }
    };

    const handleKeyDown = (index, e) => {
        if (disabled) return;

        // Handle backspace
        if (e.key === 'Backspace' && !otp[index] && index > 0) {
            inputRefs.current[index - 1].focus();
        }

        // Handle arrow key navigation
        if (e.key === 'ArrowLeft' && index > 0) {
            inputRefs.current[index - 1].focus();
        }
        if (e.key === 'ArrowRight' && index < 5) {
            inputRefs.current[index + 1].focus();
        }
    };

    const handlePaste = (e) => {
        e.preventDefault();
        if (disabled) return;

        const pastedData = e.clipboardData.getData('text').trim();

        // Check if it's a valid 6-digit OTP
        if (/^\d{6}$/.test(pastedData)) {
            const newOtp = pastedData.split('');
            setOtp(newOtp);
            onChange(pastedData);

            // Focus last input
            inputRefs.current[5].focus();

            // Call onComplete
            if (onComplete) {
                onComplete(pastedData);
            }
        }
    };

    const handleFocus = (index) => {
        // Select the content when focused
        if (inputRefs.current[index]) {
            inputRefs.current[index].select();
        }
    };

    return (
        <div className="otp-input-container">
            <div className="otp-input-boxes">
                {otp.map((digit, index) => (
                    <input
                        key={index}
                        ref={(ref) => (inputRefs.current[index] = ref)}
                        type="text"
                        inputMode="numeric"
                        maxLength="1"
                        value={digit}
                        onChange={(e) => handleChange(index, e.target.value)}
                        onKeyDown={(e) => handleKeyDown(index, e)}
                        onPaste={handlePaste}
                        onFocus={() => handleFocus(index)}
                        disabled={disabled}
                        className={`otp-input-box ${error ? 'error' : ''} ${disabled ? 'disabled' : ''}`}
                        autoFocus={index === 0}
                        aria-label={`Digit ${index + 1} of 6`}
                    />
                ))}
            </div>
            {error && (
                <p className="error-message" style={{ marginTop: '12px', textAlign: 'center' }}>
                    {error}
                </p>
            )}
        </div>
    );
}
