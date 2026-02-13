import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, Sparkles, BookOpen, Clock, Download, Edit, Share2, CheckCircle, Lightbulb, TrendingUp, Award, Zap } from 'lucide-react';
import '../styles/learn-more.css';

export default function LearnMore() {
  const navigate = useNavigate();

  return (
    <div className="learn-more-page">
      <section className="learn-more-container">
        <button className="back-button" onClick={() => navigate(-1)}>
          <ChevronLeft size={20} />
          Back to Home
        </button>

        <div className="learn-more-header">
          <div className="header-badge">
            <Sparkles size={20} />
            <span>Complete Tutor Guide</span>
          </div>
          <h1 className="learn-more-title">
            See the Magic Behind TeachGenie
          </h1>
          <p className="learn-more-subtitle">
            Transform hours of lesson planning into minutes. Free up your time for what truly matters - inspiring and connecting with your students.
          </p>
        </div>

        <div className="learn-more-content">
          {/* Step-by-Step Process */}
          <div className="process-section">
            <h2 className="section-title">
              <BookOpen size={32} />
              The Complete Process
            </h2>
            <p className="section-intro">
              Creating professional teaching materials has never been easier. Follow these simple steps to generate comprehensive, classroom-ready content in under 60 seconds.
            </p>

            <div className="steps-container">
              <div className="process-card">
                <div className="step-number">1</div>
                <div className="step-content">
                  <h3>Sign Up & Access Dashboard</h3>
                  <p>Create your free account and get instant access to your personal dashboard. No credit card required - start with 1000 free credits (10 generations).</p>
                  <ul className="step-details">
                    <li>Quick registration with email</li>
                    <li>Immediate dashboard access</li>
                    <li>1000 credits ready to use</li>
                  </ul>
                </div>
              </div>

              <div className="process-card">
                <div className="step-number">2</div>
                <div className="step-content">
                  <h3>Enter Your Topic</h3>
                  <p>Simply type in any topic you want to teach. Be as specific or as broad as you like - our AI understands both.</p>
                  <ul className="step-details">
                    <li>Enter subject or concept (e.g., "Photosynthesis", "World War II", "Quadratic Equations")</li>
                    <li>No complex formatting needed</li>
                    <li>Works with any educational topic</li>
                  </ul>
                </div>
              </div>

              <div className="process-card">
                <div className="step-number">3</div>
                <div className="step-content">
                  <h3>Choose Material Type</h3>
                  <p>Select what type of educational material you need from our comprehensive options.</p>
                  <ul className="step-details">
                    <li><strong>Lesson Plan:</strong> Complete structured lesson with objectives and activities</li>
                    <li><strong>Presentation:</strong> Slide-by-slide content for engaging lectures</li>
                    <li><strong>Quiz:</strong> Multiple choice and short answer questions</li>
                    <li><strong>Case Study:</strong> Real-world application scenarios</li>
                    <li><strong>Study Guide:</strong> Comprehensive student reference material</li>
                  </ul>
                </div>
              </div>

              <div className="process-card">
                <div className="step-number">4</div>
                <div className="step-content">
                  <h3>Select Grade Level</h3>
                  <p>Choose the appropriate complexity and depth for your students.</p>
                  <ul className="step-details">
                    <li>School</li>
                    <li>Undergraduate</li>
                    <li>Postgraduate</li>
                    <li>Research</li>
                  </ul>
                </div>
              </div>

              <div className="process-card">
                <div className="step-number">5</div>
                <div className="step-content">
                  <h3>Watch the Magic Happen</h3>
                  <p>Our AI Genie springs to life! Watch as your personalized teaching material is generated in real-time.</p>
                  <ul className="step-details">
                    <li>Animated genie mascot shows progress</li>
                    <li>AI agents research and compile information</li>
                    <li>Takes only 30-60 seconds</li>
                  </ul>
                </div>
              </div>

              <div className="process-card">
                <div className="step-number">6</div>
                <div className="step-content">
                  <h3>Review & Download</h3>
                  <p>Your material is ready! Review the comprehensive content and download it in your preferred format.</p>
                  <ul className="step-details">
                    <li>Preview full content on screen</li>
                    <li>Download as PDF or Word document</li>
                    <li>Edit and customize as needed</li>
                    <li>Save to your history for future access</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* What You Get */}
          <div className="benefits-section">
            <h2 className="section-title">
              <Award size={32} />
              What You'll Receive
            </h2>
            <p className="section-intro">
              Every generation includes professionally structured, curriculum-aligned content designed to engage students and simplify your teaching workflow.
            </p>

            <div className="benefits-grid">
              <div className="benefit-card">
                <div className="benefit-icon">
                  <BookOpen size={40} />
                </div>
                <h3>Complete Lesson Plans</h3>
                <p>Detailed lesson structures with learning objectives, materials needed, step-by-step activities, discussion questions, and assessment methods.</p>
              </div>

              <div className="benefit-card">
                <div className="benefit-icon">
                  <Edit size={40} />
                </div>
                <h3>Engaging Presentations</h3>
                <p>Slide-by-slide presentation content with key points, visual suggestions, discussion prompts, and interactive elements for classroom delivery.</p>
              </div>

              <div className="benefit-card">
                <div className="benefit-icon">
                  <CheckCircle size={40} />
                </div>
                <h3>Assessment Materials</h3>
                <p>Ready-to-use quizzes with multiple choice, true/false, and short answer questions, complete with answer keys and grading rubrics.</p>
              </div>

              <div className="benefit-card">
                <div className="benefit-icon">
                  <Lightbulb size={40} />
                </div>
                <h3>Real-World Case Studies</h3>
                <p>Practical scenarios that connect theory to real-life applications, encouraging critical thinking and problem-solving skills.</p>
              </div>

              <div className="benefit-card">
                <div className="benefit-icon">
                  <Download size={40} />
                </div>
                <h3>Student Study Guides</h3>
                <p>Comprehensive reference materials with key concepts, definitions, examples, and practice problems for independent study.</p>
              </div>

              <div className="benefit-card">
                <div className="benefit-icon">
                  <Share2 size={40} />
                </div>
                <h3>Flexible Formats</h3>
                <p>Download in PDF or Word format for easy editing, printing, and sharing with students and colleagues.</p>
              </div>
            </div>
          </div>

          {/* Time Savings */}
          <div className="time-section">
            <h2 className="section-title">
              <Clock size={32} />
              Reclaim Your Time for What Matters
            </h2>
            <p className="section-intro">
              Stop spending endless hours on repetitive lesson planning. Use that precious time for what you became a teacher for - inspiring minds and making a difference.
            </p>

            <div className="time-comparison">
              <div className="time-card traditional">
                <h3>Traditional Method</h3>
                <div className="time-amount">10-15 hours/week</div>
                <ul className="time-breakdown">
                  <li>🔍 Research: 3-4 hours</li>
                  <li>✍️ Content creation: 4-5 hours</li>
                  <li>📝 Formatting: 2-3 hours</li>
                  <li>🎨 Design & visuals: 1-2 hours</li>
                  <li>✅ Review & edit: 1-2 hours</li>
                </ul>
                <p className="time-stress">Stressful, time-consuming, repetitive</p>
              </div>

              <div className="vs-divider">
                <Zap size={32} />
                <span>VS</span>
              </div>

              <div className="time-card genie">
                <h3>With Teach Genie</h3>
                <div className="time-amount">60 seconds</div>
                <ul className="time-breakdown">
                  <li>⚡ Enter topic: 10 seconds</li>
                  <li>⚙️ Select options: 15 seconds</li>
                  <li>🎯 AI generation: 30 seconds</li>
                  <li>📥 Download: 5 seconds</li>
                  <li>✨ Done!</li>
                </ul>
                <p className="time-benefit">Quick, easy, professional results</p>
              </div>
            </div>

            <div className="time-savings-box">
              <TrendingUp size={48} />
              <h3>What Could You Do With 10+ Extra Hours Each Week?</h3>
              <div className="activities-grid">
                <div className="activity">
                  <CheckCircle size={20} />
                  <span>One-on-one student mentoring</span>
                </div>
                <div className="activity">
                  <CheckCircle size={20} />
                  <span>Develop creative teaching methods</span>
                </div>
                <div className="activity">
                  <CheckCircle size={20} />
                  <span>Personal professional development</span>
                </div>
                <div className="activity">
                  <CheckCircle size={20} />
                  <span>Work-life balance & self-care</span>
                </div>
                <div className="activity">
                  <CheckCircle size={20} />
                  <span>Build meaningful student connections</span>
                </div>
                <div className="activity">
                  <CheckCircle size={20} />
                  <span>Pursue creative educational projects</span>
                </div>
                <div className="activity">
                  <CheckCircle size={20} />
                  <span>Collaborate with other educators</span>
                </div>
                <div className="activity">
                  <CheckCircle size={20} />
                  <span>Actually enjoy your evenings and weekends</span>
                </div>
              </div>
            </div>
          </div>

          {/* CTA */}
          <div className="final-cta">
            <Sparkles size={48} />
            <h2>Ready to Transform Your Teaching Experience?</h2>
            <p>Join thousands of educators who have already discovered the freedom of automated lesson planning.</p>
            <div className="cta-stats">
              <div className="stat-item">
                <strong>1000</strong>
                <span>Free Credits</span>
              </div>
              <div className="stat-item">
                <strong>60</strong>
                <span>Seconds Average</span>
              </div>
              <div className="stat-item">
                <strong>10+</strong>
                <span>Hours Saved Weekly</span>
              </div>
            </div>
            <button className="btn btn-accent btn-large" onClick={() => navigate('/signup')}>
              Start Free - No Credit Card Required
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
