import React from 'react';

export function PageSpinner({ message = 'Loading...' }: { message?: string }) {
  return (
    <div
      className='bg-white rounded shadow p-6 min-h-[200px] flex flex-col items-center justify-center gap-3'
      aria-busy='true'
    >
      <div className='w-8 h-8 border-4 border-gray-300 border-t-blue-500 rounded-full animate-spin' />
      <div className='text-gray-500'>{message}</div>
    </div>
  );
}
