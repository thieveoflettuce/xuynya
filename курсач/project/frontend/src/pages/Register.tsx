import React, { useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useForm, SubmitHandler } from 'react-hook-form';
import {
  Box,
  Button,
  Container,
  Grid,
  Link,
  TextField,
  Typography,
  Alert,
  Paper,
  CircularProgress
} from '@mui/material';

// Тип данных формы
interface RegisterFormInputs {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

const Register: React.FC = () => {
  const { register: registerUser, error } = useAuth();
  const [loading, setLoading] = useState(false);
  const [registerError, setRegisterError] = useState<string | null>(null);

  const { register, handleSubmit, formState: { errors }, watch } = useForm<RegisterFormInputs>();
  const password = watch('password', '');

  const onSubmit: SubmitHandler<RegisterFormInputs> = async (data) => {
    if (data.password !== data.confirmPassword) {
      setRegisterError('Пароли не совпадают');
      return;
    }

    try {
      setLoading(true);
      setRegisterError(null);

      await registerUser(data.name, data.email, data.password);

      // Успешная регистрация приведет к автоматическому входу и редиректу
    } catch (err) {
      setRegisterError(error || 'Произошла ошибка при регистрации');
      setLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Paper
        elevation={3}
        sx={{
          p: 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          mt: 4
        }}
      >
        <Typography component="h1" variant="h5">
          Регистрация
        </Typography>

        <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ mt: 3 }}>
          {registerError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {registerError}
            </Alert>
          )}

          <TextField
            margin="normal"
            required
            fullWidth
            id="name"
            label="Имя"
            autoComplete="name"
            autoFocus
            error={!!errors.name}
            helperText={errors.name ? 'Введите ваше имя' : ''}
            {...register('name', { required: true })}
          />

          <TextField
            margin="normal"
            required
            fullWidth
            id="email"
            label="Email"
            autoComplete="email"
            error={!!errors.email}
            helperText={errors.email ? 'Введите корректный email' : ''}
            {...register('email', {
              required: true,
              pattern: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i
            })}
          />

          <TextField
            margin="normal"
            required
            fullWidth
            label="Пароль"
            type="password"
            id="password"
            autoComplete="new-password"
            error={!!errors.password}
            helperText={errors.password ? 'Пароль должен содержать минимум 6 символов' : ''}
            {...register('password', {
              required: true,
              minLength: 6
            })}
          />

          <TextField
            margin="normal"
            required
            fullWidth
            label="Подтверждение пароля"
            type="password"
            id="confirmPassword"
            error={!!errors.confirmPassword || (password && watch('confirmPassword') && password !== watch('confirmPassword'))}
            helperText={
              errors.confirmPassword
                ? 'Подтвердите пароль'
                : (password && watch('confirmPassword') && password !== watch('confirmPassword'))
                  ? 'Пароли не совпадают'
                  : ''
            }
            {...register('confirmPassword', {
              required: true,
              validate: value => value === password || 'Пароли не совпадают'
            })}
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Зарегистрироваться'}
          </Button>

          <Grid container justifyContent="flex-end">
            <Grid item>
              <Link component={RouterLink} to="/login" variant="body2">
                Уже есть аккаунт? Войдите
              </Link>
            </Grid>
          </Grid>
        </Box>
      </Paper>
    </Container>
  );
};

export default Register;
