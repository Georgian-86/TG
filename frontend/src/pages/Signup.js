import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Select from 'react-select';
import GoogleSignInButton from '../components/GoogleSignInButton';
import OTPInput from '../components/OTPInput';
import { Mail, Lock, User, Building2, Eye, EyeOff, Phone, MapPin, ArrowRight, ArrowLeft, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { API_BASE_URL } from '../lib/api/client';
import '../styles/auth.css';
import '../styles/otp.css';

export default function Signup() {
  const [currentStep, setCurrentStep] = useState(0); // 0=landing, 1=basic, 2=email-verify, 3=location, 4=security
  const [countries, setCountries] = useState([]);
  const [institutions, setInstitutions] = useState([]);
  const [isLoadingUnis, setIsLoadingUnis] = useState(false);
  const [showOtherInstitution, setShowOtherInstitution] = useState(false);

  // OTP verification state
  const [otp, setOtp] = useState('');
  const [isVerifyingOtp, setIsVerifyingOtp] = useState(false);

  // Helper to ensure error is always a string
  const safeError = (err) => {
    if (typeof err === 'string') return err;
    if (typeof err === 'object') {
      return err.message || err.msg || JSON.stringify(err);
    }
    return String(err);
  };
  const [otpError, setOtpError] = useState('');
  const [canResendOtp, setCanResendOtp] = useState(false);
  const [resendCountdown, setResendCountdown] = useState(60);
  const [emailVerified, setEmailVerified] = useState(false);

  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    countryCode: '+1',
    phoneNumber: '',
    country: null,
    institution: null,
    otherInstitution: '',
    password: '',
    confirmPassword: ''
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [agreed, setAgreed] = useState(false);

  const navigate = useNavigate();
  const { register } = useAuth();

  // Fetch Countries
  useEffect(() => {
    fetch('https://restcountries.com/v3.1/all?fields=name')
      .then(res => res.json())
      .then(data => {
        const options = data
          .map(c => ({ value: c.name.common, label: c.name.common }))
          .sort((a, b) => a.label.localeCompare(b.label));
        setCountries(options);
      })
      .catch(err => console.error("Error fetching countries", err));
  }, []);

  // Fetch Universities when Country changes
  useEffect(() => {
    if (formData.country?.value) {
      setIsLoadingUnis(true);
      fetch(`${API_BASE_URL}/api/v1/auth/universities?country=${formData.country.value}`)
        .then(res => res.json())
        .then(data => {
          const options = data
            .map(uni => ({ value: uni.name, label: uni.name }))
            .sort((a, b) => a.label.localeCompare(b.label));
          options.push({ value: 'other', label: 'Other (Specify below)' });
          setInstitutions(options);
          setIsLoadingUnis(false);
        })
        .catch(() => {
          setInstitutions([{ value: 'other', label: 'Other (Specify below)' }]);
          setIsLoadingUnis(false);
        });
    }
  }, [formData.country]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleSelectChange = (name, selectedOption) => {
    setFormData(prev => ({ ...prev, [name]: selectedOption }));
    setError('');
    if (name === 'institution') {
      setShowOtherInstitution(selectedOption?.value === 'other');
    }
  };

  const validateStep = (step) => {
    switch (step) {
      case 1:
        // Step 1: Basic Info (Name, Email)
        if (!formData.fullName.trim()) {
          setError('Please enter your full name');
          return false;
        }
        if (!formData.email.trim() || !/\S+@\S+\.\S+/.test(formData.email)) {
          setError('Please enter a valid email address');
          return false;
        }
        return true;
      case 2:
        // Step 2: OTP Verification (handled separately)
        return emailVerified;
      case 3:
        // Step 3: Location (Country, Institution, Phone)
        if (!formData.country) {
          setError('Please select your country');
          return false;
        }
        if (!formData.institution) {
          setError('Please select your institution');
          return false;
        }
        if (formData.institution?.value === 'other' && !formData.otherInstitution.trim()) {
          setError('Please specify your institution');
          return false;
        }
        if (!formData.phoneNumber.trim()) {
          setError('Please enter your phone number');
          return false;
        }
        return true;
      case 4:
        // Step 4: Password/Security
        if (formData.password.length < 8) {
          setError('Password must be at least 8 characters');
          return false;
        }
        if (formData.password !== formData.confirmPassword) {
          setError('Passwords do not match');
          return false;
        }
        if (!agreed) {
          setError('Please agree to the Terms and Conditions');
          return false;
        }
        return true;
      default:
        return true;
    }
  };

  const prevStep = () => {
    if (currentStep === 2 && emailVerified) {
      // If going back from email verify step, reset verification
      setEmailVerified(false);
      setOtp('');
      setOtpError('');
    }
    setCurrentStep(prev => prev - 1);
    setError('');
  };

  // Send OTP to email - returns true if successful
  const sendOtp = async () => {
    setError('');
    setOtpError('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/send-verification-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: formData.email })
      });

      const data = await response.json();

      if (response.ok) {
        // DEV MODE: Auto-fill OTP if returned
        if (data.dev_otp) {
          setOtp(data.dev_otp);
          alert(`DEV MODE OTP: ${data.dev_otp}`);
        }

        // Start countdown
        setResendCountdown(60);
        setCanResendOtp(false);
        const timer = setInterval(() => {
          setResendCountdown((prev) => {
            if (prev <= 1) {
              setCanResendOtp(true);
              clearInterval(timer);
              return 0;
            }
            return prev - 1;
          });
        }, 1000);
        return true;
      } else {
        // Show error on step 1 (not OTP error) so user sees it before advancing
        setError(data.detail || 'Failed to send OTP');
        return false;
      }
    } catch (err) {
      setError('Network error. Please try again.');
      return false;
    }
  };

  // Verify OTP
  const verifyOtp = async (otpCode) => {
    setIsVerifyingOtp(true);
    setOtpError('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/verify-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          otp: otpCode
        })
      });

      const data = await response.json();

      if (response.ok && data.verified) {
        setEmailVerified(true);
        setOtpError('');
        // Auto-advance to next step after verification
        setTimeout(() => {
          setCurrentStep(3); // Go to location step
        }, 500);
      } else {
        setOtpError(data.detail || data.error || 'Invalid verification code');
        setOtp('');
      }
    } catch (err) {
      setOtpError('Network error. Please try again.');
      setOtp('');
    } finally {
      setIsVerifyingOtp(false);
    }
  };

  // Resend OTP
  const resendOtp = async () => {
    if (!canResendOtp) return;
    await sendOtp();
  };

  const nextStep = async () => {
    if (currentStep === 0) {
      setCurrentStep(1);
    } else if (currentStep === 1 && validateStep(1)) {
      // After basic info, send OTP - only advance if successful
      const success = await sendOtp();
      if (success) {
        setCurrentStep(2);
      }
    } else if (currentStep === 2 && emailVerified) {
      // Email verified, go to location
      setCurrentStep(3);
    } else if (currentStep === 3 && validateStep(3)) {
      // Location validated, go to password/security step
      setCurrentStep(4);
    } else if (currentStep === 3) {
      // If validation fails, show error but don't advance
      console.log('Step 3 validation failed');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateStep(4)) return;

    setLoading(true);
    setError('');

    try {
      const institutionName = formData.institution?.value === 'other'
        ? formData.otherInstitution
        : formData.institution?.value;

      await register({
        fullName: formData.fullName,
        email: formData.email,
        password: formData.password,
        country: formData.country?.value,
        phoneNumber: `${formData.countryCode}${formData.phoneNumber}`,
        organization: institutionName,
      });

      // Send OTP verification email
      try {
        const otpResponse = await fetch(`${API_BASE_URL}/api/v1/auth/send-verification-email`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email: formData.email })
        });

        if (otpResponse.ok) {
          // Store email for verification page
          sessionStorage.setItem('verificationEmail', formData.email);
          // Redirect to verification page
          navigate('/verify-email', { state: { email: formData.email } });
        } else {
          // If OTP sending fails, still let them login but show a warning
          console.warn('Failed to send verification email');
          navigate('/login', {
            state: {
              message: 'Account created! Please login. (Email verification will be sent later)'
            }
          });
        }
      } catch (otpError) {
        console.error('Error sending OTP:', otpError);
        // Fall back to login if OTP fails
        navigate('/login', {
          state: {
            message: 'Account created! Please login.'
          }
        });
      }
    } catch (err) {
      console.error('Signup error:', err);
      console.log('Error type:', typeof err);
      console.log('Error keys:', Object.keys(err));
      console.log('Error.message:', err.message);
      console.log('Error.response:', err.response);
      console.log('Error response data:', err.response?.data);
      console.log('Error response detail:', err.response?.data?.detail);
      console.log('Full error JSON:', JSON.stringify(err, Object.getOwnPropertyNames(err)));

      // Extract error message from various error formats
      let errorMessage = 'Failed to create account. Please try again.';

      // Check if error.message is an array (from our API wrapper)
      if (Array.isArray(err.message)) {
        errorMessage = err.message.map(e => {
          if (typeof e === 'string') return e;
          if (e.msg) return e.msg;
          if (e.message) return e.message;
          return 'Validation error';
        }).join(', ');
      } else if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        console.log('Detail type:', typeof detail, 'Is array:', Array.isArray(detail));

        if (Array.isArray(detail)) {
          // Pydantic validation errors
          errorMessage = detail.map(e => {
            console.log('Detail item:', e, 'Type:', typeof e);
            if (typeof e === 'string') return e;
            return e.msg || e.message || 'Validation error';
          }).join(', ');
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        } else {
          // detail is an object
          errorMessage = JSON.stringify(detail);
        }
      } else if (err.response?.data?.message) {
        const message = err.response.data.message;
        if (Array.isArray(message)) {
          errorMessage = message.map(e => {
            if (typeof e === 'string') return e;
            return e.msg || e.message || String(e);
          }).join(', ');
        } else {
          errorMessage = String(message);
        }
      } else if (typeof err.message === 'string') {
        errorMessage = err.message;
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const renderProgressDots = () => {
    if (currentStep === 0) return null;
    return (
      <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginBottom: '12px' }}>
        {[1, 2, 3, 4].map(step => (
          <div
            key={step}
            style={{
              width: currentStep === step ? '32px' : '8px',
              height: '8px',
              borderRadius: '4px',
              backgroundColor: currentStep >= step ? '#f97316' : '#e5e7eb',
              transition: 'all 0.3s ease'
            }}
          />
        ))}
      </div>
    );
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="step-container" style={{ textAlign: 'center' }}>
            <button
              type="button"
              onClick={nextStep}
              className="btn btn-accent btn-large"
              style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
            >
              Get Started <ArrowRight size={20} />
            </button>

            <div className="auth-divider">
              <span>or sign up with Google</span>
            </div>

            <GoogleSignInButton text="Sign up with Google" />

            <p style={{ marginTop: '16px', fontSize: '14px', color: '#6b7280' }}>
              Already have an account? <Link to="/login" style={{ color: '#f97316', fontWeight: '600' }}>Log in</Link>
            </p>
          </div>
        );

      case 1:
        return (
          <div className="step-container">
            <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '24px', textAlign: 'center' }}>
              Let's start with the basics
            </h3>

            <div className="form-group">
              <label><User size={20} /> Full Name</label>
              <input
                type="text"
                name="fullName"
                value={formData.fullName}
                onChange={handleChange}
                placeholder="Enter your full name"
                autoFocus
              />
            </div>

            <div className="form-group">
              <label><Mail size={20} /> Email Address</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="your.email@example.com"
              />
            </div>
          </div>
        );

      case 2:
        return (
          <div className="step-container" style={{ textAlign: 'center' }}>
            <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '12px' }}>
              Verify Your Email
            </h3>
            <p style={{ color: '#6b7280', marginBottom: '30px' }}>
              We sent a 6-digit code to <strong>{formData.email}</strong>
            </p>

            <div style={{ marginTop: '30px' }}>
              <OTPInput
                value={otp}
                onChange={setOtp}
                onComplete={verifyOtp}
                error={otpError}
                disabled={isVerifyingOtp}
              />
            </div>

            {otpError && (
              <div style={{
                background: '#fee2e2',
                border: '1px solid #ef4444',
                borderRadius: '8px',
                padding: '12px',
                marginTop: '20px',
                color: '#991b1b',
                fontSize: '14px'
              }}>
                {otpError}
              </div>
            )}

            <div style={{ marginTop: '30px' }}>
              <p style={{ color: '#6b7280', fontSize: '14px', marginBottom: '15px' }}>
                Didn't receive the code?
              </p>

              {canResendOtp ? (
                <button
                  type="button"
                  onClick={resendOtp}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: '#f97316',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    textDecoration: 'underline'
                  }}
                >
                  Resend Code
                </button>
              ) : (
                <p style={{ color: '#9ca3af', fontSize: '14px' }}>
                  Resend available in {resendCountdown}s
                </p>
              )}
            </div>

            <div style={{
              marginTop: '30px',
              padding: '15px',
              background: '#fff7ed',
              borderRadius: '8px',
              borderLeft: '4px solid #f97316'
            }}>
              <p style={{ fontSize: '13px', color: '#78350f', margin: 0 }}>
                <strong>⏱️ Code expires in 10 minutes</strong><br />
                Enter the code to continue with your registration.
              </p>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="step-container">
            <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '24px', textAlign: 'center' }}>
              Where are you from?
            </h3>

            <div className="form-group">
              <label><MapPin size={20} /> Country</label>
              <Select
                name="country"
                options={countries}
                value={formData.country}
                onChange={(opt) => handleSelectChange('country', opt)}
                placeholder="Select your country"
                menuPortalTarget={document.body}
                menuPlacement="auto"
                maxMenuHeight={200}
                styles={{
                  control: (base) => ({ ...base, borderColor: '#e5e7eb', '&:hover': { borderColor: '#f97316' } }),
                  option: (base, state) => ({ ...base, backgroundColor: state.isSelected ? '#f97316' : state.isFocused ? '#fff7ed' : 'white' }),
                  menuPortal: (base) => ({ ...base, zIndex: 9999 })
                }}
              />
            </div>

            <div className="form-group">
              <label><Building2 size={20} /> Institution/Organization</label>
              <Select
                name="institution"
                options={institutions}
                value={formData.institution}
                onChange={(opt) => handleSelectChange('institution', opt)}
                placeholder="Select your institution"
                isLoading={isLoadingUnis}
                isDisabled={!formData.country}
                menuPortalTarget={document.body}
                menuPlacement="auto"
                maxMenuHeight={200}
                styles={{
                  control: (base) => ({ ...base, borderColor: '#e5e7eb', '&:hover': { borderColor: '#f97316' } }),
                  option: (base, state) => ({ ...base, backgroundColor: state.isSelected ? '#f97316' : state.isFocused ? '#fff7ed' : 'white' }),
                  menuPortal: (base) => ({ ...base, zIndex: 9999 })
                }}
              />
            </div>

            {showOtherInstitution && (
              <div className="form-group">
                <label><Building2 size={20} /> Specify Institution</label>
                <input
                  type="text"
                  name="otherInstitution"
                  value={formData.otherInstitution}
                  onChange={handleChange}
                  placeholder="Enter your institution name"
                />
              </div>
            )}

            <div className="form-group">
              <label><Phone size={20} /> Phone Number</label>
              <div style={{ display: 'flex', gap: '8px' }}>
                <select
                  name="countryCode"
                  value={formData.countryCode}
                  onChange={handleChange}
                  style={{ width: '100px', padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
                >
                  <option value="+1">+1</option>
                  <option value="+44">+44</option>
                  <option value="+91">+91</option>
                  <option value="+86">+86</option>
                  <option value="+33">+33</option>
                  <option value="+49">+49</option>
                </select>
                <input
                  type="tel"
                  name="phoneNumber"
                  value={formData.phoneNumber}
                  onChange={handleChange}
                  placeholder="123-456-7890"
                  style={{ flex: 1 }}
                />
              </div>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="step-container">
            <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '24px', textAlign: 'center' }}>
              Secure your account
            </h3>

            <div className="form-group">
              <label><Lock size={20} /> Password</label>
              <div style={{ position: 'relative' }}>
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="At least 8 characters"
                  minLength="8"
                />
                <button
                  type="button"
                  className="toggle-password"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer' }}
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              {error && error.includes('Password must be') && (
                <p style={{ color: '#ef4444', fontSize: '13px', marginTop: '6px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <AlertCircle size={14} /> {safeError(error)}
                </p>
              )}

            </div>

            <div className="form-group">
              <label><Lock size={20} /> Confirm Password</label>
              <div style={{ position: 'relative' }}>
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  placeholder="Re-enter your password"
                  minLength="8"
                />
                <button
                  type="button"
                  className="toggle-password"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer' }}
                >
                  {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              {error === 'Passwords do not match' && (
                <p style={{ color: '#ef4444', fontSize: '13px', marginTop: '6px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <AlertCircle size={14} /> Passwords do not match
                </p>
              )}

            </div>

            <div className="form-group">
              <label className="checkbox-label" style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={agreed}
                  onChange={(e) => setAgreed(e.target.checked)}
                />
                <span>I agree to the Terms and Conditions</span>
              </label>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-wrapper">
        <div className="auth-card">
          <div className="auth-header">
            <div className="logo" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px' }}>
              <img src="/TechGenieMascot.png" alt="TeachGenie" style={{ width: '50px', height: '50px', borderRadius: '50%', objectFit: 'cover' }} />
              <h1>Teach<span style={{ color: '#f97316' }}>Genie</span></h1>
            </div>
            <p className="tagline">Join Educators Using AI for Better Teaching</p>

            <div className="auth-tabs">
              <Link to="/login" className="auth-tab">Login</Link>
              <Link to="/signup" className="auth-tab active">Register</Link>
            </div>
          </div>

          {error && !error.includes('Password') && !error.includes('fields') && !error.includes('Terms') && (
            <div style={{
              padding: '12px',
              backgroundColor: '#fee2e2',
              borderRadius: '8px',
              marginBottom: '16px',
              color: '#991b1b',
              fontSize: '14px',
              textAlign: 'center'
            }}>
              ⚠️ {safeError(error)}
            </div>
          )}

          {renderProgressDots()}

          <form onSubmit={handleSubmit} className="auth-form" style={{ width: '100%', display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
            {/* Scrollable content area */}
            <div className="auth-form-container" style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden' }}>
              {renderStepContent()}
            </div>

            {/* Fixed buttons at bottom */}
            {currentStep > 0 && (
              <div style={{
                display: 'flex',
                gap: '8px',
                marginTop: '12px',
                width: '100%',
                boxSizing: 'border-box',
                flexShrink: 0
              }}>
                {currentStep > 0 && currentStep !== 2 && (
                  <button
                    type="button"
                    onClick={prevStep}
                    className="btn btn-secondary"
                    style={{
                      flex: 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px',
                      minWidth: 0,
                      padding: '14px 20px',
                    }}
                  >
                    <ArrowLeft size={20} /> Back
                  </button>
                )}

                <button
                  type={currentStep === 4 ? 'submit' : 'button'}
                  onClick={currentStep === 4 ? undefined : nextStep}
                  disabled={loading}
                  className="btn btn-primary"
                  style={{
                    flex: currentStep < 3 ? 2 : 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    minWidth: 0,
                    padding: '14px 20px',
                  }}
                >
                  {loading ? 'Creating...' : currentStep === 4 ? 'Create Account' : 'Next'}
                  {!loading && currentStep < 3 && <ArrowRight size={20} />}
                </button>
              </div>
            )}
          </form>
        </div>

        <div className="auth-benefits">
          <h2>Why Choose Teach Genie?</h2>
          <ul>
            <li>
              <span className="benefit-icon">🤖</span>
              <div>
                <h4>AI-Powered Generation</h4>
                <p>Advanced AI agents instantly generate professional lecture materials</p>
              </div>
            </li>
            <li>
              <span className="benefit-icon">⚡</span>
              <div>
                <h4>Save Hours of Work</h4>
                <p>Create complete materials in minutes, not hours</p>
              </div>
            </li>
            <li>
              <span className="benefit-icon">🎓</span>
              <div>
                <h4>For All Levels</h4>
                <p>From school to postgraduate, we've got you covered</p>
              </div>
            </li>
            <li>
              <span className="benefit-icon">📚</span>
              <div>
                <h4>Multiple Formats</h4>
                <p>PDF, PowerPoint, Word - download in your preferred format</p>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}