'use client';

import { useFormContext } from 'react-hook-form';
import { Input } from '@/shared/components/ui/Input';
import { Select } from '@/shared/components/ui/Select';
import { Textarea } from '@/shared/components/ui/Textarea';
import { OnboardingFormValues } from '../types';

export function Step2Signal() {
  const { register } = useFormContext<OnboardingFormValues>();
  const sectionTitle = "text-lg font-serif font-medium text-white mb-6";

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2">
      <h4 className={sectionTitle}>Tell us about your work.</h4>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Input 
          label="Title"
          placeholder="e.g. LLM Architect"
          {...register('title')}
        />
        <Select 
          label="Level"
          options="Beginner, Intermediate, Advanced, Expert / Researcher"
          {...register('expertise')}
        />
      </div>
      <Textarea 
        label="Background Context"
        placeholder="Summarize your technical focus..."
        {...register('background')}
      />
    </div>
  );
}
