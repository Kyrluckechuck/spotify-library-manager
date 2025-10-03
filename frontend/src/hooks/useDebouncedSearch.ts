import { useState, useEffect, useCallback, useRef } from 'react';

export function useDebouncedSearch(
  searchFunction: (query: string) => void,
  delay: number = 500
) {
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedTerm, setDebouncedTerm] = useState('');

  // Store the latest searchFunction in a ref to avoid dependency issues
  const searchFunctionRef = useRef(searchFunction);

  // Keep ref up to date with latest searchFunction
  useEffect(() => {
    searchFunctionRef.current = searchFunction;
  }, [searchFunction]);

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
    searchFunctionRef.current(debouncedTerm);
  }, [debouncedTerm]);

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
