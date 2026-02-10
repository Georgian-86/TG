import { apiClient } from '../lib/api/client';

const API_BASE = '/api/v1';  // apiClient already has baseURL configured

// ===== Profile APIs =====

export const getProfile = async () => {
    const response = await apiClient.get(`${API_BASE}/users/profile`);
    return response.data;
};

export const updateProfile = async (profileData) => {
    const response = await apiClient.put(`${API_BASE}/users/profile`, profileData);
    return response.data;
};

export const uploadAvatar = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post(`${API_BASE}/users/profile/avatar`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
    return response.data;
};

export const deleteAvatar = async () => {
    const response = await apiClient.delete(`${API_BASE}/users/profile/avatar`);
    return response.data;
};

// ===== Lesson History APIs =====

export const getLessonHistory = async ({ page = 1, pageSize = 20, search = '', favoritesOnly = false } = {}) => {
    const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        ...(search && { search }),
        ...(favoritesOnly && { favorites_only: 'true' })
    });

    const response = await apiClient.get(`${API_BASE}/lessons/history?${params}`);
    return response.data;
};

export const getLessonDetail = async (lessonId) => {
    const response = await apiClient.get(`${API_BASE}/lessons/${lessonId}`);
    return response.data;
};

export const saveLesson = async (lessonData) => {
    const response = await apiClient.post(`${API_BASE}/lessons/save`, lessonData);
    return response.data;
};

export const toggleFavorite = async (lessonId) => {
    const response = await apiClient.post(`${API_BASE}/lessons/history/${lessonId}/favorite`, {});
    return response.data;
};

export const deleteLesson = async (lessonId) => {
    const response = await apiClient.delete(`${API_BASE}/lessons/history/${lessonId}`);
    return response.data;
};
