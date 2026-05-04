'use client';

import { useState } from 'react';
import { Plus, X, ArrowRight, ArrowLeft, Check } from 'lucide-react';
import { Input } from './ui/Input';
import { Select } from './ui/Select';
import { Textarea } from './ui/Textarea';
import { Button } from './ui/Button';

export default function OnboardingForm() {
  const [step, setStep] = useState(1);
  const totalSteps = 4;

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    title: '',
    background: '',
    expertise: 'Beginner',
    interests: [''],
    youtubeChannels: [''],
    preferences: {
      digestFrequency: 'Daily',
      format: 'Summary'
    }
  });

  const handleListChange = (index: number, value: string, field: 'interests' | 'youtubeChannels') => {
    const newList = [...formData[field]];
    newList[index] = value;
    setFormData({ ...formData, [field]: newList });
  };

  const addListItem = (field: 'interests' | 'youtubeChannels') => {
    setFormData({ ...formData, [field]: [...formData[field], ''] });
  };

  const removeListItem = (index: number, field: 'interests' | 'youtubeChannels') => {
    const newList = formData[field].filter((_, i) => i !== index);
    setFormData({ ...formData, [field]: newList.length ? newList : [''] });
  };

  const nextStep = () => setStep(s => Math.min(s + 1, totalSteps));
  const prevStep = () => setStep(s => Math.max(s - 1, 1));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (step < totalSteps) {
      nextStep();
    } else {
      console.log('Final Profile Data:', formData);
    }
  };

  const sectionTitle = "text-lg font-serif font-medium text-white mb-6";

  return (
    <div className="space-y-8">
      {/* Progress Bar */}
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

      <form onSubmit={handleSubmit} className="min-h-[380px] flex flex-col justify-between">
        <div className="transition-all duration-300 animate-in fade-in slide-in-from-bottom-2">
          {step === 1 && (
            <div className="space-y-6">
              <h4 className={sectionTitle}>First, the basics.</h4>
              <div className="space-y-6">
                <Input 
                  label="Full Name"
                  placeholder="Alan Turing"
                  value={formData.name}
                  onChange={(val) => setFormData({...formData, name: val})}
                  required
                />
                <Input 
                  label="Email Address"
                  type="email"
                  placeholder="alan@turing.inst"
                  value={formData.email}
                  onChange={(val) => setFormData({...formData, email: val})}
                  required
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
                  value={formData.title}
                  onChange={(val) => setFormData({...formData, title: val})}
                />
                <Select 
                  label="Level"
                  options="Beginner, Intermediate, Advanced, Expert / Researcher"
                  value={formData.expertise}
                  onChange={(val) => setFormData({...formData, expertise: val})}
                />
              </div>
              <Textarea 
                label="Background Context"
                placeholder="Summarize your technical focus..."
                value={formData.background}
                onChange={(val) => setFormData({...formData, background: val})}
              />
            </div>
          )}

          {step === 3 && (
            <div className="space-y-8">
              <h4 className={sectionTitle}>What should we track?</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-500 mb-2 ml-1">Interests</label>
                  <div className="space-y-3 max-h-[200px] overflow-y-auto pr-2 scrollbar-hide">
                    {formData.interests.map((interest, i) => (
                      <div key={i} className="flex gap-2">
                        <input
                          type="text"
                          className="w-full bg-white/[0.03] border border-zinc-800 px-4 py-3 text-white placeholder:text-zinc-600 focus:outline-none focus:border-zinc-500 transition-all rounded-xl text-sm font-sans"
                          placeholder="e.g. RAG"
                          value={interest}
                          onChange={e => handleListChange(i, e.target.value, 'interests')}
                        />
                        <Button 
                          type="button" 
                          variant="ghost" 
                          size="icon"
                          onClick={() => removeListItem(i, 'interests')}
                        >
                          <X size={14} />
                        </Button>
                      </div>
                    ))}
                    <Button 
                      type="button" 
                      variant="ghost" 
                      size="sm"
                      onClick={() => addListItem('interests')}
                      className="mt-1"
                    >
                      <Plus size={12} /> Add Topic
                    </Button>
                  </div>
                </div>
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-500 mb-2 ml-1">YouTube Signals</label>
                  <div className="space-y-3 max-h-[200px] overflow-y-auto pr-2 scrollbar-hide">
                    {formData.youtubeChannels.map((channel, i) => (
                      <div key={i} className="flex gap-2">
                        <input
                          type="text"
                          className="w-full bg-white/[0.03] border border-zinc-800 px-4 py-3 text-white placeholder:text-zinc-600 focus:outline-none focus:border-zinc-500 transition-all rounded-xl text-sm font-sans"
                          placeholder="Channel ID"
                          value={channel}
                          onChange={e => handleListChange(i, e.target.value, 'youtubeChannels')}
                        />
                        <Button 
                          type="button" 
                          variant="ghost" 
                          size="icon"
                          onClick={() => removeListItem(i, 'youtubeChannels')}
                        >
                          <X size={14} />
                        </Button>
                      </div>
                    ))}
                    <Button 
                      type="button" 
                      variant="ghost" 
                      size="sm"
                      onClick={() => addListItem('youtubeChannels')}
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
                  value={formData.preferences.digestFrequency}
                  onChange={(val) => setFormData({...formData, preferences: {...formData.preferences, digestFrequency: val}})}
                />
                <Select 
                  label="Information Density"
                  options="Executive Summary, Technical Deep-dive, Abstracts Only"
                  value={formData.preferences.format}
                  onChange={(val) => setFormData({...formData, preferences: {...formData.preferences, format: val}})}
                />
              </div>
            </div>
          )}
        </div>

        <div className="flex gap-4 pt-12">
          {step > 1 && (
            <Button
              type="button"
              variant="secondary"
              onClick={prevStep}
              className="flex-1"
            >
              <ArrowLeft size={14} /> Back
            </Button>
          )}
          <Button
            type="submit"
            className="flex-[2]"
            size="lg"
          >
            {step === totalSteps ? (
              <>Establish Profile <Check size={14} /></>
            ) : (
              <>Continue <ArrowRight size={14} /></>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}
