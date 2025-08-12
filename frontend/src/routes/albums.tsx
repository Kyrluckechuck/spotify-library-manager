import { createFileRoute } from '@tanstack/react-router';
import { useMutation, useQuery, useApolloClient } from '@apollo/client';
import {
  GetAlbumsDocument,
  SetAlbumWantedDocument,
  GetArtistDocument,
  type GetAlbumsQuery,
} from '../types/generated/graphql';
import { useState, useMemo, useCallback } from 'react';

// Components
import { AlbumFilters } from '../components/albums/AlbumFilters';
import { AlbumsTable } from '../components/albums/AlbumsTable';
import { PageSizeSelector } from '../components/ui/PageSizeSelector';
import { InlineSpinner } from '../components/ui/InlineSpinner';
import { PageSpinner } from '../components/ui/PageSpinner';
import { ErrorBanner } from '../components/ui/ErrorBanner';
import { LoadMoreButton } from '../components/ui/LoadMoreButton';
import { ArtistContext } from '../components/ui/ArtistContext';
import { SearchInput } from '../components/ui/SearchInput';
import type { AlbumSortField } from '../components/albums/AlbumsTable';

type SortDirection = 'asc' | 'desc';

function Albums() {
  const { artistId } = Route.useSearch();
  const [wantedFilter, setWantedFilter] = useState<
    'all' | 'wanted' | 'unwanted'
  >('all');
  const [downloadFilter, setDownloadFilter] = useState<
    'all' | 'downloaded' | 'pending'
  >('all');
  const [pageSize, setPageSize] = useState(50);
  const [sortField, setSortField] = useState<AlbumSortField>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [searchQuery, setSearchQuery] = useState('');

  const client = useApolloClient();

  // Memoize query variables
  const queryVariables = useMemo(
    () => ({
      artistId: artistId || undefined,
      wanted: wantedFilter === 'all' ? undefined : wantedFilter === 'wanted',
      downloaded:
        downloadFilter === 'all' ? undefined : downloadFilter === 'downloaded',
      first: pageSize,
      sortBy: sortField,
      sortDirection: sortDirection,
      search: searchQuery || undefined,
    }),
    [
      artistId,
      wantedFilter,
      downloadFilter,
      pageSize,
      sortField,
      sortDirection,
      searchQuery,
    ]
  );

  const { data, loading, error, fetchMore, networkStatus } = useQuery(
    GetAlbumsDocument,
    {
      variables: queryVariables,
      fetchPolicy: 'cache-and-network',
      nextFetchPolicy: 'cache-first',
      notifyOnNetworkStatusChange: true,
      pollInterval: 0,
      errorPolicy: 'all',
      // Keep previous data while loading
      returnPartialData: true,
      onCompleted: data => {
        // Pre-fetch other filter combinations
        if (data && networkStatus !== 3) {
          // Not refetching
          const baseVariables = {
            artistId: artistId || undefined,
            first: pageSize,
            sortBy: sortField,
            sortDirection: sortDirection,
            search: searchQuery || undefined,
          };

          // Pre-fetch wanted/unwanted and downloaded/pending filter combinations
          ['wanted', 'unwanted'].forEach(wantedFilter => {
            ['downloaded', 'pending'].forEach(downloadFilter => {
              const variables = {
                ...baseVariables,
                wanted: wantedFilter === 'wanted' ? true : false,
                downloaded: downloadFilter === 'downloaded' ? true : false,
              };

              client
                .query({
                  query: GetAlbumsDocument,
                  variables,
                  fetchPolicy: 'cache-first',
                })
                .catch(() => {
                  // Ignore pre-fetch errors
                });
            });
          });
        }
      },
    }
  );

  // Fetch artist details if filtering by artist
  const { data: artistData } = useQuery(GetArtistDocument, {
    variables: { id: artistId ?? 0 },
    skip: !artistId,
    fetchPolicy: 'cache-first',
    nextFetchPolicy: 'cache-first',
    notifyOnNetworkStatusChange: false,
    pollInterval: 0,
  });

  const [setAlbumWanted] = useMutation(SetAlbumWantedDocument);

  const handleWantedFilterChange = (
    newFilter: 'all' | 'wanted' | 'unwanted'
  ) => {
    setWantedFilter(newFilter);

    // Pre-fetch data for the new filter
    const newVariables = {
      ...queryVariables,
      wanted: newFilter === 'all' ? undefined : newFilter === 'wanted',
    };

    client
      .query({
        query: GetAlbumsDocument,
        variables: newVariables,
        fetchPolicy: 'cache-first',
      })
      .catch(() => {
        // Silently handle errors for pre-fetching
      });
  };

  const handleDownloadFilterChange = (
    newFilter: 'all' | 'downloaded' | 'pending'
  ) => {
    setDownloadFilter(newFilter);

    // Pre-fetch data for the new filter
    const newVariables = {
      ...queryVariables,
      downloaded: newFilter === 'all' ? undefined : newFilter === 'downloaded',
    };

    client
      .query({
        query: GetAlbumsDocument,
        variables: newVariables,
        fetchPolicy: 'cache-first',
      })
      .catch(() => {
        // Silently handle errors for pre-fetching
      });
  };

  const handleSort = (field: AlbumSortField) => {
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
        query: GetAlbumsDocument,
        variables: newVariables,
        fetchPolicy: 'cache-first',
      })
      .catch(() => {
        // Silently handle errors for pre-fetching
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
        query: GetAlbumsDocument,
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

  const handleWantedToggle = async (albumId: number, wanted: boolean) => {
    try {
      await setAlbumWanted({
        variables: {
          albumId,
          wanted,
        },
      });
    } catch (error) {
      console.error('Error toggling album wanted status:', error);
    }
  };

  const handleLoadMore = () => {
    if (data?.albums.pageInfo.hasNextPage) {
      fetchMore({
        variables: {
          after: data.albums.pageInfo.endCursor,
        },
        updateQuery: (
          prevResult: GetAlbumsQuery,
          { fetchMoreResult }: { fetchMoreResult?: GetAlbumsQuery }
        ) => {
          if (!fetchMoreResult) return prevResult;

          return {
            albums: {
              ...fetchMoreResult.albums,
              edges: [
                ...prevResult.albums.edges,
                ...fetchMoreResult.albums.edges,
              ],
            },
          };
        },
      });
    }
  };

  // Subtle loading indicator for filter changes
  const isRefetching = networkStatus === 3; // NetworkStatus.refetch
  const isInitialLoading = networkStatus === 1; // initial load

  // Only show loading state on initial load
  if (isInitialLoading && !data) {
    return (
      <section>
        <h1 className='text-2xl font-semibold mb-4'>Albums</h1>
        <PageSpinner message='Loading albums...' />
      </section>
    );
  }

  if (error) {
    return (
      <section>
        <h1 className='text-2xl font-semibold mb-4'>Albums</h1>
        <ErrorBanner title='Error loading albums' message={error.message} />
      </section>
    );
  }

  const albums = data?.albums.edges || [];
  const totalCount = data?.albums.totalCount || 0;
  const pageInfo = data?.albums.pageInfo;

  return (
    <section>
      {/* Artist context when filtering by artist */}
      {artistId && artistData?.artist && (
        <ArtistContext
          artistId={artistId}
          artistName={artistData.artist.name}
          contentType='albums'
          totalCount={totalCount}
        />
      )}

      <div className='flex items-center justify-between mb-4'>
        <div className='flex items-center gap-3'>
          <h1 className='text-2xl font-semibold'>
            Albums ({albums.length} of {totalCount})
          </h1>
          {isRefetching && <InlineSpinner label='Updating...' />}
        </div>
        <div className='flex items-center gap-4'>
          <SearchInput
            placeholder='Search albums...'
            onSearch={handleSearch}
            className='w-64'
          />
          <PageSizeSelector
            pageSize={pageSize}
            onPageSizeChange={handlePageSizeChange}
          />
          {totalCount > albums.length && (
            <span className='text-sm text-gray-500'>
              Showing first {albums.length} albums
            </span>
          )}
        </div>
      </div>

      <AlbumFilters
        currentWantedFilter={wantedFilter}
        currentDownloadFilter={downloadFilter}
        onWantedFilterChange={handleWantedFilterChange}
        onDownloadFilterChange={handleDownloadFilterChange}
      />

      <div className='relative'>
        <AlbumsTable
          albums={albums}
          sortField={sortField}
          sortDirection={sortDirection}
          onSort={handleSort}
          onToggleWanted={handleWantedToggle}
          loading={loading}
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
        remainingCount={totalCount - albums.length}
        onLoadMore={handleLoadMore}
      />
    </section>
  );
}

export const Route = createFileRoute('/albums')({
  component: Albums,
  validateSearch: (search: Record<string, unknown>) => ({
    artistId: search.artistId as number | undefined,
  }),
});
