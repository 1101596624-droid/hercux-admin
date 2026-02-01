import React from 'react';
import { cn } from '@/lib/cn';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info';
  size?: 'sm' | 'md' | 'lg';
  rounded?: boolean;
}

export function Badge({
  children,
  variant = 'default',
  size = 'md',
  rounded = false,
  className,
  ...props
}: BadgeProps) {
  const baseStyles = 'inline-flex items-center justify-center font-medium';

  const variants = {
    default: 'bg-dark-100 text-dark-700',
    primary: 'bg-primary-50 text-primary-700',
    success: 'bg-green-50 text-green-700',
    warning: 'bg-yellow-50 text-yellow-700',
    danger: 'bg-red-50 text-red-700',
    info: 'bg-blue-50 text-blue-700',
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  };

  return (
    <span
      className={cn(
        baseStyles,
        variants[variant],
        sizes[size],
        rounded ? 'rounded-full' : 'rounded-md',
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
