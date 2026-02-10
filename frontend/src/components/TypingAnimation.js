import React, { useState, useEffect, useRef, useCallback } from 'react';

export function TypingAnimation({
  words = [],
  className = '',
  duration = 100,
  blinkCursor = true,
}) {
  const [displayedText, setDisplayedText] = useState('');
  const [isComplete, setIsComplete] = useState(false);
  const elementRef = useRef(null);
  const typingIndexRef = useRef(0);

  // Reset and start typing when element comes into view
  const startTyping = useCallback(() => {
    if (words.length === 0) return;

    const word = words[0] || '';
    setDisplayedText('');
    setIsComplete(false);
    typingIndexRef.current = 0;

    const typeChar = () => {
      if (typingIndexRef.current < word.length) {
        setDisplayedText(word.slice(0, typingIndexRef.current + 1));
        typingIndexRef.current++;
        setTimeout(typeChar, duration);
      } else {
        setIsComplete(true);
      }
    };

    // Small delay before starting
    setTimeout(typeChar, 300);
  }, [words, duration]);

  // Intersection Observer - triggers every time element comes into view
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          startTyping();
        }
      },
      { threshold: 0.5 }
    );

    if (elementRef.current) {
      observer.observe(elementRef.current);
    }

    return () => observer.disconnect();
  }, [startTyping]);

  return (
    <span ref={elementRef} className={className}>
      {displayedText}
      {blinkCursor && (
        <span className="typing-cursor blink-cursor">|</span>
      )}
    </span>
  );
}
