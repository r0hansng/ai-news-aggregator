/**
 * @file Onboarding Form Orchestrator
 * @module features/onboarding/components/OnboardingForm
 * @description Orchestrates the multi-step user initialization and login 
 * flows. Handles mode switching between 'Onboarding' and 'Login' and 
 * manages the sequential transition between configuration steps.
 */

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
        <LoginForm />
        <AuthToggle isLogin={true} onToggle={() => toggleMode(false)} />
      </div>
    );
  }

  return (
    <div className="space-y-12 animate-in fade-in slide-in-from-left-4 duration-500">
      <div className="space-y-8">
        {step === 1 && <Step1Identity />}
        {step === 2 && <Step2Signal />}
        {step === 3 && <Step3Inputs />}
        {step === 4 && <Step4Delivery />}
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
          isLogin={isLogin}
          loading={loading} 
          onNext={handleNext} 
          onBack={prevStep} 
        />
        <AuthToggle isLogin={false} onToggle={() => toggleMode(true)} />
      </div>
    </div>
  );
}
