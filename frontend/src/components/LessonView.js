import React, { useState } from 'react';
import { API_BASE_URL } from '../lib/api/client';
import {
    AlertCircle,
    ArrowLeft,
    ChevronDown,
    Globe,
    FileDown,
    Clock,
    GraduationCap,
    Timer,
    Trophy,
    ExternalLink,
    Target,
    BookOpen,
    Lightbulb,
    FileText,
    Download,
    HelpCircle,
    Layers,
    Zap
} from 'lucide-react';
import '../styles/lesson-view.css';

// Format subsection key to readable title
const formatTitle = (key) => {
    return key
        .replace(/_/g, ' ')
        .replace(/&/g, ' & ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
};

// Get icon for subsection
const getSubsectionIcon = (key) => {
    const k = key.toLowerCase();
    if (k.includes('context') || k.includes('background') || k.includes('intro')) return <BookOpen size={16} />;
    if (k.includes('analysis') || k.includes('main')) return <Layers size={16} />;
    if (k.includes('example') || k.includes('application')) return <Lightbulb size={16} />;
    if (k.includes('theme') || k.includes('symbol')) return <Target size={16} />;
    return <FileText size={16} />;
};

// Content Section with expandable subsections
const ContentSectionCard = ({ section, index }) => {
    const [isExpanded, setIsExpanded] = useState(index === 0);
    const [activeTab, setActiveTab] = useState(0);

    const content = section.content;
    const hasSubsections = typeof content === 'object' && content !== null && !Array.isArray(content);
    const subsections = hasSubsections ? Object.entries(content) : [];

    return (
        <div className={`content-section-card ${isExpanded ? 'expanded' : ''}`}>
            <button
                className="content-section-header"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div className="content-section-left">
                    <div className="section-number">{index + 1}</div>
                    <span className="section-title">{section.title || `Section ${index + 1}`}</span>
                </div>
                <ChevronDown className="section-chevron" />
            </button>

            <div className="content-section-body">
                {hasSubsections ? (
                    <>
                        <div className="subsection-tabs">
                            {subsections.map(([key], idx) => (
                                <button
                                    key={key}
                                    className={`subsection-tab ${activeTab === idx ? 'active' : ''}`}
                                    onClick={() => setActiveTab(idx)}
                                >
                                    {getSubsectionIcon(key)}
                                    <span>{formatTitle(key)}</span>
                                </button>
                            ))}
                        </div>
                        <div className="subsection-content">
                            <div className="subsection-text">
                                {renderContent(subsections[activeTab]?.[1])}
                            </div>
                        </div>
                    </>
                ) : (
                    <div className="subsection-content">
                        <div className="subsection-text">
                            {renderContent(content)}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

// Render content (handles strings, arrays, objects)
const renderContent = (content) => {
    if (!content) return null;

    if (typeof content === 'string') {
        // Try to parse if it looks like JSON
        if (content.startsWith('{') || content.startsWith('[')) {
            try {
                return renderContent(JSON.parse(content));
            } catch { }
        }
        return content.split('\n').map((para, i) =>
            para.trim() ? <p key={i}>{para}</p> : null
        );
    }

    if (Array.isArray(content)) {
        return (
            <ul style={{ paddingLeft: '20px', margin: '12px 0' }}>
                {content.map((item, i) => (
                    <li key={i} style={{ marginBottom: '8px' }}>{renderContent(item)}</li>
                ))}
            </ul>
        );
    }

    if (typeof content === 'object') {
        return Object.entries(content).map(([key, value]) => (
            <div key={key} style={{ marginBottom: '16px' }}>
                <strong style={{ color: '#4f46e5', display: 'block', marginBottom: '6px' }}>
                    {formatTitle(key)}
                </strong>
                <div style={{ paddingLeft: '12px' }}>{renderContent(value)}</div>
            </div>
        ));
    }

    return String(content);
};

// Get domain from URL
const getDomain = (url) => {
    try {
        return new URL(url).hostname.replace('www.', '');
    } catch {
        return url;
    }
};

// Parse objective text to extract Bloom's taxonomy level
const parseObjectiveWithBloom = (obj) => {
    const text = typeof obj === 'string' ? obj : obj.text || JSON.stringify(obj);

    // Match [BloomLevel] at the start
    const match = text.match(/^\[(\w+)\]\s*(.+)$/);

    if (match) {
        return {
            bloomLevel: match[1],
            objectiveText: match[2]
        };
    }

    // Fallback: detect Bloom level from first verb
    const bloomVerbs = {
        'Remember': ['remember', 'list', 'define', 'recall', 'state', 'identify', 'name'],
        'Understand': ['understand', 'explain', 'describe', 'summarize', 'discuss', 'interpret', 'clarify'],
        'Apply': ['apply', 'use', 'implement', 'demonstrate', 'solve', 'execute', 'employ'],
        'Analyze': ['analyze', 'compare', 'contrast', 'investigate', 'examine', 'categorize', 'differentiate'],
        'Evaluate': ['evaluate', 'assess', 'justify', 'critique', 'judge', 'appraise', 'argue'],
        'Create': ['create', 'design', 'develop', 'formulate', 'construct', 'compose', 'devise']
    };

    const lowerText = text.toLowerCase();
    for (const [level, verbs] of Object.entries(bloomVerbs)) {
        if (verbs.some(verb => lowerText.startsWith(verb))) {
            return { bloomLevel: level, objectiveText: text };
        }
    }

    return { bloomLevel: null, objectiveText: text };
};

// Bloom's Taxonomy color scheme
const getBloomColor = (level) => {
    const colors = {
        'Remember': { bg: '#dbeafe', text: '#1e40af', border: '#93c5fd' },
        'Understand': { bg: '#e0e7ff', text: '#4338ca', border: '#a5b4fc' },
        'Apply': { bg: '#ddd6fe', text: '#6d28d9', border: '#c4b5fd' },
        'Analyze': { bg: '#fce7f3', text: '#be185d', border: '#f9a8d4' },
        'Evaluate': { bg: '#fed7aa', text: '#c2410c', border: '#fdba74' },
        'Create': { bg: '#fecaca', text: '#b91c1c', border: '#fca5a5' }
    };
    return colors[level] || { bg: '#f3f4f6', text: '#4b5563', border: '#d1d5db' };
};

const ObjectivesPanel = ({ objectives }) => (
    <div className="objectives-list">
        {objectives.map((obj, idx) => {
            const { bloomLevel, objectiveText } = parseObjectiveWithBloom(obj);
            const colors = getBloomColor(bloomLevel);

            return (
                <div key={idx} className="objective-item">
                    <div className="objective-number">{idx + 1}</div>
                    <span className="objective-text">{objectiveText}</span>
                    {bloomLevel && (
                        <div
                            className="bloom-badge"
                            style={{
                                backgroundColor: colors.bg,
                                color: colors.text,
                                borderColor: colors.border
                            }}
                        >
                            {bloomLevel}
                        </div>
                    )}
                </div>
            );
        })}
    </div>
);

const ContentPanel = ({ sections }) => (
    <div className="content-sections-list">
        {sections.map((section, idx) => (
            <ContentSectionCard key={idx} section={section} index={idx} />
        ))}
    </div>
);

const TakeawaysPanel = ({ takeaways }) => (
    <div className="takeaways-list">
        {takeaways.map((item, idx) => {
            const text = typeof item === 'string' ? item : item.text || item.description || JSON.stringify(item);
            return (
                <div key={idx} className="takeaway-card">
                    <div className="takeaway-icon">
                        <Lightbulb size={16} />
                    </div>
                    <span className="takeaway-text">{text}</span>
                </div>
            );
        })}
    </div>
);

const ResourcesPanel = ({ resources }) => (
    <div className="resources-grid">
        {resources.map((res, idx) => (
            <a
                key={idx}
                href={res.url}
                target="_blank"
                rel="noopener noreferrer"
                className="resource-card"
            >
                <div className="resource-icon">
                    <Globe size={18} />
                </div>
                <div className="resource-info">
                    <div className="resource-title">{res.title}</div>
                    <div className="resource-domain">{getDomain(res.url)}</div>
                </div>
                <ExternalLink className="resource-external" size={16} />
            </a>
        ))}
    </div>
);

const QuizPanel = ({ quiz }) => {
    const [selectedAnswers, setSelectedAnswers] = React.useState({});
    const [submitted, setSubmitted] = React.useState(false);
    const [score, setScore] = React.useState(0);

    const handleAnswerSelect = (questionIdx, optionKey) => {
        if (!submitted) {
            setSelectedAnswers({
                ...selectedAnswers,
                [questionIdx]: optionKey
            });
        }
    };

    const handleSubmit = () => {
        let correctCount = 0;
        quiz.questions?.forEach((q, idx) => {
            if (selectedAnswers[idx] === q.correct_option) {
                correctCount++;
            }
        });
        const totalMarks = quiz.marks || quiz.questions?.length * 10 || 100;
        const earnedScore = Math.round((correctCount / quiz.questions.length) * totalMarks);
        setScore(earnedScore);
        setSubmitted(true);
    };

    const handleReset = () => {
        setSelectedAnswers({});
        setSubmitted(false);
        setScore(0);
    };

    const allAnswered = quiz.questions?.every((_, idx) => selectedAnswers[idx]);

    return (
        <>
            <div className="quiz-header">
                <div className="quiz-stat">
                    <Timer size={18} />
                    <span>Duration: {quiz.duration || 10} minutes</span>
                </div>
                <div className="quiz-stat">
                    <Trophy size={18} />
                    <span>Total Marks: {quiz.marks || quiz.questions?.length * 10 || 0}</span>
                </div>
                {submitted && (
                    <div className="quiz-stat" style={{ marginLeft: 'auto', fontSize: '18px', color: score >= 70 ? '#10b981' : '#f59e0b' }}>
                        <Trophy size={20} />
                        <span>Your Score: {score}/{quiz.marks || quiz.questions?.length * 10 || 0}</span>
                    </div>
                )}
            </div>

            {!submitted && (
                <div className="quiz-instructions">
                    <Lightbulb size={20} />
                    <span>Select your answers and click "Submit Quiz" to see your results</span>
                </div>
            )}

            <div className="quiz-list">
                {quiz.questions?.map((q, idx) => {
                    const userAnswer = selectedAnswers[idx];
                    const isCorrect = userAnswer === q.correct_option;
                    const showResult = submitted;

                    return (
                        <div key={idx} className="quiz-card">
                            <div className="quiz-card-header">
                                <div className="quiz-number">{idx + 1}</div>
                                <span className="quiz-label">Question</span>
                                {q.rbt_level && (
                                    <div
                                        className="bloom-badge"
                                        style={{
                                            backgroundColor: getBloomColor(q.rbt_level).bg,
                                            color: getBloomColor(q.rbt_level).text,
                                            borderColor: getBloomColor(q.rbt_level).border,
                                            marginLeft: '12px'
                                        }}
                                    >
                                        {q.rbt_level}
                                    </div>
                                )}
                                {showResult && (
                                    <span className={`quiz-result-badge ${isCorrect ? 'correct' : 'incorrect'}`}>
                                        {isCorrect ? '✓ Correct' : '✗ Incorrect'}
                                    </span>
                                )}
                            </div>
                            <div className="quiz-card-body">
                                {q.scenario && (
                                    <div className="quiz-scenario">{q.scenario}</div>
                                )}
                                <div className="quiz-question-text">{q.question}</div>
                                <div className="quiz-options">
                                    {q.options && Object.entries(q.options).map(([key, value]) => {
                                        const isSelected = userAnswer === key;
                                        const isCorrectAnswer = key === q.correct_option;
                                        const showCorrect = showResult && isCorrectAnswer;
                                        const showWrong = showResult && isSelected && !isCorrect;

                                        return (
                                            <div
                                                key={key}
                                                className={`quiz-option ${isSelected && !submitted ? 'selected' : ''} ${showCorrect ? 'correct' : ''} ${showWrong ? 'wrong' : ''}`}
                                                onClick={() => handleAnswerSelect(idx, key)}
                                                style={{ cursor: submitted ? 'default' : 'pointer' }}
                                            >
                                                <span className="quiz-option-key">{key}</span>
                                                <span>{value}</span>
                                            </div>
                                        );
                                    })}
                                </div>
                                {showResult && q.explanation && (
                                    <div className="quiz-explanation">
                                        <Lightbulb size={18} />
                                        <span>{q.explanation}</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>

            <div className="quiz-actions">
                {!submitted ? (
                    <button
                        className="btn-submit-quiz"
                        onClick={handleSubmit}
                        disabled={!allAnswered}
                    >
                        <Trophy size={20} />
                        Submit Quiz
                    </button>
                ) : (
                    <button
                        className="btn-reset-quiz"
                        onClick={handleReset}
                    >
                        Reset Quiz
                    </button>
                )}
            </div>
        </>
    );
};

const DownloadsPanel = ({ pptUrl, pdfUrl, disclaimerAcked, onDisclaimerChange, onDownloadPPT, onDownloadPDF }) => (
    <>
        {/* Disclaimer - Only in Downloads tab */}
        <div className="disclaimer-section" style={{ marginTop: 0, marginBottom: 32 }}>
            <div className="disclaimer-icon">
                <AlertCircle size={20} />
            </div>
            <div className="disclaimer-content">
                <p className="disclaimer-text">
                    <strong>Important:</strong> These AI-generated materials are supplemental only.
                    Faculty and educators should apply their expertise before using in classroom settings.
                </p>
                <label className="disclaimer-checkbox">
                    <input
                        type="checkbox"
                        checked={disclaimerAcked}
                        onChange={(e) => onDisclaimerChange(e.target.checked)}
                    />
                    <span>I acknowledge this disclaimer</span>
                </label>
            </div>
        </div>

        <div className="downloads-grid">
            <div
                className={`download-card ${!disclaimerAcked ? 'disabled' : ''}`}
                onClick={() => disclaimerAcked && onDownloadPPT()}
            >
                <FileDown size={32} />
                <span className="download-label">PowerPoint</span>
                <span className="download-format">PPT Presentation</span>
            </div>
            <div
                className={`download-card ${!disclaimerAcked ? 'disabled' : ''}`}
                onClick={() => disclaimerAcked && onDownloadPDF()}
            >
                <Download size={32} />
                <span className="download-label">PDF Document</span>
                <span className="download-format">Study Notes</span>
            </div>
        </div>
    </>
);

// Main Component
const LessonView = ({ lesson, topic, onBack }) => {
    const [activeSection, setActiveSection] = useState('objectives');
    const [disclaimerAcked, setDisclaimerAcked] = useState(false);

    // Normalize lesson data
    const data = {
        title: lesson.title || lesson.topic || lesson.lesson_plan?.title || topic || 'Untitled Lesson',
        level: lesson.level || lesson.lesson_plan?.level || 'Standard',
        duration: lesson.duration || lesson.lesson_plan?.duration || '30 minutes',
        objectives: lesson.learning_objectives || lesson.objectives || [],
        sections: lesson.lesson_data ? JSON.parse(lesson.lesson_data).lesson_plan : (lesson.sections || lesson.lesson_plan || []),
        takeaways: lesson.key_takeaways || [],
        resources: lesson.resources || [],
        quiz: lesson.quiz,
        pptUrl: lesson.ppt_url || lesson.ppt_path,
        pdfUrl: lesson.pdf_url || lesson.pdf_path
    };

    // Handle nested sections
    if (!Array.isArray(data.sections) && data.sections?.sections) {
        data.sections = data.sections.sections;
    }

    const handleDownload = (type) => {
        const url = type === 'ppt' ? data.pptUrl : data.pdfUrl;
        if (!url) {
            alert(`${type.toUpperCase()} file is not available`);
            return;
        }
        const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`;
        window.open(fullUrl, '_blank');
    };

    // Navigation items
    const navItems = [
        { id: 'objectives', label: 'Objectives', icon: Target, count: data.objectives?.length },
        { id: 'content', label: 'Content', icon: BookOpen, count: data.sections?.length },
        { id: 'takeaways', label: 'Takeaways', icon: Lightbulb, count: data.takeaways?.length },
        { id: 'resources', label: 'Resources', icon: Globe, count: data.resources?.length },
        ...(data.quiz?.questions?.length ? [{ id: 'quiz', label: 'Quiz', icon: HelpCircle, count: data.quiz.questions.length }] : []),
        { id: 'downloads', label: 'Downloads', icon: Download }
    ];

    // Panel title and subtitle
    const panelInfo = {
        objectives: { title: 'Learning Objectives', subtitle: `${data.objectives?.length || 0} key outcomes to achieve` },
        content: { title: 'Lesson Content', subtitle: `${data.sections?.length || 0} sections to explore` },
        takeaways: { title: 'Key Takeaways', subtitle: 'Important points to remember' },
        resources: { title: 'Learning Resources', subtitle: 'Curated materials for further study' },
        quiz: { title: 'Interactive Quiz', subtitle: 'Test your understanding' },
        downloads: { title: 'Download Materials', subtitle: 'Get your lesson files' }
    };

    const getPanelIcon = () => {
        const item = navItems.find(n => n.id === activeSection);
        return item ? <item.icon size={22} /> : <BookOpen size={22} />;
    };

    return (
        <div className="lesson-view-container">
            {/* Back Button */}
            {onBack && (
                <button onClick={onBack} className="lesson-back-btn">
                    <ArrowLeft size={18} />
                    Back to Dashboard
                </button>
            )}

            {/* Header */}
            <div className="lesson-header">
                <span className="lesson-badge">
                    <GraduationCap size={14} />
                    {data.level}
                </span>
                <h1 className="lesson-title">{data.title}</h1>
                <div className="lesson-meta">
                    <div className="meta-item">
                        <Clock size={18} />
                        <span className="meta-value">{data.duration}</span>
                    </div>
                    <div className="meta-item">
                        <Target size={18} />
                        <span className="meta-value">{data.objectives?.length || 0} Objectives</span>
                    </div>
                    <div className="meta-item">
                        <BookOpen size={18} />
                        <span className="meta-value">{data.sections?.length || 0} Sections</span>
                    </div>
                </div>
            </div>

            {/* Generation Time Banner - Only for newly generated lessons */}
            {(data.generation_time || data.processing_time_seconds) && (
                <div className="generation-time-banner">
                    <div className="banner-icon">
                        <Zap size={24} />
                    </div>
                    <div className="banner-content">
                        <div className="banner-title">🎓 AI-Powered Lesson Created in {(data.generation_time || data.processing_time_seconds).toFixed(2)}s</div>
                        <div className="banner-time">
                            What would take hours of manual work, our AI delivered in seconds — complete with Bloom's taxonomy, interactive quizzes, and downloadable materials!
                        </div>
                    </div>
                </div>
            )}

            {/* Main Content Grid */}
            <div className="lesson-content-grid">
                {/* Sidebar */}
                <div className="lesson-sidebar">
                    <nav className="sidebar-nav">
                        {navItems.map(item => (
                            <button
                                key={item.id}
                                className={`sidebar-item ${activeSection === item.id ? 'active' : ''}`}
                                onClick={() => setActiveSection(item.id)}
                            >
                                <item.icon size={18} />
                                <span>{item.label}</span>
                                {item.count !== undefined && (
                                    <span className="sidebar-count">{item.count}</span>
                                )}
                            </button>
                        ))}
                    </nav>
                </div>

                {/* Main Panel */}
                <div className="lesson-main-panel">
                    <div className="panel-header">
                        <div className="panel-icon">
                            {getPanelIcon()}
                        </div>
                        <div>
                            <h2 className="panel-title">{panelInfo[activeSection]?.title}</h2>
                            <p className="panel-subtitle">{panelInfo[activeSection]?.subtitle}</p>
                        </div>
                    </div>

                    <div className="panel-content" key={activeSection}>
                        {activeSection === 'objectives' && data.objectives?.length > 0 && (
                            <ObjectivesPanel objectives={data.objectives} />
                        )}
                        {activeSection === 'content' && data.sections?.length > 0 && (
                            <ContentPanel sections={data.sections} />
                        )}
                        {activeSection === 'takeaways' && data.takeaways?.length > 0 && (
                            <TakeawaysPanel takeaways={data.takeaways} />
                        )}
                        {activeSection === 'resources' && data.resources?.length > 0 && (
                            <ResourcesPanel resources={data.resources} />
                        )}
                        {activeSection === 'quiz' && data.quiz && (
                            <QuizPanel quiz={data.quiz} />
                        )}
                        {activeSection === 'downloads' && (
                            <DownloadsPanel
                                pptUrl={data.pptUrl}
                                pdfUrl={data.pdfUrl}
                                disclaimerAcked={disclaimerAcked}
                                onDisclaimerChange={setDisclaimerAcked}
                                onDownloadPPT={() => handleDownload('ppt')}
                                onDownloadPDF={() => handleDownload('pdf')}
                            />
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LessonView;
