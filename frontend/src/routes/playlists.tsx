import { createFileRoute } from '@tanstack/react-router';
import { useQuery, useMutation } from '@apollo/client';
import { GetPlaylistsDocument, TogglePlaylistDocument } from '../types/generated/graphql';
import type { TrackedPlaylist } from '../types/generated/graphql';
import { useState } from 'react';

// Components
import { PlaylistFilters } from '../components/playlists/PlaylistFilters';
import { PlaylistsTable } from '../components/playlists/PlaylistsTable';
import { PageSizeSelector } from '../components/ui/PageSizeSelector';
import { LoadMoreButton } from '../components/ui/LoadMoreButton';
import type { PlaylistSortField } from '../components/playlists/PlaylistsTable';

type SortDirection = 'asc' | 'desc';

function Playlists() {
  const [enabledFilter, setEnabledFilter] = useState<'all' | 'enabled' | 'disabled'>('all');
  const [pageSize, setPageSize] = useState(50);
  const [sortField, setSortField] = useState<PlaylistSortField>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  const { data, loading, error, refetch, fetchMore } = useQuery(GetPlaylistsDocument, {
    variables: {
      enabled: enabledFilter === 'all' ? undefined : enabledFilter === 'enabled',
      first: pageSize,
      sortBy: sortField,
      sortDirection: sortDirection
    },
    notifyOnNetworkStatusChange: true,
    fetchPolicy: 'cache-and-network'
  });

  const [togglePlaylist] = useMutation(TogglePlaylistDocument, {
    onCompleted: (data) => {
      if (data.togglePlaylist.success) {
        refetch();
      }
    }
  });

  const handleEnabledFilterChange = (newFilter: 'all' | 'enabled' | 'disabled') => {
    setEnabledFilter(newFilter);
    refetch({
      enabled: newFilter === 'all' ? undefined : newFilter === 'enabled',
      first: pageSize,
      after: undefined,
      sortBy: sortField,
      sortDirection: sortDirection
    });
  };

  const handleSort = (field: PlaylistSortField) => {
    let newDirection: SortDirection = 'asc';

    if (sortField === field && sortDirection === 'asc') {
      newDirection = 'desc';
    }

    setSortField(field);
    setSortDirection(newDirection);

    refetch({
      enabled: enabledFilter === 'all' ? undefined : enabledFilter === 'enabled',
      first: pageSize,
      after: undefined,
      sortBy: field,
      sortDirection: newDirection
    });
  };

  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize);
    refetch({
      enabled: enabledFilter === 'all' ? undefined : enabledFilter === 'enabled',
      first: newPageSize,
      after: undefined,
      sortBy: sortField,
      sortDirection: sortDirection
    });
  };

  const handleToggleEnabled = async (playlist: TrackedPlaylist) => {
    try {
      await togglePlaylist({ variables: { playlistId: playlist.id } });
    } catch (error) {
      console.error('Error toggling playlist enabled status:', error);
    }
  };

  const handleLoadMore = () => {
    if (data?.playlists.pageInfo.hasNextPage) {
      fetchMore({
        variables: {
          after: data.playlists.pageInfo.endCursor,
        },
        updateQuery: (prevResult, { fetchMoreResult }) => {
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

  if (loading && !data) {
    return (
      <section>
        <h1 className="text-2xl font-semibold mb-4">Playlists</h1>
        <div className="bg-white rounded shadow p-6 min-h-[200px] flex items-center justify-center text-gray-400">
          Loading playlists...
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section>
        <h1 className="text-2xl font-semibold mb-4">Playlists</h1>
        <div className="bg-white rounded shadow p-6 min-h-[200px] flex items-center justify-center text-red-500">
          Error loading playlists: {error.message}
        </div>
      </section>
    );
  }

  const playlists = data?.playlists.edges || [];
  const totalCount = data?.playlists.totalCount || 0;
  const pageInfo = data?.playlists.pageInfo;

  return (
    <section>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold">
          Playlists ({playlists.length} of {totalCount})
        </h1>
        <div className="flex items-center gap-4">
          <PageSizeSelector 
            pageSize={pageSize}
            onPageSizeChange={handlePageSizeChange}
          />
          {totalCount > playlists.length && (
            <span className="text-sm text-gray-500">
              Showing first {playlists.length} playlists
            </span>
          )}
        </div>
      </div>

      <PlaylistFilters 
        currentEnabledFilter={enabledFilter}
        onEnabledFilterChange={handleEnabledFilterChange}
      />

      <PlaylistsTable
        playlists={playlists}
        sortField={sortField}
        sortDirection={sortDirection}
        onSort={handleSort}
        onToggleEnabled={handleToggleEnabled}
        loading={loading}
      />

      <LoadMoreButton
        hasNextPage={!!pageInfo?.hasNextPage}
        loading={loading}
        remainingCount={totalCount - playlists.length}
        onLoadMore={handleLoadMore}
      />
    </section>
  );
}

export const Route = createFileRoute('/playlists')({
  component: Playlists,
}); 