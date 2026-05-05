'use client';

import { useFormContext } from 'react-hook-form';
import { Input } from '@/shared/components/ui/Input';
import { OnboardingFormValues } from './types';

export function LoginForm() {
  const { register, formState: { errors } } = useFormContext<OnboardingFormValues>();
  const sectionTitle = "text-lg font-serif font-medium text-white mb-6";

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2">
      <h4 className={sectionTitle}>Welcome back.</h4>
      <Input 
        label="Email Address"
        type="email"
        placeholder="alan@turing.inst"
        error={errors.email?.message || (errors.email ? 'Required' : undefined)}
        {...register('email', { required: "Email is required" })}
      />
      <Input 
        label="Password"
        type="password"
        placeholder="••••••••"
        error={errors.password?.message || (errors.password ? 'Required' : undefined)}
        {...register('password', { required: "Password is required" })}
      />
    </div>
  );
}
