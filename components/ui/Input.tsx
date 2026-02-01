import React from 'react';
import { cn } from '@/lib/cn';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      helperText,
      leftIcon,
      rightIcon,
      className,
      ...props
    },
    ref
  ) => {
    const hasError = !!error;

    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-dark-700 mb-1.5">
            {label}
          </label>
        )}

        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-dark-400">
              {leftIcon}
            </div>
          )}

          <input
            ref={ref}
            className={cn(
              'w-full rounded-lg border px-4 py-2.5 text-dark-900 placeholder:text-dark-400',
              'focus:outline-none focus:ring-2 focus:ring-offset-1 transition-all',
              hasError
                ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
                : 'border-dark-200 focus:border-primary-600 focus:ring-primary-600',
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              props.disabled && 'bg-dark-50 cursor-not-allowed',
              className
            )}
            {...props}
          />

          {rightIcon && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-dark-400">
              {rightIcon}
            </div>
          )}
        </div>

        {(error || helperText) && (
          <p
            className={cn(
              'mt-1.5 text-sm',
              error ? 'text-red-600' : 'text-dark-500'
            )}
          >
            {error || helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
