'use client';

import { cn } from '@/lib/utils';

interface LoaderProps {
  size?: 'sm' | 'default' | 'lg';
  color?: 'default' | 'white' | 'black' | 'zinc';
  className?: string;
}

const sizeMap = {
  sm: 'w-3.5 h-3.5 border-[1.5px]',
  default: 'w-5 h-5 border-2',
  lg: 'w-8 h-8 border-[2.5px]',
};

const colorMap = {
  default: 'border-zinc-500 border-t-transparent',
  white: 'border-white border-t-transparent',
  black: 'border-black border-t-transparent',
  zinc: 'border-zinc-400 border-t-transparent',
};

export function Loader({ size = 'default', color = 'default', className }: LoaderProps) {
  return (
    <span
      className={cn(
        'inline-block rounded-full animate-spin',
        sizeMap[size],
        colorMap[color],
        className
      )}
    />
  );
}
