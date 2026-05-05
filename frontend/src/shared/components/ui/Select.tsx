'use client';

import React, { forwardRef } from 'react';

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
  options: string; // comma separated
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, options, className, ...props }, ref) => {
    const optionsList = options.split(',').map(opt => opt.trim());
    
    return (
      <div className="space-y-2">
        <label className="block text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-400 ml-1">
          {label}
        </label>
        <div className="relative">
          <select
            ref={ref}
            className={`w-full bg-white/[0.03] border border-zinc-800 px-4 py-3 text-white appearance-none focus:outline-none focus:border-zinc-500 transition-all rounded-xl text-sm font-sans ${className || ''}`}
            {...props}
          >
            {optionsList.map((opt) => (
              <option key={opt} value={opt} className="bg-[#0d0d0e]">
                {opt}
              </option>
            ))}
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-zinc-500">
            <svg className="h-4 w-4 fill-current" viewBox="0 0 20 20">
              <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
            </svg>
          </div>
        </div>
      </div>
    );
  }
);

Select.displayName = 'Select';
