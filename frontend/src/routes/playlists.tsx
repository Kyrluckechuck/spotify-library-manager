import { createFileRoute } from '@tanstack/react-router';

// Components
import { PlaylistFilters } from '../components/playlists/PlaylistFilters';
import { PlaylistsTable } from '../components/playlists/PlaylistsTable';
import { PageSizeSelector } from '../components/ui/PageSizeSelector';
import { InlineSpinner } from '../components/ui/InlineSpinner';
import { PageSpinner } from '../components/ui/PageSpinner';
import { ErrorBanner } from '../components/ui/ErrorBanner';
import { LoadMoreButton } from '../components/ui/LoadMoreButton';
import { PlaylistModal } from '../components/ui/PlaylistModal';
import { SearchInput } from '../components/ui/SearchInput';

// Hooks
import { usePlaylistsPage } from '../hooks/usePlaylistsPage';

function Playlists() {
  const {
    // Data
    playlists,
    totalCount,
    pageInfo,
    loading,
    error,
    isRefreshing,
    isInitialLoading,

    // Filters & sorting
    filter,
    pageSize,
    sortField,
    sortDirection,

    // Modal state
    showPlaylistModal,
    editingPlaylist,

    // Mutation states
    enabledMutatingIds,
    enabledPulseIds,
    autoMutatingIds,
    autoPulseIds,
    syncMutatingIds,
    forceSyncMutatingIds,
    deleteMutatingIds,
    errorById,

    // Handlers
    handleEnabledFilterChange,
    handlePageSizeChange,
    handleSort,
    handleSearch,
    handleFilterHover,
    handleTogglePlaylist,
    handleSyncPlaylist,
    handleForceSyncPlaylist,
    handleDeletePlaylist,
    handleToggleAutoTrack,
    handleEditPlaylist,
    handleClosePlaylistModal,
    handleCreatePlaylist,
    handleDownloadAllPlaylists,
    handleLoadMore,
  } = usePlaylistsPage();

  // Only show loading state on initial load
  if (isInitialLoading && !playlists.length) {
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

  return (
    <section>
      <div className='flex items-center justify-between mb-4'>
        <div className='flex items-center gap-3'>
          <h1 className='text-2xl font-semibold'>
            Playlists ({playlists.length} of {totalCount})
          </h1>
          {isRefreshing && <InlineSpinner label='Updating...' />}
        </div>
        <div className='flex items-center gap-4'>
          <button
            onClick={handleDownloadAllPlaylists}
            disabled={loading}
            className='px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors'
          >
            Download All Enabled Playlists
          </button>
          <button
            onClick={handleCreatePlaylist}
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
          onForceSyncPlaylist={handleForceSyncPlaylist}
          onEditPlaylist={handleEditPlaylist}
          onDeletePlaylist={handleDeletePlaylist}
          loading={loading}
          enabledMutatingIds={enabledMutatingIds}
          autoMutatingIds={autoMutatingIds}
          syncMutatingIds={syncMutatingIds}
          forceSyncMutatingIds={forceSyncMutatingIds}
          deleteMutatingIds={deleteMutatingIds}
          enabledPulseIds={enabledPulseIds}
          autoPulseIds={autoPulseIds}
          errorById={errorById}
        />
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
