import React from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { useMutation, useQuery, useApolloClient } from '@apollo/client/react';
import {
  GetArtistsDocument,
  TrackArtistDocument,
  UntrackArtistDocument,
  SyncArtistDocument,
  DownloadArtistDocument,
} from '../types/generated/graphql';
import { useState, useMemo } from 'react';
import { InlineSpinner } from '../components/ui/InlineSpinner';
import { useRequestState } from '../hooks/useRequestState';

// Layout & shared components
import { PageContainer } from '../components/layout/PageContainer';
import { PageHeader } from '../components/layout/PageHeader';
import { DataTable } from '../components/common/DataTable';
import { FilterBar } from '../components/common/FilterBar';
import { useToast } from '../components/ui/useToast';

// Artists components
import { ArtistFilters } from '../components/artists/ArtistFilters';
import { ArtistsTable } from '../components/artists/ArtistsTable';

// Hooks
import { useDataTable } from '../hooks/useDataTable';
import {
  useMutationState,
  useMutationLoadingState,
} from '../hooks/useMutationState';
import type { SortField } from '../components/artists/ArtistsTable';

function Artists() {
  const toast = useToast();
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
    }
  );

  // Pre-fetch other filter combinations to eliminate future jitter
  useMemo(() => {
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
  }, [data, networkStatus, queryVariables, client]);

  const [trackArtist] = useMutation(TrackArtistDocument);
  const [untrackArtist] = useMutation(UntrackArtistDocument);
  const [syncArtist] = useMutation(SyncArtistDocument);
  const [downloadArtist] = useMutation(DownloadArtistDocument);

  // Track/untrack mutations with pulse animation
  const { mutatingIds, pulseIds, errorById, handleMutation } =
    useMutationState();

  // Separate loading states for sync and download actions
  const {
    loadingIds: syncMutatingIds,
    startLoading: startSync,
    stopLoading: stopSync,
  } = useMutationLoadingState();
  const {
    loadingIds: downloadMutatingIds,
    startLoading: startDownload,
    stopLoading: stopDownload,
  } = useMutationLoadingState();

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
    await handleMutation(
      artist.id,
      async () => {
        if (artist.isTracked) {
          await untrackArtist({ variables: { artistId: artist.id } });
          toast.success('Artist untracked');
        } else {
          await trackArtist({ variables: { artistId: artist.id } });
          toast.success('Artist tracked');
        }
      },
      { withPulse: true }
    );
  };

  const handleSyncArtist = async (artistId: number) => {
    try {
      startSync(artistId);
      await syncArtist({ variables: { artistId: artistId.toString() } });
      toast.success('Artist sync started');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Sync failed');
    } finally {
      stopSync(artistId);
    }
  };

  const handleDownloadArtist = async (artistId: number) => {
    try {
      startDownload(artistId);
      const result = await downloadArtist({
        variables: { artistId: artistId.toString() },
      });

      if (result.data?.downloadArtist?.success) {
        toast.success('Artist download started');
      } else {
        const errorMessage =
          result.data?.downloadArtist?.message || 'Download failed';
        toast.error(errorMessage);
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Download failed';
      toast.error(errorMessage);
    } finally {
      stopDownload(artistId);
    }
  };

  const handleLoadMore = () => {
    if (data?.artists?.pageInfo?.hasNextPage) {
      fetchMore({
        variables: {
          ...queryVariablesWithFilter,
          after: data.artists.pageInfo.endCursor,
        },
      });
    }
  };

  const artists = data?.artists?.edges || [];
  const totalCount = data?.artists?.totalCount || 0;
  const pageInfo = data?.artists?.pageInfo;
  const { isRefreshing: isRefetching } = useRequestState(networkStatus);

  return (
    <PageContainer>
      <PageHeader
        title='Artists'
        subtitle='Manage and track your favorite artists'
      >
        {isRefetching && <InlineSpinner label='Updating...' />}
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
          onDownloadArtist={handleDownloadArtist}
          loading={loading}
          mutatingIds={mutatingIds}
          syncMutatingIds={syncMutatingIds}
          downloadMutatingIds={downloadMutatingIds}
          errorById={errorById}
          pulseIds={pulseIds}
        />
      </DataTable>
    </PageContainer>
  );
}

export const Route = createFileRoute('/artists')({
  component: Artists,
});
