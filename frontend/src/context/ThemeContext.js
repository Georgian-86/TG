import React, { createContext, useState, useEffect } from 'react';

export const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    // Get theme from localStorage or default to 'light'
    const savedTheme = localStorage.getItem('techgenie-theme');
    return savedTheme || 'light';
  });

  // Update localStorage and apply theme
  useEffect(() => {
    localStorage.setItem('techgenie-theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => {
      const themes = ['light', 'dark'];
      const currentIndex = themes.indexOf(prevTheme);
      return themes[(currentIndex + 1) % themes.length];
    });
  };

  const themes = {
    light: {
      name: 'Light',
      icon: '☀️'
    },
    dark: {
      name: 'Dark',
      icon: '🌙'
    }
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, themes }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = React.useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};
