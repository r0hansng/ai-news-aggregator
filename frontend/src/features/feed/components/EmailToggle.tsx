'use client';

import { Mail, Loader } from 'lucide-react';

interface EmailToggleProps {
  enabled: boolean;
  loading: boolean;
  onToggle: (enabled: boolean) => void;
}

export const EmailToggle = ({ enabled, loading, onToggle }: EmailToggleProps) => {
  return (
    <div className="flex items-center gap-4 px-4 py-2 bg-white/[0.02] border border-zinc-900 rounded-full group transition-all hover:border-zinc-800">
      <div className={`p-1.5 rounded-full transition-colors ${enabled ? 'bg-emerald-500/10 text-emerald-500' : 'bg-zinc-900 text-zinc-600'}`}>
        <Mail size={12} />
      </div>
      
      <div className="flex flex-col">
        <span className="text-[9px] font-bold uppercase tracking-widest text-zinc-500">
          Agentic Delivery
        </span>
      </div>

      <button
        onClick={() => onToggle(!enabled)}
        disabled={loading}
        className={`relative w-8 h-4 rounded-full transition-colors duration-300 ${enabled ? 'bg-emerald-500' : 'bg-zinc-800'} disabled:opacity-50`}
      >
        <div className={`absolute top-0.5 left-0.5 w-3 h-3 bg-white rounded-full transition-transform duration-300 ${enabled ? 'translate-x-4' : 'translate-x-0'}`}>
          {loading && <Loader size={8} className="animate-spin text-zinc-400 m-auto mt-[2px]" />}
        </div>
      </button>
    </div>
  );
};
