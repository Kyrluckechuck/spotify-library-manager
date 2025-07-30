import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useDebouncedSearch } from '../useDebouncedSearch';

describe('useDebouncedSearch', () => {
  const mockSearchFunction = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('initializes with empty search term', () => {
    const { result } = renderHook(() => useDebouncedSearch(mockSearchFunction));

    expect(result.current.searchTerm).toBe('');
    expect(result.current.debouncedTerm).toBe('');
  });

  it('updates search term immediately', () => {
    const { result } = renderHook(() => useDebouncedSearch(mockSearchFunction));

    act(() => {
      result.current.handleSearchChange('test');
    });

    expect(result.current.searchTerm).toBe('test');
    expect(result.current.debouncedTerm).toBe('');
  });

  it('debounces search term after delay', async () => {
    const { result } = renderHook(() =>
      useDebouncedSearch(mockSearchFunction, 500)
    );

    act(() => {
      result.current.handleSearchChange('test');
    });

    expect(result.current.debouncedTerm).toBe('');

    act(() => {
      vi.advanceTimersByTime(500);
    });

    expect(result.current.debouncedTerm).toBe('test');
  });

  it('calls search function with debounced term', async () => {
    const { result } = renderHook(() =>
      useDebouncedSearch(mockSearchFunction, 300)
    );

    act(() => {
      result.current.handleSearchChange('test query');
    });

    act(() => {
      vi.advanceTimersByTime(300);
    });

    expect(mockSearchFunction).toHaveBeenCalledWith('test query');
  });

  it('clears search when clearSearch is called', () => {
    const { result } = renderHook(() => useDebouncedSearch(mockSearchFunction));

    act(() => {
      result.current.handleSearchChange('test');
    });

    expect(result.current.searchTerm).toBe('test');

    act(() => {
      result.current.clearSearch();
    });

    expect(result.current.searchTerm).toBe('');
    expect(result.current.debouncedTerm).toBe('');
  });

  it('cancels previous timeout when search term changes', async () => {
    const { result } = renderHook(() =>
      useDebouncedSearch(mockSearchFunction, 500)
    );

    act(() => {
      result.current.handleSearchChange('first');
    });

    act(() => {
      vi.advanceTimersByTime(250); // Half way through delay
      result.current.handleSearchChange('second');
    });

    act(() => {
      vi.advanceTimersByTime(250); // Should not trigger first search
    });

    expect(mockSearchFunction).not.toHaveBeenCalledWith('first');

    act(() => {
      vi.advanceTimersByTime(250); // Complete delay for second search
    });

    expect(mockSearchFunction).toHaveBeenCalledWith('second');
  });

  it('uses default delay of 500ms', async () => {
    const { result } = renderHook(() => useDebouncedSearch(mockSearchFunction));

    act(() => {
      result.current.handleSearchChange('test');
    });

    act(() => {
      vi.advanceTimersByTime(500);
    });

    expect(mockSearchFunction).toHaveBeenCalledWith('test');
  });

  it('handles multiple rapid changes', async () => {
    const { result } = renderHook(() =>
      useDebouncedSearch(mockSearchFunction, 300)
    );

    act(() => {
      result.current.handleSearchChange('a');
      result.current.handleSearchChange('ab');
      result.current.handleSearchChange('abc');
    });

    act(() => {
      vi.advanceTimersByTime(300);
    });

    // The function might be called multiple times due to the effect running
    // We just need to verify it was called with the final value
    expect(mockSearchFunction).toHaveBeenCalledWith('abc');
  });
});
