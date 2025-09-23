import type { ApolloError } from '@apollo/client';
import type {
  GetArtistsQuery,
  GetAlbumsQuery,
  GetPlaylistsQuery,
  GetSongsQuery,
  GetTaskHistoryQuery,
  TrackArtistMutation,
  UntrackArtistMutation,
  SyncArtistMutation,
  SyncPlaylistMutation,
  SetAlbumWantedMutation,
  TogglePlaylistMutation,
  DownloadUrlMutation,
  CreatePlaylistMutation,
  UpdatePlaylistMutation,
} from '../types/generated/graphql';

// Mock data generators
export const createMockArtist = (overrides = {}) => ({
  id: 1,
  name: 'Test Artist',
  gid: 'test-gid-123',
  spotifyUri: 'test-spotify-uri-123',
  isTracked: true,
  addedAt: '2024-01-01T00:00:00Z',
  lastSynced: '2024-01-01T00:00:00Z',
  ...overrides,
});

export const createMockAlbum = (overrides = {}) => ({
  id: 1,
  name: 'Test Album',
  spotifyGid: 'album-gid-123',
  totalTracks: 10,
  wanted: true,
  downloaded: false,
  albumType: 'album',
  albumGroup: 'album',
  artist: 'Test Artist',
  artistId: 1,
  ...overrides,
});

export const createMockPlaylist = (overrides = {}) => ({
  id: 1,
  name: 'Test Playlist',
  url: 'https://open.spotify.com/playlist/test',
  enabled: true,
  autoTrackArtists: true,
  lastSyncedAt: '2024-01-01T00:00:00Z',
  ...overrides,
});

export const createMockSong = (overrides = {}) => ({
  id: 1,
  name: 'Test Song',
  gid: 'song-gid-123',
  primaryArtist: 'Test Artist',
  primaryArtistId: 1,
  createdAt: '2024-01-01T00:00:00Z',
  failedCount: 0,
  bitrate: 320,
  unavailable: false,
  filePath: '/path/to/song.mp3',
  downloaded: true,
  spotifyUri: 'spotify:track:test123',
  ...overrides,
});

export const createMockTaskHistory = (overrides = {}) => ({
  id: '1',
  taskId: 'task-123-1',
  type: 'SYNC' as const,
  entityId: '1',
  entityType: 'ARTIST' as const,
  status: 'COMPLETED' as const,
  startedAt: '2024-01-01T00:00:00Z',
  completedAt: '2024-01-01T01:00:00Z',
  durationSeconds: 3600,
  progressPercentage: 100,
  logMessages: ['Task 1 started', 'Task 1 completed'],
  ...overrides,
});

// Mock query responses
export const mockGetArtistsResponse: GetArtistsQuery = {
  artists: {
    totalCount: 2,
    pageInfo: {
      hasNextPage: false,
      hasPreviousPage: false,
      startCursor: 'cursor1',
      endCursor: 'cursor2',
    },
    edges: [
      createMockArtist({ id: 1, name: 'Artist 1' }),
      createMockArtist({ id: 2, name: 'Artist 2', isTracked: false }),
    ],
  },
};

export const mockGetAlbumsResponse: GetAlbumsQuery = {
  albums: {
    totalCount: 2,
    pageInfo: {
      hasNextPage: false,
      hasPreviousPage: false,
      startCursor: 'cursor1',
      endCursor: 'cursor2',
    },
    edges: [
      createMockAlbum({ id: 1, name: 'Album 1' }),
      createMockAlbum({ id: 2, name: 'Album 2', wanted: false }),
    ],
  },
};

export const mockGetPlaylistsResponse: GetPlaylistsQuery = {
  playlists: {
    totalCount: 2,
    pageInfo: {
      hasNextPage: false,
      hasPreviousPage: false,
      startCursor: 'cursor1',
      endCursor: 'cursor2',
    },
    edges: [
      createMockPlaylist({ id: 1, name: 'Playlist 1' }),
      createMockPlaylist({ id: 2, name: 'Playlist 2', enabled: false }),
    ],
  },
};

export const mockGetSongsResponse: GetSongsQuery = {
  songs: {
    totalCount: 2,
    pageInfo: {
      hasNextPage: false,
      hasPreviousPage: false,
      startCursor: 'cursor1',
      endCursor: 'cursor2',
    },
    edges: [
      createMockSong({ id: 1, name: 'Song 1' }),
      createMockSong({ id: 2, name: 'Song 2', downloaded: false }),
    ],
  },
};

export const mockGetTaskHistoryResponse: GetTaskHistoryQuery = {
  taskHistory: {
    totalCount: 2,
    pageInfo: {
      hasNextPage: false,
      hasPreviousPage: false,
      startCursor: 'cursor1',
      endCursor: 'cursor2',
    },
    edges: [
      {
        node: createMockTaskHistory({ id: '1', status: 'COMPLETED' as const }),
        cursor: 'cursor1',
      },
      {
        node: createMockTaskHistory({
          id: '2',
          taskId: 'task-123-2',
          status: 'RUNNING' as const,
          durationSeconds: 1800,
          logMessages: ['Task 2 started'],
        }),
        cursor: 'cursor2',
      },
    ],
  },
};

// Mock mutation responses
export const mockTrackArtistResponse: TrackArtistMutation = {
  trackArtist: {
    success: true,
    message: 'Artist tracked successfully',
    artist: createMockArtist({ id: 1, isTracked: true }),
  },
};

export const mockUntrackArtistResponse: UntrackArtistMutation = {
  untrackArtist: {
    success: true,
    message: 'Artist untracked successfully',
    artist: createMockArtist({ id: 1, isTracked: false }),
  },
};

export const mockSyncArtistResponse: SyncArtistMutation = {
  syncArtist: createMockArtist({ id: 1, lastSynced: '2024-01-01T02:00:00Z' }),
};

export const mockSyncPlaylistResponse: SyncPlaylistMutation = {
  syncPlaylist: {
    success: true,
    message: 'Playlist synced successfully',
  },
};

export const mockSetAlbumWantedResponse: SetAlbumWantedMutation = {
  setAlbumWanted: {
    success: true,
    message: 'Album wanted status updated',
    album: createMockAlbum({ id: 1, wanted: true }),
  },
};

export const mockTogglePlaylistResponse: TogglePlaylistMutation = {
  togglePlaylist: {
    success: true,
    message: 'Playlist toggled successfully',
    playlist: createMockPlaylist({ id: 1, enabled: true }),
  },
};

export const mockDownloadUrlResponse: DownloadUrlMutation = {
  downloadUrl: {
    success: true,
    message: 'Download started successfully',
    artist: createMockArtist(),
    album: createMockAlbum(),
    playlist: createMockPlaylist(),
  },
};

export const mockCreatePlaylistResponse: CreatePlaylistMutation = {
  createPlaylist: createMockPlaylist({ id: 3, name: 'New Playlist' }),
};

export const mockUpdatePlaylistResponse: UpdatePlaylistMutation = {
  updatePlaylist: {
    success: true,
    message: 'Playlist updated successfully',
  },
};

// Error responses
export const createGraphQLError = (
  message: string,
  code?: string
): ApolloError => {
  const error = new Error(message) as ApolloError;
  error.graphQLErrors = [
    {
      message,
      extensions: { code: code || 'GRAPHQL_ERROR' },
      locations: [{ line: 1, column: 1 }],
      path: ['query'],
    },
  ];
  error.networkError = null;
  return error;
};

export const createNetworkError = (message: string): ApolloError => {
  const error = new Error(message) as ApolloError;
  error.graphQLErrors = [];
  error.networkError = new Error(message);
  return error;
};

// Mock hook factories
export const createMockUseQuery = (
  data: unknown,
  loading = false,
  error?: ApolloError
) => {
  return {
    data,
    loading,
    error,
    fetchMore: () => {
      // Mock implementation
    },
    networkStatus: loading ? 1 : 7,
    refetch: () => {
      // Mock implementation
    },
  };
};

export const createMockUseMutation = (
  data?: unknown,
  loading = false,
  error?: ApolloError
) => {
  const mutate = () =>
    error ? Promise.reject(error) : Promise.resolve({ data });
  return [mutate, { loading, error }] as const;
};
