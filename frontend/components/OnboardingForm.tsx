'use client';

import { useState } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { Plus, X, ArrowRight, ArrowLeft, Check } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { userService } from '@/lib/api';
import { Loader } from './ui/Loader';
import { Input } from './ui/Input';
import { Select } from './ui/Select';
import { Textarea } from './ui/Textarea';
import { Button } from './ui/Button';

interface OnboardingFormValues {
  name: string;
  email: string;
  password: string;
  title: string;
  background: string;
  expertise: string;
  interests: { value: string }[];
  youtubeChannels: { value: string }[];
  preferences: {
    digestFrequency: string;
    format: string;
  };
}

export default function OnboardingForm() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [isLogin, setIsLogin] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState(1);
  const totalSteps = 4;

  const { register, control, handleSubmit, trigger, formState: { errors } } = useForm<OnboardingFormValues>({
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

  const { fields: interestFields, append: appendInterest, remove: removeInterest } = useFieldArray({
    control,
    name: "interests"
  });

  const { fields: youtubeFields, append: appendYoutube, remove: removeYoutube } = useFieldArray({
    control,
    name: "youtubeChannels"
  });

  const onSubmit = async (data: OnboardingFormValues) => {
    setLoading(true);
    setError(null);
    try {
      if (isLogin) {
        await userService.login(data.email, data.password);
      } else {
        await userService.onboard({
          name: data.name,
          email: data.email,
          password: data.password,
          title: data.title,
          background: data.background,
          expertise_level: data.expertise,
          interests: data.interests.map(i => i.value).filter(val => val.trim() !== ''),
          youtube_channels: data.youtubeChannels.map(c => c.value).filter(val => val.trim() !== ''),
          preferences: data.preferences
        });
      }
      router.push('/feed');
    } catch (err: any) {
      setError(err.response?.data?.detail || (isLogin ? 'Login failed. Invalid credentials.' : 'Registration failed. Please try again.'));
      console.error('Auth error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async (e: React.MouseEvent) => {
    e.preventDefault();
    let fieldsToValidate: any[] = [];
    if (step === 1) fieldsToValidate = ['name', 'email', 'password'];
    if (step === 2) fieldsToValidate = ['title', 'expertise', 'background'];
    
    console.log('Validating fields:', fieldsToValidate);
    const isValid = await trigger(fieldsToValidate);
    console.log('Is Step Valid?', isValid, errors);
    
    if (isValid) {
      setStep(s => Math.min(s + 1, totalSteps));
    }
  };

  const prevStep = () => setStep(s => Math.max(s - 1, 1));

  const sectionTitle = "text-lg font-serif font-medium text-white mb-6";

  return (
    <div className="space-y-8">
      {/* Auth Toggle */}
      <div className="flex justify-center mb-8">
        <div className="p-1 bg-white/[0.03] border border-zinc-900 rounded-full flex gap-1">
          <Button 
            variant={!isLogin ? 'secondary' : 'ghost'} 
            size="sm" 
            onClick={() => setIsLogin(false)}
            className="rounded-full px-6 py-2 h-auto text-[10px]"
          >
            New Intelligence
          </Button>
          <Button 
            variant={isLogin ? 'secondary' : 'ghost'} 
            size="sm" 
            onClick={() => setIsLogin(true)}
            className="rounded-full px-6 py-2 h-auto text-[10px]"
          >
            Access Feed
          </Button>
        </div>
      </div>

      {/* Progress Bar (Only for Onboarding) */}
      {!isLogin && (
        <div className="flex gap-2 mb-12">
          {[1, 2, 3, 4].map((i) => (
            <div 
              key={i} 
              className={`h-1 flex-1 rounded-full transition-all duration-500 ${
                i <= step ? 'bg-white' : 'bg-zinc-900'
              }`}
            />
          ))}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="min-h-[380px] flex flex-col justify-between">
        <div className="transition-all duration-300 animate-in fade-in slide-in-from-bottom-2">
          {isLogin ? (
            <div className="space-y-6">
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
          ) : (
            <>
              {step === 1 && (
                <div className="space-y-6">
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
              )}

              {step === 2 && (
                <div className="space-y-6">
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
              )}

              {step === 3 && (
                <div className="space-y-8">
                  <h4 className={sectionTitle}>What should we track?</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div>
                      <label className="block text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-400 mb-2 ml-1">Interests</label>
                      <div className="space-y-3 max-h-[200px] overflow-y-auto pr-2 scrollbar-hide">
                        {interestFields.map((field, index) => (
                          <div key={field.id} className="flex gap-2">
                            <input
                              type="text"
                              className="w-full bg-white/[0.03] border border-zinc-800 px-4 py-3 text-white placeholder:text-zinc-600 focus:outline-none focus:border-zinc-500 transition-all rounded-xl text-sm font-sans"
                              placeholder="e.g. RAG"
                              {...register(`interests.${index}.value` as const)}
                            />
                            <Button 
                              type="button" 
                              variant="ghost" 
                              size="icon"
                              onClick={() => removeInterest(index)}
                            >
                              <X size={14} />
                            </Button>
                          </div>
                        ))}
                        <Button 
                          type="button" 
                          variant="ghost" 
                          size="sm"
                          onClick={() => appendInterest({ value: '' })}
                          className="mt-1"
                        >
                          <Plus size={12} /> Add Topic
                        </Button>
                      </div>
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-400 mb-2 ml-1">YouTube Signals</label>
                      <div className="space-y-3 max-h-[200px] overflow-y-auto pr-2 scrollbar-hide">
                        {youtubeFields.map((field, index) => (
                          <div key={field.id} className="flex gap-2">
                            <input
                              type="text"
                              className="w-full bg-white/[0.03] border border-zinc-800 px-4 py-3 text-white placeholder:text-zinc-600 focus:outline-none focus:border-zinc-500 transition-all rounded-xl text-sm font-sans"
                              placeholder="Channel ID"
                              {...register(`youtubeChannels.${index}.value` as const)}
                            />
                            <Button 
                              type="button" 
                              variant="ghost" 
                              size="icon"
                              onClick={() => removeYoutube(index)}
                            >
                              <X size={14} />
                            </Button>
                          </div>
                        ))}
                        <Button 
                          type="button" 
                          variant="ghost" 
                          size="sm"
                          onClick={() => appendYoutube({ value: '' })}
                          className="mt-1"
                        >
                          <Plus size={12} /> Add Signal
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {step === 4 && (
                <div className="space-y-6">
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
              )}
            </>
          )}
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 text-[10px] uppercase font-bold tracking-widest p-4 rounded-xl mb-4">
            {error}
          </div>
        )}

        <div className="flex gap-4 pt-12">
          {step > 1 && !isLogin && (
            <Button
              type="button"
              variant="secondary"
              onClick={prevStep}
              className="flex-1"
              disabled={loading}
            >
              <ArrowLeft size={14} /> Back
            </Button>
          )}
          {(!isLogin && step < totalSteps) ? (
            <Button
              type="button"
              className="flex-[2]"
              size="lg"
              onClick={handleNext}
              disabled={loading}
            >
              Continue <ArrowRight size={14} />
            </Button>
          ) : (
            <Button
              type="submit"
              className="flex-[2]"
              size="lg"
              disabled={loading}
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  {isLogin ? 'Authenticating' : 'Initializing'} <Loader size="sm" color="white" />
                </div>
              ) : isLogin ? (
                <>Resume Signal <ArrowRight size={14} /></>
              ) : (
                <>Establish Profile <Check size={14} /></>
              )}
            </Button>
          )}
        </div>
      </form>
    </div>
  );
}
