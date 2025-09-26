import React, { useState } from 'react';
import { useMutation } from '@apollo/client/react';
import { DOWNLOAD_URL } from '../../queries/download';

interface DownloadUrlModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export const DownloadUrlModal: React.FC<DownloadUrlModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [url, setUrl] = useState('');
  const [autoTrackArtists, setAutoTrackArtists] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [downloadUrl, { loading }] = useMutation(DOWNLOAD_URL, {
    onCompleted: data => {
      if (data.downloadUrl.success) {
        setErrorMessage(null);
        setUrl('');
        onClose();
        onSuccess?.();
      } else {
        setErrorMessage(data.downloadUrl.message);
      }
    },
    onError: err => {
      setErrorMessage(err.message);
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!url.trim()) {
      setErrorMessage('Please enter a Spotify URL or URI');
      return;
    }

    try {
      await downloadUrl({
        variables: {
          url: url.trim(),
          autoTrackArtists,
        },
      });
    } catch {
      // Error is handled in onError callback
    }
  };

  const handleClose = () => {
    setUrl('');
    setErrorMessage(null);
    setAutoTrackArtists(false);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className='fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'>
      <div className='bg-white rounded-lg p-6 w-full max-w-md mx-4'>
        <div className='flex justify-between items-center mb-4'>
          <h2 className='text-xl font-semibold'>Download Spotify URL</h2>
          <button
            onClick={handleClose}
            className='text-gray-400 hover:text-gray-600'
          >
            <svg
              className='w-6 h-6'
              fill='none'
              stroke='currentColor'
              viewBox='0 0 24 24'
            >
              <path
                strokeLinecap='round'
                strokeLinejoin='round'
                strokeWidth={2}
                d='M6 18L18 6M6 6l12 12'
              />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className='mb-4'>
            <label
              htmlFor='url'
              className='block text-sm font-medium text-gray-700 mb-2'
            >
              Spotify URL or URI
            </label>
            <input
              type='text'
              id='url'
              value={url}
              onChange={e => setUrl(e.target.value)}
              placeholder='https://open.spotify.com/playlist/... or spotify:playlist:...'
              className='w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
              disabled={loading}
            />
          </div>

          <div className='mb-4'>
            <label className='flex items-center'>
              <input
                type='checkbox'
                checked={autoTrackArtists}
                onChange={e => setAutoTrackArtists(e.target.checked)}
                className='mr-2'
                disabled={loading}
              />
              <span className='text-sm text-gray-700'>
                Track artists found in this content
              </span>
            </label>
          </div>

          {errorMessage && (
            <div className='mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded'>
              {errorMessage}
            </div>
          )}

          <div className='flex justify-end gap-2'>
            <button
              type='button'
              onClick={handleClose}
              className='px-4 py-2 text-gray-600 hover:text-gray-800'
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type='submit'
              disabled={loading || !url.trim()}
              className='px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed'
            >
              {loading ? 'Downloading...' : 'Download'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
