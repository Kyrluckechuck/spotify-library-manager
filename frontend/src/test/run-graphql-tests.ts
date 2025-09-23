#!/usr/bin/env node

/**
 * GraphQL Test Runner
 *
 * This script runs comprehensive tests to validate that all GraphQL queries
 * and mutations work correctly with the backend.
 */

import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import { gql } from '@apollo/client';
import { testLogger } from '../utils/logger';

// Configuration
const API_URL = 'http://localhost:5000/graphql';

// Create Apollo Client for testing
const httpLink = createHttpLink({
  uri: API_URL,
});

const authLink = setContext((_, { headers }) => {
  return {
    headers: {
      ...headers,
      // Add any auth headers if needed
    },
  };
});

const client = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache(),
});

// Test queries and mutations
const testQueries = [
  {
    name: 'GetArtists',
    query: gql`
      query GetArtistsTest(
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
    mutation: `
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
    mutation: `
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
    mutation: `
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
    mutation: `
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

async function testQuery(
  name: string,
  query: ReturnType<typeof gql>,
  variables: Record<string, unknown>
) {
  try {
    testLogger.action(`Testing query: ${name}`);
    const result = await client.query({ query, variables });

    if (result.data) {
      testLogger.success(`${name}: SUCCESS`);
      return { success: true, data: result.data };
    } else {
      testLogger.failure(`${name}: FAILED - No data returned`);
      return { success: false, error: 'No data returned' };
    }
  } catch (error) {
    testLogger.failure(`${name}: FAILED - ${error}`);
    return { success: false, error };
  }
}

async function testMutation(
  name: string,
  mutation: ReturnType<typeof gql>,
  variables: Record<string, unknown>
) {
  try {
    testLogger.action(`Testing mutation: ${name}`);
    const result = await client.mutate({ mutation, variables });

    if (result.data) {
      testLogger.success(`${name}: SUCCESS`);
      return { success: true, data: result.data };
    } else {
      testLogger.failure(`${name}: FAILED - No data returned`);
      return { success: false, error: 'No data returned' };
    }
  } catch (error) {
    testLogger.failure(`${name}: FAILED - ${error}`);
    return { success: false, error };
  }
}

async function runAllTests() {
  testLogger.test('🚀 Starting GraphQL Test Suite...');
  testLogger.test(`📡 Testing against: ${API_URL}`);
  testLogger.test('');

  const queryResults = [];
  const mutationResults = [];

  // Test queries
  testLogger.section('Testing Queries:');
  testLogger.test('==================');
  for (const test of testQueries) {
    const q =
      typeof test.query === 'string'
        ? gql`
            ${test.query}
          `
        : test.query;
    const result = await testQuery(test.name, q, test.variables);
    queryResults.push({ name: test.name, ...result });
  }

  testLogger.test('');
  testLogger.section('Testing Mutations:');
  testLogger.test('=====================');
  for (const test of testMutations) {
    const m =
      typeof test.mutation === 'string'
        ? gql`
            ${test.mutation}
          `
        : test.mutation;
    const result = await testMutation(test.name, m, test.variables);
    mutationResults.push({ name: test.name, ...result });
  }

  // Summary
  testLogger.test('');
  testLogger.summary('Test Summary:');
  testLogger.test('===============');

  const successfulQueries = queryResults.filter(r => r.success).length;
  const failedQueries = queryResults.length - successfulQueries;

  const successfulMutations = mutationResults.filter(r => r.success).length;
  const failedMutations = mutationResults.length - successfulMutations;

  testLogger.test(
    `Queries: ${successfulQueries}/${queryResults.length} passed`
  );
  testLogger.test(
    `Mutations: ${successfulMutations}/${mutationResults.length} passed`
  );
  testLogger.test(
    `Total: ${successfulQueries + successfulMutations}/${queryResults.length + mutationResults.length} passed`
  );

  if (failedQueries > 0 || failedMutations > 0) {
    testLogger.test('');
    testLogger.failure('Failed Tests:');
    [...queryResults, ...mutationResults]
      .filter(r => !r.success)
      .forEach(r => {
        testLogger.test(`  - ${r.name}: ${r.error}`);
      });
  }

  return {
    queries: queryResults,
    mutations: mutationResults,
    totalPassed: successfulQueries + successfulMutations,
    totalTests: queryResults.length + mutationResults.length,
  };
}

// Run tests if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  runAllTests()
    .then(results => {
      process.exit(results.totalPassed === results.totalTests ? 0 : 1);
    })
    .catch(error => {
      console.error('Test runner failed:', error);
      process.exit(1);
    });
}

export { runAllTests, testQuery, testMutation };
