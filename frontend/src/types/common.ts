// Common types used across the application

export interface Album {
  id: number;
  name: string;
  artist: string;
  totalTracks: number;
  wanted: boolean;
  downloaded: boolean;
}

export interface Artist {
  id: number;
  name: string;
  isTracked: boolean;
  lastSynced: string;
}

export interface Playlist {
  id: number;
  name: string;
  enabled: boolean;
}

export interface Song {
  id: number;
  name: string;
  primaryArtist: string;
  bitrate: number;
  unavailable: boolean;
  downloaded: boolean;
  failedCount: number;
  filePath?: string;
  spotifyUri?: string;
}

export interface TaskHistory {
  id: number;
  taskId: string;
  type: string;
  entityType: string;
  entityId: string;
  status: string;
  startedAt: string;
  completedAt?: string;
  durationSeconds?: number;
  progressPercentage?: number;
  logMessages?: string[];
}

export interface TaskCount {
  taskName: string;
  count: number;
}

export interface FilterState {
  wanted?: 'all' | 'wanted' | 'unwanted';
  downloaded?: 'all' | 'downloaded' | 'not-downloaded';
  unavailable?: 'all' | 'unavailable' | 'available';
  status?: 'all' | 'running' | 'completed' | 'failed' | 'pending';
  type?: 'all' | 'sync' | 'download' | 'fetch';
  entityType?: 'all' | 'artist' | 'album' | 'playlist';
  search?: string;
  sortBy?: string;
  sortDirection?: 'asc' | 'desc';
}

export interface SortField {
  field: string;
  direction: 'asc' | 'desc';
}

export interface PageInfo {
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  startCursor?: string | null;
  endCursor?: string | null;
}

export interface Connection<T> {
  edges: T[];
  pageInfo: PageInfo;
  totalCount: number;
}

export interface GraphQLError {
  message: string;
  extensions?: { code?: string };
  locations?: Array<{ line: number; column: number }>;
  path?: string[];
}

export interface ApolloErrorOptions {
  graphQLErrors?: GraphQLError[];
  networkError?: { message: string };
}
