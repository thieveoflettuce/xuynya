import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import AuthContextProvider from './contexts/AuthContext';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import CoursesPage from './pages/CoursesPage';
import CourseDetailsPage from './pages/CourseDetailsPage';
import ProfilePage from './pages/ProfilePage';
import NotificationsPage from './pages/NotificationsPage';
import StatisticsPage from './pages/StatisticsPage';
import NotFoundPage from './pages/NotFoundPage';

// Компонент для защищенных маршрутов
const ProtectedRoute: React.FC<{ element?: React.ReactNode }> = ({ element }) => {
  const isAuthenticated = localStorage.getItem('authToken') !== null;
  return isAuthenticated ? (element ? <>{element}</> : <Outlet />) : <Navigate to="/login" />;
};

const App: React.FC = () => {
  return (
    <AuthContextProvider>
      <Router>
        <Routes>
          {/* Публичные маршруты */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Защищённые маршруты */}
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="courses" element={<CoursesPage />} />
              <Route path="courses/:id" element={<CourseDetailsPage />} />
              <Route path="profile" element={<ProfilePage />} />
              <Route path="notifications" element={<NotificationsPage />} />
              <Route path="statistics" element={<StatisticsPage />} />
            </Route>
          </Route>

          {/* Для всех остальных маршрутов */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Router>
    </AuthContextProvider>
  );
};

export default App;
