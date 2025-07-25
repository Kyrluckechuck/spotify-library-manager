import { createFileRoute } from '@tanstack/react-router';
import { useQuery, useMutation } from '@apollo/client';
import { GetArtistsDocument, TrackArtistDocument, UntrackArtistDocument } from '../types/generated/graphql';
import type { Artist } from '../types/generated/graphql';
import { useState } from 'react';

// Components
import { ArtistFilters } from '../components/artists/ArtistFilters';
import { ArtistsTable } from '../components/artists/ArtistsTable';
import { PageSizeSelector } from '../components/ui/PageSizeSelector';
import { LoadMoreButton } from '../components/ui/LoadMoreButton';
import type { SortField } from '../components/artists/ArtistsTable';

type SortDirection = 'asc' | 'desc';

function Artists() {
  const [filter, setFilter] = useState<'all' | 'tracked' | 'untracked'>('all');
  const [pageSize, setPageSize] = useState(50);
  const [sortField, setSortField] = useState<SortField>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  
  const { data, loading, error, refetch, fetchMore } = useQuery(GetArtistsDocument, {
    variables: { 
      tracked: filter === 'all' ? undefined : filter === 'tracked',
      first: pageSize,
      sortBy: sortField,
      sortDirection: sortDirection
    },
    notifyOnNetworkStatusChange: true,
    fetchPolicy: 'cache-and-network'
  });

  const [trackArtist] = useMutation(TrackArtistDocument, {
    onCompleted: (data) => {
      if (data.trackArtist.success) {
        refetch();
      }
    }
  });

  const [untrackArtist] = useMutation(UntrackArtistDocument, {
    onCompleted: (data) => {
      if (data.untrackArtist.success) {
        refetch();
      }
    }
  });

  const handleFilterChange = (newFilter: 'all' | 'tracked' | 'untracked') => {
    setFilter(newFilter);
    refetch({
      tracked: newFilter === 'all' ? undefined : newFilter === 'tracked',
      first: pageSize,
      after: undefined,
      sortBy: sortField,
      sortDirection: sortDirection
    });
  };

  const handleSort = (field: SortField) => {
    let newDirection: SortDirection = 'asc';
    
    if (sortField === field && sortDirection === 'asc') {
      newDirection = 'desc';
    }
    
    setSortField(field);
    setSortDirection(newDirection);
    
    refetch({
      tracked: filter === 'all' ? undefined : filter === 'tracked',
      first: pageSize,
      after: undefined,
      sortBy: field,
      sortDirection: newDirection
    });
  };

  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize);
    refetch({
      tracked: filter === 'all' ? undefined : filter === 'tracked',
      first: newPageSize,
      after: undefined,
      sortBy: sortField,
      sortDirection: sortDirection
    });
  };

  const handleTrackToggle = async (artist: Artist) => {
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

  const handleLoadMore = () => {
    if (data?.artists.pageInfo.hasNextPage) {
      fetchMore({
        variables: {
          after: data.artists.pageInfo.endCursor,
        },
        updateQuery: (prevResult, { fetchMoreResult }) => {
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

  if (loading && !data) {
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
        <h1 className="text-2xl font-semibold">
          Artists ({artists.length} of {totalCount})
        </h1>
        <div className="flex items-center gap-4">
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
      />

      <ArtistsTable
        artists={artists}
        sortField={sortField}
        sortDirection={sortDirection}
        onSort={handleSort}
        onTrackToggle={handleTrackToggle}
        loading={loading}
      />

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