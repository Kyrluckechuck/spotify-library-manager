import { createFileRoute } from '@tanstack/react-router';
import { useQuery } from '@apollo/client';
import { useState, useMemo } from 'react';
import { GetSongsDocument } from '../types/generated/graphql';
import type { Song } from '../types/common';

// Layout & shared components
import { PageContainer } from '../components/layout/PageContainer';
import { PageHeader } from '../components/layout/PageHeader';
import { DataTable } from '../components/common/DataTable';
import { InlineSpinner } from '../components/ui/InlineSpinner';
import { FilterBar } from '../components/common/FilterBar';

// Songs components
import { SongsTable } from '../components/songs/SongsTable';
import type { SortField } from '../components/songs/SongsTable';

function Songs() {
  const { artistId: artistIdFromSearch, search: initialSearch } =
    Route.useSearch() as { artistId?: number; search?: string };
  // State management
  const [pageSize, setPageSize] = useState(50);
  const [sortField, setSortField] = useState<SortField>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [searchQuery, setSearchQuery] = useState(initialSearch || '');
  const [filter, setFilter] = useState<
    'all' | 'downloaded' | 'failed' | 'unavailable'
  >('all');

  // Memoize query variables to prevent unnecessary re-renders
  const queryVariables = useMemo(
    () => ({
      first: pageSize,
      artistId: artistIdFromSearch || undefined,
      sortBy: sortField,
      sortDirection: sortDirection,
      search: searchQuery || undefined,
    }),
    [pageSize, sortField, sortDirection, searchQuery, artistIdFromSearch]
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

  // Apply frontend filtering for failed songs
  const songs = useMemo(() => {
    const allSongs = data?.songs.edges || [];
    if (filter === 'failed') {
      return allSongs.filter((song: Song) => song.failedCount > 0);
    }
    return allSongs;
  }, [data?.songs.edges, filter]);
  const totalCount = data?.songs.totalCount || 0;
  const pageInfo = data?.songs.pageInfo;
  const isRefetching = networkStatus === 3;

  return (
    <PageContainer>
      <PageHeader
        title='Songs'
        subtitle='Manage and track your downloaded songs'
      >
        {isRefetching && <InlineSpinner label='Updating...' />}
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
        emptyMessage='No songs found'
        loadingMessage='Loading songs...'
        errorMessage='Error loading songs'
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
  validateSearch: (search: Record<string, unknown>) => ({
    artistId: search.artistId as number | undefined,
    search: (search.search as string | undefined) || undefined,
  }),
});
