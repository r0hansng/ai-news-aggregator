'use client';

import { useFormContext } from 'react-hook-form';
import { Select } from '@/shared/components/ui/Select';
import { OnboardingFormValues } from '../types';

export default function Step4Delivery() {
  const { register } = useFormContext<OnboardingFormValues>();
  const sectionTitle = "text-lg font-serif font-medium text-white mb-6";

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2">
      <h4 className={sectionTitle}>How should we deliver it?</h4>
      <div className="space-y-6">
        <Select 
          label="Frequency"
          options="Daily (Curated), Weekly (Synthesized), Real-time (Raw)"
          {...register('preferences.digestFrequency')}
        />
        <Select 
          label="Information Density"
          options="Executive Summary, Technical Deep-dive, Abstracts Only"
          {...register('preferences.format')}
        />
      </div>
    </div>
  );
}
