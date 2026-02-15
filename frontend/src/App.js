import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Team from './pages/Team';
import GeneratorPage from './pages/GeneratorPage';
import LearnMore from './pages/LearnMore';
import Login from './pages/Login';
import Signup from './pages/Signup';
import VerifyEmail from './pages/VerifyEmail';
import CompleteProfile from './pages/CompleteProfile';
import AuthCallback from './pages/AuthCallback';
import SettingsPage from './pages/SettingsPage';
import PricingPage from './pages/PricingPage';
import LoadingScreen from './components/LoadingScreen';
import ScrollToHash from './components/ScrollToHash';
import ErrorBoundary from './components/ErrorBoundary';
import ProtectedRoute from './components/ProtectedRoute';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './context/AuthContext';
import GlobalPrompts from './components/GlobalPrompts';
import './styles/index.css';
import './styles/responsive.css'; // Responsive design system
import './styles/mobile-responsive-fixes.css'; // Mobile fixes for all devices including iPhone 16
import './styles/ModernTheme.css'; // Add Modern Theme
import './styles/theme-light.css';
import './styles/theme-dark.css';
import './styles/theme-dark-extended.css'; // Extended dark mode contrast fixes
import './styles/theme-light-overrides.css';

function App() {
  const [isLoading, setIsLoading] = useState(true);

  return (
    <ErrorBoundary>
      {isLoading && <LoadingScreen onComplete={() => setIsLoading(false)} />}
      <AuthProvider>
        <ThemeProvider>
          <Router>
            <ScrollToHash />
            <GlobalPrompts />
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/team" element={<Team />} />
              <Route path="/learn-more" element={<LearnMore />} />
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/verify-email" element={<VerifyEmail />} />
              <Route path="/complete-profile" element={<CompleteProfile />} />
              <Route path="/auth-callback" element={<AuthCallback />} />

              {/* Protected Routes */}
              <Route path="/pricing" element={<PricingPage />} />
              <Route path="/generator" element={
                <ProtectedRoute>
                  <GeneratorPage />
                </ProtectedRoute>
              } />
              <Route path="/generator/:lessonId" element={
                <ProtectedRoute>
                  <GeneratorPage />
                </ProtectedRoute>
              } />
              <Route path="/settings" element={
                <ProtectedRoute>
                  <SettingsPage />
                </ProtectedRoute>
              } />
            </Routes>
          </Router>
        </ThemeProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
