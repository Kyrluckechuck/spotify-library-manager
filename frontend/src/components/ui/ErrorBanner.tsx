import React, { useEffect, useRef } from 'react';

interface ErrorBannerProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export function ErrorBanner({
  title = 'Something went wrong',
  message,
  onRetry,
}: ErrorBannerProps) {
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    ref.current?.focus();
  }, []);

  return (
    <div
      ref={ref}
      tabIndex={-1}
      role='alert'
      aria-live='polite'
      className='bg-red-50 border border-red-200 text-red-800 rounded p-4 flex items-start justify-between gap-4'
    >
      <div>
        <div className='font-semibold'>{title}</div>
        {message ? <div className='text-sm mt-1'>{message}</div> : null}
      </div>
      {onRetry ? (
        <button
          onClick={onRetry}
          className='px-3 py-1 text-sm bg-red-100 hover:bg-red-200 rounded border border-red-300'
        >
          Retry
        </button>
      ) : null}
    </div>
  );
}
