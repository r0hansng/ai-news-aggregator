'use client';

import { useState } from 'react';
import { useFormContext, useFieldArray } from 'react-hook-form';
import { Plus, X, Search, Check, AlertCircle } from 'lucide-react';
import { Button } from '@/shared/components/ui/Button';
import { OnboardingFormValues } from '../types';
import { signalsService } from '@/lib/api';
import { Loader } from '@/shared/components/ui/Loader';

export function Step3Inputs() {
  const { register, control, setValue, getValues } = useFormContext<OnboardingFormValues>();
  const sectionTitle = "text-lg font-serif font-medium text-white mb-6";
  const [resolving, setResolving] = useState<Record<number, boolean>>({});
  const [resolveError, setResolveError] = useState<Record<number, string>>({});

  const { fields: interestFields, append: appendInterest, remove: removeInterest } = useFieldArray({
    control,
    name: "interests"
  });

  const { fields: youtubeFields, append: appendYoutube, remove: removeYoutube } = useFieldArray({
    control,
    name: "youtubeChannels"
  });

  const handleResolve = async (index: number) => {
    const value = getValues(`youtubeChannels.${index}.value`);
    const isResolved = getValues(`youtubeChannels.${index}.id`) !== undefined;
    
    if (!value || value === '@' || isResolved) return;

    let query = value;
    if (query.includes('youtube.com/')) {
      const extracted = query.match(/@([^\/\?]+)/);
      query = extracted ? `@${extracted[1]}` : query;
    }

    setResolving(prev => ({ ...prev, [index]: true }));
    setResolveError(prev => ({ ...prev, [index]: '' }));
    
    try {
      const data = await signalsService.resolveChannel(query);
      setValue(`youtubeChannels.${index}.id`, data.channel_id);
      setValue(`youtubeChannels.${index}.name`, data.display_name);
      setValue(`youtubeChannels.${index}.handle`, data.handle || query);
      setValue(`youtubeChannels.${index}.value`, data.display_name);
    } catch (err: any) {
      setResolveError(prev => ({ ...prev, [index]: 'Channel not found. Check spelling.' }));
    } finally {
      setResolving(prev => ({ ...prev, [index]: false }));
    }
  };

  const handleFocus = (index: number) => {
    const value = getValues(`youtubeChannels.${index}.value`);
    if (!value) {
      setValue(`youtubeChannels.${index}.value`, '@');
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2">
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
          <div className="space-y-3 max-h-[240px] overflow-y-auto pr-2 scrollbar-hide">
            {youtubeFields.map((field, index) => {
              const isResolved = getValues(`youtubeChannels.${index}.id`) !== undefined;
              
              return (
                <div key={field.id} className="space-y-1">
                  <div className="flex gap-2">
                    <div className="relative flex-1">
                      <input
                        type="text"
                        className={`w-full bg-white/[0.03] border px-4 py-3 placeholder:text-zinc-600 focus:outline-none transition-all rounded-xl text-sm pr-10 ${isResolved ? 'text-emerald-400 border-zinc-800 font-medium' : 'text-white border-zinc-800 focus:border-zinc-500 font-mono'} ${resolveError[index] ? 'border-red-500/50' : ''}`}
                        placeholder="@handle or Channel ID"
                        {...register(`youtubeChannels.${index}.value` as const)}
                        onFocus={() => handleFocus(index)}
                        onBlur={(e) => {
                          register(`youtubeChannels.${index}.value`).onBlur(e);
                          handleResolve(index);
                        }}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            handleResolve(index);
                          }
                        }}
                        onChange={(e) => {
                          register(`youtubeChannels.${index}.value`).onChange(e);
                          if (isResolved) {
                            setValue(`youtubeChannels.${index}.id`, undefined);
                            setValue(`youtubeChannels.${index}.name`, undefined);
                            setValue(`youtubeChannels.${index}.handle`, undefined);
                          }
                          setResolveError(prev => ({ ...prev, [index]: '' }));
                        }}
                      />
                      <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center">
                        {resolving[index] ? (
                          <Loader size="sm" />
                        ) : isResolved ? (
                          <Check size={14} className="text-emerald-500" />
                        ) : null}
                      </div>
                    </div>
                    <Button 
                      type="button" 
                      variant="ghost" 
                      size="icon"
                      onClick={() => removeYoutube(index)}
                    >
                      <X size={14} />
                    </Button>
                  </div>
                  {resolveError[index] && (
                    <div className="flex items-center gap-1 text-[9px] text-red-400 font-bold uppercase tracking-tighter ml-1">
                      <AlertCircle size={10} /> {resolveError[index]}
                    </div>
                  )}
                </div>
              );
            })}
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
  );
}
