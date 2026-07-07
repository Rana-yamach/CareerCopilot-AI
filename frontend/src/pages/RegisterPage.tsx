import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useMutation } from '@tanstack/react-query';
import { register as registerUser } from '@/api/auth';
import { getApiErrorCode, getApiErrorMessage } from '@/api/client';
import { useAuthStore } from '@/store/authStore';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { tr } from '@/i18n/tr';
import { config } from '@/config';

const registerSchema = z
  .object({
    email: z
      .string()
      .min(1, tr.auth.emailRequired)
      .email(tr.auth.emailInvalid),
    password: z
      .string()
      .min(1, tr.auth.passwordRequired)
      .min(8, tr.auth.passwordMin),
    confirmPassword: z.string().min(1, tr.auth.passwordRequired),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: tr.auth.passwordMismatch,
    path: ['confirmPassword'],
  });

type RegisterFormValues = z.infer<typeof registerSchema>;

export function RegisterPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
  });

  const mutation = useMutation({
    mutationFn: (values: RegisterFormValues) =>
      registerUser({ email: values.email, password: values.password }),
    onSuccess: (data) => {
      setAuth(data);
      toast.success(tr.auth.registerSuccess);
      navigate('/dashboard', { replace: true });
    },
    onError: (error) => {
      if (getApiErrorCode(error) === 'CONFLICT') {
        setError('email', { message: tr.auth.emailConflict });
        toast.error(tr.auth.emailConflict);
        return;
      }
      toast.error(getApiErrorMessage(error));
    },
  });

  const onSubmit = (values: RegisterFormValues) => {
    mutation.mutate(values);
  };

  return (
    <div className="relative flex min-h-screen bg-app">
      <div className="absolute right-4 top-4 z-20">
        <ThemeToggle />
      </div>

      {/* Sol panel — marka vitrini, yalnızca lg ve üstü genişliklerde görünür */}
      <div className="relative hidden w-1/2 flex-col justify-between overflow-hidden bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900 p-12 lg:flex">
        <div aria-hidden="true" className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute -left-24 -top-24 h-96 w-96 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute bottom-0 right-0 h-80 w-80 rounded-full bg-primary-400/20 blur-3xl" />
          <div className="absolute left-1/3 top-1/2 h-64 w-64 rounded-full bg-accent-400/10 blur-3xl" />
        </div>

        <div className="relative z-10 flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-white/15 text-sm font-bold text-white backdrop-blur">
            CC
          </span>
          <span className="text-lg font-semibold text-white">{tr.common.appName}</span>
        </div>

        <div className="relative z-10">
          <h2 className="text-3xl font-semibold leading-tight text-white">
            {tr.auth.brandHeadline}
          </h2>
          <p className="mt-4 max-w-md text-base text-indigo-100">{tr.auth.brandSubline}</p>
        </div>

        <p className="relative z-10 text-sm text-indigo-200/80">
          © {new Date().getFullYear()} {tr.common.appName}
        </p>
      </div>

      {/* Sağ panel — form */}
      <div className="flex w-full flex-col items-center justify-center px-4 py-12 lg:w-1/2">
        <div className="w-full max-w-md">
          <div className="mb-6 text-center lg:text-left">
            <h1 className="text-xl font-semibold text-default lg:hidden">{tr.common.appName}</h1>
            <p className="mt-2 text-2xl font-semibold text-default">{tr.auth.registerTitle}</p>
            <p className="mt-1 text-sm text-faint">{tr.auth.registerSubtitle}</p>
          </div>

          {config.useMockAuth && (
            <div className="mb-4 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800 dark:border-amber-900/40 dark:bg-amber-950/30 dark:text-amber-300">
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
                autoComplete="new-password"
                placeholder={tr.auth.passwordPlaceholder}
                error={errors.password?.message}
                {...register('password')}
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                className="absolute right-3 top-9 text-xs font-medium text-faint hover:text-muted"
              >
                {showPassword ? 'Gizle' : 'Göster'}
              </button>
            </div>

            <Input
              label={tr.auth.confirmPassword}
              type={showPassword ? 'text' : 'password'}
              autoComplete="new-password"
              placeholder={tr.auth.passwordPlaceholder}
              error={errors.confirmPassword?.message}
              {...register('confirmPassword')}
            />

            <Button type="submit" className="w-full" isLoading={mutation.isPending}>
              {tr.auth.registerButton}
            </Button>
          </form>

          <p className="mt-4 text-center text-sm text-muted">
            {tr.auth.haveAccount}{' '}
            <Link
              to="/login"
              className="font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
            >
              {tr.auth.goToLogin}
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
