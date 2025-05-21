import axios from 'axios';

// Базовый URL API
const API_URL = 'http://localhost:5000';

// Настройка axios
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Добавляем перехватчик запросов для добавления токена авторизации
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// API для работы с курсами
export const courseApi = {
  // Получение всех курсов
  getAllCourses: () => api.get('/api/courses'),

  // Получение конкретного курса
  getCourse: (id: number) => api.get(`/api/courses/${id}`),

  // Создание нового курса
  createCourse: (data: { title: string; description: string }) =>
    api.post('/api/courses', data),

  // Обновление курса
  updateCourse: (id: number, data: { title?: string; description?: string }) =>
    api.put(`/api/courses/${id}`, data),

  // Удаление курса
  deleteCourse: (id: number) => api.delete(`/api/courses/${id}`),

  // Получение популярных курсов
  getPopularCourses: () => api.get('/api/courses/popular'),

  // Получение статистики по курсам
  getCourseStatistics: () => api.get('/api/courses/statistics'),

  // Получение статистики по модулям курсов
  getCourseModuleStatistics: () => api.get('/api/courses/module-statistics')
};

// API для работы с модулями
export const moduleApi = {
  // Получение модулей курса
  getModules: (courseId: number) => api.get(`/api/courses/${courseId}/modules`),

  // Получение конкретного модуля
  getModule: (id: number) => api.get(`/api/modules/${id}`),

  // Создание нового модуля
  createModule: (courseId: number, data: { title: string; content: string }) =>
    api.post(`/api/courses/${courseId}/modules`, data),

  // Обновление модуля
  updateModule: (id: number, data: { title?: string; content?: string }) =>
    api.put(`/api/modules/${id}`, data),

  // Удаление модуля
  deleteModule: (id: number) => api.delete(`/api/modules/${id}`)
};

// API для работы с регистрацией на курсы
export const enrollmentApi = {
  // Регистрация на курс
  enrollCourse: (courseId: number) => api.post(`/api/courses/${courseId}/enroll`),

  // Получение курсов пользователя
  getUserEnrollments: () => api.get('/api/enrollments'),

  // Отмена регистрации на курс
  unenrollCourse: (courseId: number) => api.delete(`/api/courses/${courseId}/unenroll`),

  // Получение прогресса по курсу
  getCourseProgress: (courseId: number) => api.get(`/api/courses/${courseId}/progress`)
};

// API для работы с оценками
export const assessmentApi = {
  // Получение оценок пользователя
  getUserAssessments: () => api.get('/api/assessments'),

  // Создание или обновление оценки
  saveAssessment: (moduleId: number, grade: number) =>
    api.post(`/api/modules/${moduleId}/assessment`, { grade })
};

// API для работы с отзывами
export const feedbackApi = {
  // Получение отзывов о курсе
  getCourseFeedbacks: (courseId: number) => api.get(`/api/courses/${courseId}/feedbacks`),

  // Создание отзыва
  createFeedback: (courseId: number, data: { rating: number; comment?: string }) =>
    api.post(`/api/courses/${courseId}/feedback`, data),

  // Удаление отзыва
  deleteFeedback: (id: number) => api.delete(`/api/feedbacks/${id}`)
};

// API для работы со статистикой
export const statisticsApi = {
  // Получение статистики успеваемости пользователей
  getUserPerformanceStatistics: () => api.get('/api/statistics/user-performance'),

  // Получение статистики активности пользователей
  getUserActivityStatistics: () => api.get('/api/statistics/user-activity'),

  // Получение активных пользователей с курсами
  getActiveUsersWithCourses: () => api.get('/api/statistics/active-users')
};

export default api;
