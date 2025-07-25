import { createFileRoute } from '@tanstack/react-router';
import { useQuery } from '@apollo/client';
import { GetSongsDocument } from '../types/generated/graphql';
import { useState } from 'react';

// Components
import { SongFilters } from '../components/songs/SongFilters';
import { SongsTable } from '../components/songs/SongsTable';
import { PageSizeSelector } from '../components/ui/PageSizeSelector';
import { LoadMoreButton } from '../components/ui/LoadMoreButton';
import type { SongSortField } from '../components/songs/SongsTable';

type SortDirection = 'asc' | 'desc';

function Songs() {
  const { artistId } = Route.useSearch();
  const [downloadFilter, setDownloadFilter] = useState<'all' | 'downloaded' | 'pending' | 'unavailable'>('all');
  const [pageSize, setPageSize] = useState(50);
  const [sortField, setSortField] = useState<SongSortField>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  // Convert filter to GraphQL parameters
  const getFilterParams = () => {
    const params: any = {};
    if (downloadFilter === 'downloaded') params.downloaded = true;
    else if (downloadFilter === 'pending') params.downloaded = false;
    else if (downloadFilter === 'unavailable') params.unavailable = true;
    return params;
  };

  const { data, loading, error, refetch, fetchMore } = useQuery(GetSongsDocument, {
    variables: {
      artistId: artistId || undefined,
      ...getFilterParams(),
      first: pageSize,
      sortBy: sortField,
      sortDirection: sortDirection
    },
    notifyOnNetworkStatusChange: true,
    fetchPolicy: 'cache-and-network'
  });

  const handleDownloadFilterChange = (newFilter: 'all' | 'downloaded' | 'pending' | 'unavailable') => {
    setDownloadFilter(newFilter);
    refetch({
      artistId: artistId || undefined,
      ...getFilterParams(),
      first: pageSize,
      after: undefined,
      sortBy: sortField,
      sortDirection: sortDirection
    });
  };

  const handleSort = (field: SongSortField) => {
    let newDirection: SortDirection = 'asc';

    if (sortField === field && sortDirection === 'asc') {
      newDirection = 'desc';
    }

    setSortField(field);
    setSortDirection(newDirection);

    refetch({
      artistId: artistId || undefined,
      ...getFilterParams(),
      first: pageSize,
      after: undefined,
      sortBy: field,
      sortDirection: newDirection
    });
  };

  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize);
    refetch({
      artistId: artistId || undefined,
      ...getFilterParams(),
      first: newPageSize,
      after: undefined,
      sortBy: sortField,
      sortDirection: sortDirection
    });
  };

  const handleLoadMore = () => {
    if (data?.songs.pageInfo.hasNextPage) {
      fetchMore({
        variables: {
          after: data.songs.pageInfo.endCursor,
        },
        updateQuery: (prevResult, { fetchMoreResult }) => {
          if (!fetchMoreResult) return prevResult;

          return {
            songs: {
              ...fetchMoreResult.songs,
              edges: [
                ...prevResult.songs.edges,
                ...fetchMoreResult.songs.edges,
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
        <h1 className="text-2xl font-semibold mb-4">Songs</h1>
        <div className="bg-white rounded shadow p-6 min-h-[200px] flex items-center justify-center text-gray-400">
          Loading songs...
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section>
        <h1 className="text-2xl font-semibold mb-4">Songs</h1>
        <div className="bg-white rounded shadow p-6 min-h-[200px] flex items-center justify-center text-red-500">
          Error loading songs: {error.message}
        </div>
      </section>
    );
  }

  const songs = data?.songs.edges || [];
  const totalCount = data?.songs.totalCount || 0;
  const pageInfo = data?.songs.pageInfo;

  // Build title based on filters
  let title = "Songs";
  if (artistId) title += ` (Artist ID: ${artistId})`;

  return (
    <section>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold">
          {title} ({songs.length} of {totalCount})
        </h1>
        <div className="flex items-center gap-4">
          <PageSizeSelector 
            pageSize={pageSize}
            onPageSizeChange={handlePageSizeChange}
          />
          {totalCount > songs.length && (
            <span className="text-sm text-gray-500">
              Showing first {songs.length} songs
            </span>
          )}
        </div>
      </div>

      <SongFilters 
        currentDownloadFilter={downloadFilter}
        onDownloadFilterChange={handleDownloadFilterChange}
      />

      <SongsTable
        songs={songs}
        sortField={sortField}
        sortDirection={sortDirection}
        onSort={handleSort}
        loading={loading}
      />

      <LoadMoreButton
        hasNextPage={!!pageInfo?.hasNextPage}
        loading={loading}
        remainingCount={totalCount - songs.length}
        onLoadMore={handleLoadMore}
      />
    </section>
  );
}

export const Route = createFileRoute('/songs')({
  component: Songs,
  validateSearch: (search: Record<string, unknown>) => ({
    artistId: search.artistId as number | undefined,
  }),
}); 