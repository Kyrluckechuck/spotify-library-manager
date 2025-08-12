import React from 'react';

interface EmptyStateProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className='bg-white rounded shadow p-8 text-center space-y-2'>
      <div className='text-gray-600'>{title}</div>
      {description ? (
        <div className='text-sm text-gray-400'>{description}</div>
      ) : null}
      {action ? <div className='pt-2'>{action}</div> : null}
    </div>
  );
}
