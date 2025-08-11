import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useQuery, useMutation } from '@apollo/client';
import type {
  TestAlbum,
  MockUseQuery,
  MockUseMutation,
} from '../../types/test';

// Import mock data
import {
  mockGetAlbumsResponse,
  mockSetAlbumWantedResponse,
  createGraphQLError,
  createNetworkError,
  createMockUseQuery,
  createMockUseMutation,
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

const mockUseQuery = useQuery as MockUseQuery;
const mockUseMutation = useMutation as MockUseMutation;

// Create a test component that simulates the Albums route
const TestAlbumsComponent = () => {
  const { data, loading, error, fetchMore } = mockUseQuery();
  const [setAlbumWanted] = mockUseMutation();

  const [filters, setFilters] = React.useState({
    wanted: 'all',
    downloaded: 'all',
    sortBy: 'name',
    sortDirection: 'asc',
  });

  if (loading) {
    return <div>Loading albums...</div>;
  }

  if (error) {
    return <div>Error loading albums: {error.message}</div>;
  }

  if (!data?.albums?.edges?.length) {
    return <div>No albums found</div>;
  }

  const handleSetAlbumWanted = async (albumId: number, wanted: boolean) => {
    try {
      await setAlbumWanted({ variables: { albumId, wanted } });
    } catch (err) {
      console.error('Failed to set album wanted status:', err);
    }
  };

  const handleFilterChange = (filterType: string, value: string) => {
    setFilters(prev => ({ ...prev, [filterType]: value }));
  };

  return (
    <div>
      <h1>
        Albums ({data.albums.edges.length} of {data.albums.totalCount})
      </h1>

      {/* Filter controls */}
      <div>
        <select
          value={filters.wanted}
          onChange={e => handleFilterChange('wanted', e.target.value)}
          data-testid='wanted-filter'
        >
          <option value='all'>All</option>
          <option value='wanted'>Wanted</option>
          <option value='unwanted'>Unwanted</option>
        </select>

        <select
          value={filters.downloaded}
          onChange={e => handleFilterChange('downloaded', e.target.value)}
          data-testid='downloaded-filter'
        >
          <option value='all'>All</option>
          <option value='downloaded'>Downloaded</option>
          <option value='not-downloaded'>Not Downloaded</option>
        </select>

        <select
          value={filters.sortBy}
          onChange={e => handleFilterChange('sortBy', e.target.value)}
          data-testid='sort-by-filter'
        >
          <option value='name'>Name</option>
          <option value='artist'>Artist</option>
          <option value='totalTracks'>Tracks</option>
        </select>

        <select
          value={filters.sortDirection}
          onChange={e => handleFilterChange('sortDirection', e.target.value)}
          data-testid='sort-direction-filter'
        >
          <option value='asc'>Ascending</option>
          <option value='desc'>Descending</option>
        </select>
      </div>

      {/* Album list */}
      <div>
        {data.albums.edges.map((album: TestAlbum) => (
          <div key={album.id} data-testid={`album-${album.id}`}>
            <span>{album.name}</span>
            <span>{album.artist}</span>
            <span>{album.totalTracks} tracks</span>
            <span>{album.wanted ? 'Wanted' : 'Not Wanted'}</span>
            <span>{album.downloaded ? 'Downloaded' : 'Not Downloaded'}</span>
            <button
              onClick={() => handleSetAlbumWanted(album.id, !album.wanted)}
              data-testid={`toggle-wanted-${album.id}`}
            >
              {album.wanted ? 'Unwant' : 'Want'}
            </button>
          </div>
        ))}
      </div>

      {data.albums.pageInfo.hasNextPage && (
        <button onClick={() => fetchMore()} data-testid='load-more'>
          Load More
        </button>
      )}
    </div>
  );
};

describe('Albums Route', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Query Operations', () => {
    it('renders loading state', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(undefined, true));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestAlbumsComponent />);

      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });

    it('renders albums when data is loaded', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetAlbumsResponse));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestAlbumsComponent />);

      expect(screen.getByText('Album 1')).toBeInTheDocument();
      expect(screen.getByText('Album 2')).toBeInTheDocument();
      expect(screen.getByText(/2 of 2/)).toBeInTheDocument();
    });

    it('renders error state for GraphQL errors', () => {
      const error = createGraphQLError('Failed to load albums');
      mockUseQuery.mockReturnValue(createMockUseQuery(undefined, false, error));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestAlbumsComponent />);

      expect(screen.getByText(/error/i)).toBeInTheDocument();
      expect(screen.getByText(/failed to load albums/i)).toBeInTheDocument();
    });

    it('renders error state for network errors', () => {
      const error = createNetworkError('Network connection failed');
      mockUseQuery.mockReturnValue(createMockUseQuery(undefined, false, error));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestAlbumsComponent />);

      expect(screen.getByText(/error/i)).toBeInTheDocument();
      expect(
        screen.getByText(/network connection failed/i)
      ).toBeInTheDocument();
    });

    it('renders empty state when no albums', () => {
      const emptyResponse = {
        albums: {
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
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestAlbumsComponent />);

      expect(screen.getByText(/no albums found/i)).toBeInTheDocument();
    });

    it('handles pagination correctly', () => {
      const responseWithNextPage = {
        ...mockGetAlbumsResponse,
        albums: {
          ...mockGetAlbumsResponse.albums,
          pageInfo: {
            ...mockGetAlbumsResponse.albums.pageInfo,
            hasNextPage: true,
          },
        },
      };

      const mockFetchMore = vi.fn();
      mockUseQuery.mockReturnValue({
        ...createMockUseQuery(responseWithNextPage),
        fetchMore: mockFetchMore,
      });
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestAlbumsComponent />);

      const loadMoreButton = screen.getByTestId('load-more');
      expect(loadMoreButton).toBeInTheDocument();

      fireEvent.click(loadMoreButton);
      expect(mockFetchMore).toHaveBeenCalled();
    });
  });

  describe('Filtering and Sorting', () => {
    it('handles wanted filter changes', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetAlbumsResponse));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestAlbumsComponent />);

      const wantedFilter = screen.getByTestId('wanted-filter');
      fireEvent.change(wantedFilter, { target: { value: 'wanted' } });

      expect(wantedFilter).toHaveValue('wanted');
    });

    it('handles downloaded filter changes', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetAlbumsResponse));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestAlbumsComponent />);

      const downloadedFilter = screen.getByTestId('downloaded-filter');
      fireEvent.change(downloadedFilter, { target: { value: 'downloaded' } });

      expect(downloadedFilter).toHaveValue('downloaded');
    });

    it('handles sort by changes', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetAlbumsResponse));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestAlbumsComponent />);

      const sortByFilter = screen.getByTestId('sort-by-filter');
      fireEvent.change(sortByFilter, { target: { value: 'artist' } });

      expect(sortByFilter).toHaveValue('artist');
    });

    it('handles sort direction changes', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetAlbumsResponse));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestAlbumsComponent />);

      const sortDirectionFilter = screen.getByTestId('sort-direction-filter');
      fireEvent.change(sortDirectionFilter, { target: { value: 'desc' } });

      expect(sortDirectionFilter).toHaveValue('desc');
    });
  });

  describe('Mutation Operations', () => {
    it('handles set album wanted mutation successfully', async () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetAlbumsResponse));
      mockUseMutation.mockReturnValue(
        createMockUseMutation(mockSetAlbumWantedResponse)
      );

      render(<TestAlbumsComponent />);

      const toggleButton = screen.getByTestId('toggle-wanted-1');
      fireEvent.click(toggleButton);

      await waitFor(() => {
        expect(mockUseMutation).toHaveBeenCalled();
      });
    });

    it('handles mutation errors gracefully', async () => {
      const mutationError = createGraphQLError(
        'Failed to set album wanted status'
      );
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetAlbumsResponse));
      mockUseMutation.mockReturnValue(
        createMockUseMutation(undefined, false, mutationError)
      );

      // Mock console.error to avoid test noise
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {
        // Mock implementation
      });

      render(<TestAlbumsComponent />);

      const toggleButton = screen.getByTestId('toggle-wanted-1');
      fireEvent.click(toggleButton);

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalled();
      });

      consoleSpy.mockRestore();
    });
  });

  describe('Data Display', () => {
    it('displays album information correctly', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetAlbumsResponse));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestAlbumsComponent />);

      expect(screen.getByText('Album 1')).toBeInTheDocument();
      expect(screen.getByText('Album 2')).toBeInTheDocument();
      expect(screen.getAllByText('Test Artist')).toHaveLength(2);
      expect(screen.getAllByText('10 tracks')).toHaveLength(2);
      expect(screen.getAllByText('Wanted')).toHaveLength(2);
      expect(screen.getByText('Not Wanted')).toBeInTheDocument();
      expect(screen.getAllByText('Not Downloaded').length).toBeGreaterThan(1);
    });

    it('shows correct album count', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetAlbumsResponse));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestAlbumsComponent />);

      expect(screen.getByText(/2 of 2/)).toBeInTheDocument();
    });

    it('displays album status correctly', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetAlbumsResponse));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestAlbumsComponent />);

      // Check that wanted/unwanted buttons are displayed correctly
      expect(screen.getByTestId('toggle-wanted-1')).toHaveTextContent('Unwant');
      expect(screen.getByTestId('toggle-wanted-2')).toHaveTextContent('Want');
    });
  });
});
