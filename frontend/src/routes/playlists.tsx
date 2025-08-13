import { createFileRoute } from '@tanstack/react-router';
import { useMutation, useQuery, useApolloClient } from '@apollo/client';
import {
  GetPlaylistsDocument,
  TogglePlaylistDocument,
  SyncPlaylistDocument,
  TogglePlaylistAutoTrackDocument,
  type GetPlaylistsQuery,
} from '../types/generated/graphql';
import type { Playlist } from '../types/generated/graphql';
import { useState, useMemo, useCallback } from 'react';

import { PlaylistModal } from '../components/ui/PlaylistModal';

// Components
import { PlaylistFilters } from '../components/playlists/PlaylistFilters';
import { PlaylistsTable } from '../components/playlists/PlaylistsTable';
import { PageSizeSelector } from '../components/ui/PageSizeSelector';
import { InlineSpinner } from '../components/ui/InlineSpinner';
import { PageSpinner } from '../components/ui/PageSpinner';
import { ErrorBanner } from '../components/ui/ErrorBanner';
import { useRequestState } from '../hooks/useRequestState';
import { LoadMoreButton } from '../components/ui/LoadMoreButton';
import { SearchInput } from '../components/ui/SearchInput';
import type { PlaylistSortField } from '../components/playlists/PlaylistsTable';

type SortDirection = 'asc' | 'desc';

function Playlists() {
  const [filter, setFilter] = useState<'all' | 'enabled' | 'disabled'>('all');
  const [pageSize, setPageSize] = useState(50);
  const [sortField, setSortField] = useState<PlaylistSortField>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [searchQuery, setSearchQuery] = useState('');

  // Modal states
  const [showPlaylistModal, setShowPlaylistModal] = useState(false);
  const [editingPlaylist, setEditingPlaylist] = useState<Playlist | null>(null);

  const client = useApolloClient();

  // Memoize query variables to prevent unnecessary re-renders
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

  const { data, loading, error, fetchMore, networkStatus } = useQuery(
    GetPlaylistsDocument,
    {
      variables: queryVariables,
      fetchPolicy: 'cache-and-network',
      nextFetchPolicy: 'cache-first',
      notifyOnNetworkStatusChange: true,
      pollInterval: 0,
      errorPolicy: 'all',
      // Keep previous data while loading new data
      returnPartialData: true,
      onCompleted: data => {
        // Pre-fetch other filter combinations
        if (data && networkStatus !== 3) {
          // Not refetching
          const baseVariables = {
            first: pageSize,
            sortBy: sortField,
            sortDirection: sortDirection,
            search: searchQuery || undefined,
          };

          // Pre-fetch enabled and disabled filters
          ['enabled', 'disabled'].forEach(enabledFilter => {
            const variables = {
              ...baseVariables,
              enabled: enabledFilter === 'enabled' ? true : false,
            };

            client
              .query({
                query: GetPlaylistsDocument,
                variables,
                fetchPolicy: 'cache-first',
              })
              .catch(() => {
                // Ignore pre-fetch errors
              });
          });
        }
      },
    }
  );

  const [togglePlaylist] = useMutation(TogglePlaylistDocument);
  const [syncPlaylist] = useMutation(SyncPlaylistDocument);
  const [togglePlaylistAutoTrack] = useMutation(
    TogglePlaylistAutoTrackDocument
  );
  const [mutatingIds, setMutatingIds] = useState<Set<number>>(new Set());
  const [errorById, setErrorById] = useState<Record<number, string>>({});

  const handleEnabledFilterChange = (
    newFilter: 'all' | 'enabled' | 'disabled'
  ) => {
    setFilter(newFilter);

    // Pre-fetch data for the new filter
    const newVariables = {
      ...queryVariables,
      enabled: newFilter === 'all' ? undefined : newFilter === 'enabled',
    };

    // Pre-fetch without blocking the UI
    client
      .query({
        query: GetPlaylistsDocument,
        variables: newVariables,
        fetchPolicy: 'cache-first',
      })
      .catch(() => {
        // Ignore pre-fetch errors
      });
  };

  const handleSort = (field: PlaylistSortField) => {
    let newDirection: SortDirection = 'asc';

    if (sortField === field && sortDirection === 'asc') {
      newDirection = 'desc';
    }

    setSortField(field);
    setSortDirection(newDirection);

    // Pre-fetch data for the new sort
    const newVariables = {
      ...queryVariables,
      sortBy: field,
      sortDirection: newDirection,
    };

    client
      .query({
        query: GetPlaylistsDocument,
        variables: newVariables,
        fetchPolicy: 'cache-first',
      })
      .catch(() => {
        // Ignore pre-fetch errors
      });
  };

  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize);

    // Pre-fetch data for the new page size
    const newVariables = {
      ...queryVariables,
      first: newPageSize,
    };

    client
      .query({
        query: GetPlaylistsDocument,
        variables: newVariables,
        fetchPolicy: 'cache-first',
      })
      .catch(() => {
        // Ignore pre-fetch errors
      });
  };

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  const handleFilterHover = useCallback(
    (hoverFilter: 'all' | 'enabled' | 'disabled') => {
      // Pre-fetch data on hover
      const newVariables = {
        ...queryVariables,
        enabled: hoverFilter === 'all' ? undefined : hoverFilter === 'enabled',
      };

      client
        .query({
          query: GetPlaylistsDocument,
          variables: newVariables,
          fetchPolicy: 'cache-first',
        })
        .catch(() => {
          // Ignore pre-fetch errors
        });
    },
    [queryVariables, client]
  );

  const handleTogglePlaylist = async (playlist: Playlist) => {
    try {
      setErrorById(prev => ({ ...prev, [playlist.id]: '' }));
      setMutatingIds(prev => new Set(prev).add(playlist.id));
      await togglePlaylist({ variables: { playlistId: playlist.id } });
    } catch (error) {
      setErrorById(prev => ({
        ...prev,
        [playlist.id]: error instanceof Error ? error.message : 'Action failed',
      }));
    }
    setMutatingIds(prev => {
      const next = new Set(prev);
      next.delete(playlist.id);
      return next;
    });
  };

  const handleSyncPlaylist = async (playlistId: number) => {
    try {
      setErrorById(prev => ({ ...prev, [playlistId]: '' }));
      setMutatingIds(prev => new Set(prev).add(playlistId));
      await syncPlaylist({ variables: { playlistId } });
    } catch (error) {
      setErrorById(prev => ({
        ...prev,
        [playlistId]: error instanceof Error ? error.message : 'Sync failed',
      }));
    }
    setMutatingIds(prev => {
      const next = new Set(prev);
      next.delete(playlistId);
      return next;
    });
  };

  const handleToggleAutoTrack = async (playlist: Playlist) => {
    try {
      setErrorById(prev => ({ ...prev, [playlist.id]: '' }));
      setMutatingIds(prev => new Set(prev).add(playlist.id));
      await togglePlaylistAutoTrack({
        variables: { playlistId: playlist.id },
      });
    } catch (error) {
      setErrorById(prev => ({
        ...prev,
        [playlist.id]: error instanceof Error ? error.message : 'Action failed',
      }));
    }
    setMutatingIds(prev => {
      const next = new Set(prev);
      next.delete(playlist.id);
      return next;
    });
  };

  const handleEditPlaylist = useCallback((playlist: Playlist) => {
    setEditingPlaylist(playlist);
    setShowPlaylistModal(true);
  }, []);

  const handleClosePlaylistModal = useCallback(() => {
    setShowPlaylistModal(false);
    setEditingPlaylist(null);
  }, []);

  const handleLoadMore = () => {
    if (data?.playlists.pageInfo.hasNextPage) {
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

  // Subtle loading indicator for filter changes
  const { isRefreshing: isRefetching, isInitial: isInitialLoading } =
    useRequestState(networkStatus);

  // Only show loading state on initial load
  if (isInitialLoading && !data) {
    return (
      <section>
        <h1 className='text-2xl font-semibold mb-4'>Playlists</h1>
        <PageSpinner message='Loading playlists...' />
      </section>
    );
  }

  if (error) {
    return (
      <section>
        <h1 className='text-2xl font-semibold mb-4'>Playlists</h1>
        <ErrorBanner title='Error loading playlists' message={error.message} />
      </section>
    );
  }

  const playlists = data?.playlists.edges || [];
  const totalCount = data?.playlists.totalCount || 0;
  const pageInfo = data?.playlists.pageInfo;

  return (
    <section>
      <div className='flex items-center justify-between mb-4'>
        <div className='flex items-center gap-3'>
          <h1 className='text-2xl font-semibold'>
            Playlists ({playlists.length} of {totalCount})
          </h1>
          {isRefetching && <InlineSpinner label='Updating...' />}
        </div>
        <div className='flex items-center gap-4'>
          <button
            onClick={() => setShowPlaylistModal(true)}
            className='px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors'
          >
            Create Playlist
          </button>

          <SearchInput
            placeholder='Search playlists...'
            onSearch={handleSearch}
            className='w-64'
          />
          <PageSizeSelector
            pageSize={pageSize}
            onPageSizeChange={handlePageSizeChange}
          />
          {totalCount > playlists.length && (
            <span className='text-sm text-gray-500'>
              Showing first {playlists.length} playlists
            </span>
          )}
        </div>
      </div>

      <PlaylistFilters
        currentEnabledFilter={filter}
        onEnabledFilterChange={handleEnabledFilterChange}
        onFilterHover={handleFilterHover}
      />

      <div className='relative'>
        <PlaylistsTable
          playlists={playlists}
          sortField={sortField}
          sortDirection={sortDirection}
          onSort={handleSort}
          onToggleEnabled={handleTogglePlaylist}
          onToggleAutoTrack={handleToggleAutoTrack}
          onSyncPlaylist={handleSyncPlaylist}
          onEditPlaylist={handleEditPlaylist}
          loading={loading}
          mutatingIds={mutatingIds}
          errorById={errorById}
        />
        {isRefetching && (
          <div className='absolute inset-0 bg-white/60 flex items-center justify-center pointer-events-none'>
            <InlineSpinner label='Updating...' />
          </div>
        )}
      </div>

      <LoadMoreButton
        hasNextPage={!!pageInfo?.hasNextPage}
        loading={loading}
        remainingCount={totalCount - playlists.length}
        onLoadMore={handleLoadMore}
      />

      {/* Modals */}

      <PlaylistModal
        isOpen={showPlaylistModal}
        onClose={handleClosePlaylistModal}
        playlist={editingPlaylist}
        mode={editingPlaylist ? 'edit' : 'create'}
      />
    </section>
  );
}

export const Route = createFileRoute('/playlists')({
  component: Playlists,
});
