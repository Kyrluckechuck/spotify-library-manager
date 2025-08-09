import React from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { useMutation, useQuery, useApolloClient } from '@apollo/client';
import {
  GetArtistsDocument,
  TrackArtistDocument,
  UntrackArtistDocument,
  SyncArtistDocument,
} from '../types/generated/graphql';
import { useState, useMemo } from 'react';

// Layout & shared components
import { PageContainer } from '../components/layout/PageContainer';
import { PageHeader } from '../components/layout/PageHeader';
import { DataTable } from '../components/common/DataTable';
import { FilterBar } from '../components/common/FilterBar';

// Artists components
import { ArtistFilters } from '../components/artists/ArtistFilters';
import { ArtistsTable } from '../components/artists/ArtistsTable';

// Hooks
import { useDataTable } from '../hooks/useDataTable';
import type { SortField } from '../components/artists/ArtistsTable';

function Artists() {
  const client = useApolloClient();

  // Use custom hook for data table state management
  const {
    pageSize,
    sortField,
    sortDirection,
    searchQuery,
    setPageSize,
    setSearchQuery,
    queryVariables,
    handleSort,
  } = useDataTable<SortField>({
    initialPageSize: 50,
    initialSortField: null,
    initialSortDirection: 'asc',
    initialSearchQuery: '',
  });

  const [filter, setFilter] = useState<'all' | 'tracked' | 'untracked'>('all');

  // Memoize query variables to prevent unnecessary re-renders
  const queryVariablesWithFilter = useMemo(
    () => ({
      ...queryVariables,
      isTracked: filter === 'all' ? undefined : filter === 'tracked',
    }),
    [queryVariables, filter]
  );

  const { data, loading, error, fetchMore, networkStatus } = useQuery(
    GetArtistsDocument,
    {
      variables: queryVariablesWithFilter,
      fetchPolicy: 'cache-and-network',
      nextFetchPolicy: 'cache-first',
      notifyOnNetworkStatusChange: true,
      pollInterval: 0,
      errorPolicy: 'all',
      returnPartialData: true,
      onCompleted: data => {
        // Pre-fetch other filter combinations to eliminate future jitter
        if (data && networkStatus !== 3) {
          const baseVariables = {
            ...queryVariables,
          };

          // Pre-fetch tracked and untracked filters
          ['tracked', 'untracked'].forEach(trackedFilter => {
            const variables = {
              ...baseVariables,
              isTracked: trackedFilter === 'tracked' ? true : false,
            };

            client
              .query({
                query: GetArtistsDocument,
                variables,
                fetchPolicy: 'cache-first',
              })
              .catch(() => {
                // Silently handle errors for pre-fetching
              });
          });
        }
      },
    }
  );

  const [trackArtist] = useMutation(TrackArtistDocument);
  const [untrackArtist] = useMutation(UntrackArtistDocument);
  const [syncArtist] = useMutation(SyncArtistDocument);

  const handleFilterChange = (newFilter: 'all' | 'tracked' | 'untracked') => {
    setFilter(newFilter);

    // Pre-fetch data for the new filter to eliminate jitter
    const newVariables = {
      ...queryVariablesWithFilter,
      isTracked: newFilter === 'all' ? undefined : newFilter === 'tracked',
    };

    // Pre-fetch without blocking the UI
    client
      .query({
        query: GetArtistsDocument,
        variables: newVariables,
        fetchPolicy: 'cache-first',
      })
      .catch(() => {
        // Silently handle errors for pre-fetching
      });
  };

  const handleTrackToggle = async (artist: {
    id: number;
    isTracked: boolean;
  }) => {
    try {
      if (artist.isTracked) {
        await untrackArtist({ variables: { artistId: artist.id } });
      } else {
        await trackArtist({ variables: { artistId: artist.id } });
      }
    } catch (error) {
      console.error('Error toggling artist tracking:', error);
    }
  };

  const handleSyncArtist = async (artistId: number) => {
    try {
      await syncArtist({ variables: { artistId: artistId.toString() } });
    } catch (error) {
      console.error('Error syncing artist:', error);
    }
  };

  const handleLoadMore = () => {
    if (data?.artists.pageInfo.hasNextPage) {
      fetchMore({
        variables: {
          ...queryVariablesWithFilter,
          after: data.artists.pageInfo.endCursor,
        },
      });
    }
  };

  const artists = data?.artists.edges || [];
  const totalCount = data?.artists.totalCount || 0;
  const pageInfo = data?.artists.pageInfo;
  const isRefetching = networkStatus === 3;

  return (
    <PageContainer>
      <PageHeader
        title='Artists'
        subtitle='Manage and track your favorite artists'
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
        currentCount={artists.length}
        searchPlaceholder='Search artists...'
      />

      <ArtistFilters
        currentFilter={filter}
        onFilterChange={handleFilterChange}
      />

      <DataTable
        data={artists}
        loading={loading}
        error={error}
        totalCount={totalCount}
        pageSize={pageSize}
        hasNextPage={!!pageInfo?.hasNextPage}
        onLoadMore={handleLoadMore}
        emptyMessage='No artists found'
        loadingMessage='Loading artists...'
        errorMessage='Error loading artists'
      >
        <ArtistsTable
          artists={artists}
          sortField={sortField}
          sortDirection={sortDirection}
          onSort={handleSort}
          onTrackToggle={handleTrackToggle}
          onSyncArtist={handleSyncArtist}
          loading={loading}
        />
      </DataTable>
    </PageContainer>
  );
}

export const Route = createFileRoute('/artists')({
  component: Artists,
});
