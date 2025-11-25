import { useContext } from 'react';
import { SpotifySearchContext } from './SpotifySearchContext';

export function useSpotifySearch() {
  const context = useContext(SpotifySearchContext);
  if (!context) {
    throw new Error(
      'useSpotifySearch must be used within a SpotifySearchProvider'
    );
  }
  return context;
}
