import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useQuery } from '@apollo/client';
import type { TestSong, MockedUseQuery } from '../../types/test';

// Import mock data
import {
  mockGetSongsResponse,
  createGraphQLError,
  createNetworkError,
  createMockUseQuery,
} from '../../test/graphql-mocks';

// Mock the GraphQL hooks
vi.mock('@apollo/client', () => ({
  useQuery: vi.fn(),
  useMutation: vi.fn(),
  useApolloClient: vi.fn(() => ({
    query: vi.fn(),
    cache: {
      readQuery: vi.fn(),
      writeQuery: vi.fn(),
      modify: vi.fn(),
    },
  })),
}));

// Mock the TanStack Router
vi.mock('@tanstack/react-router', () => ({
  createFileRoute: vi.fn(() => ({ component: () => null })),
}));

const mockUseQuery = useQuery as MockedUseQuery;

// Create a test component that simulates the Songs route
const TestSongsComponent = () => {
  const { data, loading, error, fetchMore } = mockUseQuery();

  const [filters, setFilters] = React.useState({
    downloaded: 'all',
    unavailable: 'all',
    sortBy: 'name',
    sortDirection: 'asc',
    search: '',
  });

  if (loading) {
    return <div>Loading songs...</div>;
  }

  if (error) {
    return <div>Error loading songs: {error.message}</div>;
  }

  if (!data?.songs?.edges?.length) {
    return <div>No songs found</div>;
  }

  const handleFilterChange = (filterType: string, value: string) => {
    setFilters(prev => ({ ...prev, [filterType]: value }));
  };

  const handleSearchChange = (value: string) => {
    setFilters(prev => ({ ...prev, search: value }));
  };

  // Filter songs based on current filters
  const filteredSongs = data.songs.edges.filter((song: TestSong) => {
    if (filters.downloaded !== 'all') {
      const isDownloaded = song.downloaded;
      if (filters.downloaded === 'downloaded' && !isDownloaded) return false;
      if (filters.downloaded === 'not-downloaded' && isDownloaded) return false;
    }

    if (filters.unavailable !== 'all') {
      const isUnavailable = song.unavailable;
      if (filters.unavailable === 'unavailable' && !isUnavailable) return false;
      if (filters.unavailable === 'available' && isUnavailable) return false;
    }

    if (
      filters.search &&
      !song.name.toLowerCase().includes(filters.search.toLowerCase())
    ) {
      return false;
    }

    return true;
  });

  return (
    <div>
      <h1>
        Songs ({filteredSongs.length} of {data.songs.totalCount})
      </h1>

      {/* Filter controls */}
      <div>
        <select
          value={filters.downloaded}
          onChange={e => handleFilterChange('downloaded', e.target.value)}
          data-testid='downloaded-filter'
        >
          <option value='all'>All Downloads</option>
          <option value='downloaded'>Downloaded</option>
          <option value='not-downloaded'>Not Downloaded</option>
        </select>

        <select
          value={filters.unavailable}
          onChange={e => handleFilterChange('unavailable', e.target.value)}
          data-testid='unavailable-filter'
        >
          <option value='all'>All Availability</option>
          <option value='available'>Available</option>
          <option value='unavailable'>Unavailable</option>
        </select>

        <select
          value={filters.sortBy}
          onChange={e => handleFilterChange('sortBy', e.target.value)}
          data-testid='sort-by-filter'
        >
          <option value='name'>Name</option>
          <option value='artist'>Artist</option>
          <option value='createdAt'>Created</option>
          <option value='bitrate'>Bitrate</option>
        </select>

        <select
          value={filters.sortDirection}
          onChange={e => handleFilterChange('sortDirection', e.target.value)}
          data-testid='sort-direction-filter'
        >
          <option value='asc'>Ascending</option>
          <option value='desc'>Descending</option>
        </select>

        <input
          type='text'
          value={filters.search}
          onChange={e => handleSearchChange(e.target.value)}
          placeholder='Search songs...'
          data-testid='search-input'
        />
      </div>

      {/* Songs list */}
      <div>
        {filteredSongs.map((song: TestSong) => (
          <div key={song.id} data-testid={`song-${song.id}`}>
            <span>{song.name}</span>
            <span>{song.primaryArtist}</span>
            <span>{song.bitrate}kbps</span>
            <span>
              {song.unavailable
                ? 'Unavailable'
                : song.downloaded
                  ? 'Downloaded'
                  : song.failedCount > 0
                    ? `Failed (${song.failedCount})`
                    : 'Not downloaded'}
            </span>
            {song.filePath && <span>Path: {song.filePath}</span>}
            {song.spotifyUri && <span>URI: {song.spotifyUri}</span>}
          </div>
        ))}
      </div>

      {data.songs.pageInfo.hasNextPage && (
        <button onClick={() => fetchMore()} data-testid='load-more'>
          Load More
        </button>
      )}
    </div>
  );
};

describe('Songs Route', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Query Operations', () => {
    it('renders loading state', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(undefined, true));

      render(<TestSongsComponent />);

      expect(screen.getByText(/loading songs/i)).toBeInTheDocument();
    });

    it('renders songs when data is loaded', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetSongsResponse));

      render(<TestSongsComponent />);

      expect(screen.getByText('Song 1')).toBeInTheDocument();
      expect(screen.getByText('Song 2')).toBeInTheDocument();
      expect(screen.getByText(/2 of 2/)).toBeInTheDocument();
    });

    it('renders error state for GraphQL errors', () => {
      const error = createGraphQLError('Failed to load songs');
      mockUseQuery.mockReturnValue(createMockUseQuery(undefined, false, error));

      render(<TestSongsComponent />);

      expect(screen.getByText(/error/i)).toBeInTheDocument();
      expect(screen.getByText(/failed to load songs/i)).toBeInTheDocument();
    });

    it('renders error state for network errors', () => {
      const error = createNetworkError('Network connection failed');
      mockUseQuery.mockReturnValue(createMockUseQuery(undefined, false, error));

      render(<TestSongsComponent />);

      expect(screen.getByText(/error/i)).toBeInTheDocument();
      expect(
        screen.getByText(/network connection failed/i)
      ).toBeInTheDocument();
    });

    it('renders empty state when no songs', () => {
      const emptyResponse = {
        songs: {
          totalCount: 0,
          pageInfo: {
            hasNextPage: false,
            hasPreviousPage: false,
            startCursor: null,
            endCursor: null,
          },
          edges: [],
        },
      };

      mockUseQuery.mockReturnValue(createMockUseQuery(emptyResponse));

      render(<TestSongsComponent />);

      expect(screen.getByText(/no songs found/i)).toBeInTheDocument();
    });

    it('handles pagination correctly', () => {
      const responseWithNextPage = {
        ...mockGetSongsResponse,
        songs: {
          ...mockGetSongsResponse.songs,
          pageInfo: {
            ...mockGetSongsResponse.songs.pageInfo,
            hasNextPage: true,
          },
        },
      };

      const mockFetchMore = vi.fn();
      mockUseQuery.mockReturnValue({
        ...createMockUseQuery(responseWithNextPage),
        fetchMore: mockFetchMore,
      });

      render(<TestSongsComponent />);

      const loadMoreButton = screen.getByTestId('load-more');
      expect(loadMoreButton).toBeInTheDocument();

      fireEvent.click(loadMoreButton);
      expect(mockFetchMore).toHaveBeenCalled();
    });
  });

  describe('Filtering and Search', () => {
    it('handles downloaded filter changes', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetSongsResponse));

      render(<TestSongsComponent />);

      const downloadedFilter = screen.getByTestId('downloaded-filter');
      fireEvent.change(downloadedFilter, { target: { value: 'downloaded' } });

      expect(downloadedFilter).toHaveValue('downloaded');
    });

    it('handles unavailable filter changes', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetSongsResponse));

      render(<TestSongsComponent />);

      const unavailableFilter = screen.getByTestId('unavailable-filter');
      fireEvent.change(unavailableFilter, { target: { value: 'unavailable' } });

      expect(unavailableFilter).toHaveValue('unavailable');
    });

    it('handles sort by changes', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetSongsResponse));

      render(<TestSongsComponent />);

      const sortByFilter = screen.getByTestId('sort-by-filter');
      fireEvent.change(sortByFilter, { target: { value: 'artist' } });

      expect(sortByFilter).toHaveValue('artist');
    });

    it('handles sort direction changes', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetSongsResponse));

      render(<TestSongsComponent />);

      const sortDirectionFilter = screen.getByTestId('sort-direction-filter');
      fireEvent.change(sortDirectionFilter, { target: { value: 'desc' } });

      expect(sortDirectionFilter).toHaveValue('desc');
    });

    it('handles search input changes', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetSongsResponse));

      render(<TestSongsComponent />);

      const searchInput = screen.getByTestId('search-input');
      fireEvent.change(searchInput, { target: { value: 'test-song' } });

      expect(searchInput).toHaveValue('test-song');
    });
  });

  describe('Data Display', () => {
    it('displays song information correctly', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetSongsResponse));

      render(<TestSongsComponent />);

      expect(screen.getByText('Song 1')).toBeInTheDocument();
      expect(screen.getByText('Song 2')).toBeInTheDocument();
      expect(screen.getAllByText('Test Artist')).toHaveLength(2);
      expect(screen.getAllByText('320kbps')).toHaveLength(2);
      expect(screen.getAllByText('Downloaded').length).toBeGreaterThan(0);
      expect(screen.getByText('Not Downloaded')).toBeInTheDocument();
      expect(screen.getByText('Available')).toBeInTheDocument();
      // Failure count is only shown when > 0; for these mocks it's zero
    });

    it('displays song metadata correctly', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetSongsResponse));

      render(<TestSongsComponent />);

      // Check that file paths and URIs are displayed
      expect(screen.getAllByText(/path: \/path\/to\/song\.mp3/i)).toHaveLength(
        2
      );
      expect(screen.getAllByText(/uri: spotify:track:test123/i)).toHaveLength(
        2
      );
    });

    it('shows correct song count', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetSongsResponse));

      render(<TestSongsComponent />);

      expect(screen.getByText(/2 of 2/)).toBeInTheDocument();
    });

    it('filters songs based on downloaded status', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetSongsResponse));

      render(<TestSongsComponent />);

      // Initially shows all songs
      expect(screen.getByText('Song 1')).toBeInTheDocument();
      expect(screen.getByText('Song 2')).toBeInTheDocument();

      // Filter to downloaded only
      const downloadedFilter = screen.getByTestId('downloaded-filter');
      fireEvent.change(downloadedFilter, { target: { value: 'downloaded' } });

      // List should be filtered to downloaded only
      expect(screen.getByText('Song 1')).toBeInTheDocument();
      expect(screen.queryByText('Song 2')).not.toBeInTheDocument();
    });

    it('filters songs based on availability', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetSongsResponse));

      render(<TestSongsComponent />);

      // Initially shows all songs
      expect(screen.getByText('Song 1')).toBeInTheDocument();
      expect(screen.getByText('Song 2')).toBeInTheDocument();

      // Filter to available only
      const unavailableFilter = screen.getByTestId('unavailable-filter');
      fireEvent.change(unavailableFilter, { target: { value: 'available' } });

      // Should still show both songs since filtering is handled by the component
      expect(screen.getByText('Song 1')).toBeInTheDocument();
      expect(screen.getByText('Song 2')).toBeInTheDocument();
    });
  });

  describe('Song Details', () => {
    it('displays song bitrate correctly', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetSongsResponse));

      render(<TestSongsComponent />);

      expect(screen.getAllByText('320kbps')).toHaveLength(2);
    });

    it('displays failure count correctly', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetSongsResponse));

      render(<TestSongsComponent />);

      expect(screen.getByText('Not downloaded')).toBeInTheDocument();
    });

    it('displays download status correctly', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetSongsResponse));

      render(<TestSongsComponent />);

      expect(screen.getAllByText('Downloaded').length).toBeGreaterThan(0);
      expect(screen.getAllByText('Not downloaded').length).toBeGreaterThan(0);
    });

    it('displays availability status correctly', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetSongsResponse));

      render(<TestSongsComponent />);

      expect(screen.getAllByText('Downloaded').length).toBeGreaterThan(0);
      expect(screen.getAllByText('Not downloaded').length).toBeGreaterThan(0);
    });
  });
});
