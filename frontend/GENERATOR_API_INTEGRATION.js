/**
 * Updated Generator Component - Real API Integration
 * 
 * This file contains the production-ready handleGenerate function
 * and download handlers to replace the mock logic in Generator.js
 * 
 * Instructions:
 * 1. Replace lines 111-244 in Generator.js with this content
 * 2. Add download handlers after the handleGenerate function
 */

// REPLACEMENT FOR LINES 111-244 in Generator.js

const handleGenerate = async (e) => {
    e.preventDefault();
    if (!topic.trim()) {
        setError('Please enter a topic');
        return;
    }

    // Check quota (use user.monthly_quota if available)
    const quota = user?.monthly_quota || 10;
    const used = user?.lessons_this_month || 0;
    if (used >= quota) {
        setError('Monthly quota exceeded. Please upgrade your plan.');
        return;
    }

    setLoading(true);
    setError(null);
    setProgress(0);
    setProgressMessage('🧞 Connecting to Teaching Genie...');

    try {
        // Start progress animation (keep for UX)
        simulateGenerationPipeline();

        // Real API call to backend
        const lessonData = await lessonService.generateLesson({
            topic: topic.trim(),
            level,
            duration: parseInt(duration),
            includeQuiz,
            quizDuration: includeQuiz ? parseInt(quizDuration) : undefined,
            quizMarks: includeQuiz ? parseInt(quizMarks) : undefined,
        });

        // Map backend response to UI state
        setLessonState({
            lesson_plan: {
                title: lessonData.title || topic,
                level: lessonData.level || level,
                duration: `${lessonData.duration_minutes || duration} minutes`,
            },
            objectives: lessonData.learning_objectives || [],
            sections: lessonData.sections || [],
            key_takeaways: lessonData.key_takeaways || [],
            resources: lessonData.resources || [],
            quiz: lessonData.quiz || null,
            ppt_path: lessonData.ppt_url || '',
            pdf_path: lessonData.pdf_url || '',
        });

        setProgress(100);
        setProgressMessage('✨ Magic complete! Your lesson is ready...');
        setGenerated(true);
        setDisclaimerAcked(false);

        // Refresh user data to get updated quota
        if (refreshUser) {
            try {
                await refreshUser();
            } catch (err) {
                console.warn('Failed to refresh user:', err);
            }
        }

        // Update local quota display
        setFreeGenerations(quota - (used + 1));
        setTotalUsed(used + 1);

    } catch (err) {
        console.error('Lesson generation error:', err);
        const errorMsg = err.message || 'Failed to generate lesson. Please try again.';
        setError(errorMsg);
        setProgress(0);
        setProgressMessage('');

        // Show user-friendly error
        alert(`Error: ${errorMsg}`);
    } finally {
        setLoading(false);
    }
};

// ADD THESE DOWNLOAD HANDLERS AFTER handleGenerate

const handleDownloadPPT = async () => {
    if (!lessonState.ppt_path) {
        alert('PPT file is not available');
        return;
    }

    try {
        await lessonService.downloadPPT(lessonState, topic);
    } catch (err) {
        console.error('PPT download error:', err);
        alert('Failed to download PPT: ' + err.message);
    }
};

const handleDownloadPDF = async () => {
    if (!lessonState.pdf_path) {
        alert('PDF file is not available');
        return;
    }

    try {
        await lessonService.downloadPDF(lessonState, topic);
    } catch (err) {
        console.error('PDF download error:', err);
        alert('Failed to download PDF: ' + err.message);
    }
};

// UPDATE THE DOWNLOAD BUTTONS (around line 668-675) TO USE THESE HANDLERS:
// Replace:
//   <button className={`btn btn-accent ${!disclaimerAcked ? 'disabled' : ''}`} disabled={!disclaimerAcked}>
// With:
//   <button onClick={handleDownloadPPT} className={`btn btn-accent ${!disclaimerAcked ? 'disabled' : ''}`} disabled={!disclaimerAcked}>
// And similarly for PDF button with handleDownloadPDF
