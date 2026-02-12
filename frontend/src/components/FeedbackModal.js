import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { ChevronRight, ChevronLeft, CheckCircle, Star, X } from 'lucide-react';
import api from '../lib/api/client';
import '../styles/feedback-modal.css';
import Toast from './Toast';

const FeedbackModal = ({ onClose, onUnlock }) => {
    // Debug log to confirm new code loaded
    console.log("FeedbackModal loaded: Refactored V3 (Split Step 11)");

    const { user, refreshUser } = useAuth();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [toast, setToast] = useState({ show: false, message: '', type: 'error' });
    const [valid, setValid] = useState(false);

    const [formData, setFormData] = useState({
        // Section 1: Context
        designation: '',
        department: '',
        teaching_experience: '',
        rating_context: 0,

        // Section 2: Usage
        usage_frequency: '',
        primary_purpose: [],
        rating_usage: 0,

        // Section 3: Time
        time_saved: '',
        speed_vs_manual: '',
        value_single_click: '',
        rating_time: 0,

        // Section 4: Zero-Prompt
        zero_prompt_ease: '',
        complexity_vs_others: '',
        rating_zero_prompt: 0,

        // Section 5: Content
        content_accuracy: '',
        classroom_suitability: '',
        quiz_scenario_relevance: '',
        rating_content: 0,

        // Section 6: UX
        interface_intuitive: '',
        technical_issues: 'No',
        technical_issues_details: '',
        rating_interface: 0,

        // Section 7: Comparison
        comparison_vs_llm: '',
        comparison_objective: '', // New objective question

        // Section 8: Adoption
        will_use_regularly: '',
        will_recommend: '',
        support_adoption: '',
        rating_adoption: 0,

        // Section 9: Open Feedback
        liked_most: '',
        liked_least: '',
        feature_requests: '',
        testimonial_consent: false,

        // Section 10: Verdict
        one_sentence_verdict: '',
        avg_generation_time: '',
        workflow_satisfaction: '',
        rating_workflow: 0,

        // Section 11: Overall (Implicit)
        overall_rating: 0
    });

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        if (type === 'checkbox' && name !== 'testimonial_consent') {
            // Handle multi-select arrays if needed, but for simple yes/no usage primarily
        } else if (type === 'checkbox' && name === 'testimonial_consent') {
            setFormData(prev => ({ ...prev, [name]: checked }));
        } else {
            setFormData(prev => ({ ...prev, [name]: value }));
        }
    };

    const handleMultiSelect = (category, item) => {
        setFormData(prev => {
            const list = prev[category] || [];
            if (list.includes(item)) {
                return { ...prev, [category]: list.filter(i => i !== item) };
            } else {
                return { ...prev, [category]: [...list, item] };
            }
        });
    };

    const steps = [
        { id: 1, title: "Basic Info & Context", fields: ['designation', 'department', 'teaching_experience', 'rating_context'] },
        { id: 2, title: "Usage & Adoption", fields: ['usage_frequency', 'primary_purpose', 'rating_usage'] },
        { id: 3, title: "Time & Productivity", fields: ['time_saved', 'speed_vs_manual', 'value_single_click', 'rating_time'] },
        { id: 4, title: "Zero-Prompt Experience", fields: ['zero_prompt_ease', 'complexity_vs_others', 'rating_zero_prompt'] },
        { id: 5, title: "Content Quality", fields: ['content_accuracy', 'classroom_suitability', 'quiz_scenario_relevance', 'rating_content'] },
        { id: 6, title: "UX & Interface", fields: ['interface_intuitive', 'technical_issues', 'rating_interface'] },
        { id: 7, title: "Comparison & Objective", fields: ['comparison_vs_llm', 'comparison_objective'] },
        { id: 8, title: "Adoption Signals", fields: ['will_use_regularly', 'will_recommend', 'support_adoption', 'rating_adoption'] },
        { id: 9, title: "Open Feedback", fields: ['liked_most', 'liked_least', 'feature_requests'] },
        { id: 10, title: "Final Verdict", fields: ['one_sentence_verdict', 'avg_generation_time', 'workflow_satisfaction', 'rating_workflow'] },
        { id: 11, title: "Overall Review", fields: ['overall_rating'] }
    ];

    // Check validity whenever formData or step changes
    useEffect(() => {
        const currentFields = steps[step - 1].fields;
        const isValid = currentFields.every(field => {
            const val = formData[field];
            if (Array.isArray(val)) return val.length > 0;
            // Ratings must be > 0. Text fields must be non-empty.
            if (field.startsWith('rating_') || field === 'overall_rating') return val > 0;
            if (typeof val === 'string') return val.trim().length > 0;
            return false;
        });
        setValid(isValid);
    }, [formData, step]);

    const nextStep = () => {
        if (valid) setStep(prev => prev + 1);
    };

    const prevStep = () => setStep(prev => prev - 1);

    const handleSubmit = async () => {
        if (!valid) return;
        setLoading(true);
        try {
            await api.post('/api/v1/feedback/', formData);
            await refreshUser(); // Update user state to reflect feedback_provided = true
            onUnlock(); // Trigger parent unlock logic
            onClose();  // Close modal
        } catch (error) {
            console.error("Feedback submission error:", error);
            // Extract error message
            let errorMessage = "Failed to submit feedback.";

            if (error.response) {
                if (error.response.status === 500) {
                    errorMessage = "Server error (500). The dev team has been notified. Please try again in moments.";
                } else {
                    errorMessage = error.response.data?.detail || error.response.data?.message || errorMessage;
                }
            } else if (error.isNetworkError) {
                errorMessage = "Network error. Please check your connection.";
            }

            setToast({ show: true, message: errorMessage, type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const SectionRating = ({ label, name }) => {
        const [hoverValue, setHoverValue] = useState(0);

        return (
            <div className="feedback-field" style={{ marginTop: '20px', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '15px' }}>
                <label style={{ textAlign: 'center', display: 'block' }}>{label} <span style={{ color: '#ef4444' }}>*</span></label>
                <div
                    className="star-rating"
                    style={{ display: 'flex', justifyContent: 'center', marginTop: '10px' }}
                    onMouseLeave={() => setHoverValue(0)}
                >
                    {[1, 2, 3, 4, 5].map(star => (
                        <Star
                            key={star}
                            size={28}
                            fill={(hoverValue || formData[name]) >= star ? "#FFD700" : "none"}
                            color={(hoverValue || formData[name]) >= star ? "#FFD700" : "#ccc"}
                            onMouseEnter={() => setHoverValue(star)}
                            onClick={() => setFormData(p => ({ ...p, [name]: star }))}
                            style={{
                                cursor: 'pointer',
                                transition: 'transform 0.1s',
                                margin: '0 5px',
                                transform: hoverValue === star ? 'scale(1.2)' : 'scale(1)'
                            }}
                        />
                    ))}
                </div>
            </div>
        );
    };

    const renderField = (label, name, type = 'text', options = []) => (
        <div className="feedback-field">
            <label>{label} <span style={{ color: '#ef4444' }}>*</span></label>
            {type === 'select' && (
                <select name={name} value={formData[name]} onChange={handleChange}>
                    <option value="">Select an option</option>
                    {options.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                </select>
            )}
            {type === 'text' && <input type="text" name={name} value={formData[name]} onChange={handleChange} />}
            {type === 'textarea' && <textarea name={name} value={formData[name]} onChange={handleChange} />}
            {type === 'radio' && (
                <div className="radio-group">
                    {options.map(opt => (
                        <label key={opt} className="radio-label">
                            <input
                                type="radio"
                                name={name}
                                value={opt}
                                checked={formData[name] === opt}
                                onChange={handleChange}
                            />
                            {opt}
                        </label>
                    ))}
                </div>
            )}
        </div>
    );

    return (
        <div className="feedback-modal-overlay">
            {/* Wrapper for positioning Close Button "outside" but attached to component */}
            <div style={{ position: 'relative', width: '90%', maxWidth: '650px' }}>
                <button
                    onClick={onClose}
                    style={{
                        position: 'absolute',
                        top: '0',
                        left: '-60px',
                        zIndex: 10001,
                        background: 'rgba(255,255,255,0.1)',
                        padding: '10px',
                        borderRadius: '50%',
                        color: '#fff',
                        transition: 'background 0.3s',
                        border: 'none',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.2)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
                >
                    <X size={24} />
                </button>

                <div className="feedback-modal" style={{ width: '100%', maxWidth: '100%' }}>
                    {/* Decorative Elements */}
                    <div className="modal-glow"></div>

                    <div className="feedback-header">
                        <div className="header-content">
                            <h2>✨ Help Us Shape TeachGenie</h2>
                            <p>Your insights help us build the perfect AI teaching assistant.</p>
                        </div>
                        {/* Progress bar and indicator logic adjusted to show 10 steps max to user */}
                        {step < 11 && (
                            <>
                                <div className="progress-container">
                                    <div className="progress-bar" style={{ width: `${(step / 10) * 100}%` }}></div>
                                </div>
                                <div className="step-indicator">Step {step} of 10: {steps[step - 1].title}</div>
                            </>
                        )}
                    </div>

                    <div className="feedback-body">
                        {step === 1 && (
                            <>
                                {renderField("Your Designation", "designation", "select", ["Assistant Professor", "Associate Professor", "Professor", "PhD Scholar / TA"])}
                                {renderField("Department / Discipline", "department", "text")}
                                {renderField("Years of Experience", "teaching_experience", "select", ["0-2", "3-5", "6-10", "10+"])}
                                <SectionRating label="Rate your basic experience" name="rating_context" />
                            </>
                        )}

                        {step === 2 && (
                            <>
                                {renderField("How many times did you use TeachGenie?", "usage_frequency", "select", ["1-2 times", "3-5 times", "6-10 times", "10+ times"])}
                                <div className="feedback-field">
                                    <label>Primary Purpose (Select all that apply) <span style={{ color: '#ef4444' }}>*</span></label>
                                    <div className="checkbox-group">
                                        {["Lecture preparation", "PPT creation", "Content enrichment", "Quiz creation", "Exploring new topics"].map(opt => (
                                            <label key={opt} className="checkbox-label">
                                                <input
                                                    type="checkbox"
                                                    checked={formData.primary_purpose.includes(opt)}
                                                    onChange={() => handleMultiSelect('primary_purpose', opt)}
                                                />
                                                {opt}
                                            </label>
                                        ))}
                                    </div>
                                </div>
                                <SectionRating label="Rate usage experience" name="rating_usage" />
                            </>
                        )}

                        {step === 3 && (
                            <>
                                {renderField("Time saved per topic?", "time_saved", "select", ["< 30 mins", "30-60 mins", "1-2 hours", "> 2 hours"])}
                                {renderField("Speed as compared to conventional methods", "speed_vs_manual", "select", ["Much faster", "Slightly faster", "No difference", "Slower"])}
                                {renderField("Value of Single-Click Generation?", "value_single_click", "radio", ["Extremely valuable", "Very valuable", "Moderately valuable", "Not valuable"])}
                                <SectionRating label="Rate productivity impact" name="rating_time" />
                            </>
                        )}

                        {step === 4 && (
                            <>
                                {renderField("Ease of Zero-Prompt usage?", "zero_prompt_ease", "radio", ["Very easy", "Easy", "Neutral", "Difficult"])}
                                {renderField("Complexity vs other AI tools?", "complexity_vs_others", "radio", ["Much simpler", "Slightly simpler", "About the same", "More complex"])}
                                <SectionRating label="Rate Zero-Prompt experience" name="rating_zero_prompt" />
                            </>
                        )}

                        {step === 5 && (
                            <>
                                {renderField("Content Accuracy?", "content_accuracy", "radio", ["Highly accurate", "Mostly accurate", "Partially accurate", "Needs improvement"])}
                                {renderField("Classroom Suitability?", "classroom_suitability", "radio", ["Fully ready", "Minor edits", "Major edits", "Not suitable"])}
                                {renderField("Quiz scenario relevance", "quiz_scenario_relevance", "radio", ["Very relevant", "Relevant", "Somewhat relevant", "Not relevant"])}
                                <SectionRating label="Rate content quality" name="rating_content" />
                            </>
                        )}

                        {step === 6 && (
                            <>
                                {renderField("Interface Intuition?", "interface_intuitive", "radio", ["Very intuitive", "Intuitive", "Neutral", "Confusing"])}
                                {renderField("Did you face technical issues?", "technical_issues", "radio", ["No", "Yes"])}
                                {formData.technical_issues === 'Yes' && renderField("Please specify issue", "technical_issues_details", "text")}
                                <SectionRating label="Rate interface experience" name="rating_interface" />
                            </>
                        )}

                        {step === 7 && (
                            <>
                                {renderField("How is it better than a General purpose LLM?", "comparison_vs_llm", "textarea")}
                                {renderField("Rate the depth of content generated compared to generic LLMs?", "comparison_objective", "radio", ["TeachGenie is MUCH deeper", "TeachGenie is deeper", "Similar depth", "Generic LLM is deeper"])}
                                {/* No section rating requested here explicitly by user query changes, but let's keep it consistent or follow previous patter? 
                               User only said "Section rating for each section" before. But didn't ask to ADD one here specifically in latest prompt. 
                               I will skip section rating here to keep step Count 11 not 12, or just follow fields. 
                           */}
                            </>
                        )}

                        {step === 8 && (
                            <>
                                {renderField("Would you use regularly?", "will_use_regularly", "radio", ["Definity Yes", "Probably", "Not sure", "No"])}
                                {renderField("Would recommend to faculty?", "will_recommend", "radio", ["Yes", "Maybe", "No"])}
                                {renderField("Support institutional adoption?", "support_adoption", "radio", ["Yes", "Maybe", "No"])}
                                <SectionRating label="Rate potential for adoption" name="rating_adoption" />
                            </>
                        )}

                        {step === 9 && (
                            <>
                                {renderField("What did you like MOST?", "liked_most", "textarea")}
                                {renderField("What to improve (LEAST liked)?", "liked_least", "textarea")}
                                {renderField("Feature suggestions?", "feature_requests", "textarea")}
                                <label className="checkbox-label" style={{ marginTop: 15 }}>
                                    <input
                                        type="checkbox"
                                        name="testimonial_consent"
                                        checked={formData.testimonial_consent}
                                        onChange={handleChange}
                                    />
                                    Can we use this as a testimonial?
                                </label>
                            </>
                        )}

                        {step === 10 && (
                            <>
                                {renderField("Describe TeachGenie in one sentence", "one_sentence_verdict", "textarea")}
                                {renderField("Avg Generation Time?", "avg_generation_time", "radio", ["< 30s", "30-60s", "1-2 min", "> 2 min"])}
                                {renderField("Workflow Satisfaction", "workflow_satisfaction", "radio", ["Extremely satisfied", "Satisfied", "Neutral", "Dissatisfied"])}
                                <SectionRating label="Rate workflow satisfaction" name="rating_workflow" />
                            </>
                        )}

                        {step === 11 && (
                            <div style={{ textAlign: 'center', padding: '40px 0' }}>
                                <h3 style={{ fontSize: '24px', color: '#fff', marginBottom: '20px' }}>Ready to Submit?</h3>
                                <p style={{ color: '#9ca3af', marginBottom: '30px' }}>Please provide your final overall rating for TeachGenie.</p>
                                <SectionRating label="Overall Rating" name="overall_rating" />
                            </div>
                        )}

                    </div>

                    <div className="feedback-footer">
                        {step > 1 && <button className="btn-secondary" onClick={prevStep}><ChevronLeft size={16} /> Back</button>}
                        {step < steps.length ? (
                            <button
                                className="btn-primary"
                                onClick={nextStep}
                                disabled={!valid}
                                style={{ opacity: valid ? 1 : 0.5, cursor: valid ? 'pointer' : 'not-allowed' }}
                            >
                                Next <ChevronRight size={16} />
                            </button>
                        ) : (
                            <button
                                className="btn-success"
                                onClick={handleSubmit}
                                disabled={loading || !valid}
                                style={{ opacity: (loading || !valid) ? 0.7 : 1, cursor: (loading || !valid) ? 'not-allowed' : 'pointer' }}
                            >
                                {loading ? 'Submitting...' : 'Submit & Unlock Trials'} <CheckCircle size={16} />
                            </button>
                        )}
                    </div>

                    {toast.show && (
                        <Toast
                            type={toast.type}
                            message={toast.message}
                            onClose={() => setToast({ ...toast, show: false })}
                        />
                    )}
                </div>
            </div>
        </div>
    );
};

export default FeedbackModal;
