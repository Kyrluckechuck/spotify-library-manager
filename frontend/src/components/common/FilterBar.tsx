import React from 'react';
import { SearchInput } from '../ui/SearchInput';
import { PageSizeSelector } from '../ui/PageSizeSelector';

interface FilterBarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  pageSize: number;
  onPageSizeChange: (size: number) => void;
  totalCount: number;
  currentCount: number;
  children?: React.ReactNode;
  searchPlaceholder?: string;
  className?: string;
}

export function FilterBar({
  searchQuery,
  onSearchChange,
  pageSize,
  onPageSizeChange,
  totalCount,
  currentCount,
  children,
  searchPlaceholder = 'Search...',
  className = '',
}: FilterBarProps) {
  return (
    <div className={`flex items-center justify-between ${className}`}>
      <div className='flex items-center gap-3'>
        <h1 className='text-2xl font-semibold'>
          {totalCount > 0 ? `${currentCount} of ${totalCount}` : '0'}
        </h1>
        {children}
      </div>
      <div className='flex items-center gap-4'>
        <SearchInput
          placeholder={searchPlaceholder}
          onSearch={onSearchChange}
          initialValue={searchQuery}
          className='w-64'
        />
        <PageSizeSelector
          pageSize={pageSize}
          onPageSizeChange={onPageSizeChange}
        />
        {totalCount > currentCount && (
          <span className='text-sm text-gray-500'>
            Showing first {currentCount} items
          </span>
        )}
      </div>
    </div>
  );
}
