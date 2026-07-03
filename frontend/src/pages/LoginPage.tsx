import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useMutation } from '@tanstack/react-query';
import { login } from '@/api/auth';
import { getApiErrorMessage } from '@/api/client';
import { useAuthStore } from '@/store/authStore';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { tr } from '@/i18n/tr';
import { config } from '@/config';

const loginSchema = z.object({
  email: z
    .string()
    .min(1, tr.auth.emailRequired)
    .email(tr.auth.emailInvalid),
  password: z
    .string()
    .min(1, tr.auth.passwordRequired)
    .min(8, tr.auth.passwordMin),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const setAuth = useAuthStore((state) => state.setAuth);
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  });

  const mutation = useMutation({
    mutationFn: login,
    onSuccess: (data) => {
      setAuth(data);
      toast.success(tr.auth.loginSuccess);
      const from = (location.state as { from?: { pathname: string } } | null)?.from?.pathname;
      navigate(from ?? '/dashboard', { replace: true });
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error));
    },
  });

  const onSubmit = (values: LoginFormValues) => {
    mutation.mutate(values);
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-semibold text-gray-900">{tr.common.appName}</h1>
          <p className="mt-1 text-sm text-gray-500">{tr.auth.loginTitle}</p>
        </div>

        {config.useMockAuth && (
          <div className="mb-4 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
            {tr.auth.mockModeNotice}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="card space-y-4" noValidate>
          <Input
            label={tr.auth.email}
            type="email"
            autoComplete="email"
            placeholder={tr.auth.emailPlaceholder}
            error={errors.email?.message}
            {...register('email')}
          />

          <div className="relative">
            <Input
              label={tr.auth.password}
              type={showPassword ? 'text' : 'password'}
              autoComplete="current-password"
              placeholder={tr.auth.passwordPlaceholder}
              error={errors.password?.message}
              {...register('password')}
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-3 top-9 text-xs font-medium text-gray-500 hover:text-gray-700"
            >
              {showPassword ? 'Gizle' : 'Göster'}
            </button>
          </div>

          <Button type="submit" className="w-full" isLoading={mutation.isPending}>
            {tr.auth.loginButton}
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-600">
          {tr.auth.noAccount}{' '}
          <Link to="/register" className="font-medium text-primary-600 hover:text-primary-700">
            {tr.auth.goToRegister}
          </Link>
        </p>
      </div>
    </div>
  );
}
