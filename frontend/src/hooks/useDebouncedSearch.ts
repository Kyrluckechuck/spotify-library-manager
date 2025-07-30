import { useState, useEffect, useCallback } from 'react';

export function useDebouncedSearch(
  searchFunction: (query: string) => void,
  delay: number = 500
) {
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedTerm, setDebouncedTerm] = useState('');

  // Debounce the search term
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedTerm(searchTerm);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [searchTerm, delay]);

  // Call search function when debounced term changes
  useEffect(() => {
    searchFunction(debouncedTerm);
  }, [debouncedTerm, searchFunction]);

  const handleSearchChange = useCallback((value: string) => {
    setSearchTerm(value);
  }, []);

  const clearSearch = useCallback(() => {
    setSearchTerm('');
    setDebouncedTerm('');
  }, []);

  return {
    searchTerm,
    debouncedTerm,
    handleSearchChange,
    clearSearch,
  };
}
