import { useState, useEffect } from 'react';
import { useMutation } from '@apollo/client';
import {
  UpdatePlaylistDocument,
  type UpdatePlaylistMutation,
  type UpdatePlaylistMutationVariables,
} from '../../types/generated/graphql';
import { CREATE_PLAYLIST } from '../../queries/download';

import type { Playlist } from '../../types/generated/graphql';

interface PlaylistModalProps {
  isOpen: boolean;
  onClose: () => void;
  playlist?: Playlist | null;
  mode: 'create' | 'edit';
}

export function PlaylistModal({
  isOpen,
  onClose,
  playlist,
  mode,
}: PlaylistModalProps) {
  const [name, setName] = useState('');
  const [url, setUrl] = useState('');
  const [autoTrackArtists, setAutoTrackArtists] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [updatePlaylist] = useMutation<
    UpdatePlaylistMutation,
    UpdatePlaylistMutationVariables
  >(UpdatePlaylistDocument);

  const [createPlaylist] = useMutation(CREATE_PLAYLIST);

  // Initialize form when editing
  useEffect(() => {
    if (playlist && mode === 'edit') {
      setName(playlist.name);
      setUrl(playlist.url);
      setAutoTrackArtists(playlist.autoTrackArtists);
    } else {
      setName('');
      setUrl('');
      setAutoTrackArtists(false);
    }
    setError(null);
  }, [playlist, mode]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      setError('Please enter a playlist name');
      return;
    }

    if (!url.trim()) {
      setError('Please enter a playlist URL or URI');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      if (mode === 'create') {
        const result = await createPlaylist({
          variables: {
            name: name.trim(),
            url: url.trim(),
            autoTrackArtists,
          },
        });

        if (result.data?.createPlaylist) {
          setName('');
          setUrl('');
          setAutoTrackArtists(false);
          onClose();
        } else {
          setError('Failed to create playlist');
        }
      } else {
        const result = await updatePlaylist({
          variables: {
            playlistId: playlist?.id ?? 0,
            name: name.trim(),
            autoTrackArtists,
          },
        });

        if (result.data?.updatePlaylist?.success) {
          setName('');
          setUrl('');
          setAutoTrackArtists(false);
          onClose();
        } else {
          setError(
            result.data?.updatePlaylist?.message || 'Failed to update playlist'
          );
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setName('');
      setUrl('');
      setAutoTrackArtists(false);
      setError(null);
      onClose();
    }
  };

  if (!isOpen) return null;

  const title = mode === 'create' ? 'Create Playlist' : 'Edit Playlist';
  const submitText = mode === 'create' ? 'Create Playlist' : 'Update Playlist';

  return (
    <div className='fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'>
      <div className='bg-white rounded-lg shadow-xl max-w-md w-full mx-4'>
        <div className='px-6 py-4 border-b border-gray-200'>
          <h3 className='text-lg font-semibold text-gray-900'>{title}</h3>
          <p className='text-sm text-gray-600 mt-1'>
            {mode === 'create'
              ? 'Create a new playlist and choose whether to auto-track artists'
              : 'Update the playlist name'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className='px-6 py-4'>
          <div className='mb-4'>
            <label
              htmlFor='name'
              className='block text-sm font-medium text-gray-700 mb-2'
            >
              Playlist Name
            </label>
            <input
              type='text'
              id='name'
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder='Enter playlist name'
              className='w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
              disabled={isSubmitting}
            />
          </div>

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
              className='w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
              disabled={isSubmitting}
            />
            <p className='text-xs text-gray-500 mt-1'>
              Copy from Spotify: Share → Copy link or Copy Spotify URI
            </p>
          </div>

          {mode === 'create' && (
            <div className='mb-6'>
              <label className='flex items-center'>
                <input
                  type='checkbox'
                  checked={autoTrackArtists}
                  onChange={e => setAutoTrackArtists(e.target.checked)}
                  className='h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
                  disabled={isSubmitting}
                />
                <span className='ml-2 text-sm text-gray-700'>
                  Track artists found in this playlist
                </span>
              </label>
              <p className='text-xs text-gray-500 mt-1'>
                When enabled, all artists from the playlist will be
                automatically tracked for future releases
              </p>
            </div>
          )}

          {error && (
            <div className='mb-4 p-3 bg-red-50 border border-red-200 rounded-md'>
              <p className='text-sm text-red-600'>{error}</p>
            </div>
          )}

          <div className='flex justify-end gap-3'>
            <button
              type='button'
              onClick={handleClose}
              disabled={isSubmitting}
              className='px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50'
            >
              Cancel
            </button>
            <button
              type='submit'
              disabled={isSubmitting || !name.trim() || !url.trim()}
              className='px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50'
            >
              {isSubmitting ? 'Updating...' : submitText}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
