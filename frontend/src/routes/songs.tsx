import { createFileRoute } from '@tanstack/react-router';
import { useQuery } from '@apollo/client';
import { useState, useMemo } from 'react';
import { GetSongsDocument } from '../types/generated/graphql';

// Shared Components
import { PageContainer } from '../components/layout/PageContainer';
import { PageHeader } from '../components/layout/PageHeader';
import { DataTable } from '../components/common/DataTable';
import { FilterBar } from '../components/common/FilterBar';

// Specific Components
import { SongsTable } from '../components/songs/SongsTable';
import type { SortField } from '../components/songs/SongsTable';

function Songs() {
  // State management
  const [pageSize, setPageSize] = useState(50);
  const [sortField, setSortField] = useState<SortField>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [searchQuery, setSearchQuery] = useState('');
  const [filter, setFilter] = useState<
    'all' | 'downloaded' | 'failed' | 'unavailable'
  >('all');

  // Memoize query variables to prevent unnecessary re-renders
  const queryVariables = useMemo(
    () => ({
      first: pageSize,
      sortBy: sortField,
      sortDirection: sortDirection,
      search: searchQuery || undefined,
    }),
    [pageSize, sortField, sortDirection, searchQuery]
  );

  const queryVariablesWithFilter = useMemo(
    () => ({
      ...queryVariables,
      downloaded: filter === 'all' ? undefined : filter === 'downloaded',
      unavailable: filter === 'unavailable' ? true : undefined,
    }),
    [queryVariables, filter]
  );

  const { data, loading, error, fetchMore, networkStatus } = useQuery(
    GetSongsDocument,
    {
      variables: queryVariablesWithFilter,
      fetchPolicy: 'cache-and-network',
      nextFetchPolicy: 'cache-first',
      notifyOnNetworkStatusChange: true,
      pollInterval: 0,
      errorPolicy: 'all',
      returnPartialData: true,
    }
  );

  const handleFilterChange = (
    newFilter: 'all' | 'downloaded' | 'failed' | 'unavailable'
  ) => {
    setFilter(newFilter);
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const handleLoadMore = () => {
    if (data?.songs.pageInfo.hasNextPage) {
      fetchMore({
        variables: {
          ...queryVariablesWithFilter,
          after: data.songs.pageInfo.endCursor,
        },
      });
    }
  };

  const allSongs = data?.songs.edges || [];

  // Apply frontend filtering for failed songs
  const songs = useMemo(() => {
    if (filter === 'failed') {
      return allSongs.filter((song: any) => song.failedCount > 0);
    }
    return allSongs;
  }, [allSongs, filter]);
  const totalCount = data?.songs.totalCount || 0;
  const pageInfo = data?.songs.pageInfo;
  const isRefetching = networkStatus === 3;

  return (
    <PageContainer>
      <PageHeader
        title='Songs'
        subtitle='Manage and track your downloaded songs'
      >
        {isRefetching && (
          <div className='flex items-center gap-2 text-sm text-gray-500'>
            <div className='w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin' />
            <span>Updating...</span>
          </div>
        )}
      </PageHeader>

      <FilterBar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        pageSize={pageSize}
        onPageSizeChange={setPageSize}
        totalCount={totalCount}
        currentCount={songs.length}
        searchPlaceholder='Search songs...'
      />

      <div className='flex gap-4 mb-6'>
        <button
          onClick={() => handleFilterChange('all')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            filter === 'all'
              ? 'bg-blue-100 text-blue-800'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All Songs
        </button>
        <button
          onClick={() => handleFilterChange('downloaded')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            filter === 'downloaded'
              ? 'bg-green-100 text-green-800'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Downloaded
        </button>
        <button
          onClick={() => handleFilterChange('failed')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            filter === 'failed'
              ? 'bg-yellow-100 text-yellow-800'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Failed
        </button>
        <button
          onClick={() => handleFilterChange('unavailable')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            filter === 'unavailable'
              ? 'bg-red-100 text-red-800'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Unavailable
        </button>
      </div>

      <DataTable
        data={songs}
        loading={loading}
        error={error}
        totalCount={totalCount}
        pageSize={pageSize}
        hasNextPage={!!pageInfo?.hasNextPage}
        onLoadMore={handleLoadMore}
      >
        <SongsTable
          songs={songs}
          sortField={sortField}
          sortDirection={sortDirection}
          onSort={handleSort}
          loading={loading}
        />
      </DataTable>
    </PageContainer>
  );
}

export const Route = createFileRoute('/songs')({
  component: Songs,
});
