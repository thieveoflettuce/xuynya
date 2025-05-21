import React, { createContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

// Определяем тип пользователя
interface User {
  id: number;
  name: string;
  email: string;
  role: string;
}

// Определяем тип контекста авторизации
interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: () => boolean;
}

// Создаем контекст с начальным состоянием
const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  loading: false,
  error: null,
  login: async () => {},
  register: async () => {},
  logout: () => {},
  isAuthenticated: () => false
});

// URL API
const API_URL = 'http://localhost:5000';

// Провайдер контекста
export const AuthProvider: React.FC<{children: ReactNode}> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Настраиваем axios с токеном
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUserProfile();
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Получение профиля пользователя
  const fetchUserProfile = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/auth/profile`);
      setUser(response.data);
      setLoading(false);
    } catch (err) {
      console.error("Ошибка при получении профиля:", err);
      setError("Не удалось загрузить профиль пользователя");
      setLoading(false);
      logout();
    }
  };

  // Функция входа
  const login = async (email: string, password: string) => {
    try {
      setLoading(true);
      setError(null);

      const response = await axios.post(`${API_URL}/auth/login`, { email, password });
      const { access_token } = response.data;

      localStorage.setItem('token', access_token);
      setToken(access_token);

      // Профиль пользователя загрузится автоматически через useEffect
      setLoading(false);
    } catch (err: any) {
      setLoading(false);
      if (err.response && err.response.data && err.response.data.message) {
        setError(err.response.data.message);
      } else {
        setError("Ошибка авторизации. Проверьте ваше соединение");
      }
      throw err;
    }
  };

  // Функция регистрации
  const register = async (name: string, email: string, password: string) => {
    try {
      setLoading(true);
      setError(null);

      await axios.post(`${API_URL}/auth/register`, { name, email, password });

      // После успешной регистрации автоматически входим
      await login(email, password);

      setLoading(false);
    } catch (err: any) {
      setLoading(false);
      if (err.response && err.response.data && err.response.data.message) {
        setError(err.response.data.message);
      } else {
        setError("Ошибка регистрации. Возможно, такой email уже используется");
      }
      throw err;
    }
  };

  // Функция выхода
  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  // Проверка авторизации
  const isAuthenticated = () => {
    return !!token;
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      loading,
      error,
      login,
      register,
      logout,
      isAuthenticated
    }}>
      {children}
    </AuthContext.Provider>
  );
};

// Хук для использования контекста авторизации
export const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
