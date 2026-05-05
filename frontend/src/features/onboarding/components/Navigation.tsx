'use client';

import { ArrowRight, ArrowLeft, Check } from 'lucide-react';
import { Button } from '@/shared/components/ui/Button';
import { Loader } from '@/shared/components/ui/Loader';

interface NavigationProps {
  step: number;
  totalSteps: number;
  isLogin: boolean;
  loading: boolean;
  onNext: (e: React.MouseEvent) => void;
  onBack: () => void;
}

export function Navigation({ step, totalSteps, isLogin, loading, onNext, onBack }: NavigationProps) {
  return (
    <div className="flex gap-4 pt-12">
      {step > 1 && !isLogin && (
        <Button
          type="button"
          variant="secondary"
          onClick={onBack}
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
          onClick={onNext}
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
  );
}
