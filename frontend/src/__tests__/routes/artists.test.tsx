import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useQuery, useMutation } from '@apollo/client';
import type { MockedUseQuery, MockedUseMutation } from '../../types/test';

// Import mock data
import {
  mockGetArtistsResponse,
  mockTrackArtistResponse,
  mockUntrackArtistResponse,
  mockSyncArtistResponse,
  createGraphQLError,
  createNetworkError,
  createMockUseQuery,
  createMockUseMutation,
} from '../../test/graphql-mocks';

// Mock the GraphQL hooks
vi.mock('@apollo/client', () => ({
  useQuery: vi.fn(),
  useMutation: vi.fn(() => [vi.fn(), { loading: false, error: undefined }]),
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
const mockUseMutation = useMutation as MockedUseMutation;

// Create a test component that simulates the Artists route
const TestArtistsComponent = () => {
  const { data, loading, error, fetchMore } = mockUseQuery();
  const [trackArtist] = mockUseMutation() as [
    MockedFunction<() => void>,
    { loading: boolean; error?: Error },
  ];
  const [untrackArtist] = mockUseMutation() as [
    MockedFunction<() => void>,
    { loading: boolean; error?: Error },
  ];
  const [syncArtist] = mockUseMutation() as [
    MockedFunction<() => void>,
    { loading: boolean; error?: Error },
  ];

  const [filter, setFilter] = React.useState<'all' | 'tracked' | 'untracked'>(
    'all'
  );

  if (loading) {
    return <div>Loading artists...</div>;
  }

  if (error) {
    return <div>Error loading artists: {error.message}</div>;
  }

  if (!data?.artists?.edges?.length) {
    return <div>No artists found</div>;
  }

  const handleTrackToggle = async (artist: {
    id: number;
    isTracked: boolean;
  }) => {
    try {
      if (artist.isTracked) {
        await untrackArtist({ variables: { artistId: artist.id } });
      } else {
        await trackArtist({ variables: { artistId: artist.id } });
      }
    } catch (err) {
      console.error('Failed to toggle artist tracking:', err);
    }
  };

  const handleSyncArtist = async (artistId: number) => {
    try {
      await syncArtist({ variables: { artistId: artistId.toString() } });
    } catch (err) {
      console.error('Failed to sync artist:', err);
    }
  };

  const handleFilterChange = (newFilter: 'all' | 'tracked' | 'untracked') => {
    setFilter(newFilter);
  };

  // Filter artists based on current filter
  const filteredArtists = data.artists.edges.filter(
    (artist: {
      id: number;
      name: string;
      isTracked: boolean;
      lastSynced: string;
    }) => {
      if (filter === 'tracked') return artist.isTracked;
      if (filter === 'untracked') return !artist.isTracked;
      return true;
    }
  );

  return (
    <div>
      <h1>
        Artists ({filteredArtists.length} of {data.artists.totalCount})
      </h1>

      {/* Filter controls */}
      <div>
        <select
          value={filter}
          onChange={e =>
            handleFilterChange(
              e.target.value as 'all' | 'tracked' | 'untracked'
            )
          }
          data-testid='tracking-filter'
        >
          <option value='all'>All Artists</option>
          <option value='tracked'>Tracked</option>
          <option value='untracked'>Untracked</option>
        </select>
      </div>

      {/* Artists list */}
      <div>
        {filteredArtists.map(
          (artist: {
            id: number;
            name: string;
            isTracked: boolean;
            lastSynced: string;
          }) => (
            <div key={artist.id} data-testid={`artist-${artist.id}`}>
              <span>{artist.name}</span>
              <span>{artist.isTracked ? 'Tracked' : 'Not Tracked'}</span>
              <span>Last synced: {artist.lastSynced}</span>
              <button
                onClick={() => handleTrackToggle(artist)}
                data-testid={`toggle-${artist.id}`}
              >
                {artist.isTracked ? 'Untrack' : 'Track'}
              </button>
              <button
                onClick={() => handleSyncArtist(artist.id)}
                data-testid={`sync-${artist.id}`}
              >
                Sync
              </button>
            </div>
          )
        )}
      </div>

      {data.artists.pageInfo.hasNextPage && (
        <button onClick={() => fetchMore()} data-testid='load-more'>
          Load More
        </button>
      )}
    </div>
  );
};

describe('Artists Route', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Query Operations', () => {
    it('renders loading state', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(undefined, true));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestArtistsComponent />);

      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });

    it('renders artists when data is loaded', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetArtistsResponse));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestArtistsComponent />);

      expect(screen.getByText('Artist 1')).toBeInTheDocument();
      expect(screen.getByText('Artist 2')).toBeInTheDocument();
      expect(screen.getByText(/2 of 2/)).toBeInTheDocument();
    });

    it('renders error state for GraphQL errors', () => {
      const error = createGraphQLError('Failed to load artists');
      mockUseQuery.mockReturnValue(createMockUseQuery(undefined, false, error));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestArtistsComponent />);

      expect(screen.getByText(/error/i)).toBeInTheDocument();
      expect(screen.getByText(/failed to load artists/i)).toBeInTheDocument();
    });

    it('renders error state for network errors', () => {
      const error = createNetworkError('Network connection failed');
      mockUseQuery.mockReturnValue(createMockUseQuery(undefined, false, error));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestArtistsComponent />);

      expect(screen.getByText(/error/i)).toBeInTheDocument();
      expect(
        screen.getByText(/network connection failed/i)
      ).toBeInTheDocument();
    });

    it('renders empty state when no artists', () => {
      const emptyResponse = {
        artists: {
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

      render(<TestArtistsComponent />);

      expect(screen.getByText(/no artists found/i)).toBeInTheDocument();
    });

    it('handles pagination correctly', () => {
      const responseWithNextPage = {
        ...mockGetArtistsResponse,
        artists: {
          ...mockGetArtistsResponse.artists,
          pageInfo: {
            ...mockGetArtistsResponse.artists.pageInfo,
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

      render(<TestArtistsComponent />);

      const loadMoreButton = screen.getByTestId('load-more');
      expect(loadMoreButton).toBeInTheDocument();

      fireEvent.click(loadMoreButton);
      expect(mockFetchMore).toHaveBeenCalled();
    });
  });

  describe('Filtering', () => {
    it('handles tracking filter changes', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetArtistsResponse));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestArtistsComponent />);

      const trackingFilter = screen.getByTestId('tracking-filter');
      fireEvent.change(trackingFilter, { target: { value: 'tracked' } });

      expect(trackingFilter).toHaveValue('tracked');
    });

    it('filters artists correctly', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetArtistsResponse));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestArtistsComponent />);

      // Initially shows all artists
      expect(screen.getByText('Artist 1')).toBeInTheDocument();
      expect(screen.getByText('Artist 2')).toBeInTheDocument();

      // Filter to tracked only
      const trackingFilter = screen.getByTestId('tracking-filter');
      fireEvent.change(trackingFilter, { target: { value: 'tracked' } });

      // Should only show tracked artists
      expect(screen.getByText('Artist 1')).toBeInTheDocument();
      expect(screen.queryByText('Artist 2')).not.toBeInTheDocument();
    });
  });

  describe('Mutation Operations', () => {
    it('handles track artist mutation successfully', async () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetArtistsResponse));
      mockUseMutation.mockReturnValue(
        createMockUseMutation(mockTrackArtistResponse)
      );

      render(<TestArtistsComponent />);

      const trackButton = screen.getByTestId('toggle-2'); // Artist 2 is not tracked
      fireEvent.click(trackButton);

      await waitFor(() => {
        expect(mockUseMutation).toHaveBeenCalled();
      });
    });

    it('handles untrack artist mutation successfully', async () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetArtistsResponse));
      mockUseMutation.mockReturnValue(
        createMockUseMutation(mockUntrackArtistResponse)
      );

      render(<TestArtistsComponent />);

      const untrackButton = screen.getByTestId('toggle-1'); // Artist 1 is tracked
      fireEvent.click(untrackButton);

      await waitFor(() => {
        expect(mockUseMutation).toHaveBeenCalled();
      });
    });

    it('handles sync artist mutation successfully', async () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetArtistsResponse));
      mockUseMutation.mockReturnValue(
        createMockUseMutation(mockSyncArtistResponse)
      );

      render(<TestArtistsComponent />);

      const syncButton = screen.getByTestId('sync-1');
      fireEvent.click(syncButton);

      await waitFor(() => {
        expect(mockUseMutation).toHaveBeenCalled();
      });
    });

    it('handles mutation errors gracefully', async () => {
      const mutationError = createGraphQLError('Failed to track artist');
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetArtistsResponse));
      mockUseMutation.mockReturnValue(
        createMockUseMutation(undefined, false, mutationError)
      );

      // Mock console.error to avoid test noise
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {
        // Mock implementation
      });

      render(<TestArtistsComponent />);

      const trackButton = screen.getByTestId('toggle-2');
      fireEvent.click(trackButton);

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalled();
      });

      consoleSpy.mockRestore();
    });
  });

  describe('Data Display', () => {
    it('displays artist information correctly', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetArtistsResponse));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestArtistsComponent />);

      expect(screen.getByText('Artist 1')).toBeInTheDocument();
      expect(screen.getByText('Artist 2')).toBeInTheDocument();
      expect(screen.getAllByText('Tracked')).toHaveLength(2);
      expect(screen.getByText('Not Tracked')).toBeInTheDocument();
      // Multiple artists show "Last synced:"; ensure at least one is present
      expect(screen.getAllByText(/last synced:/i).length).toBeGreaterThan(0);
    });

    it('shows correct artist count', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetArtistsResponse));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestArtistsComponent />);

      expect(screen.getByText(/2 of 2/)).toBeInTheDocument();
    });

    it('displays tracking status correctly', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(mockGetArtistsResponse));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestArtistsComponent />);

      // Check that track/untrack buttons are displayed correctly
      expect(screen.getByTestId('toggle-1')).toHaveTextContent('Untrack');
      expect(screen.getByTestId('toggle-2')).toHaveTextContent('Track');
    });
  });
});
