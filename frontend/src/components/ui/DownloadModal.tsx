import React, { useState, useEffect } from 'react';
import { useMutation } from '@apollo/client/react';
import {
  DownloadUrlDocument,
  CreatePlaylistDocument,
} from '../../types/generated/graphql';
import { useToast } from './useToast';
import type { ContentType } from '../../types/shared';

interface DownloadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

interface DetectedContent {
  type: ContentType;
  icon: string;
  label: string;
  buttonText: string;
}

const detectContentType = (url: string): DetectedContent => {
  const trimmedUrl = url.trim().toLowerCase();

  if (!trimmedUrl) {
    return {
      type: 'unknown',
      icon: '💡',
      label: 'Enter a Spotify URL to detect content type',
      buttonText: 'Download',
    };
  }

  // Check for playlist
  if (trimmedUrl.includes('/playlist/') || trimmedUrl.includes('playlist:')) {
    return {
      type: 'playlist',
      icon: '📜',
      label: 'Playlist detected',
      buttonText: 'Download Playlist', // Will be updated based on save setting
    };
  }

  // Check for artist
  if (trimmedUrl.includes('/artist/') || trimmedUrl.includes('artist:')) {
    return {
      type: 'artist',
      icon: '🎤',
      label: 'Artist detected',
      buttonText: 'Download Artist',
    };
  }

  // Check for album
  if (trimmedUrl.includes('/album/') || trimmedUrl.includes('album:')) {
    return {
      type: 'album',
      icon: '💿',
      label: 'Album detected',
      buttonText: 'Download Album',
    };
  }

  // Check for track/song
  if (trimmedUrl.includes('/track/') || trimmedUrl.includes('track:')) {
    return {
      type: 'track',
      icon: '🎵',
      label: 'Track detected',
      buttonText: 'Download Track',
    };
  }

  // If URL contains spotify but not recognized
  if (trimmedUrl.includes('spotify')) {
    return {
      type: 'unknown',
      icon: '❌',
      label: 'URL not recognized - please check format',
      buttonText: 'Download',
    };
  }

  // Generic URL
  return {
    type: 'unknown',
    icon: '❓',
    label: 'Unknown URL format',
    buttonText: 'Download',
  };
};

const extractPlaylistName = (url: string): string => {
  // Try to extract a reasonable name from the URL
  const match = url.match(/playlist\/([a-zA-Z0-9]+)/);
  if (match) {
    return `Playlist ${match[1]}`;
  }
  return 'Downloaded Playlist';
};

const STORAGE_KEYS = {
  SAVE_PLAYLISTS: 'download-modal-save-playlists',
  AUTO_TRACK_ARTISTS: 'download-modal-auto-track-artists',
} as const;

export const DownloadModal: React.FC<DownloadModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const toast = useToast();
  const [url, setUrl] = useState('');
  const [autoTrackArtists, setAutoTrackArtists] = useState(false);
  const [savePlaylists, setSavePlaylists] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Load preferences from localStorage
  useEffect(() => {
    const savedSavePlaylists = localStorage.getItem(
      STORAGE_KEYS.SAVE_PLAYLISTS
    );
    const savedAutoTrackArtists = localStorage.getItem(
      STORAGE_KEYS.AUTO_TRACK_ARTISTS
    );

    if (savedSavePlaylists !== null) {
      setSavePlaylists(savedSavePlaylists === 'true');
    }
    if (savedAutoTrackArtists !== null) {
      setAutoTrackArtists(savedAutoTrackArtists === 'true');
    }
  }, []);

  // Save preferences to localStorage when changed
  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.SAVE_PLAYLISTS, savePlaylists.toString());
  }, [savePlaylists]);

  useEffect(() => {
    localStorage.setItem(
      STORAGE_KEYS.AUTO_TRACK_ARTISTS,
      autoTrackArtists.toString()
    );
  }, [autoTrackArtists]);

  const [downloadUrl, { loading: downloadLoading }] =
    useMutation(DownloadUrlDocument);
  const [createPlaylist, { loading: createLoading }] = useMutation(
    CreatePlaylistDocument
  );

  const isLoading = downloadLoading || createLoading;

  // Detect content type from URL
  const detectedContent = detectContentType(url);
  const isPlaylist = detectedContent.type === 'playlist';

  // Dynamic button text for playlists based on save setting
  const getButtonText = (): string => {
    if (isLoading) return 'Processing...';

    if (isPlaylist) {
      return savePlaylists ? 'Save & Download Playlist' : 'Download Playlist';
    }

    return detectedContent.buttonText;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!url.trim()) {
      setErrorMessage('Please enter a Spotify URL or URI');
      return;
    }

    try {
      // If it's a playlist and user wants to save playlists, create playlist first
      if (isPlaylist && savePlaylists) {
        const playlistName = extractPlaylistName(url);

        const playlistResult = await createPlaylist({
          variables: {
            name: playlistName,
            url: url.trim(),
            autoTrackArtists,
          },
        });

        if (playlistResult.data?.createPlaylist) {
          toast.success(
            `Playlist "${playlistName}" saved and download started`
          );
        }
      }

      // Always perform the download
      const downloadResult = await downloadUrl({
        variables: {
          url: url.trim(),
          autoTrackArtists,
        },
      });

      if (downloadResult.data?.downloadUrl?.success) {
        if (!isPlaylist || !savePlaylists) {
          // Show generic success message if not playlist or not saving
          toast.success('Download started successfully');
        }

        setUrl('');
        onSuccess?.();
      } else {
        setErrorMessage(
          downloadResult.data?.downloadUrl?.message || 'Download failed'
        );
      }
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : 'Download failed'
      );
    }
  };

  const handleClose = () => {
    setUrl('');
    setErrorMessage(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className='fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'>
      <div className='bg-white rounded-lg p-6 w-full max-w-md mx-4'>
        <div className='flex justify-between items-center mb-4'>
          <h2 className='text-xl font-semibold'>Download Spotify Content</h2>
          <button
            onClick={handleClose}
            className='text-gray-400 hover:text-gray-600'
            disabled={isLoading}
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
              placeholder='https://open.spotify.com/playlist/... or spotify:artist:...'
              className='w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
              disabled={isLoading}
            />
            {detectedContent.type !== 'unknown' || url.trim() === '' ? (
              <p
                className={`text-sm mt-1 flex items-center ${
                  detectedContent.type === 'unknown'
                    ? url.trim() === ''
                      ? 'text-gray-500'
                      : 'text-red-600'
                    : 'text-green-600'
                }`}
              >
                <span className='mr-1'>{detectedContent.icon}</span>
                {detectedContent.label}
              </p>
            ) : null}
          </div>

          <div className='mb-4 space-y-3'>
            <label className='flex items-center'>
              <input
                type='checkbox'
                checked={autoTrackArtists}
                onChange={e => setAutoTrackArtists(e.target.checked)}
                className='mr-2'
                disabled={isLoading}
              />
              <span className='text-sm text-gray-700'>
                Track artists found in this content
              </span>
            </label>

            {isPlaylist && (
              <label className='flex items-center'>
                <input
                  type='checkbox'
                  checked={savePlaylists}
                  onChange={e => setSavePlaylists(e.target.checked)}
                  className='mr-2'
                  disabled={isLoading}
                />
                <span className='text-sm text-gray-700'>
                  Save playlist to your library for future syncing
                </span>
              </label>
            )}
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
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type='submit'
              disabled={isLoading || !url.trim()}
              className='px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center'
            >
              {isLoading && (
                <svg
                  className='animate-spin -ml-1 mr-2 h-4 w-4 text-white'
                  fill='none'
                  viewBox='0 0 24 24'
                >
                  <circle
                    className='opacity-25'
                    cx='12'
                    cy='12'
                    r='10'
                    stroke='currentColor'
                    strokeWidth='4'
                  />
                  <path
                    className='opacity-75'
                    fill='currentColor'
                    d='M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z'
                  />
                </svg>
              )}
              {getButtonText()}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
