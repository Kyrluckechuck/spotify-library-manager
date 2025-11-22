import {
  ApolloClient,
  InMemoryCache,
  createHttpLink,
  from,
} from '@apollo/client';
import { onError } from '@apollo/client/link/error';

const httpLink = createHttpLink({
  uri: import.meta.env.VITE_API_URL ?? '/graphql',
});

const errorLink = onError(context => {
  // Apollo Client v4 error handling
  const errorContext = context as {
    graphQLErrors?: Array<{
      message: string;
      locations?: Array<{ line: number; column: number }>;
      path?: string[];
    }>;
    networkError?: Error;
  };

  if (errorContext.graphQLErrors)
    errorContext.graphQLErrors.forEach(({ message, locations, path }) =>
      console.error(
        `[GraphQL error]: Message: ${message}, Location: ${locations}, Path: ${path}`
      )
    );
  if (errorContext.networkError)
    console.error(`[Network error]: ${errorContext.networkError}`);
});

const link = from([errorLink, httpLink]);

export const apolloClient = new ApolloClient({
  link: link,
  cache: new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          artists: {
            keyArgs: ['isTracked', 'search', 'sortBy', 'sortDirection'],
            merge(existing, incoming) {
              // Handle pagination merging
              // Always merge edges if we have existing data (indicates pagination)
              if (!existing) return incoming;

              // Check if this is a pagination request by seeing if edges exist
              if (existing.edges && incoming.edges) {
                return {
                  ...incoming,
                  edges: [...existing.edges, ...incoming.edges],
                };
              }

              // Not a pagination request, replace the cache
              return incoming;
            },
          },
          albums: {
            keyArgs: [
              'artistId',
              'wanted',
              'downloaded',
              'search',
              'sortBy',
              'sortDirection',
            ],
            merge(existing, incoming) {
              if (!existing) return incoming;

              // Merge edges if both have them (pagination request)
              if (existing.edges && incoming.edges) {
                return {
                  ...incoming,
                  edges: [...existing.edges, ...incoming.edges],
                };
              }

              // Not a pagination request, replace the cache
              return incoming;
            },
          },
          songs: {
            keyArgs: [
              'artistId',
              'downloaded',
              'unavailable',
              'search',
              'sortBy',
              'sortDirection',
            ],
            merge(existing, incoming) {
              if (!existing) return incoming;

              // Merge edges if both have them (pagination request)
              if (existing.edges && incoming.edges) {
                return {
                  ...incoming,
                  edges: [...existing.edges, ...incoming.edges],
                };
              }

              // Not a pagination request, replace the cache
              return incoming;
            },
          },
          playlists: {
            keyArgs: ['enabled', 'search'],
            merge(existing, incoming, { args }) {
              if (!existing) return incoming;
              if (!args?.after) return incoming;

              return {
                ...incoming,
                edges: [...existing.edges, ...incoming.edges],
              };
            },
          },
        },
      },
    },
  }),
  defaultOptions: {
    watchQuery: {
      errorPolicy: 'all',
      fetchPolicy: 'cache-first', // Use cache first, only fetch from network if not in cache
      nextFetchPolicy: 'cache-first',
    },
    query: {
      errorPolicy: 'all',
      fetchPolicy: 'cache-first',
    },
  },
});
