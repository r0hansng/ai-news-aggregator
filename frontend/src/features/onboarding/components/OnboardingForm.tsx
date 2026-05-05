'use client';

import { useOnboardingForm } from '../hooks/use-onboarding-form';
import { AuthToggle } from './AuthToggle';
import { LoginForm } from './LoginForm';
import { Navigation } from './Navigation';

import Step1Identity from './steps/Step1Identity';
import Step2Signal from './steps/Step2Signal';
import Step3Inputs from './steps/Step3Inputs';
import Step4Delivery from './steps/Step4Delivery';

/**
 * OnboardingForm Orchestrator
 * 
 * Manages the multi-step initialization flow and Auth mode switching.
 */
export default function OnboardingForm() {
  const { 
    form, 
    step, 
    totalSteps, 
    isLogin, 
    loading, 
    error, 
    onSubmit, 
    handleNext, 
    prevStep, 
    toggleMode 
  } = useOnboardingForm();

  if (isLogin) {
    return (
      <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
        <LoginForm form={form} loading={loading} error={error} onSubmit={onSubmit} />
        <AuthToggle isLogin={true} onToggle={() => toggleMode(false)} />
      </div>
    );
  }

  return (
    <div className="space-y-12 animate-in fade-in slide-in-from-left-4 duration-500">
      <div className="space-y-8">
        {step === 1 && <Step1Identity form={form} />}
        {step === 2 && <Step2Signal form={form} />}
        {step === 3 && <Step3Inputs form={form} />}
        {step === 4 && <Step4Delivery form={form} />}
      </div>

      {error && (
        <p className="text-red-400 text-[10px] font-bold uppercase tracking-widest text-center animate-pulse">
          {error}
        </p>
      )}

      <div className="space-y-6">
        <Navigation 
          step={step} 
          totalSteps={totalSteps} 
          loading={loading} 
          onNext={handleNext} 
          onBack={prevStep} 
        />
        <AuthToggle isLogin={false} onToggle={() => toggleMode(true)} />
      </div>
    </div>
  );
}
