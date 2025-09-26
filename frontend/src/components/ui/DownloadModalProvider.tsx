import React, { useCallback, useMemo, useState } from 'react';
import { DownloadModalContext } from './DownloadModalContext';
import type { DownloadModalContextValue } from './DownloadModalContext';
import { DownloadModal } from './DownloadModal';

export function DownloadModalProvider({
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

  const value = useMemo<DownloadModalContextValue>(
    () => ({
      isOpen,
      open,
      close,
    }),
    [isOpen, open, close]
  );

  return (
    <DownloadModalContext.Provider value={value}>
      {children}
      <DownloadModal isOpen={isOpen} onClose={close} onSuccess={close} />
    </DownloadModalContext.Provider>
  );
}
