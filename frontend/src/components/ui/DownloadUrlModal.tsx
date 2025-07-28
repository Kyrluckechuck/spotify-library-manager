import { useState } from 'react';
import { useMutation } from '@apollo/client';
import { DownloadUrlDocument, type DownloadUrlMutation, type DownloadUrlMutationVariables } from '../../types/generated/graphql';


interface DownloadUrlModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function DownloadUrlModal({ isOpen, onClose }: DownloadUrlModalProps) {
  const [url, setUrl] = useState('');
  const [autoTrackArtists, setAutoTrackArtists] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [downloadUrl] = useMutation<DownloadUrlMutation, DownloadUrlMutationVariables>(DownloadUrlDocument);


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!url.trim()) {
      setError('Please enter a Spotify URL or URI');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const result = await downloadUrl({
        variables: {
          url: url.trim(),
          autoTrackArtists
        }
      });

      if (result.data?.downloadUrl.success) {
        setUrl('');
        setAutoTrackArtists(false);
        onClose();
      } else {
        setError(result.data?.downloadUrl.message || 'Failed to start download');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setUrl('');
      setAutoTrackArtists(false);
      setError(null);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Download Spotify URL/URI</h3>
          <p className="text-sm text-gray-600 mt-1">
            Enter a Spotify URL or URI to download tracks, albums, or playlists
          </p>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-4">
          <div className="mb-4">
            <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
              Spotify URL or URI
            </label>
            <input
              type="text"
              id="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://open.spotify.com/playlist/... or spotify:playlist:..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              disabled={isSubmitting}
            />
          </div>

          <div className="mb-6">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={autoTrackArtists}
                onChange={(e) => setAutoTrackArtists(e.target.checked)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                disabled={isSubmitting}
              />
              <span className="ml-2 text-sm text-gray-700">
                Auto-track artists from this download
              </span>
            </label>
            <p className="text-xs text-gray-500 mt-1">
              When enabled, all artists from the downloaded content will be automatically tracked for future releases
            </p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={handleClose}
              disabled={isSubmitting}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !url.trim()}
              className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {isSubmitting ? 'Starting Download...' : 'Start Download'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
} 