import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useLazyQuery, useMutation } from '@apollo/client/react';
import { useNavigate } from '@tanstack/react-router';
import type { SpotifySearchQuery } from '../../types/generated/graphql';
import {
  SpotifySearchDocument,
  TrackArtistDocument,
  UntrackArtistDocument,
  DownloadUrlDocument,
  SavePlaylistDocument,
  GetPlaylistsDocument,
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
  const [loadingIds, setLoadingIds] = useState<Set<string>>(new Set());
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceRef = useRef<NodeJS.Timeout | null>(null);
  const modalRef = useRef<HTMLDivElement>(null);

  const [executeSearch, { data, loading, error }] =
    useLazyQuery<SpotifySearchQuery>(SpotifySearchDocument);

  const [trackArtist] = useMutation(TrackArtistDocument);
  const [untrackArtist] = useMutation(UntrackArtistDocument);
  const [downloadUrl] = useMutation(DownloadUrlDocument);
  const [savePlaylist] = useMutation(SavePlaylistDocument);

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
      setLoadingIds(new Set());
    }
  }, [isOpen]);

  // Click outside to close
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        isOpen &&
        modalRef.current &&
        !modalRef.current.contains(e.target as Node)
      ) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, onClose]);

  // Helper to track loading state per item
  const startLoading = useCallback((id: string) => {
    setLoadingIds(prev => new Set(prev).add(id));
  }, []);

  const stopLoading = useCallback((id: string) => {
    setLoadingIds(prev => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
  }, []);

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

  // Build refetch queries for search results
  const getSearchRefetchQueries = useCallback(() => {
    if (query.trim().length < 2) return [];
    return [
      {
        query: SpotifySearchDocument,
        variables: {
          query: query.trim(),
          types:
            activeTab === 'all'
              ? ['artist', 'album', 'track', 'playlist']
              : [activeTab.slice(0, -1)],
          limit: 10,
        },
      },
    ];
  }, [query, activeTab]);

  const handleTrackArtist = useCallback(
    async (
      id: string,
      localId: number | null,
      spotifyUri: string,
      name: string
    ) => {
      startLoading(id);
      try {
        if (localId) {
          // Artist exists locally, track it
          await trackArtist({
            variables: { artistId: localId },
            refetchQueries: getSearchRefetchQueries(),
          });
          toast.success(`Now tracking "${name}"`);
        } else {
          // Artist doesn't exist, download/add by URI
          await downloadUrl({
            variables: { url: spotifyUri, autoTrackArtists: true },
            refetchQueries: getSearchRefetchQueries(),
          });
          toast.success(`Adding "${name}" to library`);
        }
      } catch (err) {
        toast.error(`Failed to track artist: ${err}`);
      } finally {
        stopLoading(id);
      }
    },
    [
      trackArtist,
      downloadUrl,
      toast,
      getSearchRefetchQueries,
      startLoading,
      stopLoading,
    ]
  );

  const handleUntrackArtist = useCallback(
    async (id: string, artistId: number, name: string) => {
      startLoading(id);
      try {
        await untrackArtist({
          variables: { artistId },
          refetchQueries: getSearchRefetchQueries(),
        });
        toast.success(`Stopped tracking "${name}"`);
      } catch (err) {
        toast.error(`Failed to untrack artist: ${err}`);
      } finally {
        stopLoading(id);
      }
    },
    [untrackArtist, toast, getSearchRefetchQueries, startLoading, stopLoading]
  );

  const handleDownload = useCallback(
    async (id: string, spotifyUri: string, name: string) => {
      startLoading(id);
      try {
        const result = await downloadUrl({
          variables: { url: spotifyUri, autoTrackArtists: false },
        });
        if (result.data?.downloadUrl?.success) {
          toast.success(`Started downloading "${name}"`);
        } else {
          toast.error(
            result.data?.downloadUrl?.message || `Failed to download "${name}"`
          );
        }
      } catch (err) {
        toast.error(`Failed to start download: ${err}`);
      } finally {
        stopLoading(id);
      }
    },
    [downloadUrl, toast, startLoading, stopLoading]
  );

  const handleSavePlaylist = useCallback(
    async (id: string, spotifyId: string, name: string) => {
      startLoading(id);
      try {
        await savePlaylist({
          variables: { spotifyId, autoTrackArtists: false },
          refetchQueries: [
            ...getSearchRefetchQueries(),
            // Refetch playlists page if it's in the cache
            { query: GetPlaylistsDocument },
          ],
        });
        toast.success(`Saved playlist "${name}" for tracking`);
      } catch (err) {
        toast.error(`Failed to save playlist: ${err}`);
      } finally {
        stopLoading(id);
      }
    },
    [savePlaylist, toast, getSearchRefetchQueries, startLoading, stopLoading]
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
      <div
        ref={modalRef}
        className='bg-white rounded-lg w-full max-w-2xl mx-4 max-h-[80vh] flex flex-col shadow-2xl'
      >
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
                            artist.id,
                            artist.localId ?? null,
                            artist.spotifyUri,
                            artist.name
                          )
                        }
                        onUntrack={
                          artist.localId
                            ? () =>
                                handleUntrackArtist(
                                  artist.id,
                                  artist.localId as number,
                                  artist.name
                                )
                            : undefined
                        }
                        onNavigate={
                          artist.localId
                            ? () => handleNavigate(`/artists/${artist.localId}`)
                            : undefined
                        }
                        isLoading={loadingIds.has(artist.id)}
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
                          handleDownload(album.id, album.spotifyUri, album.name)
                        }
                        isLoading={loadingIds.has(album.id)}
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
                          handleDownload(track.id, track.spotifyUri, track.name)
                        }
                        isLoading={loadingIds.has(track.id)}
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
                          handleSavePlaylist(
                            playlist.id,
                            playlist.id,
                            playlist.name
                          )
                        }
                        onDownload={() =>
                          handleDownload(
                            playlist.id,
                            playlist.spotifyUri,
                            playlist.name
                          )
                        }
                        isLoading={loadingIds.has(playlist.id)}
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

// Reusable loading spinner for buttons
const ButtonSpinner: React.FC = () => (
  <svg className='animate-spin h-4 w-4' fill='none' viewBox='0 0 24 24'>
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
);

// Spotify icon for external links
const SpotifyIcon: React.FC = () => (
  <svg className='w-4 h-4' viewBox='0 0 24 24' fill='currentColor'>
    <path d='M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z' />
  </svg>
);

interface ArtistResultProps {
  artist: SpotifySearchQuery['spotifySearch']['artists'][0];
  onTrack: () => void;
  onUntrack?: () => void;
  onNavigate?: () => void;
  isLoading: boolean;
}

const ArtistResult: React.FC<ArtistResultProps> = ({
  artist,
  onTrack,
  onUntrack,
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
      {artist.inLibrary && !artist.isTracked && (
        <span className='px-2 py-0.5 text-xs font-medium bg-green-100 text-green-700 rounded'>
          In Library
        </span>
      )}
      <a
        href={`https://open.spotify.com/artist/${artist.id}`}
        target='_blank'
        rel='noopener noreferrer'
        className='px-3 py-1 text-sm text-green-600 hover:text-green-700 hover:bg-green-50 rounded'
        title='View on Spotify'
      >
        <SpotifyIcon />
      </a>
      {onNavigate && (
        <button
          onClick={onNavigate}
          className='px-3 py-1 text-sm text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 rounded'
        >
          View
        </button>
      )}
      {artist.isTracked && onUntrack ? (
        <button
          onClick={onUntrack}
          disabled={isLoading}
          className='px-3 py-1 text-sm bg-orange-100 text-orange-800 rounded hover:bg-orange-200 disabled:opacity-50 min-w-[70px] flex items-center justify-center'
        >
          {isLoading ? <ButtonSpinner /> : 'Untrack'}
        </button>
      ) : (
        <button
          onClick={onTrack}
          disabled={isLoading}
          className='px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50 min-w-[70px] flex items-center justify-center'
        >
          {isLoading ? (
            <ButtonSpinner />
          ) : artist.inLibrary ? (
            'Start Tracking'
          ) : (
            'Track'
          )}
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
        <a
          href={`https://open.spotify.com/artist/${album.artistId}`}
          target='_blank'
          rel='noopener noreferrer'
          className='hover:text-green-600 hover:underline'
          onClick={e => e.stopPropagation()}
        >
          {album.artistName}
        </a>
        {' · '}
        {album.albumType} · {album.totalTracks} tracks
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
      <a
        href={`https://open.spotify.com/album/${album.id}`}
        target='_blank'
        rel='noopener noreferrer'
        className='px-3 py-1 text-sm text-green-600 hover:text-green-700 hover:bg-green-50 rounded'
        title='View on Spotify'
      >
        <SpotifyIcon />
      </a>
      <button
        onClick={onDownload}
        disabled={isLoading}
        className='px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50 min-w-[80px] flex items-center justify-center'
      >
        {isLoading ? <ButtonSpinner /> : 'Download'}
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
          <a
            href={`https://open.spotify.com/artist/${track.artistId}`}
            target='_blank'
            rel='noopener noreferrer'
            className='hover:text-green-600 hover:underline'
            onClick={e => e.stopPropagation()}
          >
            {track.artistName}
          </a>
          {' · '}
          <a
            href={`https://open.spotify.com/album/${track.albumId}`}
            target='_blank'
            rel='noopener noreferrer'
            className='hover:text-green-600 hover:underline'
            onClick={e => e.stopPropagation()}
          >
            {track.albumName}
          </a>
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
        <a
          href={`https://open.spotify.com/track/${track.id}`}
          target='_blank'
          rel='noopener noreferrer'
          className='px-3 py-1 text-sm text-green-600 hover:text-green-700 hover:bg-green-50 rounded'
          title='View on Spotify'
        >
          <SpotifyIcon />
        </a>
        <button
          onClick={onDownload}
          disabled={isLoading}
          className='px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50 min-w-[80px] flex items-center justify-center'
        >
          {isLoading ? <ButtonSpinner /> : 'Download'}
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
          className='px-3 py-1 text-sm text-indigo-600 border border-indigo-600 rounded hover:bg-indigo-50 disabled:opacity-50 min-w-[50px] flex items-center justify-center'
        >
          {isLoading ? <ButtonSpinner /> : 'Save'}
        </button>
      )}
      <a
        href={`https://open.spotify.com/playlist/${playlist.id}`}
        target='_blank'
        rel='noopener noreferrer'
        className='px-3 py-1 text-sm text-green-600 hover:text-green-700 hover:bg-green-50 rounded'
        title='View on Spotify'
      >
        <SpotifyIcon />
      </a>
      <button
        onClick={onDownload}
        disabled={isLoading}
        className='px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50 min-w-[80px] flex items-center justify-center'
      >
        {isLoading ? <ButtonSpinner /> : 'Download'}
      </button>
    </div>
  </div>
);
