#!/usr/bin/env node

/**
 * Comprehensive GraphQL Operations Test Script
 *
 * This script tests all GraphQL operations to detect:
 * - Async/sync context issues
 * - Schema mismatches
 * - Performance problems
 * - Error handling issues
 */

// Configuration
const API_URL = 'http://localhost:5000/graphql';

/**
 * Test a GraphQL operation and analyze the response
 */
async function testOperation(name, query, variables = {}) {
  const startTime = Date.now();

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        variables,
      }),
    });

    const result = await response.json();
    const duration = Date.now() - startTime;

    if (result.errors) {
      const errorMessages = result.errors.map(e => e.message).join(', ');
      const isAsyncContextError =
        errorMessages.includes('async context') ||
        errorMessages.includes('sync_to_async') ||
        errorMessages.includes('You cannot call this from an async context');

      return {
        name,
        success: false,
        error: errorMessages,
        duration,
        isAsyncContextError,
        suggestions: isAsyncContextError
          ? [
              'Check for missing sync_to_async() wrappers in backend resolvers',
              'Ensure all database operations are properly wrapped',
              'Look for direct Django ORM calls in async functions',
            ]
          : [],
      };
    }

    return {
      name,
      success: true,
      error: null,
      duration,
      isAsyncContextError: false,
      dataSize: JSON.stringify(result.data).length,
    };
  } catch (error) {
    const duration = Date.now() - startTime;
    return {
      name,
      success: false,
      error: error.message,
      duration,
      isAsyncContextError: false,
      suggestions: [
        'Check if the API server is running',
        'Verify network connectivity',
      ],
    };
  }
}

/**
 * Define comprehensive test operations
 */
function getTestOperations() {
  return [
    // Query Tests
    {
      name: 'GetSongs',
      query: `
        query GetSongs($first: Int = 10, $artistId: Int, $downloaded: Boolean) {
          songs(first: $first, artistId: $artistId, downloaded: $downloaded) {
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
        }
      `,
      variables: { first: 5 },
    },
    {
      name: 'GetArtists',
      query: `
        query GetArtists($first: Int = 10, $isTracked: Boolean, $search: String) {
          artists(first: $first, isTracked: $isTracked, search: $search) {
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
      variables: { first: 5 },
    },
    {
      name: 'GetAlbums',
      query: `
        query GetAlbums($first: Int = 10, $artistId: Int, $wanted: Boolean, $downloaded: Boolean) {
          albums(first: $first, artistId: $artistId, wanted: $wanted, downloaded: $downloaded) {
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
      variables: { first: 5 },
    },
    {
      name: 'GetPlaylists',
      query: `
        query GetPlaylists($first: Int = 10, $enabled: Boolean) {
          playlists(first: $first, enabled: $enabled) {
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
      variables: { first: 5 },
    },
    {
      name: 'GetTaskHistory',
      query: `
        query GetTaskHistory($first: Int = 10) {
          taskHistory(first: $first) {
            totalCount
            pageInfo {
              hasNextPage
              hasPreviousPage
              startCursor
              endCursor
            }
            edges {
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
          }
        }
      `,
      variables: { first: 5 },
    },
    // Mutation Tests
    {
      name: 'TrackArtist',
      query: `
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
      query: `
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
      query: `
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
      variables: { artistId: 'test-gid' },
    },
  ];
}

/**
 * Run comprehensive GraphQL tests
 */
async function runComprehensiveTests() {
  console.log('🧪 Running comprehensive GraphQL operation tests...\n');

  const operations = getTestOperations();
  const results = [];

  for (const operation of operations) {
    console.log(`Testing ${operation.name}...`);
    const result = await testOperation(
      operation.name,
      operation.query,
      operation.variables
    );
    results.push(result);

    if (result.success) {
      console.log(`  ✅ ${operation.name}: Success (${result.duration}ms)`);
      if (result.dataSize) {
        console.log(`     📊 Data size: ${result.dataSize} bytes`);
      }
    } else {
      console.log(`  ❌ ${operation.name}: ${result.error}`);
      if (result.isAsyncContextError) {
        console.log(`     🔧 Async/sync context issue detected!`);
        result.suggestions.forEach(suggestion => {
          console.log(`        💡 ${suggestion}`);
        });
      }
    }
  }

  // Generate summary report
  console.log('\n📊 Test Summary:');
  const successful = results.filter(r => r.success);
  const failed = results.filter(r => !r.success);
  const asyncContextErrors = results.filter(r => r.isAsyncContextError);

  console.log(`  ✅ Successful: ${successful.length}/${results.length}`);
  console.log(`  ❌ Failed: ${failed.length}/${results.length}`);
  console.log(`  🔧 Async context errors: ${asyncContextErrors.length}`);

  if (successful.length > 0) {
    const avgDuration =
      successful.reduce((sum, r) => sum + r.duration, 0) / successful.length;
    console.log(`  ⏱️  Average response time: ${avgDuration.toFixed(0)}ms`);
  }

  if (asyncContextErrors.length > 0) {
    console.log('\n🚨 Async/Sync Context Issues Detected:');
    asyncContextErrors.forEach(result => {
      console.log(`  • ${result.name}: ${result.error}`);
    });
    console.log('\n💡 Recommended fixes:');
    console.log('  1. Wrap Django ORM calls with sync_to_async()');
    console.log('  2. Ensure all database operations are async-compatible');
    console.log('  3. Check for direct model.objects calls in async functions');
    console.log('  4. Use aget() instead of get() for async operations');
  }

  if (failed.length > 0 && asyncContextErrors.length === 0) {
    console.log('\n⚠️  Other Issues Detected:');
    failed.forEach(result => {
      console.log(`  • ${result.name}: ${result.error}`);
    });
  }

  return {
    total: results.length,
    successful: successful.length,
    failed: failed.length,
    asyncContextErrors: asyncContextErrors.length,
    results,
  };
}

/**
 * Main function
 */
async function main() {
  try {
    const summary = await runComprehensiveTests();

    if (summary.asyncContextErrors > 0) {
      console.log('\n❌ Tests failed due to async/sync context issues');
      process.exit(1);
    } else if (summary.failed > 0) {
      console.log('\n⚠️  Some tests failed');
      process.exit(1);
    } else {
      console.log('\n✅ All GraphQL operations are working correctly!');
    }
  } catch (error) {
    console.error('❌ Test execution failed:', error);
    process.exit(1);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
