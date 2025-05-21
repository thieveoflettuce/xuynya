// Базовый URL для API
export const API_URL = 'http://localhost:5000';

// Вспомогательная функция для выполнения запросов с авторизацией
export const fetchWithAuth = async (endpoint: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('authToken');

  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json'
  };

  if (token) {
    Object.assign(defaultHeaders, {
      'Authorization': `Bearer ${token}`
    });
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers
    }
  });

  // Если ошибка авторизации, сбрасываем токен
  if (response.status === 401) {
    localStorage.removeItem('authToken');
    window.location.href = '/login';
    throw new Error('Требуется авторизация');
  }

  // Проверяем успешность запроса
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || `Ошибка ${response.status}: ${response.statusText}`);
  }

  return response.json();
};

// API для работы с курсами
export const CourseAPI = {
  // Получить все курсы
  getAllCourses: () => fetchWithAuth('/api/courses'),

  // Получить конкретный курс
  getCourse: (id: number) => fetchWithAuth(`/api/courses/${id}`),

  // Создать новый курс
  createCourse: (data: { title: string; description: string }) =>
    fetchWithAuth('/api/courses', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Обновить курс
  updateCourse: (id: number, data: { title?: string; description?: string }) =>
    fetchWithAuth(`/api/courses/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    }),

  // Удалить курс
  deleteCourse: (id: number) =>
    fetchWithAuth(`/api/courses/${id}`, {
      method: 'DELETE'
    }),

  // Получить популярные курсы
  getPopularCourses: () => fetchWithAuth('/api/courses/popular'),

  // Получить статистику по курсам
  getCourseStatistics: () => fetchWithAuth('/api/courses/statistics'),

  // Получить статистику по модулям курсов
  getCourseModuleStatistics: () => fetchWithAuth('/api/courses/module-statistics')
};

// API для работы с модулями
export const ModuleAPI = {
  // Получить все модули курса
  getModules: (courseId: number) => fetchWithAuth(`/api/courses/${courseId}/modules`),

  // Получить конкретный модуль
  getModule: (id: number) => fetchWithAuth(`/api/modules/${id}`),

  // Создать новый модуль
  createModule: (courseId: number, data: { title: string; content: string }) =>
    fetchWithAuth(`/api/courses/${courseId}/modules`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Обновить модуль
  updateModule: (id: number, data: { title?: string; content?: string }) =>
    fetchWithAuth(`/api/modules/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    }),

  // Удалить модуль
  deleteModule: (id: number) =>
    fetchWithAuth(`/api/modules/${id}`, {
      method: 'DELETE'
    })
};

// API для работы с регистрацией на курсы
export const EnrollmentAPI = {
  // Зарегистрироваться на курс
  enrollCourse: (courseId: number) =>
    fetchWithAuth(`/api/courses/${courseId}/enroll`, {
      method: 'POST'
    }),

  // Получить курсы, на которые зарегистрирован пользователь
  getUserEnrollments: () => fetchWithAuth('/api/enrollments'),

  // Отменить регистрацию на курс
  unenrollCourse: (courseId: number) =>
    fetchWithAuth(`/api/courses/${courseId}/unenroll`, {
      method: 'DELETE'
    }),

  // Получить прогресс пользователя по курсу
  getCourseProgress: (courseId: number) => fetchWithAuth(`/api/courses/${courseId}/progress`)
};

// API для работы с оценками
export const AssessmentAPI = {
  // Получить оценки пользователя
  getUserAssessments: () => fetchWithAuth('/api/assessments'),

  // Сохранить оценку за модуль
  saveAssessment: (moduleId: number, grade: number) =>
    fetchWithAuth(`/api/modules/${moduleId}/assessment`, {
      method: 'POST',
      body: JSON.stringify({ grade })
    })
};

// API для работы с отзывами
export const FeedbackAPI = {
  // Получить отзывы о курсе
  getCourseFeedbacks: (courseId: number) => fetchWithAuth(`/api/courses/${courseId}/feedbacks`),

  // Создать отзыв
  createFeedback: (courseId: number, data: { rating: number; comment?: string }) =>
    fetchWithAuth(`/api/courses/${courseId}/feedback`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Удалить отзыв
  deleteFeedback: (id: number) =>
    fetchWithAuth(`/api/feedbacks/${id}`, {
      method: 'DELETE'
    })
};

// API для работы с уведомлениями
export const NotificationAPI = {
  // Получить уведомления пользователя
  getUserNotifications: (unreadOnly: boolean = false) =>
    fetchWithAuth(`/api/notifications${unreadOnly ? '?unread=true' : ''}`),

  // Получить количество непрочитанных уведомлений
  getUnreadNotificationCount: () => fetchWithAuth('/api/notifications/count'),

  // Отметить уведомление как прочитанное
  markNotificationAsRead: (id: number) =>
    fetchWithAuth(`/api/notifications/${id}/read`, {
      method: 'PUT'
    }),

  // Отметить все уведомления как прочитанные
  markAllNotificationsAsRead: () =>
    fetchWithAuth('/api/notifications/read-all', {
      method: 'PUT'
    }),

  // Удалить уведомление
  deleteNotification: (id: number) =>
    fetchWithAuth(`/api/notifications/${id}`, {
      method: 'DELETE'
    }),

  // Получить статистику по уведомлениям (только для администраторов)
  getNotificationStatistics: () => fetchWithAuth('/api/notifications/statistics')
};

// API для работы с вложениями
export const AttachmentAPI = {
  // Получить вложения модуля
  getModuleAttachments: (moduleId: number) => fetchWithAuth(`/api/modules/${moduleId}/attachments`),

  // Получить вложения курса
  getCourseAttachments: (courseId: number) => fetchWithAuth(`/api/courses/${courseId}/attachments`),

  // Загрузить вложение к модулю
  uploadAttachment: (moduleId: number, formData: FormData) => {
    const token = localStorage.getItem('authToken');

    return fetch(`${API_URL}/api/modules/${moduleId}/attachments`, {
      method: 'POST',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      body: formData
    }).then(response => {
      if (!response.ok) {
        throw new Error('Ошибка при загрузке файла');
      }
      return response.json();
    });
  },

  // Удалить вложение
  deleteAttachment: (id: number) =>
    fetchWithAuth(`/api/attachments/${id}`, {
      method: 'DELETE'
    }),

  // Получить статистику по вложениям для модулей
  getModuleAttachmentStatistics: () => fetchWithAuth('/api/modules/attachment-statistics')
};

// API для работы со статистикой
export const StatisticsAPI = {
  // Получить статистику успеваемости пользователей
  getUserPerformanceStatistics: () => fetchWithAuth('/api/statistics/user-performance'),

  // Получить статистику активности пользователей
  getUserActivityStatistics: () => fetchWithAuth('/api/statistics/user-activity'),

  // Получить активных пользователей с курсами
  getActiveUsersWithCourses: () => fetchWithAuth('/api/statistics/active-users')
};
