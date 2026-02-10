/**
 * Lessons API Service
 * 
 * Handles all lesson generation and management API calls
 * Production-ready with proper error handling and file downloads
 */

import apiClient from './client';

/**
 * Generate a new lesson
 * @param {Object} params - Lesson generation parameters
 * @param {string} params.topic - Lesson topic
 * @param {string} params.level - Education level (School, Undergraduate, Postgraduate, Professional)
 * @param {number} params.duration - Lesson duration in minutes
 * @param {boolean} params.includeQuiz - Whether to include quiz
 * @param {number} params.quizDuration - Quiz duration in minutes (optional)
 * @param {number} params.quizMarks - Total quiz marks (optional)
 * @returns {Promise<Object>} Generated lesson data
 */
export const generateLesson = async (params) => {
    try {
        // Validate required parameters
        if (!params.topic || !params.topic.trim()) {
            throw new Error('Topic is required');
        }

        if (!params.level) {
            throw new Error('Level is required');
        }

        if (!params.duration || params.duration < 20 || params.duration > 120) {
            throw new Error('Duration must be between 20 and 120 minutes');
        }

        // Capitalize level to match backend validation pattern
        const capitalizedLevel = params.level.charAt(0).toUpperCase() + params.level.slice(1).toLowerCase();

        const payload = {
            topic: params.topic.trim(),
            level: capitalizedLevel,
            duration: parseInt(params.duration),
            include_quiz: params.includeQuiz || false,
        };

        // Add quiz parameters if quiz is enabled
        if (params.includeQuiz) {
            payload.quiz_duration = params.quizDuration ? parseInt(params.quizDuration) : 10;
            payload.quiz_marks = params.quizMarks ? parseInt(params.quizMarks) : 20;
        }

        const response = await apiClient.post('/api/v1/lessons/generate', payload);

        return response.data;
    } catch (error) {
        // Enhanced error handling
        if (error.statusCode === 402) {
            throw new Error('Monthly quota exceeded. Please upgrade your plan or try again next month.');
        }
        if (error.statusCode === 429) {
            throw new Error('Too many requests. Please wait a moment and try again.');
        }
        if (error.message?.includes('timeout')) {
            throw new Error('Generation is taking longer than expected. This might happen with complex topics. Please try again.');
        }

        console.error('Lesson generation error:', error);
        throw error;
    }
};

/**
 * Get lesson by ID
 * @param {string} lessonId - Lesson ID
 * @returns {Promise<Object>} Lesson data
 */
export const getLesson = async (lessonId) => {
    try {
        if (!lessonId) {
            throw new Error('Lesson ID is required');
        }

        const response = await apiClient.get(`/api/v1/lessons/${lessonId}`);
        return response.data;
    } catch (error) {
        if (error.statusCode === 404) {
            throw new Error('Lesson not found');
        }
        throw error;
    }
};

/**
 * Get user's lesson history
 * @param {Object} options - Query options
 * @param {number} options.limit - Number of lessons to fetch
 * @param {number} options.offset - Pagination offset
 * @returns {Promise<Array>} Array of lessons
 */
export const getLessonHistory = async (options = {}) => {
    try {
        const params = {
            limit: options.limit || 10,
            offset: options.offset || 0,
        };

        const response = await apiClient.get('/api/v1/lessons', { params });
        return response.data;
    } catch (error) {
        console.error('Failed to fetch lesson history:', error);
        throw error;
    }
};

/**
 * Download file from URL
 * @param {string} fileUrl - File URL (can be relative or absolute)
 * @param {string} filename - Desired filename for download
 * @returns {Promise<void>}
 */
export const downloadFile = async (fileUrl, filename) => {
    try {
        if (!fileUrl) {
            throw new Error('File URL is required');
        }

        // Determine if URL is relative or absolute
        const url = fileUrl.startsWith('http')
            ? fileUrl
            : `${apiClient.defaults.baseURL}${fileUrl}`;

        // Use fetch with credentials if needed
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
        });

        if (!response.ok) {
            throw new Error(`Failed to download file: ${response.statusText}`);
        }

        // Get the blob
        const blob = await response.blob();

        // Create download link
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename;

        // Trigger download
        document.body.appendChild(link);
        link.click();

        // Cleanup
        document.body.removeChild(link);
        window.URL.revokeObjectURL(downloadUrl);

        return { success: true };
    } catch (error) {
        console.error('File download error:', error);

        if (error.message?.includes('Failed to fetch')) {
            throw new Error('Unable to download file. Please check your connection.');
        }

        throw error;
    }
};

/**
 * Download PPT file for a lesson
 * @param {Object} lesson - Lesson object with ppt_url
 * @param {string} topic - Lesson topic for filename
 * @returns {Promise<void>}
 */
export const downloadPPT = async (lesson, topic) => {
    if (!lesson.ppt_url) {
        throw new Error('PPT file is not available for this lesson');
    }

    const filename = `${topic.replace(/\s+/g, '_')}.pptx`;
    return downloadFile(lesson.ppt_url, filename);
};

/**
 * Download PDF file for a lesson
 * @param {Object} lesson - Lesson object with pdf_url
 * @param {string} topic - Lesson topic for filename
 * @returns {Promise<void>}
 */
export const downloadPDF = async (lesson, topic) => {
    if (!lesson.pdf_url) {
        throw new Error('PDF file is not available for this lesson');
    }

    const filename = `${topic.replace(/\s+/g, '_')}.pdf`;
    return downloadFile(lesson.pdf_url, filename);
};

/**
 * Delete a lesson
 * @param {string} lessonId - Lesson ID to delete
 * @returns {Promise<Object>} Success message
 */
export const deleteLesson = async (lessonId) => {
    try {
        if (!lessonId) {
            throw new Error('Lesson ID is required');
        }

        const response = await apiClient.delete(`/api/v1/lessons/${lessonId}`);
        return response.data;
    } catch (error) {
        console.error('Failed to delete lesson:', error);
        throw error;
    }
};

// Export all functions as a service object
const lessonService = {
    generateLesson,
    getLesson,
    getLessonHistory,
    downloadFile,
    downloadPPT,
    downloadPDF,
    deleteLesson,
};

export default lessonService;
