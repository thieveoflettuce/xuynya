import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { enrollmentApi, courseApi } from '../services/api';
import {
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Container,
  Divider,
  Grid,
  LinearProgress,
  Link,
  Paper,
  Typography,
  Alert,
  CircularProgress
} from '@mui/material';

// Тип данных для курса
interface Course {
  id: number;
  title: string;
  description: string;
}

// Тип данных для регистрации на курс
interface Enrollment {
  id: number;
  course_id: number;
  course_title: string;
  progress: number;
  enrollment_date: string;
}

// Тип данных для статистики
interface Statistics {
  enrollment_count: number;
  completed_modules_count: number;
  average_progress: number;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [popularCourses, setPopularCourses] = useState<Course[]>([]);
  const [statistics, setStatistics] = useState<Statistics>({
    enrollment_count: 0,
    completed_modules_count: 0,
    average_progress: 0
  });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Загрузка данных
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Загрузка курсов пользователя
        const enrollmentsResponse = await enrollmentApi.getUserEnrollments();
        setEnrollments(enrollmentsResponse.data);

        // Загрузка популярных курсов
        const popularCoursesResponse = await courseApi.getPopularCourses();
        setPopularCourses(popularCoursesResponse.data.slice(0, 3));

        // Рассчитываем статистику
        if (enrollmentsResponse.data.length > 0) {
          const total = enrollmentsResponse.data.length;
          const totalProgress = enrollmentsResponse.data.reduce(
            (sum: number, item: Enrollment) => sum + item.progress, 0
          );
          const completedCount = enrollmentsResponse.data.filter(
            (item: Enrollment) => item.progress >= 100
          ).length;

          setStatistics({
            enrollment_count: total,
            completed_modules_count: completedCount,
            average_progress: totalProgress / total
          });
        }

        setLoading(false);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Не удалось загрузить данные. Пожалуйста, попробуйте позже.');
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Добро пожаловать, {user?.name}!
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Ваш личный кабинет в системе управления курсами
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={4}>
        {/* Статистика */}
        <Grid item xs={12}>
          <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Ваша статистика
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Box textAlign="center">
                  <Typography variant="h3">{statistics.enrollment_count}</Typography>
                  <Typography color="text.secondary">Активных курсов</Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box textAlign="center">
                  <Typography variant="h3">{statistics.completed_modules_count}</Typography>
                  <Typography color="text.secondary">Завершенных курсов</Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box textAlign="center">
                  <Typography variant="h3">{Math.round(statistics.average_progress)}%</Typography>
                  <Typography color="text.secondary">Средний прогресс</Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Раздел курсов пользователя */}
        <Grid item xs={12} md={8}>
          <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Ваши курсы
            </Typography>
            <Divider sx={{ mb: 2 }} />

            {enrollments.length === 0 ? (
              <Box textAlign="center" py={3}>
                <Typography color="text.secondary" gutterBottom>
                  У вас пока нет активных курсов
                </Typography>
                <Button
                  component={RouterLink}
                  to="/courses"
                  variant="contained"
                  sx={{ mt: 2 }}
                >
                  Просмотреть доступные курсы
                </Button>
              </Box>
            ) : (
              <Grid container spacing={2}>
                {enrollments.map((enrollment) => (
                  <Grid item xs={12} sm={6} key={enrollment.id}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" noWrap>
                          {enrollment.course_title}
                        </Typography>
                        <Box sx={{ mt: 2, mb: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={enrollment.progress}
                            sx={{ height: 10, borderRadius: 5 }}
                          />
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          Прогресс: {Math.round(enrollment.progress)}%
                        </Typography>
                      </CardContent>
                      <CardActions>
                        <Button
                          size="small"
                          component={RouterLink}
                          to={`/courses/${enrollment.course_id}`}
                        >
                          Продолжить
                        </Button>
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            )}

            <Box textAlign="right" mt={2}>
              <Link component={RouterLink} to="/courses">
                Просмотреть все курсы
              </Link>
            </Box>
          </Paper>
        </Grid>

        {/* Популярные курсы */}
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Популярные курсы
            </Typography>
            <Divider sx={{ mb: 2 }} />

            {popularCourses.length === 0 ? (
              <Typography color="text.secondary" align="center" sx={{ py: 3 }}>
                Информация о популярных курсах недоступна
              </Typography>
            ) : (
              <Box>
                {popularCourses.map((course) => (
                  <Box key={course.id} sx={{ mb: 2 }}>
                    <Link
                      component={RouterLink}
                      to={`/courses/${course.id}`}
                      color="inherit"
                      underline="hover"
                    >
                      <Typography variant="subtitle1" gutterBottom>
                        {course.title}
                      </Typography>
                    </Link>
                    <Typography variant="body2" color="text.secondary" noWrap>
                      {course.description}
                    </Typography>
                    <Divider sx={{ mt: 1 }} />
                  </Box>
                ))}
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
