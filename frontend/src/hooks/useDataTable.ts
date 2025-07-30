import { useState, useMemo, useCallback } from 'react';

export type SortDirection = 'asc' | 'desc';

interface UseDataTableOptions<T> {
  initialPageSize?: number;
  initialSortField?: T | null;
  initialSortDirection?: SortDirection;
  initialSearchQuery?: string;
}

interface UseDataTableReturn<T> {
  // State
  pageSize: number;
  sortField: T | null;
  sortDirection: SortDirection;
  searchQuery: string;

  // Actions
  setPageSize: (size: number) => void;
  setSortField: (field: T | null) => void;
  setSortDirection: (direction: SortDirection) => void;
  setSearchQuery: (query: string) => void;

  // Computed
  queryVariables: Record<string, unknown>;
  handleSort: (field: T) => void;
  resetFilters: () => void;
}

export function useDataTable<T>({
  initialPageSize = 50,
  initialSortField = null,
  initialSortDirection = 'asc',
  initialSearchQuery = '',
}: UseDataTableOptions<T> = {}): UseDataTableReturn<T> {
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [sortField, setSortField] = useState<T | null>(initialSortField);
  const [sortDirection, setSortDirection] =
    useState<SortDirection>(initialSortDirection);
  const [searchQuery, setSearchQuery] = useState(initialSearchQuery);

  const queryVariables = useMemo(
    () => ({
      first: pageSize,
      sortBy: sortField,
      sortDirection: sortDirection,
      search: searchQuery || undefined,
    }),
    [pageSize, sortField, sortDirection, searchQuery]
  );

  const handleSort = useCallback(
    (field: T) => {
      let newDirection: SortDirection = 'asc';

      if (sortField === field && sortDirection === 'asc') {
        newDirection = 'desc';
      } else if (sortField === field && sortDirection === 'desc') {
        setSortField(null);
        setSortDirection('asc');
        return;
      }

      setSortField(field);
      setSortDirection(newDirection);
    },
    [sortField, sortDirection]
  );

  const resetFilters = useCallback(() => {
    setPageSize(initialPageSize);
    setSortField(initialSortField);
    setSortDirection(initialSortDirection);
    setSearchQuery(initialSearchQuery);
  }, [
    initialPageSize,
    initialSortField,
    initialSortDirection,
    initialSearchQuery,
  ]);

  return {
    // State
    pageSize,
    sortField,
    sortDirection,
    searchQuery,

    // Actions
    setPageSize,
    setSortField,
    setSortDirection,
    setSearchQuery,

    // Computed
    queryVariables,
    handleSort,
    resetFilters,
  };
}
