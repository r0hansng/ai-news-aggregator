'use client';

import { Button } from '@/shared/components/ui/Button';

interface AuthToggleProps {
  isLogin: boolean;
  onToggle: (isLogin: boolean) => void;
}

export function AuthToggle({ isLogin, onToggle }: AuthToggleProps) {
  return (
    <div className="flex justify-center mb-8">
      <div className="p-1 bg-white/[0.03] border border-zinc-900 rounded-full flex gap-1">
        <Button 
          variant={!isLogin ? 'secondary' : 'ghost'} 
          size="sm" 
          onClick={() => onToggle(false)}
          className="rounded-full px-6 py-2 h-auto text-[10px]"
        >
          New Intelligence
        </Button>
        <Button 
          variant={isLogin ? 'secondary' : 'ghost'} 
          size="sm" 
          onClick={() => onToggle(true)}
          className="rounded-full px-6 py-2 h-auto text-[10px]"
        >
          Access Feed
        </Button>
      </div>
    </div>
  );
}
