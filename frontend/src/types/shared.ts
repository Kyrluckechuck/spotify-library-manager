/**
 * Shared type definitions used across multiple components and routes.
 * Centralizing these types ensures consistency and easier refactoring.
 */

// Sort direction for table columns
export type SortDirection = 'asc' | 'desc';

// Task-related types
export type TaskStatus = 'running' | 'completed' | 'failed' | 'pending' | 'all';
export type TaskType = 'sync' | 'download' | 'fetch' | 'all';

// Entity types for content classification
export type EntityType = 'artist' | 'album' | 'playlist' | 'all';
export type ContentType = 'artist' | 'album' | 'track' | 'playlist' | 'unknown';

// Filter types for albums
export type WantedFilter = 'all' | 'wanted' | 'unwanted';
export type DownloadFilter = 'all' | 'downloaded' | 'pending';

// Filter types for playlists
export type PlaylistEnabledFilter = 'all' | 'enabled' | 'disabled';
