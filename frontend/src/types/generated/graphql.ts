import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
const defaultOptions = {} as const;
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
};

export type Album = {
  albumGroup?: Maybe<Scalars['String']['output']>;
  albumType?: Maybe<Scalars['String']['output']>;
  downloaded: Scalars['Boolean']['output'];
  id: Scalars['Int']['output'];
  name: Scalars['String']['output'];
  spotifyGid: Scalars['String']['output'];
  spotifyUri: Scalars['String']['output'];
  totalTracks: Scalars['Int']['output'];
  wanted: Scalars['Boolean']['output'];
};

export type Artist = {
  addedAt?: Maybe<Scalars['String']['output']>;
  gid: Scalars['String']['output'];
  id: Scalars['Int']['output'];
  lastSyncedAt?: Maybe<Scalars['String']['output']>;
  name: Scalars['String']['output'];
  tracked: Scalars['Boolean']['output'];
};

export type Query = {
  albums: Array<Album>;
  artists: Array<Artist>;
  hello: Scalars['String']['output'];
  playlists: Array<TrackedPlaylist>;
  songs: Array<Song>;
};


export type QueryAlbumsArgs = {
  artistId?: InputMaybe<Scalars['Int']['input']>;
  limit?: Scalars['Int']['input'];
};


export type QueryArtistsArgs = {
  limit?: Scalars['Int']['input'];
  tracked?: InputMaybe<Scalars['Boolean']['input']>;
};


export type QueryPlaylistsArgs = {
  enabled?: InputMaybe<Scalars['Boolean']['input']>;
  limit?: Scalars['Int']['input'];
};


export type QuerySongsArgs = {
  artistId?: InputMaybe<Scalars['Int']['input']>;
  limit?: Scalars['Int']['input'];
};

export type Song = {
  bitrate?: Maybe<Scalars['Int']['output']>;
  createdAt: Scalars['String']['output'];
  downloaded: Scalars['Boolean']['output'];
  failedCount: Scalars['Int']['output'];
  filePath?: Maybe<Scalars['String']['output']>;
  gid: Scalars['String']['output'];
  id: Scalars['Int']['output'];
  name: Scalars['String']['output'];
  spotifyUri: Scalars['String']['output'];
  unavailable: Scalars['Boolean']['output'];
};

export type TrackedPlaylist = {
  autoTrackArtists: Scalars['Boolean']['output'];
  enabled: Scalars['Boolean']['output'];
  id: Scalars['Int']['output'];
  lastSyncedAt?: Maybe<Scalars['String']['output']>;
  name: Scalars['String']['output'];
  url: Scalars['String']['output'];
};

export type GetArtistsQueryVariables = Exact<{
  tracked?: InputMaybe<Scalars['Boolean']['input']>;
  limit?: InputMaybe<Scalars['Int']['input']>;
}>;


export type GetArtistsQuery = { artists: Array<{ id: number, name: string, gid: string, tracked: boolean, addedAt?: string | null, lastSyncedAt?: string | null }> };

export type GetAlbumsQueryVariables = Exact<{
  artistId?: InputMaybe<Scalars['Int']['input']>;
  limit?: InputMaybe<Scalars['Int']['input']>;
}>;


export type GetAlbumsQuery = { albums: Array<{ id: number, name: string, spotifyGid: string, totalTracks: number, wanted: boolean, downloaded: boolean, albumType?: string | null, albumGroup?: string | null }> };

export type GetSongsQueryVariables = Exact<{
  artistId?: InputMaybe<Scalars['Int']['input']>;
  limit?: InputMaybe<Scalars['Int']['input']>;
}>;


export type GetSongsQuery = { songs: Array<{ id: number, name: string, gid: string, createdAt: string, failedCount: number, bitrate?: number | null, unavailable: boolean, filePath?: string | null, downloaded: boolean, spotifyUri: string }> };

export type GetPlaylistsQueryVariables = Exact<{
  enabled?: InputMaybe<Scalars['Boolean']['input']>;
  limit?: InputMaybe<Scalars['Int']['input']>;
}>;


export type GetPlaylistsQuery = { playlists: Array<{ id: number, name: string, url: string, enabled: boolean, autoTrackArtists: boolean, lastSyncedAt?: string | null }> };


export const GetArtistsDocument = gql`
    query GetArtists($tracked: Boolean, $limit: Int = 20) {
  artists(tracked: $tracked, limit: $limit) {
    id
    name
    gid
    tracked
    addedAt
    lastSyncedAt
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
 *      tracked: // value for 'tracked'
 *      limit: // value for 'limit'
 *   },
 * });
 */
export function useGetArtistsQuery(baseOptions?: Apollo.QueryHookOptions<GetArtistsQuery, GetArtistsQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetArtistsQuery, GetArtistsQueryVariables>(GetArtistsDocument, options);
      }
export function useGetArtistsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetArtistsQuery, GetArtistsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetArtistsQuery, GetArtistsQueryVariables>(GetArtistsDocument, options);
        }
export function useGetArtistsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetArtistsQuery, GetArtistsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetArtistsQuery, GetArtistsQueryVariables>(GetArtistsDocument, options);
        }
export type GetArtistsQueryHookResult = ReturnType<typeof useGetArtistsQuery>;
export type GetArtistsLazyQueryHookResult = ReturnType<typeof useGetArtistsLazyQuery>;
export type GetArtistsSuspenseQueryHookResult = ReturnType<typeof useGetArtistsSuspenseQuery>;
export type GetArtistsQueryResult = Apollo.QueryResult<GetArtistsQuery, GetArtistsQueryVariables>;
export const GetAlbumsDocument = gql`
    query GetAlbums($artistId: Int, $limit: Int = 20) {
  albums(artistId: $artistId, limit: $limit) {
    id
    name
    spotifyGid
    totalTracks
    wanted
    downloaded
    albumType
    albumGroup
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
 *      limit: // value for 'limit'
 *   },
 * });
 */
export function useGetAlbumsQuery(baseOptions?: Apollo.QueryHookOptions<GetAlbumsQuery, GetAlbumsQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetAlbumsQuery, GetAlbumsQueryVariables>(GetAlbumsDocument, options);
      }
export function useGetAlbumsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetAlbumsQuery, GetAlbumsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetAlbumsQuery, GetAlbumsQueryVariables>(GetAlbumsDocument, options);
        }
export function useGetAlbumsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetAlbumsQuery, GetAlbumsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetAlbumsQuery, GetAlbumsQueryVariables>(GetAlbumsDocument, options);
        }
export type GetAlbumsQueryHookResult = ReturnType<typeof useGetAlbumsQuery>;
export type GetAlbumsLazyQueryHookResult = ReturnType<typeof useGetAlbumsLazyQuery>;
export type GetAlbumsSuspenseQueryHookResult = ReturnType<typeof useGetAlbumsSuspenseQuery>;
export type GetAlbumsQueryResult = Apollo.QueryResult<GetAlbumsQuery, GetAlbumsQueryVariables>;
export const GetSongsDocument = gql`
    query GetSongs($artistId: Int, $limit: Int = 20) {
  songs(artistId: $artistId, limit: $limit) {
    id
    name
    gid
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
 *      artistId: // value for 'artistId'
 *      limit: // value for 'limit'
 *   },
 * });
 */
export function useGetSongsQuery(baseOptions?: Apollo.QueryHookOptions<GetSongsQuery, GetSongsQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetSongsQuery, GetSongsQueryVariables>(GetSongsDocument, options);
      }
export function useGetSongsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetSongsQuery, GetSongsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetSongsQuery, GetSongsQueryVariables>(GetSongsDocument, options);
        }
export function useGetSongsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetSongsQuery, GetSongsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetSongsQuery, GetSongsQueryVariables>(GetSongsDocument, options);
        }
export type GetSongsQueryHookResult = ReturnType<typeof useGetSongsQuery>;
export type GetSongsLazyQueryHookResult = ReturnType<typeof useGetSongsLazyQuery>;
export type GetSongsSuspenseQueryHookResult = ReturnType<typeof useGetSongsSuspenseQuery>;
export type GetSongsQueryResult = Apollo.QueryResult<GetSongsQuery, GetSongsQueryVariables>;
export const GetPlaylistsDocument = gql`
    query GetPlaylists($enabled: Boolean, $limit: Int = 20) {
  playlists(enabled: $enabled, limit: $limit) {
    id
    name
    url
    enabled
    autoTrackArtists
    lastSyncedAt
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
 *      limit: // value for 'limit'
 *   },
 * });
 */
export function useGetPlaylistsQuery(baseOptions?: Apollo.QueryHookOptions<GetPlaylistsQuery, GetPlaylistsQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetPlaylistsQuery, GetPlaylistsQueryVariables>(GetPlaylistsDocument, options);
      }
export function useGetPlaylistsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetPlaylistsQuery, GetPlaylistsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetPlaylistsQuery, GetPlaylistsQueryVariables>(GetPlaylistsDocument, options);
        }
export function useGetPlaylistsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetPlaylistsQuery, GetPlaylistsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetPlaylistsQuery, GetPlaylistsQueryVariables>(GetPlaylistsDocument, options);
        }
export type GetPlaylistsQueryHookResult = ReturnType<typeof useGetPlaylistsQuery>;
export type GetPlaylistsLazyQueryHookResult = ReturnType<typeof useGetPlaylistsLazyQuery>;
export type GetPlaylistsSuspenseQueryHookResult = ReturnType<typeof useGetPlaylistsSuspenseQuery>;
export type GetPlaylistsQueryResult = Apollo.QueryResult<GetPlaylistsQuery, GetPlaylistsQueryVariables>;