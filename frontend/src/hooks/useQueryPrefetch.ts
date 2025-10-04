import { useCallback } from 'react';
import type { Dispatch, SetStateAction } from 'react';
import { useApolloClient } from '@apollo/client/react';
import type { DocumentNode } from '@apollo/client';

/**
 * Hook to create filter/sort change handlers that prefetch data.
 * Eliminates duplicate setState + client.query pattern across route components.
 *
 * @param query - GraphQL query document to prefetch
 * @param baseVariables - Current query variables to merge with updates
 *
 * @example
 * const createPrefetchHandler = useQueryPrefetch(GetAlbumsDocument, queryVariables);
 *
 * const handleWantedChange = createPrefetchHandler(
 *   setWantedFilter,
 *   (newFilter) => ({
 *     wanted: newFilter === 'all' ? undefined : newFilter === 'wanted'
 *   })
 * );
 */
export function useQueryPrefetch<TVariables extends Record<string, unknown>>(
  query: DocumentNode,
  baseVariables: TVariables
) {
  const client = useApolloClient();

  /**
   * Creates a change handler that updates state and prefetches data.
   *
   * @param setState - State setter function (e.g., setFilter, setSortField), or null for prefetch-only
   * @param getVariableUpdates - Function that transforms new value into GraphQL variable updates
   * @returns Handler function that can be passed to UI components
   */
  const createPrefetchHandler = useCallback(
    <TValue>(
      setState: Dispatch<SetStateAction<TValue>> | null,
      getVariableUpdates: (value: TValue) => Partial<TVariables>
    ) => {
      return (newValue: TValue) => {
        // Update component state if setter provided
        if (setState) {
          setState(newValue as SetStateAction<TValue>);
        }

        // Build new query variables
        const newVariables = {
          ...baseVariables,
          ...getVariableUpdates(newValue),
        } as TVariables;

        // Optimistically prefetch data
        client
          .query({
            query,
            variables: newVariables,
            fetchPolicy: 'cache-first',
          })
          .catch(() => {
            // Silently ignore prefetch errors - they're optimistic
          });
      };
    },
    [client, query, baseVariables]
  );

  return createPrefetchHandler;
}
