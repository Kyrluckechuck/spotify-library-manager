import { useState, useMemo, useCallback } from 'react';
import { useMutation, useQuery } from '@apollo/client/react';
import {
  GetPlaylistsDocument,
  TogglePlaylistDocument,
  TogglePlaylistAutoTrackDocument,
  SyncPlaylistDocument,
  ForceSyncPlaylistDocument,
  DownloadAllPlaylistsDocument,
  DeletePlaylistDocument,
  type Playlist,
  type GetPlaylistsQuery,
} from '../types/generated/graphql';
import { useToast } from '../components/ui/useToast';
import { useMutationState, useMutationLoadingState } from './useMutationState';
import { useRequestState } from './useRequestState';
import {
  usePrefetchFilters,
  generateFilterCombinations,
} from './usePrefetchFilters';
import { useQueryPrefetch } from './useQueryPrefetch';
import type { PlaylistSortField } from '../components/playlists/PlaylistsTable';
import type { SortDirection, PlaylistEnabledFilter } from '../types/shared';

export function usePlaylistsPage() {
  const toast = useToast();

  // State
  const [filter, setFilter] = useState<PlaylistEnabledFilter>('all');
  const [pageSize, setPageSize] = useState(50);
  const [sortField, setSortField] = useState<PlaylistSortField>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [searchQuery, setSearchQuery] = useState('');
  const [showPlaylistModal, setShowPlaylistModal] = useState(false);
  const [editingPlaylist, setEditingPlaylist] = useState<Playlist | null>(null);

  // Memoize query variables
  const queryVariables = useMemo(
    () => ({
      enabled: filter === 'all' ? undefined : filter === 'enabled',
      first: pageSize,
      sortBy: sortField,
      sortDirection: sortDirection,
      search: searchQuery || undefined,
    }),
    [filter, pageSize, sortField, sortDirection, searchQuery]
  );

  // Data fetching
  const { data, loading, error, fetchMore, networkStatus } = useQuery(
    GetPlaylistsDocument,
    {
      variables: queryVariables,
      fetchPolicy: 'cache-and-network',
      notifyOnNetworkStatusChange: true,
      pollInterval: 0,
      errorPolicy: 'all',
    }
  );

  // Mutations
  const [togglePlaylist] = useMutation(TogglePlaylistDocument);
  const [togglePlaylistAutoTrack] = useMutation(
    TogglePlaylistAutoTrackDocument
  );
  const [syncPlaylist] = useMutation(SyncPlaylistDocument);
  const [forceSyncPlaylist] = useMutation(ForceSyncPlaylistDocument);
  const [downloadAllPlaylists] = useMutation(DownloadAllPlaylistsDocument);
  const [deletePlaylist] = useMutation(DeletePlaylistDocument);

  // Mutation states
  const {
    mutatingIds: enabledMutatingIds,
    pulseIds: enabledPulseIds,
    handleMutation: handleEnabledMutation,
    errorById,
  } = useMutationState();

  const {
    mutatingIds: autoMutatingIds,
    pulseIds: autoPulseIds,
    handleMutation: handleAutoMutation,
  } = useMutationState();

  const {
    loadingIds: syncMutatingIds,
    startLoading: startSync,
    stopLoading: stopSync,
  } = useMutationLoadingState();

  const {
    loadingIds: forceSyncMutatingIds,
    startLoading: startForceSync,
    stopLoading: stopForceSync,
  } = useMutationLoadingState();

  const {
    loadingIds: deleteMutatingIds,
    startLoading: startDelete,
    stopLoading: stopDelete,
  } = useMutationLoadingState();

  // Prefetching setup
  const createPrefetchHandler = useQueryPrefetch(
    GetPlaylistsDocument,
    queryVariables
  );

  const baseVariables = useMemo(
    () => ({
      first: pageSize,
      sortBy: sortField,
      sortDirection: sortDirection,
      search: searchQuery || undefined,
    }),
    [pageSize, sortField, sortDirection, searchQuery]
  );

  const filterCombinations = useMemo(
    () =>
      generateFilterCombinations({
        enabled: [true, false],
      }),
    []
  );

  usePrefetchFilters({
    query: GetPlaylistsDocument,
    baseVariables,
    filterCombinations,
    enabled: !!data,
    networkStatus,
  });

  // Handlers
  const handleEnabledFilterChange = createPrefetchHandler(
    setFilter,
    (newFilter: PlaylistEnabledFilter) => ({
      enabled: newFilter === 'all' ? undefined : newFilter === 'enabled',
    })
  );

  const handlePageSizeChange = createPrefetchHandler(setPageSize, newSize => ({
    first: newSize,
  }));

  const handleSort = (field: PlaylistSortField) => {
    const newDirection: SortDirection =
      sortField === field && sortDirection === 'asc' ? 'desc' : 'asc';

    setSortField(field);
    setSortDirection(newDirection);

    createPrefetchHandler(null, () => ({
      sortBy: field,
      sortDirection: newDirection,
    }))(field);
  };

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  // Prefetch-only handler for hover (no state update)
  const handleFilterHover = createPrefetchHandler(
    null,
    (hoverFilter: PlaylistEnabledFilter) => ({
      enabled: hoverFilter === 'all' ? undefined : hoverFilter === 'enabled',
    })
  );

  const handleTogglePlaylist = async (playlist: Playlist) => {
    await handleEnabledMutation(
      playlist.id,
      async () => {
        await togglePlaylist({ variables: { playlistId: playlist.id } });
        toast.success(`Playlist ${playlist.enabled ? 'disabled' : 'enabled'}`);
      },
      { withPulse: true }
    );
  };

  const handleSyncPlaylist = async (playlistId: number) => {
    try {
      startSync(playlistId);
      await syncPlaylist({ variables: { playlistId } });
      toast.success('Playlist synced');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Sync failed');
    } finally {
      stopSync(playlistId);
    }
  };

  const handleForceSyncPlaylist = async (playlistId: number) => {
    try {
      startForceSync(playlistId);
      await forceSyncPlaylist({ variables: { playlistId } });
      toast.success('Playlist force sync started');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Force sync failed');
    } finally {
      stopForceSync(playlistId);
    }
  };

  const handleDeletePlaylist = async (
    playlistId: number,
    playlistName: string
  ) => {
    if (!window.confirm(`Are you sure you want to delete "${playlistName}"?`)) {
      return;
    }

    try {
      startDelete(playlistId);
      const result = await deletePlaylist({
        variables: { playlistId },
        refetchQueries: [
          { query: GetPlaylistsDocument, variables: queryVariables },
        ],
      });

      if (result.data?.deletePlaylist?.success) {
        toast.success(result.data.deletePlaylist.message || 'Playlist deleted');
      } else {
        toast.error(result.data?.deletePlaylist?.message || 'Delete failed');
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Delete failed');
    } finally {
      stopDelete(playlistId);
    }
  };

  const handleToggleAutoTrack = async (playlist: Playlist) => {
    await handleAutoMutation(
      playlist.id,
      async () => {
        await togglePlaylistAutoTrack({
          variables: { playlistId: playlist.id },
        });
        toast.success(
          `Track Artists ${playlist.autoTrackArtists ? 'disabled' : 'enabled'}`
        );
      },
      { withPulse: true }
    );
  };

  const handleEditPlaylist = useCallback((playlist: Playlist) => {
    setEditingPlaylist(playlist);
    setShowPlaylistModal(true);
  }, []);

  const handleClosePlaylistModal = useCallback(() => {
    setShowPlaylistModal(false);
    setEditingPlaylist(null);
  }, []);

  const handleCreatePlaylist = useCallback(() => {
    setShowPlaylistModal(true);
  }, []);

  const handleDownloadAllPlaylists = async () => {
    try {
      const result = await downloadAllPlaylists();

      if (result.data?.downloadAllPlaylists?.success) {
        toast.success(
          result.data.downloadAllPlaylists.message ||
            'Download started for all enabled playlists'
        );
      } else {
        const errorMessage =
          result.data?.downloadAllPlaylists?.message || 'Download failed';
        toast.error(errorMessage);
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Download failed';
      toast.error(errorMessage);
    }
  };

  const handleLoadMore = () => {
    if (data?.playlists?.pageInfo?.hasNextPage) {
      fetchMore({
        variables: {
          after: data.playlists.pageInfo.endCursor,
        },
        updateQuery: (
          prevResult: GetPlaylistsQuery,
          { fetchMoreResult }: { fetchMoreResult?: GetPlaylistsQuery }
        ) => {
          if (!fetchMoreResult) return prevResult;

          return {
            playlists: {
              ...fetchMoreResult.playlists,
              edges: [
                ...prevResult.playlists.edges,
                ...fetchMoreResult.playlists.edges,
              ],
            },
          };
        },
      });
    }
  };

  // Derived state
  const playlists = data?.playlists?.edges || [];
  const totalCount = data?.playlists?.totalCount || 0;
  const pageInfo = data?.playlists?.pageInfo;
  const { isRefreshing, isInitial: isInitialLoading } =
    useRequestState(networkStatus);

  return {
    // Data
    playlists,
    totalCount,
    pageInfo,
    loading,
    error,
    isRefreshing,
    isInitialLoading,

    // Filters & sorting
    filter,
    pageSize,
    sortField,
    sortDirection,
    searchQuery,

    // Modal state
    showPlaylistModal,
    editingPlaylist,

    // Mutation states
    enabledMutatingIds,
    enabledPulseIds,
    autoMutatingIds,
    autoPulseIds,
    syncMutatingIds,
    forceSyncMutatingIds,
    deleteMutatingIds,
    errorById,

    // Handlers
    handleEnabledFilterChange,
    handlePageSizeChange,
    handleSort,
    handleSearch,
    handleFilterHover,
    handleTogglePlaylist,
    handleSyncPlaylist,
    handleForceSyncPlaylist,
    handleDeletePlaylist,
    handleToggleAutoTrack,
    handleEditPlaylist,
    handleClosePlaylistModal,
    handleCreatePlaylist,
    handleDownloadAllPlaylists,
    handleLoadMore,
  };
}
