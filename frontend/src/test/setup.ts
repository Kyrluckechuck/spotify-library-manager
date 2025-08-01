import '@testing-library/jest-dom';
import { vi } from 'vitest';
import React from 'react';

// Mock Apollo Client
vi.mock('@apollo/client', async importOriginal => {
  const actual = (await importOriginal()) as Record<string, unknown>;
  return {
    ...actual,
    useQuery: vi.fn(),
    useMutation: vi.fn(),
    useApolloClient: vi.fn(),
    gql: vi.fn(),
    ApolloProvider: ({ children }: { children: React.ReactNode }) => children,
    ApolloError: class ApolloError extends Error {
      constructor(options: import('../types/common').ApolloErrorOptions) {
        super(
          options.graphQLErrors?.[0]?.message ||
            options.networkError?.message ||
            'Apollo Error'
        );
        this.name = 'ApolloError';
      }
    },
  };
});

// Mock TanStack Router
vi.mock('@tanstack/react-router', () => ({
  createFileRoute: vi.fn(),
  Link: ({
    children,
    ...props
  }: {
    children: React.ReactNode;
    [key: string]: unknown;
  }) => React.createElement('a', { ...props, role: 'link' }, children),
  useNavigate: vi.fn(() => vi.fn()),
  useParams: vi.fn(() => ({})),
}));

// Mock GraphQL types
vi.mock('./types/generated/graphql', () => ({
  GetArtistsDocument: 'GetArtistsDocument',
  GetAlbumsDocument: 'GetAlbumsDocument',
  GetSongsDocument: 'GetSongsDocument',
  GetPlaylistsDocument: 'GetPlaylistsDocument',
  GetTaskHistoryDocument: 'GetTaskHistoryDocument',
  GetActiveTasksDocument: 'GetActiveTasksDocument',
  TrackArtistDocument: 'TrackArtistDocument',
  UntrackArtistDocument: 'UntrackArtistDocument',
}));

// Global test utilities
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

global.matchMedia = vi.fn().mockImplementation(query => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: vi.fn(),
  removeListener: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  dispatchEvent: vi.fn(),
}));
