'use client';

import React, { forwardRef } from 'react';

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, className, ...props }, ref) => {
    return (
      <div className="space-y-2">
        <label className="block text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-400 ml-1">
          {label}
        </label>
        <textarea
          ref={ref}
          className={`w-full bg-white/[0.03] border border-zinc-800 px-4 py-3 text-white placeholder:text-zinc-600 focus:outline-none focus:border-zinc-500 transition-all rounded-xl text-sm font-sans min-h-[120px] ${className || ''}`}
          {...props}
        />
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';
