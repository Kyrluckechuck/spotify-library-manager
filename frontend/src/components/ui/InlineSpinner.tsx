import React from 'react';

interface InlineSpinnerProps {
  label?: string;
  className?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg';
}

const sizeClasses = {
  xs: 'w-3 h-3 border',
  sm: 'w-4 h-4 border-2',
  md: 'w-5 h-5 border-2',
  lg: 'w-6 h-6 border-2',
};

export function InlineSpinner({
  label,
  className,
  size = 'sm',
}: InlineSpinnerProps) {
  return (
    <span className={`inline-flex items-center gap-2 ${className ?? ''}`}>
      <span
        className={`${sizeClasses[size]} border-gray-300 border-t-blue-500 rounded-full animate-spin`}
        aria-hidden='true'
      />
      {label ? (
        <span className='text-sm text-gray-500' aria-live='polite'>
          {label}
        </span>
      ) : null}
    </span>
  );
}
