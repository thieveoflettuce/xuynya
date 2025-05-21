import React, { createContext, useState, useEffect, ReactNode } from 'react';
import { API_URL } from '../services/api';

interface AuthContextType {
  currentUser: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

interface User {
  id: number;
  name: string;
  email: string;
  role: string;
}

interface AuthContextProviderProps {
  children: ReactNode;
}

// Создаем контекст с дефолтными значениями
export const AuthContext = createContext<AuthContextType>({
  currentUser: null,
  login: async () => {},
  register: async () => {},
  logout: () => {},
  isAuthenticated: false
});

export const AuthContextProvider: React.FC<AuthContextProviderProps> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Проверка наличия токена и данных пользователя при загрузке
  useEffect(() => {
    const checkUser = async () => {
      try {
        const token = localStorage.getItem('authToken');
        if (!token) {
          throw new Error('No token found');
        }

        // Получаем данные о пользователе
        const response = await fetch(`${API_URL}/auth/profile`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch user data');
        }

        const userData = await response.json();
        setCurrentUser({
          id: userData.id,
          name: userData.name,
          email: userData.email,
          role: userData.role || 'student'
        });
      } catch (error) {
        // Если ошибка, удаляем токен и сбрасываем пользователя
        localStorage.removeItem('authToken');
        setCurrentUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkUser();
  }, []);

  // Функция для авторизации
  const login = async (email: string, password: string) => {
    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Ошибка авторизации');
      }

      const data = await response.json();
      localStorage.setItem('authToken', data.access_token);

      // Получаем данные пользователя
      const userResponse = await fetch(`${API_URL}/auth/profile`, {
        headers: {
          Authorization: `Bearer ${data.access_token}`
        }
      });

      if (!userResponse.ok) {
        throw new Error('Не удалось получить данные пользователя');
      }

      const userData = await userResponse.json();
      setCurrentUser({
        id: userData.id,
        name: userData.name,
        email: userData.email,
        role: userData.role || 'student'
      });
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(error.message);
      }
      throw new Error('Неизвестная ошибка при авторизации');
    }
  };

  // Функция для регистрации
  const register = async (name: string, email: string, password: string) => {
    try {
      const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name, email, password })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Ошибка регистрации');
      }

      // Возвращаем успешный результат, но не выполняем автоматический вход
      // Пользователю нужно будет отдельно войти после регистрации
      return;
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(error.message);
      }
      throw new Error('Неизвестная ошибка при регистрации');
    }
  };

  // Функция для выхода
  const logout = () => {
    localStorage.removeItem('authToken');
    setCurrentUser(null);
  };

  const value = {
    currentUser,
    login,
    register,
    logout,
    isAuthenticated: !!currentUser
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export default AuthContextProvider;
