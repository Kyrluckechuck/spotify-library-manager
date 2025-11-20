import { useState, useMemo, useEffect } from 'react';
import { useMutation, useQuery, useApolloClient } from '@apollo/client/react';
import {
  GetArtistsDocument,
  GetTaskHistoryDocument,
  TrackArtistDocument,
  UntrackArtistDocument,
  SyncArtistDocument,
  DownloadArtistDocument,
  SyncAllTrackedArtistsDocument,
  DownloadAllTrackedArtistsDocument,
  type Artist,
} from '../types/generated/graphql';
import { useToast } from '../components/ui/useToast';
import { useDataTable } from './useDataTable';
import { useMutationState, useMutationLoadingState } from './useMutationState';
import { useRequestState } from './useRequestState';
import type { SortField } from '../components/artists/ArtistsTable';

export function useArtistsPage() {
  const toast = useToast();
  const client = useApolloClient();

  // Table state management
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

  // Memoize query variables with filter
  const queryVariablesWithFilter = useMemo(
    () => ({
      ...queryVariables,
      isTracked: filter === 'all' ? undefined : filter === 'tracked',
    }),
    [queryVariables, filter]
  );

  // Query for running artist tasks to enable smart polling
  const { data: taskData } = useQuery(GetTaskHistoryDocument, {
    variables: {
      status: 'RUNNING',
      first: 100,
    },
    fetchPolicy: 'cache-first',
    pollInterval: 5000, // Poll every 5 seconds to detect active tasks
  });

  // Compute whether there are active artist-related tasks
  const hasActiveArtistTasks = useMemo(() => {
    const edges = taskData?.taskHistory?.edges || [];
    return edges.some(edge => {
      const task = edge.node;
      return (
        task.status === 'RUNNING' &&
        task.entityType === 'ARTIST' &&
        (task.type === 'SYNC' || task.type === 'DOWNLOAD')
      );
    });
  }, [taskData]);

  // Dynamic poll interval: 5s when tasks active, 0 (disabled) when idle
  const artistsPollInterval = hasActiveArtistTasks ? 5000 : 0;

  // Data fetching
  const { data, loading, error, fetchMore, networkStatus } = useQuery(
    GetArtistsDocument,
    {
      variables: queryVariablesWithFilter,
      fetchPolicy: 'cache-and-network',
      notifyOnNetworkStatusChange: true,
      pollInterval: artistsPollInterval,
      errorPolicy: 'all',
    }
  );

  // Pre-fetch other filter combinations to eliminate jitter
  useEffect(() => {
    if (data && networkStatus !== 3) {
      const baseVariables = { ...queryVariables };

      ['tracked', 'untracked'].forEach(trackedFilter => {
        const variables = {
          ...baseVariables,
          isTracked: trackedFilter === 'tracked',
        };

        client
          .query({
            query: GetArtistsDocument,
            variables,
            fetchPolicy: 'cache-first',
          })
          .catch(() => {
            // Silently handle pre-fetch errors
          });
      });
    }
  }, [data, networkStatus, queryVariables, client]);

  // Mutations
  const [trackArtist] = useMutation(TrackArtistDocument);
  const [untrackArtist] = useMutation(UntrackArtistDocument);
  const [syncArtist] = useMutation(SyncArtistDocument);
  const [downloadArtist] = useMutation(DownloadArtistDocument);
  const [syncAllTrackedArtists] = useMutation(SyncAllTrackedArtistsDocument);
  const [downloadAllTrackedArtists] = useMutation(
    DownloadAllTrackedArtistsDocument
  );

  // Mutation state management
  const { mutatingIds, pulseIds, errorById, handleMutation } =
    useMutationState();

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

  // Handlers
  const handleFilterChange = (newFilter: 'all' | 'tracked' | 'untracked') => {
    setFilter(newFilter);

    // Pre-fetch data for the new filter
    const newVariables = {
      ...queryVariablesWithFilter,
      isTracked: newFilter === 'all' ? undefined : newFilter === 'tracked',
    };

    client
      .query({
        query: GetArtistsDocument,
        variables: newVariables,
        fetchPolicy: 'cache-first',
      })
      .catch(() => {
        // Silently handle pre-fetch errors
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

  const handleSyncAllTrackedArtists = async () => {
    try {
      const result = await syncAllTrackedArtists();

      if (result.data?.syncAllTrackedArtists?.success) {
        toast.success(
          result.data.syncAllTrackedArtists.message ||
            'Sync started for all tracked artists'
        );
      } else {
        const errorMessage =
          result.data?.syncAllTrackedArtists?.message || 'Sync failed';
        toast.error(errorMessage);
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Sync failed';
      toast.error(errorMessage);
    }
  };

  const handleDownloadAllTrackedArtists = async () => {
    try {
      const result = await downloadAllTrackedArtists();

      if (result.data?.downloadAllTrackedArtists?.success) {
        toast.success(
          result.data.downloadAllTrackedArtists.message ||
            'Download started for all tracked artists'
        );
      } else {
        const errorMessage =
          result.data?.downloadAllTrackedArtists?.message || 'Download failed';
        toast.error(errorMessage);
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Download failed';
      toast.error(errorMessage);
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

  // Derived state
  const artists = (data?.artists?.edges as Artist[]) || [];
  const totalCount = data?.artists?.totalCount || 0;
  const pageInfo = data?.artists?.pageInfo;
  const { isRefreshing, isInitial: isInitialLoading } =
    useRequestState(networkStatus);

  return {
    // Data
    artists,
    totalCount,
    pageInfo,
    loading,
    error,
    isRefreshing,
    isInitialLoading,

    // Filters & sorting
    filter,
    searchQuery,
    pageSize,
    sortField,
    sortDirection,

    // Mutation states
    mutatingIds,
    pulseIds,
    errorById,
    syncMutatingIds,
    downloadMutatingIds,

    // Handlers
    handleFilterChange,
    setSearchQuery,
    setPageSize,
    handleSort,
    handleTrackToggle,
    handleSyncArtist,
    handleDownloadArtist,
    handleSyncAllTrackedArtists,
    handleDownloadAllTrackedArtists,
    handleLoadMore,
  };
}
