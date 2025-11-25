import type { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';
export type Maybe<T> = T | null;
export type InputMaybe<T> = T | null | undefined;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
  DateTime: { input: string; output: string; }
};

export type Album = {
  __typename?: 'Album';
  albumGroup: Maybe<Scalars['String']['output']>;
  albumType: Maybe<Scalars['String']['output']>;
  artist: Maybe<Scalars['String']['output']>;
  artistGid: Maybe<Scalars['String']['output']>;
  artistId: Maybe<Scalars['Int']['output']>;
  downloaded: Scalars['Boolean']['output'];
  id: Scalars['Int']['output'];
  name: Scalars['String']['output'];
  spotifyGid: Scalars['String']['output'];
  totalTracks: Scalars['Int']['output'];
  wanted: Scalars['Boolean']['output'];
};

export type AlbumConnection = {
  __typename?: 'AlbumConnection';
  edges: Array<Album>;
  pageInfo: PageInfo;
  totalCount: Scalars['Int']['output'];
};

export type Artist = {
  __typename?: 'Artist';
  addedAt: Maybe<Scalars['DateTime']['output']>;
  albumCount: Scalars['Int']['output'];
  downloadedAlbumCount: Scalars['Int']['output'];
  gid: Scalars['String']['output'];
  id: Scalars['Int']['output'];
  isTracked: Scalars['Boolean']['output'];
  lastDownloaded: Maybe<Scalars['DateTime']['output']>;
  lastSynced: Maybe<Scalars['DateTime']['output']>;
  name: Scalars['String']['output'];
  songCount: Scalars['Int']['output'];
  spotifyUri: Scalars['String']['output'];
  undownloadedCount: Scalars['Int']['output'];
};

export type ArtistConnection = {
  __typename?: 'ArtistConnection';
  edges: Array<Artist>;
  pageInfo: PageInfo;
  totalCount: Scalars['Int']['output'];
};

export type AuthenticationStatus = {
  __typename?: 'AuthenticationStatus';
  cookiesErrorMessage: Maybe<Scalars['String']['output']>;
  cookiesErrorType: Maybe<Scalars['String']['output']>;
  cookiesExpireInDays: Maybe<Scalars['Int']['output']>;
  cookiesValid: Scalars['Boolean']['output'];
  poTokenConfigured: Scalars['Boolean']['output'];
  poTokenErrorMessage: Maybe<Scalars['String']['output']>;
  poTokenValid: Scalars['Boolean']['output'];
  spotifyAuthMode: Scalars['String']['output'];
  spotifyTokenErrorMessage: Maybe<Scalars['String']['output']>;
  spotifyTokenExpired: Scalars['Boolean']['output'];
  spotifyTokenExpiresInHours: Maybe<Scalars['Int']['output']>;
  spotifyTokenValid: Scalars['Boolean']['output'];
  spotifyUserAuthEnabled: Scalars['Boolean']['output'];
};

export type DownloadHistory = {
  __typename?: 'DownloadHistory';
  completedAt: Maybe<Scalars['DateTime']['output']>;
  entityId: Scalars['String']['output'];
  entityType: Scalars['String']['output'];
  errorMessage: Maybe<Scalars['String']['output']>;
  id: Scalars['String']['output'];
  startedAt: Scalars['DateTime']['output'];
  status: DownloadStatus;
};

export type DownloadProgress = {
  __typename?: 'DownloadProgress';
  entityId: Scalars['String']['output'];
  entityType: Scalars['String']['output'];
  message: Scalars['String']['output'];
  progress: Scalars['Float']['output'];
  status: DownloadStatus;
};

export type DownloadStatus =
  | 'COMPLETED'
  | 'FAILED'
  | 'IN_PROGRESS'
  | 'PENDING'
  | 'SKIPPED';

export type EntityType =
  | 'ALBUM'
  | 'ARTIST'
  | 'PLAYLIST'
  | 'TRACK';

export type HistoryConnection = {
  __typename?: 'HistoryConnection';
  edges: Array<HistoryEdge>;
  pageInfo: PageInfo;
  totalCount: Scalars['Int']['output'];
};

export type HistoryEdge = {
  __typename?: 'HistoryEdge';
  cursor: Scalars['String']['output'];
  node: DownloadHistory;
};

export type Mutation = {
  __typename?: 'Mutation';
  batchArtistOperations: MutationResult;
  cancelAllPendingTasks: MutationResult;
  cancelAllTasks: MutationResult;
  cancelRunningTasksByName: MutationResult;
  cancelTasksByName: MutationResult;
  createPlaylist: Playlist;
  disconnectSpotify: MutationResult;
  downloadAlbum: Album;
  downloadAllPlaylists: MutationResult;
  downloadAllTrackedArtists: MutationResult;
  downloadArtist: MutationResult;
  downloadUrl: MutationResult;
  setAlbumWanted: MutationResult;
  syncAllTrackedArtists: MutationResult;
  syncArtist: Artist;
  syncPlaylist: MutationResult;
  togglePlaylist: MutationResult;
  togglePlaylistAutoTrack: MutationResult;
  trackArtist: MutationResult;
  trackPlaylist: Playlist;
  untrackArtist: MutationResult;
  updateAlbum: Album;
  updateArtist: Artist;
  updatePlaylist: MutationResult;
};


export type MutationBatchArtistOperationsArgs = {
  artistIds: Array<Scalars['Int']['input']>;
  operations?: InputMaybe<Array<Scalars['String']['input']>>;
};


export type MutationCancelRunningTasksByNameArgs = {
  taskName: Scalars['String']['input'];
};


export type MutationCancelTasksByNameArgs = {
  taskName: Scalars['String']['input'];
};


export type MutationCreatePlaylistArgs = {
  autoTrackArtists?: Scalars['Boolean']['input'];
  name: Scalars['String']['input'];
  url: Scalars['String']['input'];
};


export type MutationDownloadAlbumArgs = {
  albumId: Scalars['String']['input'];
};


export type MutationDownloadArtistArgs = {
  artistId: Scalars['String']['input'];
};


export type MutationDownloadUrlArgs = {
  autoTrackArtists?: Scalars['Boolean']['input'];
  url: Scalars['String']['input'];
};


export type MutationSetAlbumWantedArgs = {
  albumId: Scalars['Int']['input'];
  wanted: Scalars['Boolean']['input'];
};


export type MutationSyncArtistArgs = {
  artistId: Scalars['String']['input'];
};


export type MutationSyncPlaylistArgs = {
  force?: Scalars['Boolean']['input'];
  playlistId: Scalars['Int']['input'];
};


export type MutationTogglePlaylistArgs = {
  playlistId: Scalars['Int']['input'];
};


export type MutationTogglePlaylistAutoTrackArgs = {
  playlistId: Scalars['Int']['input'];
};


export type MutationTrackArtistArgs = {
  artistId: Scalars['Int']['input'];
};


export type MutationTrackPlaylistArgs = {
  input: TrackPlaylistInput;
};


export type MutationUntrackArtistArgs = {
  artistId: Scalars['Int']['input'];
};


export type MutationUpdateAlbumArgs = {
  input: UpdateAlbumInput;
};


export type MutationUpdateArtistArgs = {
  input: UpdateArtistInput;
};


export type MutationUpdatePlaylistArgs = {
  autoTrackArtists: Scalars['Boolean']['input'];
  name: Scalars['String']['input'];
  playlistId: Scalars['Int']['input'];
  url: Scalars['String']['input'];
};

export type MutationResult = {
  __typename?: 'MutationResult';
  album: Maybe<Album>;
  artist: Maybe<Artist>;
  message: Scalars['String']['output'];
  playlist: Maybe<Playlist>;
  success: Scalars['Boolean']['output'];
};

export type PageInfo = {
  __typename?: 'PageInfo';
  endCursor: Maybe<Scalars['String']['output']>;
  hasNextPage: Scalars['Boolean']['output'];
  hasPreviousPage: Scalars['Boolean']['output'];
  startCursor: Maybe<Scalars['String']['output']>;
};

export type Playlist = {
  __typename?: 'Playlist';
  autoTrackArtists: Scalars['Boolean']['output'];
  enabled: Scalars['Boolean']['output'];
  id: Scalars['Int']['output'];
  lastSyncedAt: Maybe<Scalars['DateTime']['output']>;
  name: Scalars['String']['output'];
  url: Scalars['String']['output'];
};

export type PlaylistConnection = {
  __typename?: 'PlaylistConnection';
  edges: Array<Playlist>;
  pageInfo: PageInfo;
  totalCount: Scalars['Int']['output'];
};

export type Query = {
  __typename?: 'Query';
  album: Maybe<Album>;
  albums: AlbumConnection;
  artist: Maybe<Artist>;
  artists: ArtistConnection;
  downloadHistory: HistoryConnection;
  playlist: Maybe<Playlist>;
  playlists: PlaylistConnection;
  queueStatus: QueueStatus;
  song: Maybe<Song>;
  songs: SongConnection;
  systemHealth: SystemHealth;
  taskHistory: TaskHistoryConnection;
};


export type QueryAlbumArgs = {
  id: Scalars['String']['input'];
};


export type QueryAlbumsArgs = {
  after?: InputMaybe<Scalars['String']['input']>;
  artistId?: InputMaybe<Scalars['Int']['input']>;
  downloaded?: InputMaybe<Scalars['Boolean']['input']>;
  first?: InputMaybe<Scalars['Int']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
  sortBy?: InputMaybe<Scalars['String']['input']>;
  sortDirection?: InputMaybe<Scalars['String']['input']>;
  wanted?: InputMaybe<Scalars['Boolean']['input']>;
};


export type QueryArtistArgs = {
  id: Scalars['String']['input'];
};


export type QueryArtistsArgs = {
  after?: InputMaybe<Scalars['String']['input']>;
  first?: InputMaybe<Scalars['Int']['input']>;
  isTracked?: InputMaybe<Scalars['Boolean']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
  sortBy?: InputMaybe<Scalars['String']['input']>;
  sortDirection?: InputMaybe<Scalars['String']['input']>;
};


export type QueryDownloadHistoryArgs = {
  after?: InputMaybe<Scalars['String']['input']>;
  entityType?: InputMaybe<Scalars['String']['input']>;
  first?: InputMaybe<Scalars['Int']['input']>;
  status?: InputMaybe<Scalars['String']['input']>;
};


export type QueryPlaylistArgs = {
  id: Scalars['String']['input'];
};


export type QueryPlaylistsArgs = {
  after?: InputMaybe<Scalars['String']['input']>;
  enabled?: InputMaybe<Scalars['Boolean']['input']>;
  first?: InputMaybe<Scalars['Int']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
  sortBy?: InputMaybe<Scalars['String']['input']>;
  sortDirection?: InputMaybe<Scalars['String']['input']>;
};


export type QuerySongArgs = {
  id: Scalars['String']['input'];
};


export type QuerySongsArgs = {
  after?: InputMaybe<Scalars['String']['input']>;
  artistId?: InputMaybe<Scalars['Int']['input']>;
  downloaded?: InputMaybe<Scalars['Boolean']['input']>;
  first?: InputMaybe<Scalars['Int']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
  sortBy?: InputMaybe<Scalars['String']['input']>;
  sortDirection?: InputMaybe<Scalars['String']['input']>;
  unavailable?: InputMaybe<Scalars['Boolean']['input']>;
};


export type QueryTaskHistoryArgs = {
  after?: InputMaybe<Scalars['String']['input']>;
  entityType?: InputMaybe<Scalars['String']['input']>;
  first?: InputMaybe<Scalars['Int']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
  status?: InputMaybe<Scalars['String']['input']>;
  type?: InputMaybe<Scalars['String']['input']>;
};

export type QueueStatus = {
  __typename?: 'QueueStatus';
  queueSize: Scalars['Int']['output'];
  taskCounts: Array<TaskCount>;
  totalPendingTasks: Scalars['Int']['output'];
};

export type Song = {
  __typename?: 'Song';
  bitrate: Scalars['Int']['output'];
  createdAt: Scalars['DateTime']['output'];
  downloaded: Scalars['Boolean']['output'];
  failedCount: Scalars['Int']['output'];
  filePath: Maybe<Scalars['String']['output']>;
  gid: Scalars['String']['output'];
  id: Scalars['Int']['output'];
  name: Scalars['String']['output'];
  primaryArtist: Scalars['String']['output'];
  primaryArtistGid: Scalars['String']['output'];
  primaryArtistId: Scalars['Int']['output'];
  spotifyUri: Scalars['String']['output'];
  unavailable: Scalars['Boolean']['output'];
};

export type SongConnection = {
  __typename?: 'SongConnection';
  edges: Array<Song>;
  pageInfo: PageInfo;
  totalCount: Scalars['Int']['output'];
};

export type Subscription = {
  __typename?: 'Subscription';
  allDownloadProgress: DownloadProgress;
  downloadProgress: DownloadProgress;
};


export type SubscriptionDownloadProgressArgs = {
  entityId: Scalars['String']['input'];
};

export type SystemHealth = {
  __typename?: 'SystemHealth';
  authentication: AuthenticationStatus;
  canDownload: Scalars['Boolean']['output'];
  downloadBlockerReason: Maybe<Scalars['String']['output']>;
};

export type TaskCount = {
  __typename?: 'TaskCount';
  count: Scalars['Int']['output'];
  taskName: Scalars['String']['output'];
};

export type TaskHistory = {
  __typename?: 'TaskHistory';
  completedAt: Maybe<Scalars['DateTime']['output']>;
  durationSeconds: Maybe<Scalars['Int']['output']>;
  entityId: Scalars['String']['output'];
  entityType: EntityType;
  id: Scalars['String']['output'];
  logMessages: Array<Scalars['String']['output']>;
  progressPercentage: Maybe<Scalars['Float']['output']>;
  startedAt: Scalars['DateTime']['output'];
  status: TaskStatus;
  taskId: Scalars['String']['output'];
  type: TaskType;
};

export type TaskHistoryConnection = {
  __typename?: 'TaskHistoryConnection';
  edges: Array<TaskHistoryEdge>;
  pageInfo: PageInfo;
  totalCount: Scalars['Int']['output'];
};

export type TaskHistoryEdge = {
  __typename?: 'TaskHistoryEdge';
  cursor: Scalars['String']['output'];
  node: TaskHistory;
};

export type TaskStatus =
  | 'CANCELLED'
  | 'COMPLETED'
  | 'FAILED'
  | 'PENDING'
  | 'RUNNING';

export type TaskType =
  | 'DOWNLOAD'
  | 'FETCH'
  | 'SYNC';

export type TrackPlaylistInput = {
  autoTrackArtists?: Scalars['Boolean']['input'];
  playlistId: Scalars['String']['input'];
};

export type UpdateAlbumInput = {
  albumId: Scalars['String']['input'];
  isWanted?: InputMaybe<Scalars['Boolean']['input']>;
};

export type UpdateArtistInput = {
  artistId: Scalars['String']['input'];
  autoDownload?: InputMaybe<Scalars['Boolean']['input']>;
  isTracked?: InputMaybe<Scalars['Boolean']['input']>;
};

export type GetArtistQueryVariables = Exact<{
  id: Scalars['String']['input'];
}>;


export type GetArtistQuery = { __typename?: 'Query', artist: { __typename?: 'Artist', id: number, name: string, gid: string, spotifyUri: string, isTracked: boolean, addedAt: string | null, lastSynced: string | null, lastDownloaded: string | null, undownloadedCount: number, albumCount: number, downloadedAlbumCount: number, songCount: number } | null };

export type GetAlbumQueryVariables = Exact<{
  id: Scalars['String']['input'];
}>;


export type GetAlbumQuery = { __typename?: 'Query', album: { __typename?: 'Album', id: number, name: string, spotifyGid: string, totalTracks: number, wanted: boolean, downloaded: boolean, albumType: string | null, albumGroup: string | null, artist: string | null, artistId: number | null, artistGid: string | null } | null };

export type GetArtistsQueryVariables = Exact<{
  isTracked?: InputMaybe<Scalars['Boolean']['input']>;
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  sortBy?: InputMaybe<Scalars['String']['input']>;
  sortDirection?: InputMaybe<Scalars['String']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
}>;


export type GetArtistsQuery = { __typename?: 'Query', artists: { __typename?: 'ArtistConnection', totalCount: number, pageInfo: { __typename?: 'PageInfo', hasNextPage: boolean, hasPreviousPage: boolean, startCursor: string | null, endCursor: string | null }, edges: Array<{ __typename?: 'Artist', id: number, name: string, gid: string, spotifyUri: string, isTracked: boolean, addedAt: string | null, lastSynced: string | null, lastDownloaded: string | null, undownloadedCount: number }> } };

export type GetAlbumsQueryVariables = Exact<{
  artistId?: InputMaybe<Scalars['Int']['input']>;
  wanted?: InputMaybe<Scalars['Boolean']['input']>;
  downloaded?: InputMaybe<Scalars['Boolean']['input']>;
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  sortBy?: InputMaybe<Scalars['String']['input']>;
  sortDirection?: InputMaybe<Scalars['String']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
}>;


export type GetAlbumsQuery = { __typename?: 'Query', albums: { __typename?: 'AlbumConnection', totalCount: number, pageInfo: { __typename?: 'PageInfo', hasNextPage: boolean, hasPreviousPage: boolean, startCursor: string | null, endCursor: string | null }, edges: Array<{ __typename?: 'Album', id: number, name: string, spotifyGid: string, totalTracks: number, wanted: boolean, downloaded: boolean, albumType: string | null, albumGroup: string | null, artist: string | null, artistId: number | null, artistGid: string | null }> } };

export type GetPlaylistsQueryVariables = Exact<{
  enabled?: InputMaybe<Scalars['Boolean']['input']>;
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  sortBy?: InputMaybe<Scalars['String']['input']>;
  sortDirection?: InputMaybe<Scalars['String']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
}>;


export type GetPlaylistsQuery = { __typename?: 'Query', playlists: { __typename?: 'PlaylistConnection', totalCount: number, pageInfo: { __typename?: 'PageInfo', hasNextPage: boolean, hasPreviousPage: boolean, startCursor: string | null, endCursor: string | null }, edges: Array<{ __typename?: 'Playlist', id: number, name: string, url: string, enabled: boolean, autoTrackArtists: boolean, lastSyncedAt: string | null }> } };

export type SyncArtistMutationVariables = Exact<{
  artistId: Scalars['String']['input'];
}>;


export type SyncArtistMutation = { __typename?: 'Mutation', syncArtist: { __typename?: 'Artist', id: number, name: string, gid: string, spotifyUri: string, isTracked: boolean, addedAt: string | null, lastSynced: string | null, undownloadedCount: number } };

export type DownloadArtistMutationVariables = Exact<{
  artistId: Scalars['String']['input'];
}>;


export type DownloadArtistMutation = { __typename?: 'Mutation', downloadArtist: { __typename?: 'MutationResult', success: boolean, message: string } };

export type SyncPlaylistMutationVariables = Exact<{
  playlistId: Scalars['Int']['input'];
}>;


export type SyncPlaylistMutation = { __typename?: 'Mutation', syncPlaylist: { __typename?: 'MutationResult', success: boolean, message: string } };

export type TrackArtistMutationVariables = Exact<{
  artistId: Scalars['Int']['input'];
}>;


export type TrackArtistMutation = { __typename?: 'Mutation', trackArtist: { __typename?: 'MutationResult', success: boolean, message: string, artist: { __typename?: 'Artist', id: number, name: string, isTracked: boolean } | null } };

export type UntrackArtistMutationVariables = Exact<{
  artistId: Scalars['Int']['input'];
}>;


export type UntrackArtistMutation = { __typename?: 'Mutation', untrackArtist: { __typename?: 'MutationResult', success: boolean, message: string, artist: { __typename?: 'Artist', id: number, name: string, isTracked: boolean } | null } };

export type SetAlbumWantedMutationVariables = Exact<{
  albumId: Scalars['Int']['input'];
  wanted: Scalars['Boolean']['input'];
}>;


export type SetAlbumWantedMutation = { __typename?: 'Mutation', setAlbumWanted: { __typename?: 'MutationResult', success: boolean, message: string, album: { __typename?: 'Album', id: number, name: string, wanted: boolean } | null } };

export type DownloadAlbumMutationVariables = Exact<{
  albumId: Scalars['String']['input'];
}>;


export type DownloadAlbumMutation = { __typename?: 'Mutation', downloadAlbum: { __typename?: 'Album', id: number, name: string, spotifyGid: string, wanted: boolean, downloaded: boolean } };

export type TogglePlaylistMutationVariables = Exact<{
  playlistId: Scalars['Int']['input'];
}>;


export type TogglePlaylistMutation = { __typename?: 'Mutation', togglePlaylist: { __typename?: 'MutationResult', success: boolean, message: string, playlist: { __typename?: 'Playlist', id: number, name: string, enabled: boolean } | null } };

export type ForceSyncPlaylistMutationVariables = Exact<{
  playlistId: Scalars['Int']['input'];
}>;


export type ForceSyncPlaylistMutation = { __typename?: 'Mutation', syncPlaylist: { __typename?: 'MutationResult', success: boolean, message: string } };

export type TogglePlaylistAutoTrackMutationVariables = Exact<{
  playlistId: Scalars['Int']['input'];
}>;


export type TogglePlaylistAutoTrackMutation = { __typename?: 'Mutation', togglePlaylistAutoTrack: { __typename?: 'MutationResult', success: boolean, message: string, playlist: { __typename?: 'Playlist', id: number, name: string, autoTrackArtists: boolean } | null } };

export type UpdatePlaylistMutationVariables = Exact<{
  playlistId: Scalars['Int']['input'];
  name: Scalars['String']['input'];
  url: Scalars['String']['input'];
  autoTrackArtists: Scalars['Boolean']['input'];
}>;


export type UpdatePlaylistMutation = { __typename?: 'Mutation', updatePlaylist: { __typename?: 'MutationResult', success: boolean, message: string } };

export type CreatePlaylistMutationVariables = Exact<{
  name: Scalars['String']['input'];
  url: Scalars['String']['input'];
  autoTrackArtists: Scalars['Boolean']['input'];
}>;


export type CreatePlaylistMutation = { __typename?: 'Mutation', createPlaylist: { __typename?: 'Playlist', id: number, name: string, url: string, enabled: boolean, autoTrackArtists: boolean } };

export type SyncAllTrackedArtistsMutationVariables = Exact<{ [key: string]: never; }>;


export type SyncAllTrackedArtistsMutation = { __typename?: 'Mutation', syncAllTrackedArtists: { __typename?: 'MutationResult', success: boolean, message: string } };

export type DownloadAllTrackedArtistsMutationVariables = Exact<{ [key: string]: never; }>;


export type DownloadAllTrackedArtistsMutation = { __typename?: 'Mutation', downloadAllTrackedArtists: { __typename?: 'MutationResult', success: boolean, message: string } };

export type DownloadAllPlaylistsMutationVariables = Exact<{ [key: string]: never; }>;


export type DownloadAllPlaylistsMutation = { __typename?: 'Mutation', downloadAllPlaylists: { __typename?: 'MutationResult', success: boolean, message: string } };

export type DownloadUrlMutationVariables = Exact<{
  url: Scalars['String']['input'];
  autoTrackArtists?: InputMaybe<Scalars['Boolean']['input']>;
}>;


export type DownloadUrlMutation = { __typename?: 'Mutation', downloadUrl: { __typename?: 'MutationResult', success: boolean, message: string, artist: { __typename?: 'Artist', id: number, name: string, gid: string, isTracked: boolean, addedAt: string | null, lastSynced: string | null } | null, album: { __typename?: 'Album', id: number, name: string, spotifyGid: string, totalTracks: number, wanted: boolean, downloaded: boolean, albumType: string | null, albumGroup: string | null, artist: string | null, artistId: number | null } | null, playlist: { __typename?: 'Playlist', id: number, name: string, url: string, enabled: boolean, autoTrackArtists: boolean, lastSyncedAt: string | null } | null } };

export type CreatePlaylistFromDownloadMutationVariables = Exact<{
  name: Scalars['String']['input'];
  url: Scalars['String']['input'];
  autoTrackArtists: Scalars['Boolean']['input'];
}>;


export type CreatePlaylistFromDownloadMutation = { __typename?: 'Mutation', createPlaylist: { __typename?: 'Playlist', id: number, name: string, url: string, enabled: boolean, autoTrackArtists: boolean, lastSyncedAt: string | null } };

export type GetSystemStatusQueryVariables = Exact<{ [key: string]: never; }>;


export type GetSystemStatusQuery = { __typename?: 'Query', systemHealth: { __typename?: 'SystemHealth', canDownload: boolean, downloadBlockerReason: string | null, authentication: { __typename?: 'AuthenticationStatus', cookiesValid: boolean, cookiesErrorType: string | null, cookiesExpireInDays: number | null, poTokenConfigured: boolean, spotifyUserAuthEnabled: boolean, spotifyAuthMode: string } }, queueStatus: { __typename?: 'QueueStatus', totalPendingTasks: number, queueSize: number } };

export type DisconnectSpotifyMutationVariables = Exact<{ [key: string]: never; }>;


export type DisconnectSpotifyMutation = { __typename?: 'Mutation', disconnectSpotify: { __typename?: 'MutationResult', success: boolean, message: string } };

export type GetSongsQueryVariables = Exact<{
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  artistId?: InputMaybe<Scalars['Int']['input']>;
  downloaded?: InputMaybe<Scalars['Boolean']['input']>;
  unavailable?: InputMaybe<Scalars['Boolean']['input']>;
  sortBy?: InputMaybe<Scalars['String']['input']>;
  sortDirection?: InputMaybe<Scalars['String']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
}>;


export type GetSongsQuery = { __typename?: 'Query', songs: { __typename?: 'SongConnection', totalCount: number, edges: Array<{ __typename?: 'Song', id: number, name: string, gid: string, primaryArtist: string, primaryArtistId: number, primaryArtistGid: string, createdAt: string, failedCount: number, bitrate: number, unavailable: boolean, filePath: string | null, downloaded: boolean, spotifyUri: string }>, pageInfo: { __typename?: 'PageInfo', hasNextPage: boolean, hasPreviousPage: boolean, startCursor: string | null, endCursor: string | null } } };

export type GetSongQueryVariables = Exact<{
  id: Scalars['String']['input'];
}>;


export type GetSongQuery = { __typename?: 'Query', song: { __typename?: 'Song', id: number, name: string, gid: string, primaryArtist: string, primaryArtistId: number, createdAt: string, failedCount: number, bitrate: number, unavailable: boolean, filePath: string | null, downloaded: boolean, spotifyUri: string } | null };

export type GetSystemHealthQueryVariables = Exact<{ [key: string]: never; }>;


export type GetSystemHealthQuery = { __typename?: 'Query', systemHealth: { __typename?: 'SystemHealth', canDownload: boolean, downloadBlockerReason: string | null, authentication: { __typename?: 'AuthenticationStatus', cookiesValid: boolean, cookiesErrorType: string | null, cookiesErrorMessage: string | null, cookiesExpireInDays: number | null, poTokenConfigured: boolean, spotifyAuthMode: string, spotifyTokenValid: boolean, spotifyTokenExpired: boolean, spotifyTokenExpiresInHours: number | null, spotifyTokenErrorMessage: string | null } } };

export type GetQueueStatusQueryVariables = Exact<{ [key: string]: never; }>;


export type GetQueueStatusQuery = { __typename?: 'Query', queueStatus: { __typename?: 'QueueStatus', totalPendingTasks: number, queueSize: number, taskCounts: Array<{ __typename?: 'TaskCount', taskName: string, count: number }> } };

export type CancelAllPendingTasksMutationVariables = Exact<{ [key: string]: never; }>;


export type CancelAllPendingTasksMutation = { __typename?: 'Mutation', cancelAllPendingTasks: { __typename?: 'MutationResult', success: boolean, message: string } };

export type CancelTasksByNameMutationVariables = Exact<{
  taskName: Scalars['String']['input'];
}>;


export type CancelTasksByNameMutation = { __typename?: 'Mutation', cancelTasksByName: { __typename?: 'MutationResult', success: boolean, message: string } };

export type CancelRunningTasksByNameMutationVariables = Exact<{
  taskName: Scalars['String']['input'];
}>;


export type CancelRunningTasksByNameMutation = { __typename?: 'Mutation', cancelRunningTasksByName: { __typename?: 'MutationResult', success: boolean, message: string } };

export type CancelAllTasksMutationVariables = Exact<{ [key: string]: never; }>;


export type CancelAllTasksMutation = { __typename?: 'Mutation', cancelAllTasks: { __typename?: 'MutationResult', success: boolean, message: string } };

export type GetTaskHistoryQueryVariables = Exact<{
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  status?: InputMaybe<Scalars['String']['input']>;
  type?: InputMaybe<Scalars['String']['input']>;
  entityType?: InputMaybe<Scalars['String']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
}>;


export type GetTaskHistoryQuery = { __typename?: 'Query', taskHistory: { __typename?: 'TaskHistoryConnection', totalCount: number, pageInfo: { __typename?: 'PageInfo', hasNextPage: boolean, hasPreviousPage: boolean, startCursor: string | null, endCursor: string | null }, edges: Array<{ __typename?: 'TaskHistoryEdge', cursor: string, node: { __typename?: 'TaskHistory', id: string, taskId: string, type: TaskType, entityId: string, entityType: EntityType, status: TaskStatus, startedAt: string, completedAt: string | null, durationSeconds: number | null, progressPercentage: number | null, logMessages: Array<string> } }> } };

export type GetArtistsTestQueryVariables = Exact<{
  isTracked?: InputMaybe<Scalars['Boolean']['input']>;
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
}>;


export type GetArtistsTestQuery = { __typename?: 'Query', artists: { __typename?: 'ArtistConnection', totalCount: number, pageInfo: { __typename?: 'PageInfo', hasNextPage: boolean, hasPreviousPage: boolean, startCursor: string | null, endCursor: string | null }, edges: Array<{ __typename?: 'Artist', id: number, name: string, gid: string, isTracked: boolean, addedAt: string | null, lastSynced: string | null }> } };

export type GetAlbumsTestQueryVariables = Exact<{
  artistId?: InputMaybe<Scalars['Int']['input']>;
  wanted?: InputMaybe<Scalars['Boolean']['input']>;
  downloaded?: InputMaybe<Scalars['Boolean']['input']>;
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  sortBy?: InputMaybe<Scalars['String']['input']>;
  sortDirection?: InputMaybe<Scalars['String']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
}>;


export type GetAlbumsTestQuery = { __typename?: 'Query', albums: { __typename?: 'AlbumConnection', totalCount: number, pageInfo: { __typename?: 'PageInfo', hasNextPage: boolean, hasPreviousPage: boolean, startCursor: string | null, endCursor: string | null }, edges: Array<{ __typename?: 'Album', id: number, name: string, spotifyGid: string, totalTracks: number, wanted: boolean, downloaded: boolean, albumType: string | null, albumGroup: string | null, artist: string | null, artistId: number | null }> } };

export type GetSongsTestQueryVariables = Exact<{
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  artistId?: InputMaybe<Scalars['Int']['input']>;
  downloaded?: InputMaybe<Scalars['Boolean']['input']>;
  unavailable?: InputMaybe<Scalars['Boolean']['input']>;
  sortBy?: InputMaybe<Scalars['String']['input']>;
  sortDirection?: InputMaybe<Scalars['String']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
}>;


export type GetSongsTestQuery = { __typename?: 'Query', songs: { __typename?: 'SongConnection', totalCount: number, edges: Array<{ __typename?: 'Song', id: number, name: string, gid: string, primaryArtist: string, primaryArtistId: number, createdAt: string, failedCount: number, bitrate: number, unavailable: boolean, filePath: string | null, downloaded: boolean, spotifyUri: string }>, pageInfo: { __typename?: 'PageInfo', hasNextPage: boolean, hasPreviousPage: boolean, startCursor: string | null, endCursor: string | null } } };


export const GetArtistDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetArtist"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"id"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"artist"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"id"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"gid"}},{"kind":"Field","name":{"kind":"Name","value":"spotifyUri"}},{"kind":"Field","name":{"kind":"Name","value":"isTracked"}},{"kind":"Field","name":{"kind":"Name","value":"addedAt"}},{"kind":"Field","name":{"kind":"Name","value":"lastSynced"}},{"kind":"Field","name":{"kind":"Name","value":"lastDownloaded"}},{"kind":"Field","name":{"kind":"Name","value":"undownloadedCount"}},{"kind":"Field","name":{"kind":"Name","value":"albumCount"}},{"kind":"Field","name":{"kind":"Name","value":"downloadedAlbumCount"}},{"kind":"Field","name":{"kind":"Name","value":"songCount"}}]}}]}}]} as unknown as DocumentNode<GetArtistQuery, GetArtistQueryVariables>;
export const GetAlbumDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetAlbum"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"id"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"album"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"id"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"spotifyGid"}},{"kind":"Field","name":{"kind":"Name","value":"totalTracks"}},{"kind":"Field","name":{"kind":"Name","value":"wanted"}},{"kind":"Field","name":{"kind":"Name","value":"downloaded"}},{"kind":"Field","name":{"kind":"Name","value":"albumType"}},{"kind":"Field","name":{"kind":"Name","value":"albumGroup"}},{"kind":"Field","name":{"kind":"Name","value":"artist"}},{"kind":"Field","name":{"kind":"Name","value":"artistId"}},{"kind":"Field","name":{"kind":"Name","value":"artistGid"}}]}}]}}]} as unknown as DocumentNode<GetAlbumQuery, GetAlbumQueryVariables>;
export const GetArtistsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetArtists"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"isTracked"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"first"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}},"defaultValue":{"kind":"IntValue","value":"20"}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"after"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"sortBy"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"sortDirection"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"search"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"artists"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"isTracked"},"value":{"kind":"Variable","name":{"kind":"Name","value":"isTracked"}}},{"kind":"Argument","name":{"kind":"Name","value":"first"},"value":{"kind":"Variable","name":{"kind":"Name","value":"first"}}},{"kind":"Argument","name":{"kind":"Name","value":"after"},"value":{"kind":"Variable","name":{"kind":"Name","value":"after"}}},{"kind":"Argument","name":{"kind":"Name","value":"sortBy"},"value":{"kind":"Variable","name":{"kind":"Name","value":"sortBy"}}},{"kind":"Argument","name":{"kind":"Name","value":"sortDirection"},"value":{"kind":"Variable","name":{"kind":"Name","value":"sortDirection"}}},{"kind":"Argument","name":{"kind":"Name","value":"search"},"value":{"kind":"Variable","name":{"kind":"Name","value":"search"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalCount"}},{"kind":"Field","name":{"kind":"Name","value":"pageInfo"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"hasNextPage"}},{"kind":"Field","name":{"kind":"Name","value":"hasPreviousPage"}},{"kind":"Field","name":{"kind":"Name","value":"startCursor"}},{"kind":"Field","name":{"kind":"Name","value":"endCursor"}}]}},{"kind":"Field","name":{"kind":"Name","value":"edges"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"gid"}},{"kind":"Field","name":{"kind":"Name","value":"spotifyUri"}},{"kind":"Field","name":{"kind":"Name","value":"isTracked"}},{"kind":"Field","name":{"kind":"Name","value":"addedAt"}},{"kind":"Field","name":{"kind":"Name","value":"lastSynced"}},{"kind":"Field","name":{"kind":"Name","value":"lastDownloaded"}},{"kind":"Field","name":{"kind":"Name","value":"undownloadedCount"}}]}}]}}]}}]} as unknown as DocumentNode<GetArtistsQuery, GetArtistsQueryVariables>;
export const GetAlbumsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetAlbums"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"artistId"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"wanted"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"downloaded"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"first"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}},"defaultValue":{"kind":"IntValue","value":"20"}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"after"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"sortBy"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"sortDirection"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"search"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"albums"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"artistId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"artistId"}}},{"kind":"Argument","name":{"kind":"Name","value":"wanted"},"value":{"kind":"Variable","name":{"kind":"Name","value":"wanted"}}},{"kind":"Argument","name":{"kind":"Name","value":"downloaded"},"value":{"kind":"Variable","name":{"kind":"Name","value":"downloaded"}}},{"kind":"Argument","name":{"kind":"Name","value":"first"},"value":{"kind":"Variable","name":{"kind":"Name","value":"first"}}},{"kind":"Argument","name":{"kind":"Name","value":"after"},"value":{"kind":"Variable","name":{"kind":"Name","value":"after"}}},{"kind":"Argument","name":{"kind":"Name","value":"sortBy"},"value":{"kind":"Variable","name":{"kind":"Name","value":"sortBy"}}},{"kind":"Argument","name":{"kind":"Name","value":"sortDirection"},"value":{"kind":"Variable","name":{"kind":"Name","value":"sortDirection"}}},{"kind":"Argument","name":{"kind":"Name","value":"search"},"value":{"kind":"Variable","name":{"kind":"Name","value":"search"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalCount"}},{"kind":"Field","name":{"kind":"Name","value":"pageInfo"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"hasNextPage"}},{"kind":"Field","name":{"kind":"Name","value":"hasPreviousPage"}},{"kind":"Field","name":{"kind":"Name","value":"startCursor"}},{"kind":"Field","name":{"kind":"Name","value":"endCursor"}}]}},{"kind":"Field","name":{"kind":"Name","value":"edges"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"spotifyGid"}},{"kind":"Field","name":{"kind":"Name","value":"totalTracks"}},{"kind":"Field","name":{"kind":"Name","value":"wanted"}},{"kind":"Field","name":{"kind":"Name","value":"downloaded"}},{"kind":"Field","name":{"kind":"Name","value":"albumType"}},{"kind":"Field","name":{"kind":"Name","value":"albumGroup"}},{"kind":"Field","name":{"kind":"Name","value":"artist"}},{"kind":"Field","name":{"kind":"Name","value":"artistId"}},{"kind":"Field","name":{"kind":"Name","value":"artistGid"}}]}}]}}]}}]} as unknown as DocumentNode<GetAlbumsQuery, GetAlbumsQueryVariables>;
export const GetPlaylistsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetPlaylists"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"enabled"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"first"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}},"defaultValue":{"kind":"IntValue","value":"20"}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"after"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"sortBy"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"sortDirection"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"search"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"playlists"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"enabled"},"value":{"kind":"Variable","name":{"kind":"Name","value":"enabled"}}},{"kind":"Argument","name":{"kind":"Name","value":"first"},"value":{"kind":"Variable","name":{"kind":"Name","value":"first"}}},{"kind":"Argument","name":{"kind":"Name","value":"after"},"value":{"kind":"Variable","name":{"kind":"Name","value":"after"}}},{"kind":"Argument","name":{"kind":"Name","value":"sortBy"},"value":{"kind":"Variable","name":{"kind":"Name","value":"sortBy"}}},{"kind":"Argument","name":{"kind":"Name","value":"sortDirection"},"value":{"kind":"Variable","name":{"kind":"Name","value":"sortDirection"}}},{"kind":"Argument","name":{"kind":"Name","value":"search"},"value":{"kind":"Variable","name":{"kind":"Name","value":"search"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalCount"}},{"kind":"Field","name":{"kind":"Name","value":"pageInfo"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"hasNextPage"}},{"kind":"Field","name":{"kind":"Name","value":"hasPreviousPage"}},{"kind":"Field","name":{"kind":"Name","value":"startCursor"}},{"kind":"Field","name":{"kind":"Name","value":"endCursor"}}]}},{"kind":"Field","name":{"kind":"Name","value":"edges"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"url"}},{"kind":"Field","name":{"kind":"Name","value":"enabled"}},{"kind":"Field","name":{"kind":"Name","value":"autoTrackArtists"}},{"kind":"Field","name":{"kind":"Name","value":"lastSyncedAt"}}]}}]}}]}}]} as unknown as DocumentNode<GetPlaylistsQuery, GetPlaylistsQueryVariables>;
export const SyncArtistDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"SyncArtist"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"artistId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"syncArtist"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"artistId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"artistId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"gid"}},{"kind":"Field","name":{"kind":"Name","value":"spotifyUri"}},{"kind":"Field","name":{"kind":"Name","value":"isTracked"}},{"kind":"Field","name":{"kind":"Name","value":"addedAt"}},{"kind":"Field","name":{"kind":"Name","value":"lastSynced"}},{"kind":"Field","name":{"kind":"Name","value":"undownloadedCount"}}]}}]}}]} as unknown as DocumentNode<SyncArtistMutation, SyncArtistMutationVariables>;
export const DownloadArtistDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DownloadArtist"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"artistId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"downloadArtist"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"artistId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"artistId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}}]}}]}}]} as unknown as DocumentNode<DownloadArtistMutation, DownloadArtistMutationVariables>;
export const SyncPlaylistDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"SyncPlaylist"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"playlistId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"syncPlaylist"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"playlistId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"playlistId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}}]}}]}}]} as unknown as DocumentNode<SyncPlaylistMutation, SyncPlaylistMutationVariables>;
export const TrackArtistDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"TrackArtist"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"artistId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"trackArtist"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"artistId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"artistId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"artist"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"isTracked"}}]}}]}}]}}]} as unknown as DocumentNode<TrackArtistMutation, TrackArtistMutationVariables>;
export const UntrackArtistDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UntrackArtist"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"artistId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"untrackArtist"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"artistId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"artistId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"artist"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"isTracked"}}]}}]}}]}}]} as unknown as DocumentNode<UntrackArtistMutation, UntrackArtistMutationVariables>;
export const SetAlbumWantedDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"SetAlbumWanted"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"albumId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"wanted"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"setAlbumWanted"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"albumId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"albumId"}}},{"kind":"Argument","name":{"kind":"Name","value":"wanted"},"value":{"kind":"Variable","name":{"kind":"Name","value":"wanted"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"album"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"wanted"}}]}}]}}]}}]} as unknown as DocumentNode<SetAlbumWantedMutation, SetAlbumWantedMutationVariables>;
export const DownloadAlbumDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DownloadAlbum"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"albumId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"downloadAlbum"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"albumId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"albumId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"spotifyGid"}},{"kind":"Field","name":{"kind":"Name","value":"wanted"}},{"kind":"Field","name":{"kind":"Name","value":"downloaded"}}]}}]}}]} as unknown as DocumentNode<DownloadAlbumMutation, DownloadAlbumMutationVariables>;
export const TogglePlaylistDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"TogglePlaylist"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"playlistId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"togglePlaylist"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"playlistId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"playlistId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"playlist"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"enabled"}}]}}]}}]}}]} as unknown as DocumentNode<TogglePlaylistMutation, TogglePlaylistMutationVariables>;
export const ForceSyncPlaylistDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"ForceSyncPlaylist"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"playlistId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"syncPlaylist"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"playlistId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"playlistId"}}},{"kind":"Argument","name":{"kind":"Name","value":"force"},"value":{"kind":"BooleanValue","value":true}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}}]}}]}}]} as unknown as DocumentNode<ForceSyncPlaylistMutation, ForceSyncPlaylistMutationVariables>;
export const TogglePlaylistAutoTrackDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"TogglePlaylistAutoTrack"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"playlistId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"togglePlaylistAutoTrack"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"playlistId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"playlistId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"playlist"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"autoTrackArtists"}}]}}]}}]}}]} as unknown as DocumentNode<TogglePlaylistAutoTrackMutation, TogglePlaylistAutoTrackMutationVariables>;
export const UpdatePlaylistDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdatePlaylist"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"playlistId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"name"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"url"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"autoTrackArtists"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updatePlaylist"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"playlistId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"playlistId"}}},{"kind":"Argument","name":{"kind":"Name","value":"name"},"value":{"kind":"Variable","name":{"kind":"Name","value":"name"}}},{"kind":"Argument","name":{"kind":"Name","value":"url"},"value":{"kind":"Variable","name":{"kind":"Name","value":"url"}}},{"kind":"Argument","name":{"kind":"Name","value":"autoTrackArtists"},"value":{"kind":"Variable","name":{"kind":"Name","value":"autoTrackArtists"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}}]}}]}}]} as unknown as DocumentNode<UpdatePlaylistMutation, UpdatePlaylistMutationVariables>;
export const CreatePlaylistDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CreatePlaylist"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"name"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"url"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"autoTrackArtists"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createPlaylist"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"name"},"value":{"kind":"Variable","name":{"kind":"Name","value":"name"}}},{"kind":"Argument","name":{"kind":"Name","value":"url"},"value":{"kind":"Variable","name":{"kind":"Name","value":"url"}}},{"kind":"Argument","name":{"kind":"Name","value":"autoTrackArtists"},"value":{"kind":"Variable","name":{"kind":"Name","value":"autoTrackArtists"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"url"}},{"kind":"Field","name":{"kind":"Name","value":"enabled"}},{"kind":"Field","name":{"kind":"Name","value":"autoTrackArtists"}}]}}]}}]} as unknown as DocumentNode<CreatePlaylistMutation, CreatePlaylistMutationVariables>;
export const SyncAllTrackedArtistsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"SyncAllTrackedArtists"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"syncAllTrackedArtists"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}}]}}]}}]} as unknown as DocumentNode<SyncAllTrackedArtistsMutation, SyncAllTrackedArtistsMutationVariables>;
export const DownloadAllTrackedArtistsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DownloadAllTrackedArtists"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"downloadAllTrackedArtists"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}}]}}]}}]} as unknown as DocumentNode<DownloadAllTrackedArtistsMutation, DownloadAllTrackedArtistsMutationVariables>;
export const DownloadAllPlaylistsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DownloadAllPlaylists"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"downloadAllPlaylists"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}}]}}]}}]} as unknown as DocumentNode<DownloadAllPlaylistsMutation, DownloadAllPlaylistsMutationVariables>;
export const DownloadUrlDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DownloadUrl"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"url"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"autoTrackArtists"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"downloadUrl"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"url"},"value":{"kind":"Variable","name":{"kind":"Name","value":"url"}}},{"kind":"Argument","name":{"kind":"Name","value":"autoTrackArtists"},"value":{"kind":"Variable","name":{"kind":"Name","value":"autoTrackArtists"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"artist"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"gid"}},{"kind":"Field","name":{"kind":"Name","value":"isTracked"}},{"kind":"Field","name":{"kind":"Name","value":"addedAt"}},{"kind":"Field","name":{"kind":"Name","value":"lastSynced"}}]}},{"kind":"Field","name":{"kind":"Name","value":"album"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"spotifyGid"}},{"kind":"Field","name":{"kind":"Name","value":"totalTracks"}},{"kind":"Field","name":{"kind":"Name","value":"wanted"}},{"kind":"Field","name":{"kind":"Name","value":"downloaded"}},{"kind":"Field","name":{"kind":"Name","value":"albumType"}},{"kind":"Field","name":{"kind":"Name","value":"albumGroup"}},{"kind":"Field","name":{"kind":"Name","value":"artist"}},{"kind":"Field","name":{"kind":"Name","value":"artistId"}}]}},{"kind":"Field","name":{"kind":"Name","value":"playlist"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"url"}},{"kind":"Field","name":{"kind":"Name","value":"enabled"}},{"kind":"Field","name":{"kind":"Name","value":"autoTrackArtists"}},{"kind":"Field","name":{"kind":"Name","value":"lastSyncedAt"}}]}}]}}]}}]} as unknown as DocumentNode<DownloadUrlMutation, DownloadUrlMutationVariables>;
export const CreatePlaylistFromDownloadDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CreatePlaylistFromDownload"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"name"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"url"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"autoTrackArtists"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createPlaylist"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"name"},"value":{"kind":"Variable","name":{"kind":"Name","value":"name"}}},{"kind":"Argument","name":{"kind":"Name","value":"url"},"value":{"kind":"Variable","name":{"kind":"Name","value":"url"}}},{"kind":"Argument","name":{"kind":"Name","value":"autoTrackArtists"},"value":{"kind":"Variable","name":{"kind":"Name","value":"autoTrackArtists"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"url"}},{"kind":"Field","name":{"kind":"Name","value":"enabled"}},{"kind":"Field","name":{"kind":"Name","value":"autoTrackArtists"}},{"kind":"Field","name":{"kind":"Name","value":"lastSyncedAt"}}]}}]}}]} as unknown as DocumentNode<CreatePlaylistFromDownloadMutation, CreatePlaylistFromDownloadMutationVariables>;
export const GetSystemStatusDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetSystemStatus"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"systemHealth"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"canDownload"}},{"kind":"Field","name":{"kind":"Name","value":"downloadBlockerReason"}},{"kind":"Field","name":{"kind":"Name","value":"authentication"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"cookiesValid"}},{"kind":"Field","name":{"kind":"Name","value":"cookiesErrorType"}},{"kind":"Field","name":{"kind":"Name","value":"cookiesExpireInDays"}},{"kind":"Field","name":{"kind":"Name","value":"poTokenConfigured"}},{"kind":"Field","name":{"kind":"Name","value":"spotifyUserAuthEnabled"}},{"kind":"Field","name":{"kind":"Name","value":"spotifyAuthMode"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"queueStatus"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalPendingTasks"}},{"kind":"Field","name":{"kind":"Name","value":"queueSize"}}]}}]}}]} as unknown as DocumentNode<GetSystemStatusQuery, GetSystemStatusQueryVariables>;
export const DisconnectSpotifyDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DisconnectSpotify"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"disconnectSpotify"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}}]}}]}}]} as unknown as DocumentNode<DisconnectSpotifyMutation, DisconnectSpotifyMutationVariables>;
export const GetSongsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetSongs"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"first"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"after"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"artistId"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"downloaded"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"unavailable"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"sortBy"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"sortDirection"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"search"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"songs"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"first"},"value":{"kind":"Variable","name":{"kind":"Name","value":"first"}}},{"kind":"Argument","name":{"kind":"Name","value":"after"},"value":{"kind":"Variable","name":{"kind":"Name","value":"after"}}},{"kind":"Argument","name":{"kind":"Name","value":"artistId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"artistId"}}},{"kind":"Argument","name":{"kind":"Name","value":"downloaded"},"value":{"kind":"Variable","name":{"kind":"Name","value":"downloaded"}}},{"kind":"Argument","name":{"kind":"Name","value":"unavailable"},"value":{"kind":"Variable","name":{"kind":"Name","value":"unavailable"}}},{"kind":"Argument","name":{"kind":"Name","value":"sortBy"},"value":{"kind":"Variable","name":{"kind":"Name","value":"sortBy"}}},{"kind":"Argument","name":{"kind":"Name","value":"sortDirection"},"value":{"kind":"Variable","name":{"kind":"Name","value":"sortDirection"}}},{"kind":"Argument","name":{"kind":"Name","value":"search"},"value":{"kind":"Variable","name":{"kind":"Name","value":"search"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"edges"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"gid"}},{"kind":"Field","name":{"kind":"Name","value":"primaryArtist"}},{"kind":"Field","name":{"kind":"Name","value":"primaryArtistId"}},{"kind":"Field","name":{"kind":"Name","value":"primaryArtistGid"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"failedCount"}},{"kind":"Field","name":{"kind":"Name","value":"bitrate"}},{"kind":"Field","name":{"kind":"Name","value":"unavailable"}},{"kind":"Field","name":{"kind":"Name","value":"filePath"}},{"kind":"Field","name":{"kind":"Name","value":"downloaded"}},{"kind":"Field","name":{"kind":"Name","value":"spotifyUri"}}]}},{"kind":"Field","name":{"kind":"Name","value":"pageInfo"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"hasNextPage"}},{"kind":"Field","name":{"kind":"Name","value":"hasPreviousPage"}},{"kind":"Field","name":{"kind":"Name","value":"startCursor"}},{"kind":"Field","name":{"kind":"Name","value":"endCursor"}}]}},{"kind":"Field","name":{"kind":"Name","value":"totalCount"}}]}}]}}]} as unknown as DocumentNode<GetSongsQuery, GetSongsQueryVariables>;
export const GetSongDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetSong"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"id"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"song"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"id"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"gid"}},{"kind":"Field","name":{"kind":"Name","value":"primaryArtist"}},{"kind":"Field","name":{"kind":"Name","value":"primaryArtistId"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"failedCount"}},{"kind":"Field","name":{"kind":"Name","value":"bitrate"}},{"kind":"Field","name":{"kind":"Name","value":"unavailable"}},{"kind":"Field","name":{"kind":"Name","value":"filePath"}},{"kind":"Field","name":{"kind":"Name","value":"downloaded"}},{"kind":"Field","name":{"kind":"Name","value":"spotifyUri"}}]}}]}}]} as unknown as DocumentNode<GetSongQuery, GetSongQueryVariables>;
export const GetSystemHealthDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetSystemHealth"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"systemHealth"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"canDownload"}},{"kind":"Field","name":{"kind":"Name","value":"downloadBlockerReason"}},{"kind":"Field","name":{"kind":"Name","value":"authentication"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"cookiesValid"}},{"kind":"Field","name":{"kind":"Name","value":"cookiesErrorType"}},{"kind":"Field","name":{"kind":"Name","value":"cookiesErrorMessage"}},{"kind":"Field","name":{"kind":"Name","value":"cookiesExpireInDays"}},{"kind":"Field","name":{"kind":"Name","value":"poTokenConfigured"}},{"kind":"Field","name":{"kind":"Name","value":"spotifyAuthMode"}},{"kind":"Field","name":{"kind":"Name","value":"spotifyTokenValid"}},{"kind":"Field","name":{"kind":"Name","value":"spotifyTokenExpired"}},{"kind":"Field","name":{"kind":"Name","value":"spotifyTokenExpiresInHours"}},{"kind":"Field","name":{"kind":"Name","value":"spotifyTokenErrorMessage"}}]}}]}}]}}]} as unknown as DocumentNode<GetSystemHealthQuery, GetSystemHealthQueryVariables>;
export const GetQueueStatusDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetQueueStatus"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"queueStatus"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalPendingTasks"}},{"kind":"Field","name":{"kind":"Name","value":"taskCounts"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"taskName"}},{"kind":"Field","name":{"kind":"Name","value":"count"}}]}},{"kind":"Field","name":{"kind":"Name","value":"queueSize"}}]}}]}}]} as unknown as DocumentNode<GetQueueStatusQuery, GetQueueStatusQueryVariables>;
export const CancelAllPendingTasksDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CancelAllPendingTasks"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"cancelAllPendingTasks"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}}]}}]}}]} as unknown as DocumentNode<CancelAllPendingTasksMutation, CancelAllPendingTasksMutationVariables>;
export const CancelTasksByNameDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CancelTasksByName"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"taskName"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"cancelTasksByName"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"taskName"},"value":{"kind":"Variable","name":{"kind":"Name","value":"taskName"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}}]}}]}}]} as unknown as DocumentNode<CancelTasksByNameMutation, CancelTasksByNameMutationVariables>;
export const CancelRunningTasksByNameDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CancelRunningTasksByName"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"taskName"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"cancelRunningTasksByName"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"taskName"},"value":{"kind":"Variable","name":{"kind":"Name","value":"taskName"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}}]}}]}}]} as unknown as DocumentNode<CancelRunningTasksByNameMutation, CancelRunningTasksByNameMutationVariables>;
export const CancelAllTasksDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CancelAllTasks"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"cancelAllTasks"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}}]}}]}}]} as unknown as DocumentNode<CancelAllTasksMutation, CancelAllTasksMutationVariables>;
export const GetTaskHistoryDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetTaskHistory"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"first"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}},"defaultValue":{"kind":"IntValue","value":"20"}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"after"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"status"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"type"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"entityType"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"search"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"taskHistory"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"first"},"value":{"kind":"Variable","name":{"kind":"Name","value":"first"}}},{"kind":"Argument","name":{"kind":"Name","value":"after"},"value":{"kind":"Variable","name":{"kind":"Name","value":"after"}}},{"kind":"Argument","name":{"kind":"Name","value":"status"},"value":{"kind":"Variable","name":{"kind":"Name","value":"status"}}},{"kind":"Argument","name":{"kind":"Name","value":"type"},"value":{"kind":"Variable","name":{"kind":"Name","value":"type"}}},{"kind":"Argument","name":{"kind":"Name","value":"entityType"},"value":{"kind":"Variable","name":{"kind":"Name","value":"entityType"}}},{"kind":"Argument","name":{"kind":"Name","value":"search"},"value":{"kind":"Variable","name":{"kind":"Name","value":"search"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalCount"}},{"kind":"Field","name":{"kind":"Name","value":"pageInfo"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"hasNextPage"}},{"kind":"Field","name":{"kind":"Name","value":"hasPreviousPage"}},{"kind":"Field","name":{"kind":"Name","value":"startCursor"}},{"kind":"Field","name":{"kind":"Name","value":"endCursor"}}]}},{"kind":"Field","name":{"kind":"Name","value":"edges"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"node"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"taskId"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"entityId"}},{"kind":"Field","name":{"kind":"Name","value":"entityType"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"startedAt"}},{"kind":"Field","name":{"kind":"Name","value":"completedAt"}},{"kind":"Field","name":{"kind":"Name","value":"durationSeconds"}},{"kind":"Field","name":{"kind":"Name","value":"progressPercentage"}},{"kind":"Field","name":{"kind":"Name","value":"logMessages"}}]}},{"kind":"Field","name":{"kind":"Name","value":"cursor"}}]}}]}}]}}]} as unknown as DocumentNode<GetTaskHistoryQuery, GetTaskHistoryQueryVariables>;
export const GetArtistsTestDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetArtistsTest"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"isTracked"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"first"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}},"defaultValue":{"kind":"IntValue","value":"20"}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"after"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"search"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"artists"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"isTracked"},"value":{"kind":"Variable","name":{"kind":"Name","value":"isTracked"}}},{"kind":"Argument","name":{"kind":"Name","value":"first"},"value":{"kind":"Variable","name":{"kind":"Name","value":"first"}}},{"kind":"Argument","name":{"kind":"Name","value":"after"},"value":{"kind":"Variable","name":{"kind":"Name","value":"after"}}},{"kind":"Argument","name":{"kind":"Name","value":"search"},"value":{"kind":"Variable","name":{"kind":"Name","value":"search"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalCount"}},{"kind":"Field","name":{"kind":"Name","value":"pageInfo"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"hasNextPage"}},{"kind":"Field","name":{"kind":"Name","value":"hasPreviousPage"}},{"kind":"Field","name":{"kind":"Name","value":"startCursor"}},{"kind":"Field","name":{"kind":"Name","value":"endCursor"}}]}},{"kind":"Field","name":{"kind":"Name","value":"edges"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"gid"}},{"kind":"Field","name":{"kind":"Name","value":"isTracked"}},{"kind":"Field","name":{"kind":"Name","value":"addedAt"}},{"kind":"Field","name":{"kind":"Name","value":"lastSynced"}}]}}]}}]}}]} as unknown as DocumentNode<GetArtistsTestQuery, GetArtistsTestQueryVariables>;
export const GetAlbumsTestDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetAlbumsTest"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"artistId"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"wanted"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"downloaded"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"first"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}},"defaultValue":{"kind":"IntValue","value":"20"}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"after"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"sortBy"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"sortDirection"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"search"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"albums"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"artistId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"artistId"}}},{"kind":"Argument","name":{"kind":"Name","value":"wanted"},"value":{"kind":"Variable","name":{"kind":"Name","value":"wanted"}}},{"kind":"Argument","name":{"kind":"Name","value":"downloaded"},"value":{"kind":"Variable","name":{"kind":"Name","value":"downloaded"}}},{"kind":"Argument","name":{"kind":"Name","value":"first"},"value":{"kind":"Variable","name":{"kind":"Name","value":"first"}}},{"kind":"Argument","name":{"kind":"Name","value":"after"},"value":{"kind":"Variable","name":{"kind":"Name","value":"after"}}},{"kind":"Argument","name":{"kind":"Name","value":"sortBy"},"value":{"kind":"Variable","name":{"kind":"Name","value":"sortBy"}}},{"kind":"Argument","name":{"kind":"Name","value":"sortDirection"},"value":{"kind":"Variable","name":{"kind":"Name","value":"sortDirection"}}},{"kind":"Argument","name":{"kind":"Name","value":"search"},"value":{"kind":"Variable","name":{"kind":"Name","value":"search"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalCount"}},{"kind":"Field","name":{"kind":"Name","value":"pageInfo"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"hasNextPage"}},{"kind":"Field","name":{"kind":"Name","value":"hasPreviousPage"}},{"kind":"Field","name":{"kind":"Name","value":"startCursor"}},{"kind":"Field","name":{"kind":"Name","value":"endCursor"}}]}},{"kind":"Field","name":{"kind":"Name","value":"edges"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"spotifyGid"}},{"kind":"Field","name":{"kind":"Name","value":"totalTracks"}},{"kind":"Field","name":{"kind":"Name","value":"wanted"}},{"kind":"Field","name":{"kind":"Name","value":"downloaded"}},{"kind":"Field","name":{"kind":"Name","value":"albumType"}},{"kind":"Field","name":{"kind":"Name","value":"albumGroup"}},{"kind":"Field","name":{"kind":"Name","value":"artist"}},{"kind":"Field","name":{"kind":"Name","value":"artistId"}}]}}]}}]}}]} as unknown as DocumentNode<GetAlbumsTestQuery, GetAlbumsTestQueryVariables>;
export const GetSongsTestDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetSongsTest"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"first"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"after"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"artistId"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"downloaded"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"unavailable"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"sortBy"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"sortDirection"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"search"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"songs"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"first"},"value":{"kind":"Variable","name":{"kind":"Name","value":"first"}}},{"kind":"Argument","name":{"kind":"Name","value":"after"},"value":{"kind":"Variable","name":{"kind":"Name","value":"after"}}},{"kind":"Argument","name":{"kind":"Name","value":"artistId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"artistId"}}},{"kind":"Argument","name":{"kind":"Name","value":"downloaded"},"value":{"kind":"Variable","name":{"kind":"Name","value":"downloaded"}}},{"kind":"Argument","name":{"kind":"Name","value":"unavailable"},"value":{"kind":"Variable","name":{"kind":"Name","value":"unavailable"}}},{"kind":"Argument","name":{"kind":"Name","value":"sortBy"},"value":{"kind":"Variable","name":{"kind":"Name","value":"sortBy"}}},{"kind":"Argument","name":{"kind":"Name","value":"sortDirection"},"value":{"kind":"Variable","name":{"kind":"Name","value":"sortDirection"}}},{"kind":"Argument","name":{"kind":"Name","value":"search"},"value":{"kind":"Variable","name":{"kind":"Name","value":"search"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"edges"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"gid"}},{"kind":"Field","name":{"kind":"Name","value":"primaryArtist"}},{"kind":"Field","name":{"kind":"Name","value":"primaryArtistId"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"failedCount"}},{"kind":"Field","name":{"kind":"Name","value":"bitrate"}},{"kind":"Field","name":{"kind":"Name","value":"unavailable"}},{"kind":"Field","name":{"kind":"Name","value":"filePath"}},{"kind":"Field","name":{"kind":"Name","value":"downloaded"}},{"kind":"Field","name":{"kind":"Name","value":"spotifyUri"}}]}},{"kind":"Field","name":{"kind":"Name","value":"pageInfo"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"hasNextPage"}},{"kind":"Field","name":{"kind":"Name","value":"hasPreviousPage"}},{"kind":"Field","name":{"kind":"Name","value":"startCursor"}},{"kind":"Field","name":{"kind":"Name","value":"endCursor"}}]}},{"kind":"Field","name":{"kind":"Name","value":"totalCount"}}]}}]}}]} as unknown as DocumentNode<GetSongsTestQuery, GetSongsTestQueryVariables>;