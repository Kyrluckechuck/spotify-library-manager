import '@testing-library/jest-dom';
import { vi } from 'vitest';
import React from 'react';
import type { ApolloErrorOptions } from '../types/common';

// Mock Apollo Client core
vi.mock('@apollo/client', async importOriginal => {
  const actual = (await importOriginal()) as Record<string, unknown>;
  return {
    ...actual,
    gql: vi.fn(),
    ApolloError: class ApolloError extends Error {
      constructor(options: ApolloErrorOptions) {
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

// Mock Apollo Client React hooks
vi.mock('@apollo/client/react', () => ({
  useQuery: vi.fn(() => ({
    data: undefined,
    loading: false,
    error: undefined,
  })),
  useLazyQuery: vi.fn(() => [
    vi.fn(),
    { data: undefined, loading: false, error: undefined },
  ]),
  useMutation: vi.fn(() => [vi.fn(), { loading: false, error: undefined }]),
  useApolloClient: vi.fn(() => ({ query: vi.fn() })),
  ApolloProvider: ({ children }: { children: React.ReactNode }) => children,
}));

// Mock TanStack Router
vi.mock('@tanstack/react-router', () => ({
  createFileRoute: vi.fn(),
  Link: ({
    children,
    activeProps: _activeProps,
    activeOptions: _activeOptions,
    to,
    ...rest
  }: {
    children: React.ReactNode;
    to?: string;
    [key: string]: unknown;
  }) => React.createElement('a', { href: to, role: 'link', ...rest }, children),
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
