import React from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { InlineSpinner } from '../components/ui/InlineSpinner';
import { PageSpinner } from '../components/ui/PageSpinner';

// Layout & shared components
import { PageContainer } from '../components/layout/PageContainer';
import { PageHeader } from '../components/layout/PageHeader';
import { DataTable } from '../components/common/DataTable';
import { FilterBar } from '../components/common/FilterBar';

// Artists components
import { ArtistFilters } from '../components/artists/ArtistFilters';
import { ArtistsTable } from '../components/artists/ArtistsTable';

// Hooks
import { useArtistsPage } from '../hooks/useArtistsPage';

function Artists() {
  const {
    // Data
    artists,
    totalCount,
    pageInfo,
    loading,
    error,
    isRefreshing,
    isInitialLoading,

    // Filters & sorting
    filter,
    searchQuery,
    pageSize,
    sortField,
    sortDirection,

    // Mutation states
    mutatingIds,
    pulseIds,
    errorById,
    syncMutatingIds,
    downloadMutatingIds,

    // Handlers
    handleFilterChange,
    setSearchQuery,
    setPageSize,
    handleSort,
    handleTrackToggle,
    handleSyncArtist,
    handleDownloadArtist,
    handleSyncAllTrackedArtists,
    handleDownloadAllTrackedArtists,
    handleLoadMore,
  } = useArtistsPage();

  // Show loading state on initial load
  if (isInitialLoading && !artists.length) {
    return (
      <PageContainer>
        <PageHeader
          title='Artists'
          subtitle='Manage and track your favorite artists'
        />
        <PageSpinner message='Loading artists...' />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageHeader
        title='Artists'
        subtitle='Manage and track your favorite artists'
      >
        <div className='flex items-center gap-3'>
          {isRefreshing && <InlineSpinner label='Updating...' />}
          <button
            onClick={handleSyncAllTrackedArtists}
            disabled={loading}
            className='px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors'
          >
            Sync All Tracked Artists
          </button>
          <button
            onClick={handleDownloadAllTrackedArtists}
            disabled={loading}
            className='px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors'
          >
            Download All Tracked Artists
          </button>
        </div>
      </PageHeader>

      <FilterBar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        pageSize={pageSize}
        onPageSizeChange={setPageSize}
        totalCount={totalCount}
        currentCount={artists.length}
        searchPlaceholder='Search artists...'
      />

      <ArtistFilters
        currentFilter={filter}
        onFilterChange={handleFilterChange}
      />

      <DataTable
        data={artists}
        loading={loading}
        error={error}
        totalCount={totalCount}
        pageSize={pageSize}
        hasNextPage={!!pageInfo?.hasNextPage}
        onLoadMore={handleLoadMore}
        emptyMessage='No artists found'
        loadingMessage='Loading artists...'
        errorMessage='Error loading artists'
      >
        <ArtistsTable
          artists={artists}
          sortField={sortField}
          sortDirection={sortDirection}
          onSort={handleSort}
          onTrackToggle={handleTrackToggle}
          onSyncArtist={handleSyncArtist}
          onDownloadArtist={handleDownloadArtist}
          loading={loading}
          mutatingIds={mutatingIds}
          syncMutatingIds={syncMutatingIds}
          downloadMutatingIds={downloadMutatingIds}
          errorById={errorById}
          pulseIds={pulseIds}
        />
      </DataTable>
    </PageContainer>
  );
}

export const Route = createFileRoute('/artists')({
  component: Artists,
});
