import { useContext } from 'react';
import { DownloadModalContext } from './DownloadModalContext';

export function useDownloadModal() {
  const context = useContext(DownloadModalContext);
  if (!context) {
    throw new Error(
      'useDownloadModal must be used within a DownloadModalProvider'
    );
  }
  return context;
}
