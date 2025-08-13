import React from 'react';
import { LoadMoreButton } from '../ui/LoadMoreButton';
// import { PageSpinner } from '../ui/PageSpinner';
import { ErrorBanner } from '../ui/ErrorBanner';
import { EmptyState } from '../ui/EmptyState';
// import { RetryButton } from '../ui/RetryButton';
import { SkeletonTable } from '../ui/SkeletonTable';

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
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  loadingMessage = 'Loading...',
  errorMessage = 'Error loading data',
}: DataTableProps<T>) {
  if (loading && data.length === 0) {
    // Skeletons for initial loads
    return <SkeletonTable columns={4} rows={10} />;
  }

  if (error) {
    return (
      <ErrorBanner
        title={errorMessage}
        message={error.message}
        onRetry={onLoadMore}
      />
    );
  }

  if (data.length === 0) {
    return <EmptyState title={emptyMessage} />;
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
