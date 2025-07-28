import { createFileRoute } from '@tanstack/react-router';
import { useMutation, useQuery, useApolloClient } from '@apollo/client';
import { GetArtistsDocument, TrackArtistDocument, UntrackArtistDocument, SyncArtistDocument, type GetArtistsQuery } from '../types/generated/graphql';
import { useState, useMemo, useCallback } from 'react';


// Components
import { ArtistFilters } from '../components/artists/ArtistFilters';
import { ArtistsTable } from '../components/artists/ArtistsTable';
import { PageSizeSelector } from '../components/ui/PageSizeSelector';
import { LoadMoreButton } from '../components/ui/LoadMoreButton';
import { SearchInput } from '../components/ui/SearchInput';
import type { SortField } from '../components/artists/ArtistsTable';

type SortDirection = 'asc' | 'desc';

function Artists() {
  const [filter, setFilter] = useState<'all' | 'tracked' | 'untracked'>('all');
  const [pageSize, setPageSize] = useState(50);
  const [sortField, setSortField] = useState<SortField>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [searchQuery, setSearchQuery] = useState('');


  const client = useApolloClient();
  
  // Memoize query variables to prevent unnecessary re-renders
  const queryVariables = useMemo(() => ({
    tracked: filter === 'all' ? undefined : filter === 'tracked',
    first: pageSize,
    sortBy: sortField,
    sortDirection: sortDirection,
    search: searchQuery || undefined
  }), [filter, pageSize, sortField, sortDirection, searchQuery]);

  const { data, loading, error, fetchMore, networkStatus } = useQuery(GetArtistsDocument, {
    variables: queryVariables,
    fetchPolicy: 'cache-and-network',
    nextFetchPolicy: 'cache-first',
    notifyOnNetworkStatusChange: true,
    pollInterval: 0, // No polling needed since we're not tracking frontend tasks
    errorPolicy: 'all',
    // Keep previous data while loading new data
    returnPartialData: true,
    onCompleted: (data) => {
      // Pre-fetch other filter combinations to eliminate future jitter
      if (data && networkStatus !== 3) { // Not refetching
        const baseVariables = {
          first: pageSize,
          sortBy: sortField,
          sortDirection: sortDirection,
          search: searchQuery || undefined
        };
        
        // Pre-fetch tracked and untracked filters
        ['tracked', 'untracked'].forEach(trackedFilter => {
          const variables = {
            ...baseVariables,
            tracked: trackedFilter === 'tracked' ? true : false,
          };
          
          client.query({
            query: GetArtistsDocument,
            variables,
            fetchPolicy: 'cache-first',
          }).catch(() => {
            // Silently handle errors for pre-fetching
          });
        });
      }
    },
  });

  const [trackArtist] = useMutation(TrackArtistDocument);
  const [untrackArtist] = useMutation(UntrackArtistDocument);
  const [syncArtist] = useMutation(SyncArtistDocument);

  const handleFilterChange = (newFilter: 'all' | 'tracked' | 'untracked') => {
    setFilter(newFilter);
    
    // Pre-fetch data for the new filter to eliminate jitter
    const newVariables = {
      ...queryVariables,
      tracked: newFilter === 'all' ? undefined : newFilter === 'tracked',
    };
    
    // Pre-fetch without blocking the UI
    client.query({
      query: GetArtistsDocument,
      variables: newVariables,
      fetchPolicy: 'cache-first',
    }).catch(() => {
      // Silently handle errors for pre-fetching
    });
  };

  const handleSort = (field: SortField) => {
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
    
    client.query({
      query: GetArtistsDocument,
      variables: newVariables,
      fetchPolicy: 'cache-first',
    }).catch(() => {
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
    
    client.query({
      query: GetArtistsDocument,
      variables: newVariables,
      fetchPolicy: 'cache-first',
    }).catch(() => {
      // Silently handle errors for pre-fetching
    });
  };

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  const handleFilterHover = useCallback((hoverFilter: 'all' | 'tracked' | 'untracked') => {
    // Pre-fetch data on hover to eliminate jitter
    const newVariables = {
      ...queryVariables,
      tracked: hoverFilter === 'all' ? undefined : hoverFilter === 'tracked',
    };
    
    client.query({
      query: GetArtistsDocument,
      variables: newVariables,
      fetchPolicy: 'cache-first',
    }).catch(() => {
      // Silently handle errors for pre-fetching
    });
  }, [queryVariables, client]);

  const handleTrackToggle = async (artist: any) => {
    try {
      if (artist.tracked) {
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
      await syncArtist({ variables: { artistId } });
    } catch (error) {
      console.error('Error syncing artist:', error);
    }
  };

  const handleLoadMore = () => {
    if (data?.artists.pageInfo.hasNextPage) {
      fetchMore({
        variables: {
          after: data.artists.pageInfo.endCursor,
        },
        updateQuery: (prevResult: GetArtistsQuery, { fetchMoreResult }: { fetchMoreResult?: GetArtistsQuery }) => {
          if (!fetchMoreResult) return prevResult;
          
          return {
            artists: {
              ...fetchMoreResult.artists,
              edges: [
                ...prevResult.artists.edges,
                ...fetchMoreResult.artists.edges,
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
        <h1 className="text-2xl font-semibold mb-4">Artists</h1>
        <div className="bg-white rounded shadow p-6 min-h-[200px] flex items-center justify-center text-gray-400">
          Loading artists...
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section>
        <h1 className="text-2xl font-semibold mb-4">Artists</h1>
        <div className="bg-white rounded shadow p-6 min-h-[200px] flex items-center justify-center text-red-500">
          Error loading artists: {error.message}
        </div>
      </section>
    );
  }

  const artists = data?.artists.edges || [];
  const totalCount = data?.artists.totalCount || 0;
  const pageInfo = data?.artists.pageInfo;

  return (
    <section>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold">
            Artists ({artists.length} of {totalCount})
          </h1>
          {isRefetching && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <div className="w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin"></div>
              <span>Updating...</span>
            </div>
          )}
        </div>
        <div className="flex items-center gap-4">
          <SearchInput
            placeholder="Search artists..."
            onSearch={handleSearch}
            className="w-64"
          />
          <PageSizeSelector 
            pageSize={pageSize}
            onPageSizeChange={handlePageSizeChange}
          />
          {totalCount > artists.length && (
            <span className="text-sm text-gray-500">
              Showing first {artists.length} artists
            </span>
          )}
        </div>
      </div>

      <ArtistFilters 
        currentFilter={filter}
        onFilterChange={handleFilterChange}
        onFilterHover={handleFilterHover}
      />

      <div className="relative">
        <ArtistsTable
          artists={artists}
          sortField={sortField}
          sortDirection={sortDirection}
          onSort={handleSort}
          onTrackToggle={handleTrackToggle}
          onSyncArtist={handleSyncArtist}
          loading={loading}
        />
        {isRefetching && (
          <div className="absolute inset-0 bg-white bg-opacity-50 flex items-center justify-center pointer-events-none">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <div className="w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin"></div>
              <span>Updating...</span>
            </div>
          </div>
        )}
      </div>

      <LoadMoreButton
        hasNextPage={!!pageInfo?.hasNextPage}
        loading={loading}
        remainingCount={totalCount - artists.length}
        onLoadMore={handleLoadMore}
      />
    </section>
  );
}

export const Route = createFileRoute('/artists')({
  component: Artists,
}); 