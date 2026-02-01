'use client';

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  fullScreen?: boolean;
}

export function Loading({ size = 'md', text, fullScreen = false }: LoadingProps) {
  const sizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-12 w-12',
    lg: 'h-16 w-16',
  };

  const containerClasses = fullScreen
    ? 'fixed inset-0 flex items-center justify-center bg-white/80 backdrop-blur-sm z-50'
    : 'flex items-center justify-center';

  return (
    <div className={containerClasses}>
      <div className="text-center">
        <div
          className={`inline-block animate-spin rounded-full border-b-2 border-primary-600 ${sizeClasses[size]} mb-4`}
        />
        {text && <p className="text-dark-600">{text}</p>}
      </div>
    </div>
  );
}

export function LoadingSpinner({ className = '' }: { className?: string }) {
  return (
    <div className={`inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-current ${className}`} />
  );
}

export function LoadingSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`animate-pulse bg-dark-200 rounded ${className}`} />
  );
}
