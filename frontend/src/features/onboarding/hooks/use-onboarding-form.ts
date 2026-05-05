'use client';

import { useState, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import { useRouter } from 'next/navigation';
import { authApi } from '../../auth/api';
import { OnboardingFormValues } from '../components/types';

/**
 * ============================================================================
 * useOnboardingForm — Multi-Step Form Orchestrator
 * ============================================================================
 *
 * **Purpose**: Manage the 4-step onboarding flow with progressive validation,
 * data accumulation, and submission handling.
 *
 * **Architecture**: Combines react-hook-form (validation) + useState (step tracking).
 *
 * **Why 4 Steps?**
 * 1. **Identity**: Email, password (quick entry, instant validation).
 * 2. **Profile**: Title, background, expertise (context-setting).
 * 3. **Interests**: Topics + YouTube channels (signal source discovery).
 * 4. **Preferences**: Digest frequency, format (fine-tuning before first digest).
 *
 * **Rationale**:
 * - Breaks cognitive load: ~3-5 fields per step vs. 15 fields on one page.
 * - Progressive disclosure: YouTube discovery only after interests.
 * - Validation trigger: Each step validates before advancing.
 * - Recovery: User can go back to edit previous steps.
 * - Reduces drop-off: Visible progress bar encourages completion.
 *
 * **State Management**:
 * - **step (useState)**: Current step (1-4), can only progress/regress sequentially.
 * - **form (react-hook-form)**: Holds form values + validation state.
 * - **isLogin (useState)**: Toggle between login & registration modes.
 * - **loading (useState)**: Submission in flight (disables buttons).
 * - **error (useState)**: Display form-level error (invalid credentials, network).
 *
 * **Complexity**:
 * - Field validation: O(k) where k = fields in current step (~3-5).
 * - Trigger validation: O(k) async validation.
 * - Step progression: O(1) state update.
 * - Submission: O(1) network request.
 *
 * **Integration**: Used by OnboardingForm.tsx component.
 */
export function useOnboardingForm() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [isLogin, setIsLogin] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState(1);
  const totalSteps = 4;

  /**
   * ========================================================================
   * Form State Management (react-hook-form)
   * ========================================================================
   *
   * **Stores**: Multi-step form data + validation errors.
   *
   * **Validation Strategy**:
   * - Per-step validation via trigger(fieldsToValidate).
   * - Error state persists across steps (user can review on next step).
   * - Manual trigger on "Next" prevents auto-submit of partial form.
   *
   * **Default Values**:
   * - Empty strings for identity/profile fields.
   * - Array of empty interests/channels (dynamic fields).
   * - Preferences pre-filled with sensible defaults.
   *
   * **Why this pattern over useState?**
   * - Built-in validation (required, email, min-length).
   * - Zero boilerplate for multi-field forms.
   * - Automatic error handling.
   */
  const form = useForm<OnboardingFormValues>({
    defaultValues: {
      name: '',
      email: '',
      password: '',
      title: '',
      background: '',
      expertise: 'Beginner',
      interests: [{ value: '' }],
      youtubeChannels: [{ value: '' }],
      preferences: {
        digestFrequency: 'Daily',
        format: 'Summary'
      }
    }
  });

  const { handleSubmit, trigger } = form;

  /**
   * ========================================================================
   * Form Submission Handler
   * ========================================================================
   *
   * **Dual Mode**: Login or Onboarding based on isLogin toggle.\n   *
   * **Login Mode**:
   * 1. authApi.login(email, password).\n   * 2. Sets cookies → apiClient injects headers.\n   * 3. Redirect to /feed.\n   *\n   * **Onboarding Mode**:
   * 1. Collect interests (filter empty).\n   * 2. Collect YouTube channels (only those with id).\n   * 3. authApi.onboard(full payload).\n   * 4. Creates user → sets user_id cookie.\n   * 5. User must login separately (see TODO in auth/api.ts).\n   * 6. Redirect to /feed.\n   *\n   * **Error Handling**:
   * - Backend error detail → displayed to user.\n   * - Network error → generic fallback message.\n   * - Loading spinner → prevents double-submit.\n   *\n   * **Complexity**: O(1) network request, O(k) for array filtering.\n   */
  const onSubmit = async (data: OnboardingFormValues) => {
    setLoading(true);
    setError(null);
    try {
      if (isLogin) {
        await authApi.login(data.email, data.password);
      } else {
        await authApi.onboard({
          name: data.name,
          email: data.email,
          password: data.password,
          title: data.title,
          background: data.background,
          expertise_level: data.expertise,
          interests: data.interests.map((i: {value: string}) => i.value).filter((val: string) => val.trim() !== ''),
          youtube_channels: data.youtubeChannels.filter((c: {id?: string}) => c.id).map((c: {id?: string; name?: string; handle?: string}) => ({ id: c.id, name: c.name, handle: c.handle })),
          preferences: data.preferences
        });
      }
      router.push('/feed');
    } catch (err: unknown) {
      const error = err as {response?: {data?: {detail?: string}}};
      setError(error.response?.data?.detail || (isLogin ? 'Login failed. Invalid credentials.' : 'Registration failed. Please try again.'));
      console.error('Auth error:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * ========================================================================
   * Step Navigation Handlers
   * ========================================================================
   *
   * **handleNext**: Validate current step, progress to next (or submit on step 4).
   * **prevStep**: Go back one step (no validation).
   * **toggleMode**: Switch between login/registration modes.
   *
   * **Validation Strategy**:
   * - Step 1 (Identity): name, email, password required.
   * - Step 2 (Profile): title, expertise, background required.
   * - Step 3 (Interests): Optional (skip with empty interests).
   * - Step 4 (Preferences): Optional (use defaults).
   *
   * **Why trigger() instead of handleSubmit()?**
   * - Partial form validation: only current step fields.
   * - Preserve form state: don't submit yet.
   * - Allow user to progress without completing all fields (if optional).
   *
   * **Complexity**: O(k) for trigger() validation.
   */
  const handleNext = useCallback(async (e: React.MouseEvent) => {
    e.preventDefault();
    const fieldsToValidate: Array<keyof OnboardingFormValues> = [];
    if (step === 1) fieldsToValidate.push('name', 'email', 'password');
    if (step === 2) fieldsToValidate.push('title', 'expertise', 'background');
    
    const isValid = await trigger(fieldsToValidate);
    if (isValid) {
      setStep(s => Math.min(s + 1, totalSteps));
    }
  }, [step, trigger, totalSteps]);

  const prevStep = useCallback(() => setStep(s => Math.max(s - 1, 1)), []);

  const toggleMode = useCallback((loginMode: boolean) => {
    setIsLogin(loginMode);
    setError(null);
    setStep(1);
  }, []);

  return {
    form,
    step,
    totalSteps,
    isLogin,
    loading,
    error,
    onSubmit: handleSubmit(onSubmit),
    handleNext,
    prevStep,
    toggleMode
  };
}
