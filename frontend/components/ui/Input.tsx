'use client';

import React, { forwardRef } from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className, ...props }, ref) => {
    return (
      <div className="space-y-2">
        <label className="block text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-400 ml-1">
          {label}
        </label>
        <input
          ref={ref}
          className={`w-full bg-white/[0.03] border ${error ? 'border-red-500/50 focus:border-red-500' : 'border-zinc-800 focus:border-zinc-500'} px-4 py-3 text-white placeholder:text-zinc-600 focus:outline-none transition-all rounded-xl text-sm font-sans ${className || ''}`}
          {...props}
        />
        {error && (
          <p className="text-[10px] text-red-400 font-bold uppercase tracking-wider ml-1 mt-1">
            {error}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
