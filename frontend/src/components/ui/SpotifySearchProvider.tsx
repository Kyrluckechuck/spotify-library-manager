import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { SpotifySearchContext } from './SpotifySearchContext';
import type { SpotifySearchContextValue } from './SpotifySearchContext';
import { SpotifySearchModal } from './SpotifySearchModal';

export function SpotifySearchProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isOpen, setIsOpen] = useState(false);

  const open = useCallback(() => {
    setIsOpen(true);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
  }, []);

  // Global keyboard shortcut: Cmd/Ctrl + K to open search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen(prev => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const value = useMemo<SpotifySearchContextValue>(
    () => ({
      isOpen,
      open,
      close,
    }),
    [isOpen, open, close]
  );

  return (
    <SpotifySearchContext.Provider value={value}>
      {children}
      <SpotifySearchModal isOpen={isOpen} onClose={close} />
    </SpotifySearchContext.Provider>
  );
}
