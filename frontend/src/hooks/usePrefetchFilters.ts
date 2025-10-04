import { useEffect } from 'react';
import { useApolloClient } from '@apollo/client/react';
import type { DocumentNode, NetworkStatus } from '@apollo/client';

interface FilterCombination {
  [key: string]: string | number | boolean | undefined;
}

interface PrefetchConfig {
  query: DocumentNode;
  baseVariables: Record<string, unknown>;
  filterCombinations: FilterCombination[];
  enabled?: boolean;
  networkStatus?: NetworkStatus;
}

/**
 * Hook to pre-fetch multiple filter combinations for a GraphQL query.
 * This improves perceived performance by warming the Apollo cache with
 * likely-to-be-requested data combinations.
 *
 * @param config.query - GraphQL query document to pre-fetch
 * @param config.baseVariables - Base variables for all queries (pagination, sort, search, etc)
 * @param config.filterCombinations - Array of filter variable combinations to pre-fetch
 * @param config.enabled - Whether prefetching is enabled (default: true when data is loaded)
 * @param config.networkStatus - Apollo network status (skip prefetch during refetch)
 */
export function usePrefetchFilters({
  query,
  baseVariables,
  filterCombinations,
  enabled = true,
  networkStatus,
}: PrefetchConfig) {
  const client = useApolloClient();

  useEffect(() => {
    // Skip if disabled or if currently refetching (networkStatus 3)
    if (!enabled || networkStatus === 3) {
      return;
    }

    // Pre-fetch each filter combination
    filterCombinations.forEach(filterVars => {
      const variables = {
        ...baseVariables,
        ...filterVars,
      };

      client
        .query({
          query,
          variables,
          fetchPolicy: 'cache-first',
        })
        .catch(() => {
          // Silently ignore pre-fetch errors - they're optimistic
        });
    });
  }, [
    enabled,
    networkStatus,
    query,
    baseVariables,
    filterCombinations,
    client,
  ]);
}

/**
 * Helper function to generate all combinations of filter values.
 * Useful for creating filterCombinations array.
 *
 * @example
 * const combinations = generateFilterCombinations({
 *   wanted: [true, false],
 *   downloaded: [true, false],
 * });
 * // Returns: [
 * //   { wanted: true, downloaded: true },
 * //   { wanted: true, downloaded: false },
 * //   { wanted: false, downloaded: true },
 * //   { wanted: false, downloaded: false },
 * // ]
 */
export function generateFilterCombinations(
  filters: Record<string, unknown[]>
): FilterCombination[] {
  const keys = Object.keys(filters);
  if (keys.length === 0) return [];

  const combinations: FilterCombination[] = [];

  function recurse(index: number, current: FilterCombination) {
    if (index === keys.length) {
      combinations.push({ ...current });
      return;
    }

    const key = keys[index];
    const values = filters[key];

    values.forEach((value: unknown) => {
      current[key] = value as string | number | boolean | undefined;
      recurse(index + 1, current);
    });
  }

  recurse(0, {});
  return combinations;
}
