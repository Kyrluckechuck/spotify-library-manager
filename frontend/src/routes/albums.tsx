import { createFileRoute } from '@tanstack/react-router';

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

// Hooks
import { useAlbumsPage } from '../hooks/useAlbumsPage';

function Albums() {
  const { artistId } = Route.useSearch();

  const {
    // Data
    albums,
    totalCount,
    pageInfo,
    loading,
    error,
    isRefreshing,
    isInitialLoading,
    artist,

    // Filters & sorting
    wantedFilter,
    downloadFilter,
    pageSize,
    sortField,
    sortDirection,

    // Mutation states
    mutatingIds,
    pulseIds,

    // Handlers
    handleWantedFilterChange,
    handleDownloadFilterChange,
    handlePageSizeChange,
    handleSort,
    handleSearch,
    handleWantedToggle,
    handleDownloadAlbum,
    handleLoadMore,
  } = useAlbumsPage({ artistId });

  // Only show loading state on initial load
  if (isInitialLoading && !albums.length) {
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

  return (
    <section>
      {/* Artist context when filtering by artist */}
      {artistId && artist && (
        <ArtistContext
          artistId={artistId}
          artistName={artist.name}
          contentType='albums'
          totalCount={totalCount}
        />
      )}

      <div className='flex items-center justify-between mb-4'>
        <div className='flex items-center gap-3'>
          <h1 className='text-2xl font-semibold'>
            Albums ({albums.length} of {totalCount})
          </h1>
          {isRefreshing && <InlineSpinner label='Updating...' />}
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
          onDownloadAlbum={handleDownloadAlbum}
          loading={loading}
          mutatingIds={mutatingIds}
          pulseIds={pulseIds}
        />
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
