import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import { CourseAPI, EnrollmentAPI } from '../services/api';

interface Course {
  id: number;
  title: string;
  description: string;
  average_rating: number;
  enrollment_count: number;
}

interface Enrollment {
  id: number;
  course_id: number;
  course_title: string;
  progress: number;
  enrollment_date: string;
}

const Dashboard: React.FC = () => {
  const { currentUser } = useContext(AuthContext);
  const [popularCourses, setPopularCourses] = useState<Course[]>([]);
  const [enrolledCourses, setEnrolledCourses] = useState<Enrollment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Загружаем популярные курсы и курсы, на которые записан пользователь
        const [popularCoursesData, enrollmentsData] = await Promise.all([
          CourseAPI.getPopularCourses(),
          EnrollmentAPI.getUserEnrollments()
        ]);

        setPopularCourses(popularCoursesData);
        setEnrolledCourses(enrollmentsData);
      } catch (err) {
        console.error('Ошибка при загрузке данных:', err);
        setError('Не удалось загрузить данные. Пожалуйста, попробуйте позже.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Форматирование даты
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU');
  };

  // Форматирование прогресса
  const formatProgress = (progress: number) => {
    return `${Math.round(progress)}%`;
  };

  return (
    <div>
      <div className="pb-5 border-b border-gray-200 mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Главная страница</h1>
        <p className="mt-2 text-sm text-gray-500">
          Добро пожаловать, {currentUser?.name || 'пользователь'}!
        </p>
      </div>

      {loading ? (
        <div className="flex justify-center py-10">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-500"></div>
        </div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative my-4">
          {error}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Курсы, на которые записан пользователь */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Ваши курсы</h2>
            {enrolledCourses.length === 0 ? (
              <p className="text-gray-500">
                Вы еще не записаны ни на один курс.{' '}
                <Link to="/courses" className="text-indigo-600 hover:text-indigo-500">
                  Просмотреть все курсы
                </Link>
              </p>
            ) : (
              <div className="space-y-4">
                {enrolledCourses.map((enrollment) => (
                  <div key={enrollment.id} className="bg-white shadow overflow-hidden rounded-lg">
                    <div className="px-4 py-5 sm:p-6">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="text-lg font-medium text-gray-900">
                            <Link to={`/courses/${enrollment.course_id}`} className="hover:text-indigo-600">
                              {enrollment.course_title}
                            </Link>
                          </h3>
                          <p className="mt-1 text-sm text-gray-500">
                            Дата регистрации: {formatDate(enrollment.enrollment_date)}
                          </p>
                        </div>
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                          Прогресс: {formatProgress(enrollment.progress)}
                        </span>
                      </div>
                      <div className="mt-4">
                        <div className="relative pt-1">
                          <div className="overflow-hidden h-2 text-xs flex rounded bg-indigo-200">
                            <div
                              style={{ width: `${enrollment.progress}%` }}
                              className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-indigo-500"
                            ></div>
                          </div>
                        </div>
                      </div>
                      <div className="mt-4">
                        <Link
                          to={`/courses/${enrollment.course_id}`}
                          className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                        >
                          Продолжить обучение
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Популярные курсы */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Популярные курсы</h2>
            {popularCourses.length === 0 ? (
              <p className="text-gray-500">
                Сейчас нет популярных курсов.{' '}
                <Link to="/courses" className="text-indigo-600 hover:text-indigo-500">
                  Просмотреть все курсы
                </Link>
              </p>
            ) : (
              <div className="space-y-4">
                {popularCourses.slice(0, 3).map((course) => (
                  <div key={course.id} className="bg-white shadow overflow-hidden rounded-lg">
                    <div className="px-4 py-5 sm:p-6">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="text-lg font-medium text-gray-900">
                            <Link to={`/courses/${course.id}`} className="hover:text-indigo-600">
                              {course.title}
                            </Link>
                          </h3>
                          <p className="mt-1 text-sm text-gray-500">
                            {course.description?.substring(0, 100)}
                            {course.description?.length > 100 ? '...' : ''}
                          </p>
                        </div>
                        <div className="flex flex-col items-end">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                            Рейтинг: {course.average_rating?.toFixed(1) || 'Нет оценок'}
                          </span>
                          <span className="mt-1 text-xs text-gray-500">
                            {course.enrollment_count} записавшихся
                          </span>
                        </div>
                      </div>
                      <div className="mt-4">
                        <Link
                          to={`/courses/${course.id}`}
                          className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                        >
                          Подробнее
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}
                <div className="text-center mt-4">
                  <Link
                    to="/courses"
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Посмотреть все курсы
                  </Link>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
