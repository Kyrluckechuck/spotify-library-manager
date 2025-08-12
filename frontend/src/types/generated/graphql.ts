import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = {
  [K in keyof T]: T[K];
};
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & {
  [SubKey in K]?: Maybe<T[SubKey]>;
};
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & {
  [SubKey in K]: Maybe<T[SubKey]>;
};
export type MakeEmpty<
  T extends { [key: string]: unknown },
  K extends keyof T,
> = { [_ in K]?: never };
export type Incremental<T> =
  | T
  | {
      [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never;
    };
const defaultOptions = {} as const;
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string };
  String: { input: string; output: string };
  Boolean: { input: boolean; output: boolean };
  Int: { input: number; output: number };
  Float: { input: number; output: number };
  DateTime: { input: string; output: string };
};

export type Album = {
  albumGroup?: Maybe<Scalars['String']['output']>;
  albumType?: Maybe<Scalars['String']['output']>;
  artist?: Maybe<Scalars['String']['output']>;
  artistId?: Maybe<Scalars['Int']['output']>;
  downloaded: Scalars['Boolean']['output'];
  id: Scalars['Int']['output'];
  name: Scalars['String']['output'];
  spotifyGid: Scalars['String']['output'];
  totalTracks: Scalars['Int']['output'];
  wanted: Scalars['Boolean']['output'];
};

export type AlbumConnection = {
  edges: Array<Album>;
  pageInfo: PageInfo;
  totalCount: Scalars['Int']['output'];
};

export type Artist = {
  addedAt?: Maybe<Scalars['DateTime']['output']>;
  gid: Scalars['String']['output'];
  id: Scalars['Int']['output'];
  isTracked: Scalars['Boolean']['output'];
  lastSynced?: Maybe<Scalars['DateTime']['output']>;
  name: Scalars['String']['output'];
};

export type ArtistConnection = {
  edges: Array<Artist>;
  pageInfo: PageInfo;
  totalCount: Scalars['Int']['output'];
};

export type DownloadHistory = {
  completedAt?: Maybe<Scalars['DateTime']['output']>;
  entityId: Scalars['String']['output'];
  entityType: Scalars['String']['output'];
  errorMessage?: Maybe<Scalars['String']['output']>;
  id: Scalars['String']['output'];
  startedAt: Scalars['DateTime']['output'];
  status: DownloadStatus;
};

export type DownloadProgress = {
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

export type EntityType = 'ALBUM' | 'ARTIST' | 'PLAYLIST' | 'TRACK';

export type HistoryConnection = {
  edges: Array<HistoryEdge>;
  pageInfo: PageInfo;
  totalCount: Scalars['Int']['output'];
};

export type HistoryEdge = {
  cursor: Scalars['String']['output'];
  node: DownloadHistory;
};

export type Mutation = {
  cancelAllPendingTasks: MutationResult;
  cancelAllTasks: MutationResult;
  cancelRunningTasksByName: MutationResult;
  cancelTasksByName: MutationResult;
  createPlaylist: Playlist;
  downloadAlbum: Album;
  downloadUrl: MutationResult;
  setAlbumWanted: MutationResult;
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
};

export type MutationResult = {
  album?: Maybe<Album>;
  artist?: Maybe<Artist>;
  message: Scalars['String']['output'];
  playlist?: Maybe<Playlist>;
  success: Scalars['Boolean']['output'];
};

export type PageInfo = {
  endCursor?: Maybe<Scalars['String']['output']>;
  hasNextPage: Scalars['Boolean']['output'];
  hasPreviousPage: Scalars['Boolean']['output'];
  startCursor?: Maybe<Scalars['String']['output']>;
};

export type Playlist = {
  autoTrackArtists: Scalars['Boolean']['output'];
  enabled: Scalars['Boolean']['output'];
  id: Scalars['Int']['output'];
  lastSyncedAt?: Maybe<Scalars['DateTime']['output']>;
  name: Scalars['String']['output'];
  url: Scalars['String']['output'];
};

export type PlaylistConnection = {
  edges: Array<Playlist>;
  pageInfo: PageInfo;
  totalCount: Scalars['Int']['output'];
};

export type Query = {
  album?: Maybe<Album>;
  albums: AlbumConnection;
  artist?: Maybe<Artist>;
  artists: ArtistConnection;
  downloadHistory: HistoryConnection;
  playlist?: Maybe<Playlist>;
  playlists: PlaylistConnection;
  queueStatus: QueueStatus;
  song?: Maybe<Song>;
  songs: SongConnection;
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
  queueSize: Scalars['Int']['output'];
  taskCounts: Array<TaskCount>;
  totalPendingTasks: Scalars['Int']['output'];
};

export type Song = {
  bitrate: Scalars['Int']['output'];
  createdAt: Scalars['DateTime']['output'];
  downloaded: Scalars['Boolean']['output'];
  failedCount: Scalars['Int']['output'];
  filePath?: Maybe<Scalars['String']['output']>;
  gid: Scalars['String']['output'];
  id: Scalars['Int']['output'];
  name: Scalars['String']['output'];
  primaryArtist: Scalars['String']['output'];
  primaryArtistId: Scalars['Int']['output'];
  spotifyUri: Scalars['String']['output'];
  unavailable: Scalars['Boolean']['output'];
};

export type SongConnection = {
  edges: Array<Song>;
  pageInfo: PageInfo;
  totalCount: Scalars['Int']['output'];
};

export type Subscription = {
  allDownloadProgress: DownloadProgress;
  downloadProgress: DownloadProgress;
};

export type SubscriptionDownloadProgressArgs = {
  entityId: Scalars['String']['input'];
};

export type TaskCount = {
  count: Scalars['Int']['output'];
  taskName: Scalars['String']['output'];
};

export type TaskHistory = {
  completedAt?: Maybe<Scalars['DateTime']['output']>;
  durationSeconds?: Maybe<Scalars['Int']['output']>;
  entityId: Scalars['String']['output'];
  entityType: EntityType;
  id: Scalars['String']['output'];
  logMessages: Array<Scalars['String']['output']>;
  progressPercentage?: Maybe<Scalars['Float']['output']>;
  startedAt: Scalars['DateTime']['output'];
  status: TaskStatus;
  taskId: Scalars['String']['output'];
  type: TaskType;
};

export type TaskHistoryConnection = {
  edges: Array<TaskHistoryEdge>;
  pageInfo: PageInfo;
  totalCount: Scalars['Int']['output'];
};

export type TaskHistoryEdge = {
  cursor: Scalars['String']['output'];
  node: TaskHistory;
};

export type TaskStatus = 'COMPLETED' | 'FAILED' | 'PENDING' | 'RUNNING';

export type TaskType = 'DOWNLOAD' | 'FETCH' | 'SYNC';

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

export type GetArtistQuery = {
  artist?: {
    id: number;
    name: string;
    gid: string;
    isTracked: boolean;
    addedAt?: string | null;
    lastSynced?: string | null;
  } | null;
};

export type GetArtistsQueryVariables = Exact<{
  isTracked?: InputMaybe<Scalars['Boolean']['input']>;
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
}>;

export type GetArtistsQuery = {
  artists: {
    totalCount: number;
    pageInfo: {
      hasNextPage: boolean;
      hasPreviousPage: boolean;
      startCursor?: string | null;
      endCursor?: string | null;
    };
    edges: Array<{
      id: number;
      name: string;
      gid: string;
      isTracked: boolean;
      addedAt?: string | null;
      lastSynced?: string | null;
    }>;
  };
};

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

export type GetAlbumsQuery = {
  albums: {
    totalCount: number;
    pageInfo: {
      hasNextPage: boolean;
      hasPreviousPage: boolean;
      startCursor?: string | null;
      endCursor?: string | null;
    };
    edges: Array<{
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
    }>;
  };
};

export type GetPlaylistsQueryVariables = Exact<{
  enabled?: InputMaybe<Scalars['Boolean']['input']>;
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  sortBy?: InputMaybe<Scalars['String']['input']>;
  sortDirection?: InputMaybe<Scalars['String']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
}>;

export type GetPlaylistsQuery = {
  playlists: {
    totalCount: number;
    pageInfo: {
      hasNextPage: boolean;
      hasPreviousPage: boolean;
      startCursor?: string | null;
      endCursor?: string | null;
    };
    edges: Array<{
      id: number;
      name: string;
      url: string;
      enabled: boolean;
      autoTrackArtists: boolean;
      lastSyncedAt?: string | null;
    }>;
  };
};

export type SyncArtistMutationVariables = Exact<{
  artistId: Scalars['String']['input'];
}>;

export type SyncArtistMutation = {
  syncArtist: {
    id: number;
    name: string;
    gid: string;
    isTracked: boolean;
    addedAt?: string | null;
    lastSynced?: string | null;
  };
};

export type SyncPlaylistMutationVariables = Exact<{
  playlistId: Scalars['Int']['input'];
}>;

export type SyncPlaylistMutation = {
  syncPlaylist: { success: boolean; message: string };
};

export type TrackArtistMutationVariables = Exact<{
  artistId: Scalars['Int']['input'];
}>;

export type TrackArtistMutation = {
  trackArtist: {
    success: boolean;
    message: string;
    artist?: { id: number; name: string; isTracked: boolean } | null;
  };
};

export type UntrackArtistMutationVariables = Exact<{
  artistId: Scalars['Int']['input'];
}>;

export type UntrackArtistMutation = {
  untrackArtist: {
    success: boolean;
    message: string;
    artist?: { id: number; name: string; isTracked: boolean } | null;
  };
};

export type SetAlbumWantedMutationVariables = Exact<{
  albumId: Scalars['Int']['input'];
  wanted: Scalars['Boolean']['input'];
}>;

export type SetAlbumWantedMutation = {
  setAlbumWanted: {
    success: boolean;
    message: string;
    album?: { id: number; name: string; wanted: boolean } | null;
  };
};

export type TogglePlaylistMutationVariables = Exact<{
  playlistId: Scalars['Int']['input'];
}>;

export type TogglePlaylistMutation = {
  togglePlaylist: {
    success: boolean;
    message: string;
    playlist?: { id: number; name: string; enabled: boolean } | null;
  };
};

export type DownloadUrlMutationVariables = Exact<{
  url: Scalars['String']['input'];
  autoTrackArtists?: InputMaybe<Scalars['Boolean']['input']>;
}>;

export type DownloadUrlMutation = {
  downloadUrl: {
    success: boolean;
    message: string;
    artist?: {
      id: number;
      name: string;
      gid: string;
      isTracked: boolean;
      addedAt?: string | null;
      lastSynced?: string | null;
    } | null;
    album?: {
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
    } | null;
    playlist?: {
      id: number;
      name: string;
      url: string;
      enabled: boolean;
      autoTrackArtists: boolean;
      lastSyncedAt?: string | null;
    } | null;
  };
};

export type CreatePlaylistMutationVariables = Exact<{
  name: Scalars['String']['input'];
  url: Scalars['String']['input'];
  autoTrackArtists: Scalars['Boolean']['input'];
}>;

export type CreatePlaylistMutation = {
  createPlaylist: {
    id: number;
    name: string;
    url: string;
    enabled: boolean;
    autoTrackArtists: boolean;
    lastSyncedAt?: string | null;
  };
};

export type UpdatePlaylistMutationVariables = Exact<{
  playlistId: Scalars['Int']['input'];
  name: Scalars['String']['input'];
  autoTrackArtists: Scalars['Boolean']['input'];
}>;

export type UpdatePlaylistMutation = {
  updatePlaylist: { success: boolean; message: string };
};

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

export type GetSongsQuery = {
  songs: {
    totalCount: number;
    edges: Array<{
      id: number;
      name: string;
      gid: string;
      primaryArtist: string;
      primaryArtistId: number;
      createdAt: string;
      failedCount: number;
      bitrate: number;
      unavailable: boolean;
      filePath?: string | null;
      downloaded: boolean;
      spotifyUri: string;
    }>;
    pageInfo: {
      hasNextPage: boolean;
      hasPreviousPage: boolean;
      startCursor?: string | null;
      endCursor?: string | null;
    };
  };
};

export type GetSongQueryVariables = Exact<{
  id: Scalars['String']['input'];
}>;

export type GetSongQuery = {
  song?: {
    id: number;
    name: string;
    gid: string;
    primaryArtist: string;
    primaryArtistId: number;
    createdAt: string;
    failedCount: number;
    bitrate: number;
    unavailable: boolean;
    filePath?: string | null;
    downloaded: boolean;
    spotifyUri: string;
  } | null;
};

export type GetQueueStatusQueryVariables = Exact<{ [key: string]: never }>;

export type GetQueueStatusQuery = {
  queueStatus: {
    totalPendingTasks: number;
    queueSize: number;
    taskCounts: Array<{ taskName: string; count: number }>;
  };
};

export type CancelAllPendingTasksMutationVariables = Exact<{
  [key: string]: never;
}>;

export type CancelAllPendingTasksMutation = {
  cancelAllPendingTasks: { success: boolean; message: string };
};

export type CancelTasksByNameMutationVariables = Exact<{
  taskName: Scalars['String']['input'];
}>;

export type CancelTasksByNameMutation = {
  cancelTasksByName: { success: boolean; message: string };
};

export type CancelRunningTasksByNameMutationVariables = Exact<{
  taskName: Scalars['String']['input'];
}>;

export type CancelRunningTasksByNameMutation = {
  cancelRunningTasksByName: { success: boolean; message: string };
};

export type CancelAllTasksMutationVariables = Exact<{ [key: string]: never }>;

export type CancelAllTasksMutation = {
  cancelAllTasks: { success: boolean; message: string };
};

export type GetTaskHistoryQueryVariables = Exact<{
  first?: InputMaybe<Scalars['Int']['input']>;
  after?: InputMaybe<Scalars['String']['input']>;
  status?: InputMaybe<Scalars['String']['input']>;
  type?: InputMaybe<Scalars['String']['input']>;
  entityType?: InputMaybe<Scalars['String']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
}>;

export type GetTaskHistoryQuery = {
  taskHistory: {
    totalCount: number;
    pageInfo: {
      hasNextPage: boolean;
      hasPreviousPage: boolean;
      startCursor?: string | null;
      endCursor?: string | null;
    };
    edges: Array<{
      cursor: string;
      node: {
        id: string;
        taskId: string;
        type: TaskType;
        entityId: string;
        entityType: EntityType;
        status: TaskStatus;
        startedAt: string;
        completedAt?: string | null;
        durationSeconds?: number | null;
        progressPercentage?: number | null;
        logMessages: Array<string>;
      };
    }>;
  };
};

export const GetArtistDocument = gql`
  query GetArtist($id: String!) {
    artist(id: $id) {
      id
      name
      gid
      isTracked
      addedAt
      lastSynced
    }
  }
`;

/**
 * __useGetArtistQuery__
 *
 * To run a query within a React component, call `useGetArtistQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetArtistQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetArtistQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useGetArtistQuery(
  baseOptions: Apollo.QueryHookOptions<
    GetArtistQuery,
    GetArtistQueryVariables
  > &
    ({ variables: GetArtistQueryVariables; skip?: boolean } | { skip: boolean })
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<GetArtistQuery, GetArtistQueryVariables>(
    GetArtistDocument,
    options
  );
}
export function useGetArtistLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<
    GetArtistQuery,
    GetArtistQueryVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<GetArtistQuery, GetArtistQueryVariables>(
    GetArtistDocument,
    options
  );
}
export function useGetArtistSuspenseQuery(
  baseOptions?:
    | Apollo.SkipToken
    | Apollo.SuspenseQueryHookOptions<GetArtistQuery, GetArtistQueryVariables>
) {
  const options =
    baseOptions === Apollo.skipToken
      ? baseOptions
      : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<GetArtistQuery, GetArtistQueryVariables>(
    GetArtistDocument,
    options
  );
}
export type GetArtistQueryHookResult = ReturnType<typeof useGetArtistQuery>;
export type GetArtistLazyQueryHookResult = ReturnType<
  typeof useGetArtistLazyQuery
>;
export type GetArtistSuspenseQueryHookResult = ReturnType<
  typeof useGetArtistSuspenseQuery
>;
export type GetArtistQueryResult = Apollo.QueryResult<
  GetArtistQuery,
  GetArtistQueryVariables
>;
export const GetArtistsDocument = gql`
  query GetArtists(
    $isTracked: Boolean
    $first: Int = 20
    $after: String
    $search: String
  ) {
    artists(
      isTracked: $isTracked
      first: $first
      after: $after
      search: $search
    ) {
      totalCount
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        id
        name
        gid
        isTracked
        addedAt
        lastSynced
      }
    }
  }
`;

/**
 * __useGetArtistsQuery__
 *
 * To run a query within a React component, call `useGetArtistsQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetArtistsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetArtistsQuery({
 *   variables: {
 *      isTracked: // value for 'isTracked'
 *      first: // value for 'first'
 *      after: // value for 'after'
 *      search: // value for 'search'
 *   },
 * });
 */
export function useGetArtistsQuery(
  baseOptions?: Apollo.QueryHookOptions<
    GetArtistsQuery,
    GetArtistsQueryVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<GetArtistsQuery, GetArtistsQueryVariables>(
    GetArtistsDocument,
    options
  );
}
export function useGetArtistsLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<
    GetArtistsQuery,
    GetArtistsQueryVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<GetArtistsQuery, GetArtistsQueryVariables>(
    GetArtistsDocument,
    options
  );
}
export function useGetArtistsSuspenseQuery(
  baseOptions?:
    | Apollo.SkipToken
    | Apollo.SuspenseQueryHookOptions<GetArtistsQuery, GetArtistsQueryVariables>
) {
  const options =
    baseOptions === Apollo.skipToken
      ? baseOptions
      : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<GetArtistsQuery, GetArtistsQueryVariables>(
    GetArtistsDocument,
    options
  );
}
export type GetArtistsQueryHookResult = ReturnType<typeof useGetArtistsQuery>;
export type GetArtistsLazyQueryHookResult = ReturnType<
  typeof useGetArtistsLazyQuery
>;
export type GetArtistsSuspenseQueryHookResult = ReturnType<
  typeof useGetArtistsSuspenseQuery
>;
export type GetArtistsQueryResult = Apollo.QueryResult<
  GetArtistsQuery,
  GetArtistsQueryVariables
>;
export const GetAlbumsDocument = gql`
  query GetAlbums(
    $artistId: Int
    $wanted: Boolean
    $downloaded: Boolean
    $first: Int = 20
    $after: String
    $sortBy: String
    $sortDirection: String
    $search: String
  ) {
    albums(
      artistId: $artistId
      wanted: $wanted
      downloaded: $downloaded
      first: $first
      after: $after
      sortBy: $sortBy
      sortDirection: $sortDirection
      search: $search
    ) {
      totalCount
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        id
        name
        spotifyGid
        totalTracks
        wanted
        downloaded
        albumType
        albumGroup
        artist
        artistId
      }
    }
  }
`;

/**
 * __useGetAlbumsQuery__
 *
 * To run a query within a React component, call `useGetAlbumsQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetAlbumsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetAlbumsQuery({
 *   variables: {
 *      artistId: // value for 'artistId'
 *      wanted: // value for 'wanted'
 *      downloaded: // value for 'downloaded'
 *      first: // value for 'first'
 *      after: // value for 'after'
 *      sortBy: // value for 'sortBy'
 *      sortDirection: // value for 'sortDirection'
 *      search: // value for 'search'
 *   },
 * });
 */
export function useGetAlbumsQuery(
  baseOptions?: Apollo.QueryHookOptions<GetAlbumsQuery, GetAlbumsQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<GetAlbumsQuery, GetAlbumsQueryVariables>(
    GetAlbumsDocument,
    options
  );
}
export function useGetAlbumsLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<
    GetAlbumsQuery,
    GetAlbumsQueryVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<GetAlbumsQuery, GetAlbumsQueryVariables>(
    GetAlbumsDocument,
    options
  );
}
export function useGetAlbumsSuspenseQuery(
  baseOptions?:
    | Apollo.SkipToken
    | Apollo.SuspenseQueryHookOptions<GetAlbumsQuery, GetAlbumsQueryVariables>
) {
  const options =
    baseOptions === Apollo.skipToken
      ? baseOptions
      : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<GetAlbumsQuery, GetAlbumsQueryVariables>(
    GetAlbumsDocument,
    options
  );
}
export type GetAlbumsQueryHookResult = ReturnType<typeof useGetAlbumsQuery>;
export type GetAlbumsLazyQueryHookResult = ReturnType<
  typeof useGetAlbumsLazyQuery
>;
export type GetAlbumsSuspenseQueryHookResult = ReturnType<
  typeof useGetAlbumsSuspenseQuery
>;
export type GetAlbumsQueryResult = Apollo.QueryResult<
  GetAlbumsQuery,
  GetAlbumsQueryVariables
>;
export const GetPlaylistsDocument = gql`
  query GetPlaylists(
    $enabled: Boolean
    $first: Int = 20
    $after: String
    $sortBy: String
    $sortDirection: String
    $search: String
  ) {
    playlists(
      enabled: $enabled
      first: $first
      after: $after
      sortBy: $sortBy
      sortDirection: $sortDirection
      search: $search
    ) {
      totalCount
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        id
        name
        url
        enabled
        autoTrackArtists
        lastSyncedAt
      }
    }
  }
`;

/**
 * __useGetPlaylistsQuery__
 *
 * To run a query within a React component, call `useGetPlaylistsQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetPlaylistsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetPlaylistsQuery({
 *   variables: {
 *      enabled: // value for 'enabled'
 *      first: // value for 'first'
 *      after: // value for 'after'
 *      sortBy: // value for 'sortBy'
 *      sortDirection: // value for 'sortDirection'
 *      search: // value for 'search'
 *   },
 * });
 */
export function useGetPlaylistsQuery(
  baseOptions?: Apollo.QueryHookOptions<
    GetPlaylistsQuery,
    GetPlaylistsQueryVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<GetPlaylistsQuery, GetPlaylistsQueryVariables>(
    GetPlaylistsDocument,
    options
  );
}
export function useGetPlaylistsLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<
    GetPlaylistsQuery,
    GetPlaylistsQueryVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<GetPlaylistsQuery, GetPlaylistsQueryVariables>(
    GetPlaylistsDocument,
    options
  );
}
export function useGetPlaylistsSuspenseQuery(
  baseOptions?:
    | Apollo.SkipToken
    | Apollo.SuspenseQueryHookOptions<
        GetPlaylistsQuery,
        GetPlaylistsQueryVariables
      >
) {
  const options =
    baseOptions === Apollo.skipToken
      ? baseOptions
      : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<GetPlaylistsQuery, GetPlaylistsQueryVariables>(
    GetPlaylistsDocument,
    options
  );
}
export type GetPlaylistsQueryHookResult = ReturnType<
  typeof useGetPlaylistsQuery
>;
export type GetPlaylistsLazyQueryHookResult = ReturnType<
  typeof useGetPlaylistsLazyQuery
>;
export type GetPlaylistsSuspenseQueryHookResult = ReturnType<
  typeof useGetPlaylistsSuspenseQuery
>;
export type GetPlaylistsQueryResult = Apollo.QueryResult<
  GetPlaylistsQuery,
  GetPlaylistsQueryVariables
>;
export const SyncArtistDocument = gql`
  mutation SyncArtist($artistId: String!) {
    syncArtist(artistId: $artistId) {
      id
      name
      gid
      isTracked
      addedAt
      lastSynced
    }
  }
`;
export type SyncArtistMutationFn = Apollo.MutationFunction<
  SyncArtistMutation,
  SyncArtistMutationVariables
>;

/**
 * __useSyncArtistMutation__
 *
 * To run a mutation, you first call `useSyncArtistMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useSyncArtistMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [syncArtistMutation, { data, loading, error }] = useSyncArtistMutation({
 *   variables: {
 *      artistId: // value for 'artistId'
 *   },
 * });
 */
export function useSyncArtistMutation(
  baseOptions?: Apollo.MutationHookOptions<
    SyncArtistMutation,
    SyncArtistMutationVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<SyncArtistMutation, SyncArtistMutationVariables>(
    SyncArtistDocument,
    options
  );
}
export type SyncArtistMutationHookResult = ReturnType<
  typeof useSyncArtistMutation
>;
export type SyncArtistMutationResult =
  Apollo.MutationResult<SyncArtistMutation>;
export type SyncArtistMutationOptions = Apollo.BaseMutationOptions<
  SyncArtistMutation,
  SyncArtistMutationVariables
>;
export const SyncPlaylistDocument = gql`
  mutation SyncPlaylist($playlistId: Int!) {
    syncPlaylist(playlistId: $playlistId) {
      success
      message
    }
  }
`;
export type SyncPlaylistMutationFn = Apollo.MutationFunction<
  SyncPlaylistMutation,
  SyncPlaylistMutationVariables
>;

/**
 * __useSyncPlaylistMutation__
 *
 * To run a mutation, you first call `useSyncPlaylistMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useSyncPlaylistMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [syncPlaylistMutation, { data, loading, error }] = useSyncPlaylistMutation({
 *   variables: {
 *      playlistId: // value for 'playlistId'
 *   },
 * });
 */
export function useSyncPlaylistMutation(
  baseOptions?: Apollo.MutationHookOptions<
    SyncPlaylistMutation,
    SyncPlaylistMutationVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<
    SyncPlaylistMutation,
    SyncPlaylistMutationVariables
  >(SyncPlaylistDocument, options);
}
export type SyncPlaylistMutationHookResult = ReturnType<
  typeof useSyncPlaylistMutation
>;
export type SyncPlaylistMutationResult =
  Apollo.MutationResult<SyncPlaylistMutation>;
export type SyncPlaylistMutationOptions = Apollo.BaseMutationOptions<
  SyncPlaylistMutation,
  SyncPlaylistMutationVariables
>;
export const TrackArtistDocument = gql`
  mutation TrackArtist($artistId: Int!) {
    trackArtist(artistId: $artistId) {
      success
      message
      artist {
        id
        name
        isTracked
      }
    }
  }
`;
export type TrackArtistMutationFn = Apollo.MutationFunction<
  TrackArtistMutation,
  TrackArtistMutationVariables
>;

/**
 * __useTrackArtistMutation__
 *
 * To run a mutation, you first call `useTrackArtistMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useTrackArtistMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [trackArtistMutation, { data, loading, error }] = useTrackArtistMutation({
 *   variables: {
 *      artistId: // value for 'artistId'
 *   },
 * });
 */
export function useTrackArtistMutation(
  baseOptions?: Apollo.MutationHookOptions<
    TrackArtistMutation,
    TrackArtistMutationVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<TrackArtistMutation, TrackArtistMutationVariables>(
    TrackArtistDocument,
    options
  );
}
export type TrackArtistMutationHookResult = ReturnType<
  typeof useTrackArtistMutation
>;
export type TrackArtistMutationResult =
  Apollo.MutationResult<TrackArtistMutation>;
export type TrackArtistMutationOptions = Apollo.BaseMutationOptions<
  TrackArtistMutation,
  TrackArtistMutationVariables
>;
export const UntrackArtistDocument = gql`
  mutation UntrackArtist($artistId: Int!) {
    untrackArtist(artistId: $artistId) {
      success
      message
      artist {
        id
        name
        isTracked
      }
    }
  }
`;
export type UntrackArtistMutationFn = Apollo.MutationFunction<
  UntrackArtistMutation,
  UntrackArtistMutationVariables
>;

/**
 * __useUntrackArtistMutation__
 *
 * To run a mutation, you first call `useUntrackArtistMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUntrackArtistMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [untrackArtistMutation, { data, loading, error }] = useUntrackArtistMutation({
 *   variables: {
 *      artistId: // value for 'artistId'
 *   },
 * });
 */
export function useUntrackArtistMutation(
  baseOptions?: Apollo.MutationHookOptions<
    UntrackArtistMutation,
    UntrackArtistMutationVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<
    UntrackArtistMutation,
    UntrackArtistMutationVariables
  >(UntrackArtistDocument, options);
}
export type UntrackArtistMutationHookResult = ReturnType<
  typeof useUntrackArtistMutation
>;
export type UntrackArtistMutationResult =
  Apollo.MutationResult<UntrackArtistMutation>;
export type UntrackArtistMutationOptions = Apollo.BaseMutationOptions<
  UntrackArtistMutation,
  UntrackArtistMutationVariables
>;
export const SetAlbumWantedDocument = gql`
  mutation SetAlbumWanted($albumId: Int!, $wanted: Boolean!) {
    setAlbumWanted(albumId: $albumId, wanted: $wanted) {
      success
      message
      album {
        id
        name
        wanted
      }
    }
  }
`;
export type SetAlbumWantedMutationFn = Apollo.MutationFunction<
  SetAlbumWantedMutation,
  SetAlbumWantedMutationVariables
>;

/**
 * __useSetAlbumWantedMutation__
 *
 * To run a mutation, you first call `useSetAlbumWantedMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useSetAlbumWantedMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [setAlbumWantedMutation, { data, loading, error }] = useSetAlbumWantedMutation({
 *   variables: {
 *      albumId: // value for 'albumId'
 *      wanted: // value for 'wanted'
 *   },
 * });
 */
export function useSetAlbumWantedMutation(
  baseOptions?: Apollo.MutationHookOptions<
    SetAlbumWantedMutation,
    SetAlbumWantedMutationVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<
    SetAlbumWantedMutation,
    SetAlbumWantedMutationVariables
  >(SetAlbumWantedDocument, options);
}
export type SetAlbumWantedMutationHookResult = ReturnType<
  typeof useSetAlbumWantedMutation
>;
export type SetAlbumWantedMutationResult =
  Apollo.MutationResult<SetAlbumWantedMutation>;
export type SetAlbumWantedMutationOptions = Apollo.BaseMutationOptions<
  SetAlbumWantedMutation,
  SetAlbumWantedMutationVariables
>;
export const TogglePlaylistDocument = gql`
  mutation TogglePlaylist($playlistId: Int!) {
    togglePlaylist(playlistId: $playlistId) {
      success
      message
      playlist {
        id
        name
        enabled
      }
    }
  }
`;
export type TogglePlaylistMutationFn = Apollo.MutationFunction<
  TogglePlaylistMutation,
  TogglePlaylistMutationVariables
>;

/**
 * __useTogglePlaylistMutation__
 *
 * To run a mutation, you first call `useTogglePlaylistMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useTogglePlaylistMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [togglePlaylistMutation, { data, loading, error }] = useTogglePlaylistMutation({
 *   variables: {
 *      playlistId: // value for 'playlistId'
 *   },
 * });
 */
export function useTogglePlaylistMutation(
  baseOptions?: Apollo.MutationHookOptions<
    TogglePlaylistMutation,
    TogglePlaylistMutationVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<
    TogglePlaylistMutation,
    TogglePlaylistMutationVariables
  >(TogglePlaylistDocument, options);
}
export type TogglePlaylistMutationHookResult = ReturnType<
  typeof useTogglePlaylistMutation
>;
export type TogglePlaylistMutationResult =
  Apollo.MutationResult<TogglePlaylistMutation>;
export type TogglePlaylistMutationOptions = Apollo.BaseMutationOptions<
  TogglePlaylistMutation,
  TogglePlaylistMutationVariables
>;
export const DownloadUrlDocument = gql`
  mutation DownloadUrl($url: String!, $autoTrackArtists: Boolean) {
    downloadUrl(url: $url, autoTrackArtists: $autoTrackArtists) {
      success
      message
      artist {
        id
        name
        gid
        isTracked
        addedAt
        lastSynced
      }
      album {
        id
        name
        spotifyGid
        totalTracks
        wanted
        downloaded
        albumType
        albumGroup
        artist
        artistId
      }
      playlist {
        id
        name
        url
        enabled
        autoTrackArtists
        lastSyncedAt
      }
    }
  }
`;
export type DownloadUrlMutationFn = Apollo.MutationFunction<
  DownloadUrlMutation,
  DownloadUrlMutationVariables
>;

/**
 * __useDownloadUrlMutation__
 *
 * To run a mutation, you first call `useDownloadUrlMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDownloadUrlMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [downloadUrlMutation, { data, loading, error }] = useDownloadUrlMutation({
 *   variables: {
 *      url: // value for 'url'
 *      autoTrackArtists: // value for 'autoTrackArtists'
 *   },
 * });
 */
export function useDownloadUrlMutation(
  baseOptions?: Apollo.MutationHookOptions<
    DownloadUrlMutation,
    DownloadUrlMutationVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<DownloadUrlMutation, DownloadUrlMutationVariables>(
    DownloadUrlDocument,
    options
  );
}
export type DownloadUrlMutationHookResult = ReturnType<
  typeof useDownloadUrlMutation
>;
export type DownloadUrlMutationResult =
  Apollo.MutationResult<DownloadUrlMutation>;
export type DownloadUrlMutationOptions = Apollo.BaseMutationOptions<
  DownloadUrlMutation,
  DownloadUrlMutationVariables
>;
export const CreatePlaylistDocument = gql`
  mutation CreatePlaylist(
    $name: String!
    $url: String!
    $autoTrackArtists: Boolean!
  ) {
    createPlaylist(
      name: $name
      url: $url
      autoTrackArtists: $autoTrackArtists
    ) {
      id
      name
      url
      enabled
      autoTrackArtists
      lastSyncedAt
    }
  }
`;
export type CreatePlaylistMutationFn = Apollo.MutationFunction<
  CreatePlaylistMutation,
  CreatePlaylistMutationVariables
>;

/**
 * __useCreatePlaylistMutation__
 *
 * To run a mutation, you first call `useCreatePlaylistMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreatePlaylistMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createPlaylistMutation, { data, loading, error }] = useCreatePlaylistMutation({
 *   variables: {
 *      name: // value for 'name'
 *      url: // value for 'url'
 *      autoTrackArtists: // value for 'autoTrackArtists'
 *   },
 * });
 */
export function useCreatePlaylistMutation(
  baseOptions?: Apollo.MutationHookOptions<
    CreatePlaylistMutation,
    CreatePlaylistMutationVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<
    CreatePlaylistMutation,
    CreatePlaylistMutationVariables
  >(CreatePlaylistDocument, options);
}
export type CreatePlaylistMutationHookResult = ReturnType<
  typeof useCreatePlaylistMutation
>;
export type CreatePlaylistMutationResult =
  Apollo.MutationResult<CreatePlaylistMutation>;
export type CreatePlaylistMutationOptions = Apollo.BaseMutationOptions<
  CreatePlaylistMutation,
  CreatePlaylistMutationVariables
>;
export const UpdatePlaylistDocument = gql`
  mutation UpdatePlaylist(
    $playlistId: Int!
    $name: String!
    $autoTrackArtists: Boolean!
  ) {
    updatePlaylist(
      playlistId: $playlistId
      name: $name
      autoTrackArtists: $autoTrackArtists
    ) {
      success
      message
    }
  }
`;
export type UpdatePlaylistMutationFn = Apollo.MutationFunction<
  UpdatePlaylistMutation,
  UpdatePlaylistMutationVariables
>;

/**
 * __useUpdatePlaylistMutation__
 *
 * To run a mutation, you first call `useUpdatePlaylistMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdatePlaylistMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updatePlaylistMutation, { data, loading, error }] = useUpdatePlaylistMutation({
 *   variables: {
 *      playlistId: // value for 'playlistId'
 *      name: // value for 'name'
 *      autoTrackArtists: // value for 'autoTrackArtists'
 *   },
 * });
 */
export function useUpdatePlaylistMutation(
  baseOptions?: Apollo.MutationHookOptions<
    UpdatePlaylistMutation,
    UpdatePlaylistMutationVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<
    UpdatePlaylistMutation,
    UpdatePlaylistMutationVariables
  >(UpdatePlaylistDocument, options);
}
export type UpdatePlaylistMutationHookResult = ReturnType<
  typeof useUpdatePlaylistMutation
>;
export type UpdatePlaylistMutationResult =
  Apollo.MutationResult<UpdatePlaylistMutation>;
export type UpdatePlaylistMutationOptions = Apollo.BaseMutationOptions<
  UpdatePlaylistMutation,
  UpdatePlaylistMutationVariables
>;
export const TogglePlaylistAutoTrackDocument = gql`
  mutation TogglePlaylistAutoTrack($playlistId: Int!) {
    togglePlaylistAutoTrack(playlistId: $playlistId) {
      success
      message
      playlist {
        id
        name
        autoTrackArtists
      }
    }
  }
`;
export type TogglePlaylistAutoTrackMutation = {
  __typename?: 'Mutation';
  togglePlaylistAutoTrack: {
    __typename?: 'MutationResult';
    success: boolean;
    message: string;
    playlist?: {
      __typename?: 'Playlist';
      id: number;
      name: string;
      autoTrackArtists: boolean;
    } | null;
  };
};
export type TogglePlaylistAutoTrackMutationVariables = Exact<{
  playlistId: Scalars['Int']['input'];
}>;

export type TogglePlaylistAutoTrackMutationFn = Apollo.MutationFunction<
  TogglePlaylistAutoTrackMutation,
  TogglePlaylistAutoTrackMutationVariables
>;

export function useTogglePlaylistAutoTrackMutation(
  baseOptions?: Apollo.MutationHookOptions<
    TogglePlaylistAutoTrackMutation,
    TogglePlaylistAutoTrackMutationVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<
    TogglePlaylistAutoTrackMutation,
    TogglePlaylistAutoTrackMutationVariables
  >(TogglePlaylistAutoTrackDocument, options);
}
export type TogglePlaylistAutoTrackMutationHookResult = ReturnType<
  typeof useTogglePlaylistAutoTrackMutation
>;
export type TogglePlaylistAutoTrackMutationResult =
  Apollo.MutationResult<TogglePlaylistAutoTrackMutation>;
export type TogglePlaylistAutoTrackMutationOptions = Apollo.BaseMutationOptions<
  TogglePlaylistAutoTrackMutation,
  TogglePlaylistAutoTrackMutationVariables
>;
export const GetSongsDocument = gql`
  query GetSongs(
    $first: Int
    $after: String
    $artistId: Int
    $downloaded: Boolean
    $unavailable: Boolean
    $sortBy: String
    $sortDirection: String
    $search: String
  ) {
    songs(
      first: $first
      after: $after
      artistId: $artistId
      downloaded: $downloaded
      unavailable: $unavailable
      sortBy: $sortBy
      sortDirection: $sortDirection
      search: $search
    ) {
      edges {
        id
        name
        gid
        primaryArtist
        primaryArtistId
        createdAt
        failedCount
        bitrate
        unavailable
        filePath
        downloaded
        spotifyUri
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      totalCount
    }
  }
`;

/**
 * __useGetSongsQuery__
 *
 * To run a query within a React component, call `useGetSongsQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetSongsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetSongsQuery({
 *   variables: {
 *      first: // value for 'first'
 *      after: // value for 'after'
 *      artistId: // value for 'artistId'
 *      downloaded: // value for 'downloaded'
 *      unavailable: // value for 'unavailable'
 *      sortBy: // value for 'sortBy'
 *      sortDirection: // value for 'sortDirection'
 *      search: // value for 'search'
 *   },
 * });
 */
export function useGetSongsQuery(
  baseOptions?: Apollo.QueryHookOptions<GetSongsQuery, GetSongsQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<GetSongsQuery, GetSongsQueryVariables>(
    GetSongsDocument,
    options
  );
}
export function useGetSongsLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<
    GetSongsQuery,
    GetSongsQueryVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<GetSongsQuery, GetSongsQueryVariables>(
    GetSongsDocument,
    options
  );
}
export function useGetSongsSuspenseQuery(
  baseOptions?:
    | Apollo.SkipToken
    | Apollo.SuspenseQueryHookOptions<GetSongsQuery, GetSongsQueryVariables>
) {
  const options =
    baseOptions === Apollo.skipToken
      ? baseOptions
      : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<GetSongsQuery, GetSongsQueryVariables>(
    GetSongsDocument,
    options
  );
}
export type GetSongsQueryHookResult = ReturnType<typeof useGetSongsQuery>;
export type GetSongsLazyQueryHookResult = ReturnType<
  typeof useGetSongsLazyQuery
>;
export type GetSongsSuspenseQueryHookResult = ReturnType<
  typeof useGetSongsSuspenseQuery
>;
export type GetSongsQueryResult = Apollo.QueryResult<
  GetSongsQuery,
  GetSongsQueryVariables
>;
export const GetSongDocument = gql`
  query GetSong($id: String!) {
    song(id: $id) {
      id
      name
      gid
      primaryArtist
      primaryArtistId
      createdAt
      failedCount
      bitrate
      unavailable
      filePath
      downloaded
      spotifyUri
    }
  }
`;

/**
 * __useGetSongQuery__
 *
 * To run a query within a React component, call `useGetSongQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetSongQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetSongQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useGetSongQuery(
  baseOptions: Apollo.QueryHookOptions<GetSongQuery, GetSongQueryVariables> &
    ({ variables: GetSongQueryVariables; skip?: boolean } | { skip: boolean })
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<GetSongQuery, GetSongQueryVariables>(
    GetSongDocument,
    options
  );
}
export function useGetSongLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<GetSongQuery, GetSongQueryVariables>
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<GetSongQuery, GetSongQueryVariables>(
    GetSongDocument,
    options
  );
}
export function useGetSongSuspenseQuery(
  baseOptions?:
    | Apollo.SkipToken
    | Apollo.SuspenseQueryHookOptions<GetSongQuery, GetSongQueryVariables>
) {
  const options =
    baseOptions === Apollo.skipToken
      ? baseOptions
      : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<GetSongQuery, GetSongQueryVariables>(
    GetSongDocument,
    options
  );
}
export type GetSongQueryHookResult = ReturnType<typeof useGetSongQuery>;
export type GetSongLazyQueryHookResult = ReturnType<typeof useGetSongLazyQuery>;
export type GetSongSuspenseQueryHookResult = ReturnType<
  typeof useGetSongSuspenseQuery
>;
export type GetSongQueryResult = Apollo.QueryResult<
  GetSongQuery,
  GetSongQueryVariables
>;
export const GetQueueStatusDocument = gql`
  query GetQueueStatus {
    queueStatus {
      totalPendingTasks
      taskCounts {
        taskName
        count
      }
      queueSize
    }
  }
`;

/**
 * __useGetQueueStatusQuery__
 *
 * To run a query within a React component, call `useGetQueueStatusQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetQueueStatusQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetQueueStatusQuery({
 *   variables: {
 *   },
 * });
 */
export function useGetQueueStatusQuery(
  baseOptions?: Apollo.QueryHookOptions<
    GetQueueStatusQuery,
    GetQueueStatusQueryVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<GetQueueStatusQuery, GetQueueStatusQueryVariables>(
    GetQueueStatusDocument,
    options
  );
}
export function useGetQueueStatusLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<
    GetQueueStatusQuery,
    GetQueueStatusQueryVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<GetQueueStatusQuery, GetQueueStatusQueryVariables>(
    GetQueueStatusDocument,
    options
  );
}
export function useGetQueueStatusSuspenseQuery(
  baseOptions?:
    | Apollo.SkipToken
    | Apollo.SuspenseQueryHookOptions<
        GetQueueStatusQuery,
        GetQueueStatusQueryVariables
      >
) {
  const options =
    baseOptions === Apollo.skipToken
      ? baseOptions
      : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<
    GetQueueStatusQuery,
    GetQueueStatusQueryVariables
  >(GetQueueStatusDocument, options);
}
export type GetQueueStatusQueryHookResult = ReturnType<
  typeof useGetQueueStatusQuery
>;
export type GetQueueStatusLazyQueryHookResult = ReturnType<
  typeof useGetQueueStatusLazyQuery
>;
export type GetQueueStatusSuspenseQueryHookResult = ReturnType<
  typeof useGetQueueStatusSuspenseQuery
>;
export type GetQueueStatusQueryResult = Apollo.QueryResult<
  GetQueueStatusQuery,
  GetQueueStatusQueryVariables
>;
export const CancelAllPendingTasksDocument = gql`
  mutation CancelAllPendingTasks {
    cancelAllPendingTasks {
      success
      message
    }
  }
`;
export type CancelAllPendingTasksMutationFn = Apollo.MutationFunction<
  CancelAllPendingTasksMutation,
  CancelAllPendingTasksMutationVariables
>;

/**
 * __useCancelAllPendingTasksMutation__
 *
 * To run a mutation, you first call `useCancelAllPendingTasksMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCancelAllPendingTasksMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [cancelAllPendingTasksMutation, { data, loading, error }] = useCancelAllPendingTasksMutation({
 *   variables: {
 *   },
 * });
 */
export function useCancelAllPendingTasksMutation(
  baseOptions?: Apollo.MutationHookOptions<
    CancelAllPendingTasksMutation,
    CancelAllPendingTasksMutationVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<
    CancelAllPendingTasksMutation,
    CancelAllPendingTasksMutationVariables
  >(CancelAllPendingTasksDocument, options);
}
export type CancelAllPendingTasksMutationHookResult = ReturnType<
  typeof useCancelAllPendingTasksMutation
>;
export type CancelAllPendingTasksMutationResult =
  Apollo.MutationResult<CancelAllPendingTasksMutation>;
export type CancelAllPendingTasksMutationOptions = Apollo.BaseMutationOptions<
  CancelAllPendingTasksMutation,
  CancelAllPendingTasksMutationVariables
>;
export const CancelTasksByNameDocument = gql`
  mutation CancelTasksByName($taskName: String!) {
    cancelTasksByName(taskName: $taskName) {
      success
      message
    }
  }
`;
export type CancelTasksByNameMutationFn = Apollo.MutationFunction<
  CancelTasksByNameMutation,
  CancelTasksByNameMutationVariables
>;

/**
 * __useCancelTasksByNameMutation__
 *
 * To run a mutation, you first call `useCancelTasksByNameMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCancelTasksByNameMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [cancelTasksByNameMutation, { data, loading, error }] = useCancelTasksByNameMutation({
 *   variables: {
 *      taskName: // value for 'taskName'
 *   },
 * });
 */
export function useCancelTasksByNameMutation(
  baseOptions?: Apollo.MutationHookOptions<
    CancelTasksByNameMutation,
    CancelTasksByNameMutationVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<
    CancelTasksByNameMutation,
    CancelTasksByNameMutationVariables
  >(CancelTasksByNameDocument, options);
}
export type CancelTasksByNameMutationHookResult = ReturnType<
  typeof useCancelTasksByNameMutation
>;
export type CancelTasksByNameMutationResult =
  Apollo.MutationResult<CancelTasksByNameMutation>;
export type CancelTasksByNameMutationOptions = Apollo.BaseMutationOptions<
  CancelTasksByNameMutation,
  CancelTasksByNameMutationVariables
>;
export const CancelRunningTasksByNameDocument = gql`
  mutation CancelRunningTasksByName($taskName: String!) {
    cancelRunningTasksByName(taskName: $taskName) {
      success
      message
    }
  }
`;
export type CancelRunningTasksByNameMutationFn = Apollo.MutationFunction<
  CancelRunningTasksByNameMutation,
  CancelRunningTasksByNameMutationVariables
>;

/**
 * __useCancelRunningTasksByNameMutation__
 *
 * To run a mutation, you first call `useCancelRunningTasksByNameMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCancelRunningTasksByNameMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [cancelRunningTasksByNameMutation, { data, loading, error }] = useCancelRunningTasksByNameMutation({
 *   variables: {
 *      taskName: // value for 'taskName'
 *   },
 * });
 */
export function useCancelRunningTasksByNameMutation(
  baseOptions?: Apollo.MutationHookOptions<
    CancelRunningTasksByNameMutation,
    CancelRunningTasksByNameMutationVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<
    CancelRunningTasksByNameMutation,
    CancelRunningTasksByNameMutationVariables
  >(CancelRunningTasksByNameDocument, options);
}
export type CancelRunningTasksByNameMutationHookResult = ReturnType<
  typeof useCancelRunningTasksByNameMutation
>;
export type CancelRunningTasksByNameMutationResult =
  Apollo.MutationResult<CancelRunningTasksByNameMutation>;
export type CancelRunningTasksByNameMutationOptions =
  Apollo.BaseMutationOptions<
    CancelRunningTasksByNameMutation,
    CancelRunningTasksByNameMutationVariables
  >;
export const CancelAllTasksDocument = gql`
  mutation CancelAllTasks {
    cancelAllTasks {
      success
      message
    }
  }
`;
export type CancelAllTasksMutationFn = Apollo.MutationFunction<
  CancelAllTasksMutation,
  CancelAllTasksMutationVariables
>;

/**
 * __useCancelAllTasksMutation__
 *
 * To run a mutation, you first call `useCancelAllTasksMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCancelAllTasksMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [cancelAllTasksMutation, { data, loading, error }] = useCancelAllTasksMutation({
 *   variables: {
 *   },
 * });
 */
export function useCancelAllTasksMutation(
  baseOptions?: Apollo.MutationHookOptions<
    CancelAllTasksMutation,
    CancelAllTasksMutationVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useMutation<
    CancelAllTasksMutation,
    CancelAllTasksMutationVariables
  >(CancelAllTasksDocument, options);
}
export type CancelAllTasksMutationHookResult = ReturnType<
  typeof useCancelAllTasksMutation
>;
export type CancelAllTasksMutationResult =
  Apollo.MutationResult<CancelAllTasksMutation>;
export type CancelAllTasksMutationOptions = Apollo.BaseMutationOptions<
  CancelAllTasksMutation,
  CancelAllTasksMutationVariables
>;
export const GetTaskHistoryDocument = gql`
  query GetTaskHistory(
    $first: Int = 20
    $after: String
    $status: String
    $type: String
    $entityType: String
    $search: String
  ) {
    taskHistory(
      first: $first
      after: $after
      status: $status
      type: $type
      entityType: $entityType
      search: $search
    ) {
      totalCount
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          taskId
          type
          entityId
          entityType
          status
          startedAt
          completedAt
          durationSeconds
          progressPercentage
          logMessages
        }
        cursor
      }
    }
  }
`;

/**
 * __useGetTaskHistoryQuery__
 *
 * To run a query within a React component, call `useGetTaskHistoryQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetTaskHistoryQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetTaskHistoryQuery({
 *   variables: {
 *      first: // value for 'first'
 *      after: // value for 'after'
 *      status: // value for 'status'
 *      type: // value for 'type'
 *      entityType: // value for 'entityType'
 *      search: // value for 'search'
 *   },
 * });
 */
export function useGetTaskHistoryQuery(
  baseOptions?: Apollo.QueryHookOptions<
    GetTaskHistoryQuery,
    GetTaskHistoryQueryVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useQuery<GetTaskHistoryQuery, GetTaskHistoryQueryVariables>(
    GetTaskHistoryDocument,
    options
  );
}
export function useGetTaskHistoryLazyQuery(
  baseOptions?: Apollo.LazyQueryHookOptions<
    GetTaskHistoryQuery,
    GetTaskHistoryQueryVariables
  >
) {
  const options = { ...defaultOptions, ...baseOptions };
  return Apollo.useLazyQuery<GetTaskHistoryQuery, GetTaskHistoryQueryVariables>(
    GetTaskHistoryDocument,
    options
  );
}
export function useGetTaskHistorySuspenseQuery(
  baseOptions?:
    | Apollo.SkipToken
    | Apollo.SuspenseQueryHookOptions<
        GetTaskHistoryQuery,
        GetTaskHistoryQueryVariables
      >
) {
  const options =
    baseOptions === Apollo.skipToken
      ? baseOptions
      : { ...defaultOptions, ...baseOptions };
  return Apollo.useSuspenseQuery<
    GetTaskHistoryQuery,
    GetTaskHistoryQueryVariables
  >(GetTaskHistoryDocument, options);
}
export type GetTaskHistoryQueryHookResult = ReturnType<
  typeof useGetTaskHistoryQuery
>;
export type GetTaskHistoryLazyQueryHookResult = ReturnType<
  typeof useGetTaskHistoryLazyQuery
>;
export type GetTaskHistorySuspenseQueryHookResult = ReturnType<
  typeof useGetTaskHistorySuspenseQuery
>;
export type GetTaskHistoryQueryResult = Apollo.QueryResult<
  GetTaskHistoryQuery,
  GetTaskHistoryQueryVariables
>;
