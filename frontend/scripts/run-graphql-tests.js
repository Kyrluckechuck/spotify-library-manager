#!/usr/bin/env node

// GraphQL Test Runner (Node ESM JS version)
// Runs real queries/mutations against API_URL. Safe to run locally.

import {
  ApolloClient,
  InMemoryCache,
  createHttpLink,
  gql,
} from '@apollo/client/core/index.js';
import fetch from 'node-fetch';

const API_URL = process.env.API_URL || 'http://localhost:5000/graphql';

const client = new ApolloClient({
  link: createHttpLink({ uri: API_URL, fetch }),
  cache: new InMemoryCache(),
});

const testQueries = [
  {
    name: 'GetArtists',
    query: gql`
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
    `,
    variables: {},
  },
  {
    name: 'GetAlbums',
    query: gql`
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
    `,
    variables: {},
  },
  {
    name: 'GetPlaylists',
    query: gql`
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
    `,
    variables: {},
  },
  {
    name: 'GetSongs',
    query: gql`
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
    `,
    variables: {},
  },
  {
    name: 'GetTaskHistory',
    query: gql`
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
    `,
    variables: {},
  },
];

const testMutations = [
  {
    name: 'TrackArtist',
    mutation: gql`
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
    `,
    variables: { artistId: 1 },
  },
  {
    name: 'UntrackArtist',
    mutation: gql`
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
    `,
    variables: { artistId: 1 },
  },
  {
    name: 'SyncArtist',
    mutation: gql`
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
    `,
    variables: { artistId: '1' },
  },
  {
    name: 'SetAlbumWanted',
    mutation: gql`
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
    `,
    variables: { albumId: 1, wanted: true },
  },
  {
    name: 'TogglePlaylist',
    mutation: gql`
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
    `,
    variables: { playlistId: 1 },
  },
];

async function testQuery(name, query, variables) {
  try {
    console.log(`→ Query: ${name}`);
    const result = await client.query({
      query,
      variables,
      fetchPolicy: 'no-cache',
    });
    const ok = !!result.data;
    console.log(ok ? `✓ ${name}` : `✗ ${name} (no data)`);
    return { success: ok, data: result.data };
  } catch (error) {
    console.log(`✗ ${name}: ${error}`);
    return { success: false, error };
  }
}

async function testMutation(name, mutation, variables) {
  try {
    console.log(`→ Mutation: ${name}`);
    const result = await client.mutate({ mutation, variables });
    const ok = !!result.data;
    console.log(ok ? `✓ ${name}` : `✗ ${name} (no data)`);
    return { success: ok, data: result.data };
  } catch (error) {
    console.log(`✗ ${name}: ${error}`);
    return { success: false, error };
  }
}

async function runAllTests() {
  console.log('🚀 Starting GraphQL Test Suite...');
  console.log(`📡 API: ${API_URL}`);

  const queryResults = [];
  const mutationResults = [];

  for (const t of testQueries)
    queryResults.push({
      name: t.name,
      ...(await testQuery(t.name, t.query, t.variables)),
    });
  for (const t of testMutations)
    mutationResults.push({
      name: t.name,
      ...(await testMutation(t.name, t.mutation, t.variables)),
    });

  const qPass = queryResults.filter(r => r.success).length;
  const mPass = mutationResults.filter(r => r.success).length;
  const total = testQueries.length + testMutations.length;
  const passed = qPass + mPass;

  console.log('');
  console.log(`Queries:   ${qPass}/${testQueries.length}`);
  console.log(`Mutations: ${mPass}/${testMutations.length}`);
  console.log(`Total:     ${passed}/${total}`);

  return {
    queries: queryResults,
    mutations: mutationResults,
    totalPassed: passed,
    totalTests: total,
  };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  runAllTests()
    .then(results =>
      process.exit(results.totalPassed === results.totalTests ? 0 : 1)
    )
    .catch(err => {
      console.error('Test runner failed:', err);
      process.exit(1);
    });
}

export { runAllTests };
