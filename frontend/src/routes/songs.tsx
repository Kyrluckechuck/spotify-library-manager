import { createFileRoute } from '@tanstack/react-router';
import { useQuery, useApolloClient } from '@apollo/client';
import {
  GetSongsDocument,
  GetArtistDocument,
  type GetSongsQuery,
} from '../types/generated/graphql';
import { useState, useMemo, useCallback } from 'react';

// Components
import { SongFilters } from '../components/songs/SongFilters';
import { SongsTable } from '../components/songs/SongsTable';
import { PageSizeSelector } from '../components/ui/PageSizeSelector';
import { LoadMoreButton } from '../components/ui/LoadMoreButton';
import { ArtistContext } from '../components/ui/ArtistContext';
import type { SongSortField } from '../components/songs/SongsTable';
import { SearchInput } from '../components/ui/SearchInput';

type SortDirection = 'asc' | 'desc';

function Songs() {
  const { artistId } = Route.useSearch();
  const [downloadFilter, setDownloadFilter] = useState<
    'all' | 'downloaded' | 'pending' | 'unavailable'
  >('all');
  const [pageSize, setPageSize] = useState(50);
  const [sortField, setSortField] = useState<SongSortField>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [searchQuery, setSearchQuery] = useState('');

  const client = useApolloClient();

  // Memoize query variables to prevent unnecessary re-renders
  const queryVariables = useMemo(() => {
    // Convert filter to GraphQL parameters
    const params: Record<string, boolean | undefined> = {};
    if (downloadFilter === 'downloaded') params.downloaded = true;
    else if (downloadFilter === 'pending') params.downloaded = false;
    else if (downloadFilter === 'unavailable') params.unavailable = true;

    return {
      artistId: artistId || undefined,
      ...params,
      first: pageSize,
      sortBy: sortField,
      sortDirection: sortDirection,
      search: searchQuery || undefined,
    };
  }, [
    artistId,
    downloadFilter,
    pageSize,
    sortField,
    sortDirection,
    searchQuery,
  ]);

  const { data, loading, error, fetchMore, networkStatus } = useQuery(
    GetSongsDocument,
    {
      variables: queryVariables,
      fetchPolicy: 'cache-and-network',
      nextFetchPolicy: 'cache-first',
      notifyOnNetworkStatusChange: true,
      pollInterval: 0, // No polling needed since we're not tracking frontend tasks
      errorPolicy: 'all',
      // Keep previous data while loading new data
      returnPartialData: true,
      onCompleted: data => {
        // Pre-fetch other filter combinations to eliminate future jitter
        if (data && networkStatus !== 3) {
          // Not refetching
          const baseVariables = {
            artistId: artistId || undefined,
            first: pageSize,
            sortBy: sortField,
            sortDirection: sortDirection,
            search: searchQuery || undefined,
          };

          // Pre-fetch download filter combinations
          ['downloaded', 'pending', 'unavailable'].forEach(downloadFilter => {
            const variables = {
              ...baseVariables,
              ...(downloadFilter === 'downloaded' ? { downloaded: true } : {}),
              ...(downloadFilter === 'pending' ? { downloaded: false } : {}),
              ...(downloadFilter === 'unavailable'
                ? { unavailable: true }
                : {}),
            };

            client
              .query({
                query: GetSongsDocument,
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

  // Get artist information if filtering by artist
  const { data: artistData } = useQuery(GetArtistDocument, {
    variables: { id: artistId ?? 0 },
    skip: !artistId,
    fetchPolicy: 'cache-first',
    nextFetchPolicy: 'cache-first',
    notifyOnNetworkStatusChange: false,
    pollInterval: 0, // No polling for artist data
  });

  const handleDownloadFilterChange = (
    newFilter: 'all' | 'downloaded' | 'pending' | 'unavailable'
  ) => {
    setDownloadFilter(newFilter);

    // Pre-fetch data for the new filter to eliminate jitter
    const newVariables = {
      ...queryVariables,
      ...(newFilter === 'downloaded' ? { downloaded: true } : {}),
      ...(newFilter === 'pending' ? { downloaded: false } : {}),
      ...(newFilter === 'unavailable' ? { unavailable: true } : {}),
    };

    client
      .query({
        query: GetSongsDocument,
        variables: newVariables,
        fetchPolicy: 'cache-first',
      })
      .catch(() => {
        // Silently handle errors for pre-fetching
      });
  };

  const handleSort = (field: SongSortField) => {
    let newDirection: SortDirection = 'asc';

    if (sortField === field && sortDirection === 'asc') {
      newDirection = 'desc';
    }

    setSortField(field);
    setSortDirection(newDirection);

    // Pre-fetch data for the new sort to eliminate jitter
    const newVariables = {
      ...queryVariables,
      sortBy: field,
      sortDirection: newDirection,
    };

    client
      .query({
        query: GetSongsDocument,
        variables: newVariables,
        fetchPolicy: 'cache-first',
      })
      .catch(() => {
        // Silently handle errors for pre-fetching
      });
  };

  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize);

    // Pre-fetch data for the new page size to eliminate jitter
    const newVariables = {
      ...queryVariables,
      first: newPageSize,
    };

    client
      .query({
        query: GetSongsDocument,
        variables: newVariables,
        fetchPolicy: 'cache-first',
      })
      .catch(() => {
        // Silently handle errors for pre-fetching
      });
  };

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  const handleLoadMore = () => {
    if (data?.songs.pageInfo.hasNextPage) {
      fetchMore({
        variables: {
          after: data.songs.pageInfo.endCursor,
        },
        updateQuery: (
          prevResult: GetSongsQuery,
          { fetchMoreResult }: { fetchMoreResult?: GetSongsQuery }
        ) => {
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

  // Show subtle loading indicator for filter changes while keeping current data visible
  const isRefetching = networkStatus === 3; // NetworkStatus.refetch
  const isInitialLoading = networkStatus === 1; // NetworkStatus.loading (initial load)

  // Only show loading state on initial load, not on filter changes
  if (isInitialLoading && !data) {
    return (
      <section>
        <h1 className='text-2xl font-semibold mb-4'>Songs</h1>
        <div className='bg-white rounded shadow p-6 min-h-[200px] flex items-center justify-center text-gray-400'>
          Loading songs...
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section>
        <h1 className='text-2xl font-semibold mb-4'>Songs</h1>
        <div className='bg-white rounded shadow p-6 min-h-[200px] flex items-center justify-center text-red-500'>
          Error loading songs: {error.message}
        </div>
      </section>
    );
  }

  const songs = data?.songs.edges || [];
  const totalCount = data?.songs.totalCount || 0;
  const pageInfo = data?.songs.pageInfo;

  // Build title based on filters
  let title = 'Songs';
  if (artistId) title += ` (Artist ID: ${artistId})`;

  return (
    <section>
      {/* Show artist context when filtering by artist */}
      {artistId && artistData?.artist && (
        <ArtistContext
          artistId={artistId}
          artistName={artistData.artist.name}
          contentType='songs'
          totalCount={totalCount}
        />
      )}

      <div className='flex items-center justify-between mb-4'>
        <div className='flex items-center gap-3'>
          <h1 className='text-2xl font-semibold'>
            {title} ({songs.length} of {totalCount})
          </h1>
          {isRefetching && (
            <div className='flex items-center gap-2 text-sm text-gray-500'>
              <div className='w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin' />
              <span>Updating...</span>
            </div>
          )}
        </div>
        <div className='flex items-center gap-4'>
          <SearchInput
            placeholder='Search songs...'
            onSearch={handleSearch}
            className='w-64'
          />
          <PageSizeSelector
            pageSize={pageSize}
            onPageSizeChange={handlePageSizeChange}
          />
          {totalCount > songs.length && (
            <span className='text-sm text-gray-500'>
              Showing first {songs.length} songs
            </span>
          )}
        </div>
      </div>

      <SongFilters
        currentDownloadFilter={downloadFilter}
        onDownloadFilterChange={handleDownloadFilterChange}
      />

      <div className='relative'>
        <SongsTable
          songs={songs}
          sortField={sortField}
          sortDirection={sortDirection}
          onSort={handleSort}
          loading={loading}
          showArtist={!artistId} // Show artist column when not filtered by artist
        />
        {isRefetching && (
          <div className='absolute inset-0 bg-white bg-opacity-50 flex items-center justify-center pointer-events-none'>
            <div className='flex items-center gap-2 text-sm text-gray-600'>
              <div className='w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin' />
              <span>Updating...</span>
            </div>
          </div>
        )}
      </div>

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
