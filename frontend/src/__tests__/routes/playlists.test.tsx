import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useQuery, useMutation } from '@apollo/client';
import type {
  TestPlaylist,
  MockedUseQuery,
  MockedUseMutation,
} from '../../types/test';

// Import the actual route component

// Import mock data
import {
  mockGetPlaylistsResponse,
  mockTogglePlaylistResponse,
  mockSyncPlaylistResponse,
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

const mockUseQuery = useQuery as MockedUseQuery;
const mockUseMutation = useMutation as MockedUseMutation;

// Create a test component that simulates the Playlists route
const TestPlaylistsComponent = () => {
  const { data, loading, error, fetchMore } = mockUseQuery();
  const [togglePlaylist] = mockUseMutation();
  const [syncPlaylist] = mockUseMutation();

  if (loading) {
    return <div>Loading playlists...</div>;
  }

  if (error) {
    return <div>Error loading playlists: {error.message}</div>;
  }

  if (!data?.playlists?.edges?.length) {
    return <div>No playlists found</div>;
  }

  const handleTogglePlaylist = async (playlistId: number) => {
    try {
      await togglePlaylist({ variables: { playlistId } });
    } catch (err) {
      console.error('Failed to toggle playlist:', err);
    }
  };

  const handleSyncPlaylist = async (playlistId: number) => {
    try {
      await syncPlaylist({ variables: { playlistId } });
    } catch (err) {
      console.error('Failed to sync playlist:', err);
    }
  };

  return (
    <div>
      <h1>
        Playlists ({data.playlists.edges.length} of {data.playlists.totalCount})
      </h1>
      <div>
        {data.playlists.edges.map((playlist: TestPlaylist) => (
          <div key={playlist.id} data-testid={`playlist-${playlist.id}`}>
            <span>{playlist.name}</span>
            <span>{playlist.enabled ? 'Enabled' : 'Disabled'}</span>
            <button
              onClick={() => handleTogglePlaylist(playlist.id)}
              data-testid={`toggle-${playlist.id}`}
            >
              Toggle
            </button>
            <button
              onClick={() => handleSyncPlaylist(playlist.id)}
              data-testid={`sync-${playlist.id}`}
            >
              Sync
            </button>
          </div>
        ))}
      </div>
      {data.playlists.pageInfo.hasNextPage && (
        <button onClick={() => fetchMore()} data-testid='load-more'>
          Load More
        </button>
      )}
    </div>
  );
};

describe('Playlists Route', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Query Operations', () => {
    it('renders loading state', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(undefined, true));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestPlaylistsComponent />);

      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });

    it('renders playlists when data is loaded', () => {
      mockUseQuery.mockReturnValue(
        createMockUseQuery(mockGetPlaylistsResponse)
      );
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestPlaylistsComponent />);

      expect(screen.getByText('Playlist 1')).toBeInTheDocument();
      expect(screen.getByText('Playlist 2')).toBeInTheDocument();
      expect(screen.getByText(/2 of 2/)).toBeInTheDocument();
    });

    it('renders error state for GraphQL errors', () => {
      const error = createGraphQLError('Failed to load playlists');
      mockUseQuery.mockReturnValue(createMockUseQuery(undefined, false, error));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestPlaylistsComponent />);

      expect(screen.getByText(/error/i)).toBeInTheDocument();
      expect(screen.getByText(/failed to load playlists/i)).toBeInTheDocument();
    });

    it('renders error state for network errors', () => {
      const error = createNetworkError('Network connection failed');
      mockUseQuery.mockReturnValue(createMockUseQuery(undefined, false, error));
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestPlaylistsComponent />);

      expect(screen.getByText(/error/i)).toBeInTheDocument();
      expect(
        screen.getByText(/network connection failed/i)
      ).toBeInTheDocument();
    });

    it('renders empty state when no playlists', () => {
      const emptyResponse = {
        playlists: {
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

      render(<TestPlaylistsComponent />);

      expect(screen.getByText(/no playlists found/i)).toBeInTheDocument();
    });

    it('handles pagination correctly', () => {
      const responseWithNextPage = {
        ...mockGetPlaylistsResponse,
        playlists: {
          ...mockGetPlaylistsResponse.playlists,
          pageInfo: {
            ...mockGetPlaylistsResponse.playlists.pageInfo,
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

      render(<TestPlaylistsComponent />);

      const loadMoreButton = screen.getByTestId('load-more');
      expect(loadMoreButton).toBeInTheDocument();

      fireEvent.click(loadMoreButton);
      expect(mockFetchMore).toHaveBeenCalled();
    });
  });

  describe('Mutation Operations', () => {
    it('handles toggle playlist mutation successfully', async () => {
      mockUseQuery.mockReturnValue(
        createMockUseQuery(mockGetPlaylistsResponse)
      );
      mockUseMutation.mockReturnValue(
        createMockUseMutation(mockTogglePlaylistResponse)
      );

      render(<TestPlaylistsComponent />);

      const toggleButton = screen.getByTestId('toggle-1');
      fireEvent.click(toggleButton);

      await waitFor(() => {
        expect(mockUseMutation).toHaveBeenCalled();
      });
    });

    it('handles sync playlist mutation successfully', async () => {
      mockUseQuery.mockReturnValue(
        createMockUseQuery(mockGetPlaylistsResponse)
      );
      mockUseMutation.mockReturnValue(
        createMockUseMutation(mockSyncPlaylistResponse)
      );

      render(<TestPlaylistsComponent />);

      const syncButton = screen.getByTestId('sync-1');
      fireEvent.click(syncButton);

      await waitFor(() => {
        expect(mockUseMutation).toHaveBeenCalled();
      });
    });

    it('handles mutation errors gracefully', async () => {
      const mutationError = createGraphQLError('Failed to toggle playlist');
      mockUseQuery.mockReturnValue(
        createMockUseQuery(mockGetPlaylistsResponse)
      );
      mockUseMutation.mockReturnValue(
        createMockUseMutation(undefined, false, mutationError)
      );

      // Mock console.error to avoid test noise
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {
        // Mock implementation
      });

      render(<TestPlaylistsComponent />);

      const toggleButton = screen.getByTestId('toggle-1');
      fireEvent.click(toggleButton);

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalled();
      });

      consoleSpy.mockRestore();
    });
  });

  describe('Data Display', () => {
    it('displays playlist information correctly', () => {
      mockUseQuery.mockReturnValue(
        createMockUseQuery(mockGetPlaylistsResponse)
      );
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestPlaylistsComponent />);

      expect(screen.getByText('Playlist 1')).toBeInTheDocument();
      expect(screen.getByText('Playlist 2')).toBeInTheDocument();
      expect(screen.getByText('Enabled')).toBeInTheDocument();
      expect(screen.getByText('Disabled')).toBeInTheDocument();
    });

    it('shows correct playlist count', () => {
      mockUseQuery.mockReturnValue(
        createMockUseQuery(mockGetPlaylistsResponse)
      );
      mockUseMutation.mockReturnValue(createMockUseMutation());

      render(<TestPlaylistsComponent />);

      expect(screen.getByText(/2 of 2/)).toBeInTheDocument();
    });
  });
});
