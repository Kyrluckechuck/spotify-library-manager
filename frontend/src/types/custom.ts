/**
 * Custom type definitions for complex objects used throughout the application.
 */
import type { ReactNode } from 'react';

// Artist-related types
export interface Artist {
  id: number;
  name: string;
  gid: string;
  tracked: boolean;
  addedAt?: string | null;
  lastSyncedAt?: string | null;
}

export interface ArtistEdge {
  node: Artist;
  cursor: string;
}

export interface ArtistsConnection {
  edges: ArtistEdge[];
  pageInfo: PageInfo;
  totalCount: number;
}

// Album-related types
export interface Album {
  id: number;
  name: string;
  spotifyGid: string;
  totalTracks: number;
  wanted: boolean;
  downloaded: boolean;
  albumType?: string | null;
  albumGroup?: string | null;
  artist?: string | null;
  artistId?: number | null;
}

export interface AlbumEdge {
  node: Album;
  cursor: string;
}

export interface AlbumsConnection {
  edges: AlbumEdge[];
  pageInfo: PageInfo;
  totalCount: number;
}

// Song-related types
export interface Song {
  id: number;
  name: string;
  gid: string;
  createdAt: string;
  failedCount: number;
  bitrate?: number | null;
  unavailable: boolean;
  filePath?: string | null;
  downloaded: boolean;
  spotifyUri: string;
  artist?: string | null;
}

export interface SongEdge {
  node: Song;
  cursor: string;
}

export interface SongsConnection {
  edges: SongEdge[];
  pageInfo: PageInfo;
  totalCount: number;
}

// Playlist-related types
export interface Playlist {
  id: number;
  name: string;
  url: string;
  enabled: boolean;
  autoTrackArtists: boolean;
  lastSyncedAt?: string | null;
}

export interface PlaylistEdge {
  node: Playlist;
  cursor: string;
}

export interface PlaylistsConnection {
  edges: PlaylistEdge[];
  pageInfo: PageInfo;
  totalCount: number;
}

// Task-related types
export interface TaskHistory {
  id: string;
  taskId: string;
  type: string;
  entityId: string;
  entityType: string;
  status: string;
  startedAt: string;
  completedAt?: string | null;
  errorMessage?: string | null;
  durationSeconds?: number | null;
  progressPercentage: number;
  logMessages: LogMessage[];
}

export interface LogMessage {
  timestamp: string;
  message: string;
}

export interface TaskHistoryEdge {
  node: TaskHistory;
  cursor: string;
}

export interface TaskHistoryConnection {
  edges: TaskHistoryEdge[];
  pageInfo: PageInfo;
  totalCount: number;
}

// Common types
export interface PageInfo {
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  startCursor?: string | null;
  endCursor?: string | null;
}

// Filter and sort types
export type SortDirection = 'asc' | 'desc';

export type TaskStatus = 'running' | 'completed' | 'failed' | 'pending' | 'all';
export type TaskType = 'sync' | 'download' | 'fetch' | 'all';
export type EntityType = 'artist' | 'album' | 'playlist' | 'all';

// Form and input types
export interface SearchFilters {
  search?: string;
  sortBy?: string;
  sortDirection?: SortDirection;
  pageSize?: number;
}

export interface ArtistFilters extends SearchFilters {
  filter?: 'all' | 'tracked' | 'untracked';
}

export interface AlbumFilters extends SearchFilters {
  artistId?: number;
  wanted?: boolean;
  downloaded?: boolean;
}

export interface SongFilters extends SearchFilters {
  artistId?: number;
  downloaded?: boolean;
  unavailable?: boolean;
}

export interface PlaylistFilters extends SearchFilters {
  enabled?: boolean;
}

export interface TaskFilters extends SearchFilters {
  status?: TaskStatus;
  type?: TaskType;
  entityType?: EntityType;
}

// API response types
export interface MutationResult {
  success: boolean;
  message: string;
  artist?: Artist | null;
  album?: Album | null;
  playlist?: Playlist | null;
}

export interface TaskResult {
  success: boolean;
  message: string;
  taskId?: string | null;
}

export interface CleanupResult {
  success: boolean;
  message: string;
  cleanedCount: number;
}

// Component prop types
export interface TableColumn<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  width?: string;
  render?: (value: unknown, item: T) => ReactNode;
}

export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
}

export interface SortableHeaderProps {
  field: string;
  currentSort: string | null;
  currentDirection: SortDirection;
  onSort: (field: string) => void;
  children: ReactNode;
}

// Hook return types
export interface UseQueryResult<T> {
  data: T | undefined;
  loading: boolean;
  error: Error | null;
  refetch: () => void;
}

export interface UseMutationResult<T, V> {
  mutate: (variables: V) => Promise<T>;
  loading: boolean;
  error: Error | null;
  reset: () => void;
}

// Event handler types
export type ClickHandler<T = unknown> = (item: T) => void;
export type ChangeHandler<T = unknown> = (value: T) => void;
export type SubmitHandler<T = unknown> = (data: T) => void;

// Utility types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type MakeRequired<T, K extends keyof T> = T & Required<Pick<T, K>>;
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};
