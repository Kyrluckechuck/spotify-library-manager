import React from 'react';

interface InlineSpinnerProps {
  label?: string;
  className?: string;
}

export function InlineSpinner({ label, className }: InlineSpinnerProps) {
  return (
    <span className={`inline-flex items-center gap-2 ${className ?? ''}`}>
      <span
        className='w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin'
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
