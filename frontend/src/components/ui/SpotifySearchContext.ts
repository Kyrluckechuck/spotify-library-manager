import { createContext } from 'react';

export interface SpotifySearchContextValue {
  isOpen: boolean;
  open: () => void;
  close: () => void;
}

export const SpotifySearchContext =
  createContext<SpotifySearchContextValue | null>(null);
