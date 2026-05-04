'use client';

import { motion } from 'framer-motion';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const loaderVariants = cva(
  "flex items-center justify-center",
  {
    variants: {
      variant: {
        default: "",
        button: "inline-flex",
        overlay: "fixed inset-0 bg-background/80 backdrop-blur-sm z-[200]",
      },
      size: {
        sm: "w-3 h-3",
        default: "w-5 h-5",
        lg: "w-10 h-10",
      }
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    }
  }
);

const spinnerVariants = cva(
  "rounded-full border-t-transparent border-current animate-spin",
  {
    variants: {
      size: {
        sm: "border-2",
        default: "border-2",
        lg: "border-3",
      },
      color: {
        default: "text-zinc-500",
        white: "text-white",
        zinc: "text-zinc-400",
      }
    },
    defaultVariants: {
      size: "default",
      color: "default",
    }
  }
);

interface LoaderProps extends VariantProps<typeof loaderVariants>, VariantProps<typeof spinnerVariants> {
  className?: string;
}

export function Loader({ variant, size, color, className }: LoaderProps) {
  return (
    <div className={cn(loaderVariants({ variant, size, className }))}>
      <motion.div
        className={cn(
          "w-full h-full rounded-full border-t-transparent border-current",
          size === 'lg' ? 'border-[3px]' : 'border-2',
          color === 'white' ? 'text-white' : color === 'zinc' ? 'text-zinc-400' : 'text-zinc-500'
        )}
        animate={{ rotate: 360 }}
        transition={{
          duration: 0.8,
          repeat: Infinity,
          ease: "linear",
        }}
      />
    </div>
  );
}
