'use client';

import { useFormContext } from 'react-hook-form';
import { Input } from '@/shared/components/ui/Input';
import { OnboardingFormValues } from '../types';

export default function Step1Identity() {
  const { register, formState: { errors } } = useFormContext<OnboardingFormValues>();
  const sectionTitle = "text-lg font-serif font-medium text-white mb-6";

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2">
      <h4 className={sectionTitle}>First, the basics.</h4>
      <div className="space-y-6">
        <Input 
          label="Full Name"
          placeholder="Alan Turing"
          error={errors.name?.message || (errors.name ? 'Required' : undefined)}
          {...register('name', { required: "Name is required" })}
        />
        <Input 
          label="Email Address"
          type="email"
          placeholder="alan@turing.inst"
          error={errors.email?.message || (errors.email ? 'Invalid email' : undefined)}
          {...register('email', { required: "Email is required", pattern: /^\S+@\S+$/i })}
        />
        <Input 
          label="Password"
          type="password"
          placeholder="Create a secure password"
          error={errors.password?.message || (errors.password ? 'Min 6 characters' : undefined)}
          {...register('password', { required: "Password is required", minLength: { value: 6, message: "Min 6 characters" } })}
        />
      </div>
    </div>
  );
}
