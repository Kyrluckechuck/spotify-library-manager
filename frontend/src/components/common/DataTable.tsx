import React from 'react';
import { LoadMoreButton } from '../ui/LoadMoreButton';

interface DataTableProps<T> {
  data: T[];
  loading: boolean;
  error?: Error | null;
  totalCount: number;
  pageSize: number;
  hasNextPage: boolean;
  onLoadMore: () => void;
  children: React.ReactNode;
  emptyMessage?: string;
  loadingMessage?: string;
  errorMessage?: string;
}

export function DataTable<T>({
  data,
  loading,
  error,
  totalCount,
  hasNextPage,
  onLoadMore,
  children,
  emptyMessage = 'No data found',
  loadingMessage = 'Loading...',
  errorMessage = 'Error loading data',
}: DataTableProps<T>) {
  if (loading && data.length === 0) {
    return (
      <div className='bg-white rounded shadow p-6 min-h-[200px] flex items-center justify-center text-gray-400'>
        {loadingMessage}
      </div>
    );
  }

  if (error) {
    return (
      <div className='bg-white rounded shadow p-6 min-h-[200px] flex items-center justify-center text-red-500'>
        {errorMessage}: {error.message}
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className='bg-white rounded shadow p-6 min-h-[200px] flex items-center justify-center text-gray-400'>
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className='space-y-4'>
      <div className='bg-white rounded shadow overflow-hidden'>{children}</div>

      <LoadMoreButton
        hasNextPage={hasNextPage}
        loading={loading}
        remainingCount={totalCount - data.length}
        onLoadMore={onLoadMore}
      />
    </div>
  );
}
