'use client';

import { Signal, RefreshCw } from 'lucide-react';

interface EmptyStateProps {
  onRefresh: () => void;
}

export const EmptyState = ({ onRefresh }: EmptyStateProps) => {
  return (
    <div className="flex flex-col items-center justify-center py-24 px-6 text-center space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">
      <div className="relative">
        <div className="absolute inset-0 bg-white/5 blur-3xl rounded-full" />
        <div className="relative w-20 h-20 border border-zinc-800 rounded-2xl flex items-center justify-center rotate-12 group-hover:rotate-0 transition-transform duration-500">
          <Signal size={32} className="text-zinc-600" />
        </div>
      </div>
      
      <div className="space-y-3 max-w-sm">
        <h3 className="text-2xl font-serif text-white">Signal Silence</h3>
        <p className="text-zinc-500 font-serif leading-relaxed">
          The research stream is currently quiet. Re-synchronize with the global AI engine to fetch the latest signals.
        </p>
      </div>

      <button
        onClick={onRefresh}
        className="group flex items-center gap-3 px-8 py-4 bg-white text-black rounded-full font-bold text-xs uppercase tracking-widest hover:bg-zinc-200 transition-all active:scale-95"
      >
        <RefreshCw size={14} className="group-hover:rotate-180 transition-transform duration-500" />
        Initialize Sync
      </button>
    </div>
  );
};
