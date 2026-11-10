import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { getErrorMessage } from '../services/apiClient';
import { FormField } from '../components/ui/FormField';

const loginSchema = z.object({
  email: z.string().email('Enter a valid email'),
  password: z.string().min(1, 'Password is required'),
});

const signupSchema = loginSchema.extend({
  password: z.string().min(8, 'At least 8 characters'),
  phone_number: z.string().optional(),
  country_code: z.string().optional(),
});

function Shell({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="container-px flex justify-center py-16">
      <div className="w-full max-w-md space-y-6 rounded-3xl border border-forest-100 bg-white p-8 shadow-sm">
        <h1 className="font-display text-3xl font-semibold text-forest-900">{title}</h1>
        {children}
      </div>
    </div>
  );
}

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState<string | null>(null);
  const from = (location.state as { from?: string } | null)?.from ?? '/shop';
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<z.infer<typeof loginSchema>>({ resolver: zodResolver(loginSchema) });

  const onSubmit = handleSubmit(async (values) => {
    setError(null);
    try {
      await login(values.email, values.password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(getErrorMessage(err));
    }
  });

  return (
    <Shell title="Welcome back">
      <form onSubmit={onSubmit} className="space-y-4" noValidate>
        <FormField label="Email" type="email" {...register('email')} error={errors.email?.message} />
        <FormField label="Password" type="password" {...register('password')} error={errors.password?.message} />
        {error && <p className="text-sm text-red-600" role="alert">{error}</p>}
        <button className="btn-primary w-full py-2.5" disabled={isSubmitting}>
          {isSubmitting ? 'Signing in…' : 'Log in'}
        </button>
      </form>
      <p className="text-sm text-forest-600">
        New here? <Link to="/signup" className="font-medium underline">Create an account</Link>
      </p>
    </Shell>
  );
}

export function SignupPage() {
  const { signup } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<z.infer<typeof signupSchema>>({ resolver: zodResolver(signupSchema) });

  const onSubmit = handleSubmit(async (values) => {
    setError(null);
    try {
      await signup({
        email: values.email,
        password: values.password,
        phone_number: values.phone_number || null,
        country_code: values.country_code || null,
      });
      showToast('Account created — please log in.', 'success');
      navigate('/login');
    } catch (err) {
      setError(getErrorMessage(err));
    }
  });

  return (
    <Shell title="Create your account">
      <form onSubmit={onSubmit} className="space-y-4" noValidate>
        <FormField label="Email" type="email" {...register('email')} error={errors.email?.message} />
        <FormField label="Password" type="password" {...register('password')} error={errors.password?.message} />
        <FormField label="Country code (optional)" placeholder="+91" {...register('country_code')} />
        <FormField label="Phone number (optional)" type="tel" {...register('phone_number')} />
        {error && <p className="text-sm text-red-600" role="alert">{error}</p>}
        <button className="btn-primary w-full py-2.5" disabled={isSubmitting}>
          {isSubmitting ? 'Creating…' : 'Sign up'}
        </button>
      </form>
      <p className="text-sm text-forest-600">
        Already registered? <Link to="/login" className="font-medium underline">Log in</Link>
      </p>
    </Shell>
  );
}
