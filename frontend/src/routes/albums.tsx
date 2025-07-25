import { createFileRoute } from '@tanstack/react-router';
import { useQuery, useMutation } from '@apollo/client';
import { GetAlbumsDocument, SetAlbumWantedDocument } from '../types/generated/graphql';
import type { Album } from '../types/generated/graphql';
import { useState } from 'react';

// Components
import { AlbumFilters } from '../components/albums/AlbumFilters';
import { AlbumsTable } from '../components/albums/AlbumsTable';
import { PageSizeSelector } from '../components/ui/PageSizeSelector';
import { LoadMoreButton } from '../components/ui/LoadMoreButton';
import type { AlbumSortField } from '../components/albums/AlbumsTable';

type SortDirection = 'asc' | 'desc';

function Albums() {
  const { artistId } = Route.useSearch();
  const [wantedFilter, setWantedFilter] = useState<'all' | 'wanted' | 'unwanted'>('all');
  const [downloadFilter, setDownloadFilter] = useState<'all' | 'downloaded' | 'pending'>('all');
  const [pageSize, setPageSize] = useState(50);
  const [sortField, setSortField] = useState<AlbumSortField>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  const { data, loading, error, refetch, fetchMore } = useQuery(GetAlbumsDocument, {
    variables: {
      artistId: artistId || undefined,
      wanted: wantedFilter === 'all' ? undefined : wantedFilter === 'wanted',
      downloaded: downloadFilter === 'all' ? undefined : downloadFilter === 'downloaded',
      first: pageSize,
      sortBy: sortField,
      sortDirection: sortDirection
    },
    notifyOnNetworkStatusChange: true,
    fetchPolicy: 'cache-and-network'
  });

  const [setAlbumWanted] = useMutation(SetAlbumWantedDocument, {
    onCompleted: (data) => {
      if (data.setAlbumWanted.success) {
        refetch();
      }
    }
  });

  const handleWantedFilterChange = (newFilter: 'all' | 'wanted' | 'unwanted') => {
    setWantedFilter(newFilter);
    refetch({
      artistId: artistId || undefined,
      wanted: newFilter === 'all' ? undefined : newFilter === 'wanted',
      downloaded: downloadFilter === 'all' ? undefined : downloadFilter === 'downloaded',
      first: pageSize,
      after: undefined,
      sortBy: sortField,
      sortDirection: sortDirection
    });
  };

  const handleDownloadFilterChange = (newFilter: 'all' | 'downloaded' | 'pending') => {
    setDownloadFilter(newFilter);
    refetch({
      artistId: artistId || undefined,
      wanted: wantedFilter === 'all' ? undefined : wantedFilter === 'wanted',
      downloaded: newFilter === 'all' ? undefined : newFilter === 'downloaded',
      first: pageSize,
      after: undefined,
      sortBy: sortField,
      sortDirection: sortDirection
    });
  };

  const handleSort = (field: AlbumSortField) => {
    let newDirection: SortDirection = 'asc';

    if (sortField === field && sortDirection === 'asc') {
      newDirection = 'desc';
    }

    setSortField(field);
    setSortDirection(newDirection);

    refetch({
      artistId: artistId || undefined,
      wanted: wantedFilter === 'all' ? undefined : wantedFilter === 'wanted',
      downloaded: downloadFilter === 'all' ? undefined : downloadFilter === 'downloaded',
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
      wanted: wantedFilter === 'all' ? undefined : wantedFilter === 'wanted',
      downloaded: downloadFilter === 'all' ? undefined : downloadFilter === 'downloaded',
      first: newPageSize,
      after: undefined,
      sortBy: sortField,
      sortDirection: sortDirection
    });
  };

  const handleWantedToggle = async (album: Album) => {
    try {
      await setAlbumWanted({ 
        variables: { 
          albumId: album.id, 
          wanted: !album.wanted 
        } 
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
        updateQuery: (prevResult, { fetchMoreResult }) => {
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

  if (loading && !data) {
    return (
      <section>
        <h1 className="text-2xl font-semibold mb-4">Albums</h1>
        <div className="bg-white rounded shadow p-6 min-h-[200px] flex items-center justify-center text-gray-400">
          Loading albums...
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section>
        <h1 className="text-2xl font-semibold mb-4">Albums</h1>
        <div className="bg-white rounded shadow p-6 min-h-[200px] flex items-center justify-center text-red-500">
          Error loading albums: {error.message}
        </div>
      </section>
    );
  }

  const albums = data?.albums.edges || [];
  const totalCount = data?.albums.totalCount || 0;
  const pageInfo = data?.albums.pageInfo;

  return (
    <section>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold">
          Albums ({albums.length} of {totalCount})
        </h1>
        <div className="flex items-center gap-4">
          <PageSizeSelector 
            pageSize={pageSize}
            onPageSizeChange={handlePageSizeChange}
          />
          {totalCount > albums.length && (
            <span className="text-sm text-gray-500">
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

      <AlbumsTable
        albums={albums}
        sortField={sortField}
        sortDirection={sortDirection}
        onSort={handleSort}
        onWantedToggle={handleWantedToggle}
        loading={loading}
      />

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