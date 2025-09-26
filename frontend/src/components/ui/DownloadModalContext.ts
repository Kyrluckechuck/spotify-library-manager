import { createContext } from 'react';

export interface DownloadModalContextValue {
  isOpen: boolean;
  open: () => void;
  close: () => void;
}

export const DownloadModalContext =
  createContext<DownloadModalContextValue | null>(null);
