// Types used in test files

import type { MockedFunction } from 'vitest';
import type { Album, Artist, Playlist, Song, TaskHistory } from './common';

export interface MockUseQueryResult {
  data: unknown;
  loading: boolean;
  error?: Error;
  fetchMore: () => void;
  networkStatus: number;
  refetch: () => void;
}

export interface MockUseMutationResult {
  loading: boolean;
  error?: Error;
}

export type MockUseQuery = MockedFunction<() => MockUseQueryResult>;
export type MockUseMutation = MockedFunction<
  () => [MockedFunction<() => void>, MockUseMutationResult]
>;

// Type aliases for easier use in test files
export type MockedUseQuery = MockedFunction<() => MockUseQueryResult>;
export type MockedUseMutation = MockedFunction<
  () => [MockedFunction<() => void>, MockUseMutationResult]
>;

export interface TestAlbum extends Album {
  // Additional test-specific properties if needed
}

export interface TestArtist extends Artist {
  // Additional test-specific properties if needed
}

export interface TestPlaylist extends Playlist {
  // Additional test-specific properties if needed
}

export interface TestSong extends Song {
  // Additional test-specific properties if needed
}

export interface TestTaskHistory extends TaskHistory {
  // Additional test-specific properties if needed
}

export interface TestEdge<T> {
  node: T;
}

export interface TestConnection<T> {
  edges: TestEdge<T>[];
  totalCount: number;
  pageInfo: {
    hasNextPage: boolean;
    hasPreviousPage: boolean;
    startCursor?: string | null;
    endCursor?: string | null;
  };
}
