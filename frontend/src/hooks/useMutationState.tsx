import { useState, useCallback, useRef, useEffect } from 'react';

/**
 * Custom hook to manage mutation state (loading, pulse animations, errors) for table items.
 *
 * This hook provides a standardized way to track:
 * - Which items are currently mutating (shows loading spinners)
 * - Which items should show success pulse animation (brief green flash)
 * - Error messages per item ID
 *
 * @example
 * ```tsx
 * const { mutatingIds, pulseIds, errorById, handleMutation } = useMutationState();
 *
 * const handleToggle = async (itemId: number) => {
 *   await handleMutation(itemId, async () => {
 *     await toggleMutation({ variables: { id: itemId } });
 *     toast.success('Item toggled');
 *   }, { withPulse: true });
 * };
 * ```
 */
export function useMutationState() {
  const [mutatingIds, setMutatingIds] = useState<Set<number>>(new Set());
  const [pulseIds, setPulseIds] = useState<Set<number>>(new Set());
  const [errorById, setErrorById] = useState<Record<number, string>>({});

  // Track active timeouts for cleanup on unmount
  const timeoutIdsRef = useRef<Set<number>>(new Set());

  /**
   * Executes a mutation with automatic state management.
   *
   * @param id - The ID of the item being mutated
   * @param mutationFn - Async function that performs the mutation
   * @param options.withPulse - Whether to show success pulse animation (default: false)
   * @param options.pulseDuration - Duration of pulse animation in ms (default: 500)
   */
  const handleMutation = useCallback(
    async (
      id: number,
      mutationFn: () => Promise<void>,
      options: { withPulse?: boolean; pulseDuration?: number } = {}
    ) => {
      const { withPulse = false, pulseDuration = 500 } = options;

      try {
        // Clear any previous error
        setErrorById(prev => ({ ...prev, [id]: '' }));

        // Mark as mutating (shows loading spinner)
        setMutatingIds(prev => new Set(prev).add(id));

        // Execute the mutation
        await mutationFn();

        // Show success pulse if requested
        if (withPulse) {
          setPulseIds(prev => new Set(prev).add(id));
        }
      } catch (error) {
        // Store error message for display
        setErrorById(prev => ({
          ...prev,
          [id]: error instanceof Error ? error.message : 'Action failed',
        }));
      } finally {
        // Always remove from mutating set
        setMutatingIds(prev => {
          const next = new Set(prev);
          next.delete(id);
          return next;
        });

        // Remove pulse after animation duration
        if (withPulse) {
          const timeoutId = window.setTimeout(() => {
            setPulseIds(prev => {
              const next = new Set(prev);
              next.delete(id);
              return next;
            });
            // Remove this timeout from tracking set once it fires
            timeoutIdsRef.current.delete(timeoutId);
          }, pulseDuration);

          // Track this timeout for cleanup
          timeoutIdsRef.current.add(timeoutId);
        }
      }
    },
    []
  );

  // Cleanup all pending timeouts on unmount
  useEffect(() => {
    const timeouts = timeoutIdsRef.current;
    return () => {
      timeouts.forEach(timeoutId => clearTimeout(timeoutId));
      timeouts.clear();
    };
  }, []);

  /**
   * Clears the error for a specific item ID.
   */
  const clearError = useCallback((id: number) => {
    setErrorById(prev => ({ ...prev, [id]: '' }));
  }, []);

  /**
   * Clears all errors.
   */
  const clearAllErrors = useCallback(() => {
    setErrorById({});
  }, []);

  return {
    mutatingIds,
    pulseIds,
    errorById,
    handleMutation,
    clearError,
    clearAllErrors,
  };
}

/**
 * Hook variant that only manages a loading state Set (no pulse or errors).
 * Useful when you need multiple independent loading states in the same component.
 *
 * @example
 * ```tsx
 * const syncState = useMutationLoadingState();
 * const downloadState = useMutationLoadingState();
 *
 * <button disabled={syncState.isLoading(itemId)}>Sync</button>
 * <button disabled={downloadState.isLoading(itemId)}>Download</button>
 * ```
 */
export function useMutationLoadingState() {
  const [loadingIds, setLoadingIds] = useState<Set<number>>(new Set());

  const startLoading = useCallback((id: number) => {
    setLoadingIds(prev => new Set(prev).add(id));
  }, []);

  const stopLoading = useCallback((id: number) => {
    setLoadingIds(prev => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
  }, []);

  const isLoading = useCallback(
    (id: number) => {
      return loadingIds.has(id);
    },
    [loadingIds]
  );

  return {
    loadingIds,
    isLoading,
    startLoading,
    stopLoading,
  };
}
