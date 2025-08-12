import React from 'react';

export function RetryButton({
  onClick,
  children,
}: {
  onClick: () => void;
  children?: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className='inline-flex items-center gap-2 px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded border border-gray-300'
    >
      <svg
        className='w-4 h-4'
        viewBox='0 0 20 20'
        fill='currentColor'
        aria-hidden='true'
      >
        <path
          fillRule='evenodd'
          d='M4 4a8 8 0 0113.657 3H20l-3.5 3.5L13 7h2.223A6 6 0 106 16h2a4 4 0 110-8h1v2L13 6 9 2v2H8A8 8 0 004 4z'
          clipRule='evenodd'
        />
      </svg>
      {children ?? 'Retry'}
    </button>
  );
}
