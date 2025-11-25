import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useLazyQuery, useMutation } from '@apollo/client/react';
import { useNavigate } from '@tanstack/react-router';
import type { SpotifySearchQuery } from '../../types/generated/graphql';
import {
  SpotifySearchDocument,
  TrackArtistDocument,
  DownloadUrlDocument,
  SavePlaylistDocument,
} from '../../types/generated/graphql';
import { useToast } from './useToast';

interface SpotifySearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type TabType = 'all' | 'artists' | 'albums' | 'tracks' | 'playlists';

const DEBOUNCE_MS = 400;

export const SpotifySearchModal: React.FC<SpotifySearchModalProps> = ({
  isOpen,
  onClose,
}) => {
  const toast = useToast();
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [activeTab, setActiveTab] = useState<TabType>('all');
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceRef = useRef<NodeJS.Timeout | null>(null);

  const [executeSearch, { data, loading, error }] =
    useLazyQuery<SpotifySearchQuery>(SpotifySearchDocument);

  const [trackArtist, { loading: trackingArtist }] =
    useMutation(TrackArtistDocument);
  const [downloadUrl, { loading: downloading }] =
    useMutation(DownloadUrlDocument);
  const [savePlaylist, { loading: savingPlaylist }] =
    useMutation(SavePlaylistDocument);

  // Focus input when modal opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  // Reset state when modal closes
  useEffect(() => {
    if (!isOpen) {
      setQuery('');
      setActiveTab('all');
    }
  }, [isOpen]);

  // Debounced search
  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    if (query.trim().length < 2) return;

    debounceRef.current = setTimeout(() => {
      const types =
        activeTab === 'all'
          ? ['artist', 'album', 'track', 'playlist']
          : [activeTab.slice(0, -1)]; // Remove trailing 's'

      executeSearch({
        variables: {
          query: query.trim(),
          types,
          limit: 10,
        },
      });
    }, DEBOUNCE_MS);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [query, activeTab, executeSearch]);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const handleTrackArtist = useCallback(
    async (localId: number | null, spotifyUri: string, name: string) => {
      try {
        if (localId) {
          // Artist exists locally, track it
          await trackArtist({ variables: { artistId: localId } });
          toast.success(`Now tracking "${name}"`);
        } else {
          // Artist doesn't exist, download/add by URI
          await downloadUrl({
            variables: { url: spotifyUri, autoTrackArtists: true },
          });
          toast.success(`Adding "${name}" to library`);
        }
      } catch (err) {
        toast.error(`Failed to track artist: ${err}`);
      }
    },
    [trackArtist, downloadUrl, toast]
  );

  const handleDownload = useCallback(
    async (spotifyUri: string, name: string) => {
      try {
        await downloadUrl({
          variables: { url: spotifyUri, autoTrackArtists: false },
        });
        toast.success(`Started downloading "${name}"`);
      } catch (err) {
        toast.error(`Failed to start download: ${err}`);
      }
    },
    [downloadUrl, toast]
  );

  const handleSavePlaylist = useCallback(
    async (spotifyId: string, name: string) => {
      try {
        await savePlaylist({
          variables: { spotifyId, autoTrackArtists: false },
        });
        toast.success(`Saved playlist "${name}" for tracking`);
      } catch (err) {
        toast.error(`Failed to save playlist: ${err}`);
      }
    },
    [savePlaylist, toast]
  );

  const handleNavigate = useCallback(
    (path: string) => {
      onClose();
      navigate({ to: path });
    },
    [onClose, navigate]
  );

  const results = data?.spotifySearch;
  const hasResults =
    results &&
    (results.artists.length > 0 ||
      results.albums.length > 0 ||
      results.tracks.length > 0 ||
      results.playlists.length > 0);

  if (!isOpen) return null;

  const tabs: { id: TabType; label: string; count?: number }[] = [
    { id: 'all', label: 'All' },
    { id: 'artists', label: 'Artists', count: results?.artists.length },
    { id: 'albums', label: 'Albums', count: results?.albums.length },
    { id: 'tracks', label: 'Tracks', count: results?.tracks.length },
    { id: 'playlists', label: 'Playlists', count: results?.playlists.length },
  ];

  return (
    <div className='fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center z-50 pt-[10vh]'>
      <div className='bg-white rounded-lg w-full max-w-2xl mx-4 max-h-[80vh] flex flex-col shadow-2xl'>
        {/* Header with search input */}
        <div className='p-4 border-b'>
          <div className='flex items-center gap-3'>
            <svg
              className='w-5 h-5 text-gray-400'
              fill='none'
              stroke='currentColor'
              viewBox='0 0 24 24'
            >
              <path
                strokeLinecap='round'
                strokeLinejoin='round'
                strokeWidth={2}
                d='M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z'
              />
            </svg>
            <input
              ref={inputRef}
              type='text'
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder='Search Spotify for artists, albums, tracks, or playlists...'
              className='flex-1 text-lg outline-none placeholder-gray-400'
            />
            <button
              onClick={onClose}
              className='text-gray-400 hover:text-gray-600 p-1'
            >
              <svg
                className='w-5 h-5'
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

          {/* Tabs */}
          {query.trim().length >= 2 && (
            <div className='flex gap-1 mt-3'>
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                    activeTab === tab.id
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
                  }`}
                >
                  {tab.label}
                  {tab.count !== undefined && tab.count > 0 && (
                    <span className='ml-1 text-xs opacity-70'>
                      ({tab.count})
                    </span>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Results */}
        <div className='flex-1 overflow-y-auto'>
          {loading && (
            <div className='flex items-center justify-center py-12'>
              <svg
                className='animate-spin h-8 w-8 text-indigo-600'
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
            </div>
          )}

          {error && (
            <div className='p-4 text-red-600 text-center'>
              Search failed: {error.message}
            </div>
          )}

          {!loading && !error && query.trim().length < 2 && (
            <div className='flex flex-col items-center justify-center py-12 text-gray-500'>
              <svg
                className='w-12 h-12 mb-3 opacity-50'
                fill='none'
                stroke='currentColor'
                viewBox='0 0 24 24'
              >
                <path
                  strokeLinecap='round'
                  strokeLinejoin='round'
                  strokeWidth={1.5}
                  d='M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z'
                />
              </svg>
              <p>Type at least 2 characters to search Spotify</p>
            </div>
          )}

          {!loading && !error && query.trim().length >= 2 && !hasResults && (
            <div className='flex flex-col items-center justify-center py-12 text-gray-500'>
              <p>No results found for &ldquo;{query}&rdquo;</p>
            </div>
          )}

          {!loading && hasResults && (
            <div className='divide-y'>
              {/* Artists */}
              {(activeTab === 'all' || activeTab === 'artists') &&
                results.artists.length > 0 && (
                  <ResultSection title='Artists'>
                    {results.artists.map(artist => (
                      <ArtistResult
                        key={artist.id}
                        artist={artist}
                        onTrack={() =>
                          handleTrackArtist(
                            artist.localId ?? null,
                            artist.spotifyUri,
                            artist.name
                          )
                        }
                        onNavigate={
                          artist.localId
                            ? () => handleNavigate(`/artists/${artist.localId}`)
                            : undefined
                        }
                        isLoading={trackingArtist || downloading}
                      />
                    ))}
                  </ResultSection>
                )}

              {/* Albums */}
              {(activeTab === 'all' || activeTab === 'albums') &&
                results.albums.length > 0 && (
                  <ResultSection title='Albums'>
                    {results.albums.map(album => (
                      <AlbumResult
                        key={album.id}
                        album={album}
                        onDownload={() =>
                          handleDownload(album.spotifyUri, album.name)
                        }
                        isLoading={downloading}
                      />
                    ))}
                  </ResultSection>
                )}

              {/* Tracks */}
              {(activeTab === 'all' || activeTab === 'tracks') &&
                results.tracks.length > 0 && (
                  <ResultSection title='Tracks'>
                    {results.tracks.map(track => (
                      <TrackResult
                        key={track.id}
                        track={track}
                        onDownload={() =>
                          handleDownload(track.spotifyUri, track.name)
                        }
                        isLoading={downloading}
                      />
                    ))}
                  </ResultSection>
                )}

              {/* Playlists */}
              {(activeTab === 'all' || activeTab === 'playlists') &&
                results.playlists.length > 0 && (
                  <ResultSection title='Playlists'>
                    {results.playlists.map(playlist => (
                      <PlaylistResult
                        key={playlist.id}
                        playlist={playlist}
                        onSave={() =>
                          handleSavePlaylist(playlist.id, playlist.name)
                        }
                        onDownload={() =>
                          handleDownload(playlist.spotifyUri, playlist.name)
                        }
                        isLoading={downloading || savingPlaylist}
                      />
                    ))}
                  </ResultSection>
                )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className='px-4 py-2 border-t bg-gray-50 text-xs text-gray-500 flex justify-between items-center rounded-b-lg'>
          <span>Press ESC to close</span>
          <span>
            Powered by{' '}
            <span className='text-green-600 font-medium'>Spotify</span>
          </span>
        </div>
      </div>
    </div>
  );
};

// Sub-components

interface ResultSectionProps {
  title: string;
  children: React.ReactNode;
}

const ResultSection: React.FC<ResultSectionProps> = ({ title, children }) => (
  <div className='py-2'>
    <h3 className='px-4 py-1 text-xs font-semibold text-gray-500 uppercase tracking-wider'>
      {title}
    </h3>
    <div>{children}</div>
  </div>
);

interface ArtistResultProps {
  artist: SpotifySearchQuery['spotifySearch']['artists'][0];
  onTrack: () => void;
  onNavigate?: () => void;
  isLoading: boolean;
}

const ArtistResult: React.FC<ArtistResultProps> = ({
  artist,
  onTrack,
  onNavigate,
  isLoading,
}) => (
  <div className='flex items-center gap-3 px-4 py-2 hover:bg-gray-50'>
    {artist.imageUrl ? (
      <img
        src={artist.imageUrl}
        alt={artist.name}
        className='w-12 h-12 rounded-full object-cover'
      />
    ) : (
      <div className='w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center'>
        <svg
          className='w-6 h-6 text-gray-400'
          fill='currentColor'
          viewBox='0 0 24 24'
        >
          <path d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z' />
        </svg>
      </div>
    )}
    <div className='flex-1 min-w-0'>
      <div className='font-medium text-gray-900 truncate'>{artist.name}</div>
      <div className='text-sm text-gray-500'>
        {artist.followerCount.toLocaleString()} followers
        {artist.genres.length > 0 && (
          <span className='ml-2 text-gray-400'>
            · {artist.genres.slice(0, 2).join(', ')}
          </span>
        )}
      </div>
    </div>
    <div className='flex items-center gap-2'>
      {artist.isTracked ? (
        <span className='px-2 py-0.5 text-xs font-medium bg-indigo-100 text-indigo-700 rounded'>
          Tracked
        </span>
      ) : artist.inLibrary ? (
        <span className='px-2 py-0.5 text-xs font-medium bg-green-100 text-green-700 rounded'>
          In Library
        </span>
      ) : null}
      {onNavigate && (
        <button
          onClick={onNavigate}
          className='px-3 py-1 text-sm text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 rounded'
        >
          View
        </button>
      )}
      {!artist.isTracked && (
        <button
          onClick={onTrack}
          disabled={isLoading}
          className='px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50'
        >
          {artist.inLibrary ? 'Start Tracking' : 'Track'}
        </button>
      )}
    </div>
  </div>
);

interface AlbumResultProps {
  album: SpotifySearchQuery['spotifySearch']['albums'][0];
  onDownload: () => void;
  isLoading: boolean;
}

const AlbumResult: React.FC<AlbumResultProps> = ({
  album,
  onDownload,
  isLoading,
}) => (
  <div className='flex items-center gap-3 px-4 py-2 hover:bg-gray-50'>
    {album.imageUrl ? (
      <img
        src={album.imageUrl}
        alt={album.name}
        className='w-12 h-12 rounded object-cover'
      />
    ) : (
      <div className='w-12 h-12 rounded bg-gray-200 flex items-center justify-center'>
        <svg
          className='w-6 h-6 text-gray-400'
          fill='currentColor'
          viewBox='0 0 24 24'
        >
          <path d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 14.5c-2.49 0-4.5-2.01-4.5-4.5S9.51 7.5 12 7.5s4.5 2.01 4.5 4.5-2.01 4.5-4.5 4.5zm0-5.5c-.55 0-1 .45-1 1s.45 1 1 1 1-.45 1-1-.45-1-1-1z' />
        </svg>
      </div>
    )}
    <div className='flex-1 min-w-0'>
      <div className='font-medium text-gray-900 truncate'>{album.name}</div>
      <div className='text-sm text-gray-500 truncate'>
        {album.artistName} · {album.albumType} · {album.totalTracks} tracks
        {album.releaseDate && (
          <span className='ml-1'>· {album.releaseDate.slice(0, 4)}</span>
        )}
      </div>
    </div>
    <div className='flex items-center gap-2'>
      {album.inLibrary && (
        <span className='px-2 py-0.5 text-xs font-medium bg-green-100 text-green-700 rounded'>
          In Library
        </span>
      )}
      <button
        onClick={onDownload}
        disabled={isLoading}
        className='px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50'
      >
        Download
      </button>
    </div>
  </div>
);

interface TrackResultProps {
  track: SpotifySearchQuery['spotifySearch']['tracks'][0];
  onDownload: () => void;
  isLoading: boolean;
}

const TrackResult: React.FC<TrackResultProps> = ({
  track,
  onDownload,
  isLoading,
}) => {
  const formatDuration = (ms: number) => {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className='flex items-center gap-3 px-4 py-2 hover:bg-gray-50'>
      <div className='w-10 h-10 rounded bg-gray-200 flex items-center justify-center'>
        <svg
          className='w-5 h-5 text-gray-400'
          fill='currentColor'
          viewBox='0 0 24 24'
        >
          <path d='M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z' />
        </svg>
      </div>
      <div className='flex-1 min-w-0'>
        <div className='font-medium text-gray-900 truncate'>{track.name}</div>
        <div className='text-sm text-gray-500 truncate'>
          {track.artistName} · {track.albumName}
        </div>
      </div>
      <div className='text-sm text-gray-400'>
        {formatDuration(track.durationMs)}
      </div>
      <div className='flex items-center gap-2'>
        {track.inLibrary && (
          <span className='px-2 py-0.5 text-xs font-medium bg-green-100 text-green-700 rounded'>
            In Library
          </span>
        )}
        <button
          onClick={onDownload}
          disabled={isLoading}
          className='px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50'
        >
          Download
        </button>
      </div>
    </div>
  );
};

interface PlaylistResultProps {
  playlist: SpotifySearchQuery['spotifySearch']['playlists'][0];
  onSave: () => void;
  onDownload: () => void;
  isLoading: boolean;
}

const PlaylistResult: React.FC<PlaylistResultProps> = ({
  playlist,
  onSave,
  onDownload,
  isLoading,
}) => (
  <div className='flex items-center gap-3 px-4 py-2 hover:bg-gray-50'>
    {playlist.imageUrl ? (
      <img
        src={playlist.imageUrl}
        alt={playlist.name}
        className='w-12 h-12 rounded object-cover'
      />
    ) : (
      <div className='w-12 h-12 rounded bg-gray-200 flex items-center justify-center'>
        <svg
          className='w-6 h-6 text-gray-400'
          fill='currentColor'
          viewBox='0 0 24 24'
        >
          <path d='M15 6H3v2h12V6zm0 4H3v2h12v-2zM3 16h8v-2H3v2zM17 6v8.18c-.31-.11-.65-.18-1-.18-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3V8h3V6h-5z' />
        </svg>
      </div>
    )}
    <div className='flex-1 min-w-0'>
      <div className='font-medium text-gray-900 truncate'>{playlist.name}</div>
      <div className='text-sm text-gray-500 truncate'>
        by {playlist.ownerName} · {playlist.trackCount} tracks
      </div>
      {playlist.description && (
        <div className='text-xs text-gray-400 truncate'>
          {playlist.description}
        </div>
      )}
    </div>
    <div className='flex items-center gap-2'>
      {playlist.inLibrary ? (
        <span className='px-2 py-0.5 text-xs font-medium bg-green-100 text-green-700 rounded'>
          Saved
        </span>
      ) : (
        <button
          onClick={onSave}
          disabled={isLoading}
          className='px-3 py-1 text-sm text-indigo-600 border border-indigo-600 rounded hover:bg-indigo-50 disabled:opacity-50'
        >
          Save
        </button>
      )}
      <button
        onClick={onDownload}
        disabled={isLoading}
        className='px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50'
      >
        Download
      </button>
    </div>
  </div>
);
