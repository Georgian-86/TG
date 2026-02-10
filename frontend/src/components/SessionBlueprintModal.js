import React from 'react';
import { X, ArrowLeft, GraduationCap, Clock, FileText, Target, Lightbulb, Zap, TrendingUp } from 'lucide-react';
import CognitiveLoadGauge from './CognitiveLoadGauge';
import '../styles/blueprint-modal.css';

/**
 * Session Blueprint Confirmation Modal
 * Shows lesson plan preview before generation with edit/confirm options
 */
const SessionBlueprintModal = ({
    isOpen,
    onClose,
    onGenerate,
    topic,
    level,
    duration,
    contentType,
    includeQuiz,
    quizDuration,
    quizMarks,
    profile // { objectives, sections, takeaways, quiz }
}) => {
    if (!isOpen) return null;

    // Format content type label
    const formatContentType = (type) => {
        const labels = {
            'slides': 'Slides Only',
            'notes': 'Notes Only',
            'both': 'Slides + Notes'
        };
        return labels[type] || 'Slides + Notes';
    };

    // Calculate estimated time (rough estimate based on complexity)
    const getEstimatedTime = () => {
        const baseTime = 30;
        const sectionMultiplier = profile.sections.length * 5;
        const quizTime = includeQuiz ? 10 : 0;
        return baseTime + sectionMultiplier + quizTime;
    };

    return (
        <>
            {/* Backdrop */}
            <div className="blueprint-modal-backdrop" onClick={onClose} />

            {/* Modal */}
            <div className="blueprint-modal">
                {/* Close button */}
                <button className="modal-close-btn" onClick={onClose} aria-label="Close">
                    <X size={24} />
                </button>

                {/* Header */}
                <div className="modal-header">
                    <h2 className="modal-title">Session Blueprint Preview</h2>
                    <p className="modal-subtitle">Review your lesson plan before generation</p>
                </div>

                {/* Content */}
                <div className="modal-content">
                    {/* Topic Card */}
                    <div className="blueprint-card topic-card">
                        <div className="card-icon">
                            <FileText size={20} />
                        </div>
                        <div className="card-content">
                            <span className="card-label">Lesson Topic</span>
                            <h3 className="topic-text">{topic}</h3>
                        </div>
                    </div>

                    {/* Parameters Grid */}
                    <div className="blueprint-grid">
                        {/* Level */}
                        <div className="blueprint-param">
                            <div className="param-icon">
                                <GraduationCap size={18} />
                            </div>
                            <div className="param-content">
                                <span className="param-label">Education Level</span>
                                <span className="param-value">{level.charAt(0).toUpperCase() + level.slice(1)}</span>
                            </div>
                        </div>

                        {/* Duration */}
                        <div className="blueprint-param">
                            <div className="param-icon">
                                <Clock size={18} />
                            </div>
                            <div className="param-content">
                                <span className="param-label">Session Duration</span>
                                <span className="param-value">{duration} minutes</span>
                            </div>
                        </div>

                        {/* Content Type */}
                        <div className="blueprint-param">
                            <div className="param-icon">
                                <FileText size={18} />
                            </div>
                            <div className="param-content">
                                <span className="param-label">Content Format</span>
                                <span className="param-value">{formatContentType(contentType)}</span>
                            </div>
                        </div>

                        {/* Quiz */}
                        <div className="blueprint-param">
                            <div className="param-icon">
                                <Zap size={18} />
                            </div>
                            <div className="param-content">
                                <span className="param-label">Assessment Quiz</span>
                                <span className="param-value">
                                    {includeQuiz ? `${quizDuration} min • ${quizMarks} marks` : 'Disabled'}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Cognitive Load Gauge */}
                    <div className="blueprint-gauge-section">
                        <CognitiveLoadGauge level={level} duration={duration} />
                    </div>

                    {/* Learning Structure */}
                    <div className="blueprint-card structure-card">
                        <div className="structure-header">
                            <TrendingUp size={20} />
                            <span>Learning Structure</span>
                        </div>
                        <div className="structure-stats">
                            <div className="stat-item">
                                <Target size={16} />
                                <span className="stat-label">Objectives</span>
                                <span className="stat-value">{profile.objectives}</span>
                            </div>
                            <div className="stat-divider" />
                            <div className="stat-item">
                                <Lightbulb size={16} />
                                <span className="stat-label">Takeaways</span>
                                <span className="stat-value">{profile.takeaways}</span>
                            </div>
                            <div className="stat-divider" />
                            <div className="stat-item">
                                <Zap size={16} />
                                <span className="stat-label">Quiz Questions</span>
                                <span className="stat-value">{includeQuiz ? profile.quiz * 3 : 0}</span>
                            </div>
                        </div>
                    </div>

                    {/* Learning Path */}
                    <div className="blueprint-card path-card">
                        <div className="path-header">
                            <span className="path-label">📚 Learning Path</span>
                        </div>
                        <div className="path-flow">
                            {profile.sections.map((section, index) => (
                                <div key={section} className="path-step">
                                    <span className="step-number">{index + 1}</span>
                                    <span className="step-name">{section}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Estimated Time */}
                    <div className="blueprint-estimate">
                        <Clock size={16} />
                        <span>Estimated Generation Time: <strong>~{getEstimatedTime()} seconds</strong></span>
                    </div>
                </div>

                {/* Footer Actions */}
                <div className="modal-footer">
                    <button className="btn-edit" onClick={onClose}>
                        <ArrowLeft size={20} />
                        Edit Parameters
                    </button>
                    <button className="btn-confirm" onClick={onGenerate}>
                        <Zap size={20} />
                        Generate Lesson
                    </button>
                </div>
            </div>
        </>
    );
};

export default SessionBlueprintModal;
