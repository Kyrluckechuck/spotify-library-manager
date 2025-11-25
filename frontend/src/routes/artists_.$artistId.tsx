import { createFileRoute, Link } from '@tanstack/react-router';

// Components
import { PageContainer } from '../components/layout/PageContainer';
import { AlbumFilters } from '../components/albums/AlbumFilters';
import { AlbumsTable } from '../components/albums/AlbumsTable';
import { SongsTable } from '../components/songs/SongsTable';
import { PageSizeSelector } from '../components/ui/PageSizeSelector';
import { InlineSpinner } from '../components/ui/InlineSpinner';
import { PageSpinner } from '../components/ui/PageSpinner';
import { ErrorBanner } from '../components/ui/ErrorBanner';
import { LoadMoreButton } from '../components/ui/LoadMoreButton';
import { SearchInput } from '../components/ui/SearchInput';

// Hooks
import { useArtistDetailPage } from '../hooks/useArtistDetailPage';

// Types
import type { DownloadFilter } from '../types/shared';

function ArtistDetail() {
  const { artistId } = Route.useParams();

  const {
    // Artist data
    artist,
    artistError,
    artistRefreshing,
    artistInitialLoading,

    // Artist actions
    handleTrackToggle,
    handleSyncArtist,
    handleDownloadArtist,
    syncMutatingIds,
    downloadMutatingIds,

    // Albums data
    albums,
    albumsTotalCount,
    albumsPageInfo,
    albumsLoading,
    albumsRefreshing,

    // Albums filters & sorting
    albumWantedFilter,
    albumDownloadFilter,
    albumPageSize,
    albumSortField,
    albumSortDirection,

    // Albums mutation states
    albumMutatingIds,
    albumPulseIds,

    // Albums handlers
    handleAlbumWantedFilterChange,
    handleAlbumDownloadFilterChange,
    handleAlbumPageSizeChange,
    handleAlbumSort,
    handleAlbumSearch,
    handleAlbumWantedToggle,
    handleDownloadAlbum,
    handleLoadMoreAlbums,

    // Songs data
    songs,
    songsTotalCount,
    songsPageInfo,
    songsLoading,
    songsRefreshing,

    // Songs filters & sorting
    songDownloadFilter,
    songPageSize,
    songSortField,
    songSortDirection,

    // Songs handlers
    handleSongDownloadFilterChange,
    handleSongPageSizeChange,
    handleSongSort,
    handleSongSearch,
    handleLoadMoreSongs,
  } = useArtistDetailPage({ artistId });

  if (artistInitialLoading) {
    return (
      <PageContainer>
        <PageSpinner message='Loading artist...' />
      </PageContainer>
    );
  }

  if (artistError) {
    return (
      <PageContainer>
        <ErrorBanner
          title='Error loading artist'
          message={artistError.message}
        />
      </PageContainer>
    );
  }

  if (!artist) {
    return (
      <PageContainer>
        <ErrorBanner
          title='Artist not found'
          message='The requested artist could not be found.'
        />
      </PageContainer>
    );
  }

  const isSyncing = syncMutatingIds.has(artist.id);
  const isDownloading = downloadMutatingIds.has(artist.id);

  return (
    <PageContainer>
      {/* Back navigation */}
      <div className='mb-4'>
        <Link
          to='/artists'
          className='text-sm text-indigo-600 hover:text-indigo-800 flex items-center gap-1'
        >
          ← Back to Artists
        </Link>
      </div>

      {/* Artist Header */}
      <div className='bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg p-6 mb-6'>
        <div className='flex items-start justify-between'>
          <div>
            <div className='flex items-center gap-3 mb-2'>
              <h1 className='text-3xl font-bold text-indigo-900'>
                {artist.name}
              </h1>
              {artistRefreshing && <InlineSpinner label='Updating...' />}
            </div>
            <div className='flex items-center gap-4 text-sm text-indigo-700'>
              <a
                href={`https://open.spotify.com/artist/${artist.gid}`}
                target='_blank'
                rel='noopener noreferrer'
                className='hover:text-indigo-900 underline'
              >
                Open in Spotify
              </a>
              <span
                className={`px-2 py-0.5 rounded text-xs font-medium ${
                  artist.isTracked
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-600'
                }`}
              >
                {artist.isTracked ? 'Tracked' : 'Not Tracked'}
              </span>
            </div>
          </div>
          <div className='flex items-center gap-2'>
            <button
              onClick={handleTrackToggle}
              className={`px-4 py-2 rounded-md transition-colors ${
                artist.isTracked
                  ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  : 'bg-indigo-600 text-white hover:bg-indigo-700'
              }`}
            >
              {artist.isTracked ? 'Untrack' : 'Track'}
            </button>
            <button
              onClick={handleSyncArtist}
              disabled={isSyncing}
              className='px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors'
            >
              {isSyncing ? 'Syncing...' : 'Sync'}
            </button>
            <button
              onClick={handleDownloadArtist}
              disabled={isDownloading}
              className='px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors'
            >
              {isDownloading ? 'Starting...' : 'Download'}
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className='grid grid-cols-2 md:grid-cols-4 gap-4 mt-6'>
          <div className='bg-white/60 rounded-lg p-3'>
            <div className='text-2xl font-bold text-indigo-900'>
              {artist.albumCount}
            </div>
            <div className='text-xs text-indigo-600'>Total Albums</div>
          </div>
          <div className='bg-white/60 rounded-lg p-3'>
            <div className='text-2xl font-bold text-green-700'>
              {artist.downloadedAlbumCount}
            </div>
            <div className='text-xs text-green-600'>Downloaded</div>
          </div>
          <div className='bg-white/60 rounded-lg p-3'>
            <div className='text-2xl font-bold text-orange-700'>
              {artist.undownloadedCount}
            </div>
            <div className='text-xs text-orange-600'>Pending</div>
          </div>
          <div className='bg-white/60 rounded-lg p-3'>
            <div className='text-2xl font-bold text-indigo-900'>
              {artist.songCount}
            </div>
            <div className='text-xs text-indigo-600'>Total Songs</div>
          </div>
        </div>

        {/* Timestamps */}
        <div className='flex gap-6 mt-4 text-xs text-indigo-600'>
          {artist.addedAt && (
            <span>Added: {new Date(artist.addedAt).toLocaleDateString()}</span>
          )}
          {artist.lastSynced && (
            <span>
              Last Synced: {new Date(artist.lastSynced).toLocaleDateString()}
            </span>
          )}
          {artist.lastDownloaded && (
            <span>
              Last Downloaded:{' '}
              {new Date(artist.lastDownloaded).toLocaleDateString()}
            </span>
          )}
        </div>
      </div>

      {/* Albums Section */}
      <section className='mb-8'>
        <div className='flex items-center justify-between mb-4'>
          <div className='flex items-center gap-3'>
            <h2 className='text-xl font-semibold'>
              Albums ({albums.length} of {albumsTotalCount})
            </h2>
            {albumsRefreshing && <InlineSpinner label='Updating...' />}
          </div>
          <div className='flex items-center gap-4'>
            <SearchInput
              placeholder='Search albums...'
              onSearch={handleAlbumSearch}
              className='w-48'
            />
            <PageSizeSelector
              pageSize={albumPageSize}
              onPageSizeChange={handleAlbumPageSizeChange}
            />
          </div>
        </div>

        <AlbumFilters
          currentWantedFilter={albumWantedFilter}
          currentDownloadFilter={albumDownloadFilter}
          onWantedFilterChange={handleAlbumWantedFilterChange}
          onDownloadFilterChange={handleAlbumDownloadFilterChange}
        />

        <AlbumsTable
          albums={albums}
          sortField={albumSortField}
          sortDirection={albumSortDirection}
          onSort={handleAlbumSort}
          onToggleWanted={handleAlbumWantedToggle}
          onDownloadAlbum={handleDownloadAlbum}
          loading={albumsLoading}
          mutatingIds={albumMutatingIds}
          pulseIds={albumPulseIds}
        />

        <LoadMoreButton
          hasNextPage={!!albumsPageInfo?.hasNextPage}
          loading={albumsLoading}
          remainingCount={albumsTotalCount - albums.length}
          onLoadMore={handleLoadMoreAlbums}
        />
      </section>

      {/* Songs Section */}
      <section>
        <div className='flex items-center justify-between mb-4'>
          <div className='flex items-center gap-3'>
            <h2 className='text-xl font-semibold'>
              Songs ({songs.length} of {songsTotalCount})
            </h2>
            {songsRefreshing && <InlineSpinner label='Updating...' />}
          </div>
          <div className='flex items-center gap-4'>
            <SearchInput
              placeholder='Search songs...'
              onSearch={handleSongSearch}
              className='w-48'
            />
            <PageSizeSelector
              pageSize={songPageSize}
              onPageSizeChange={handleSongPageSizeChange}
            />
          </div>
        </div>

        {/* Simple download filter for songs */}
        <div className='flex gap-2 mb-4'>
          {(['all', 'downloaded', 'not_downloaded'] as const).map(filter => (
            <button
              key={filter}
              onClick={() =>
                handleSongDownloadFilterChange(filter as DownloadFilter)
              }
              className={`px-3 py-1 rounded-full text-sm transition-colors ${
                songDownloadFilter === filter
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {filter === 'all'
                ? 'All'
                : filter === 'downloaded'
                  ? 'Downloaded'
                  : 'Not Downloaded'}
            </button>
          ))}
        </div>

        <SongsTable
          songs={songs}
          sortField={songSortField}
          sortDirection={songSortDirection}
          onSort={handleSongSort}
          loading={songsLoading}
        />

        <LoadMoreButton
          hasNextPage={!!songsPageInfo?.hasNextPage}
          loading={songsLoading}
          remainingCount={songsTotalCount - songs.length}
          onLoadMore={handleLoadMoreSongs}
        />
      </section>
    </PageContainer>
  );
}

export const Route = createFileRoute('/artists_/$artistId')({
  component: ArtistDetail,
});
