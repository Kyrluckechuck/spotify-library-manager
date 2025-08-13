import type { Playlist } from '../../types/generated/graphql';
import { SortableTableHeader } from '../ui/SortableTableHeader';

export type PlaylistSortField =
  | 'name'
  | 'enabled'
  | 'auto_track_artists'
  | 'last_synced_at'
  | null;

interface PlaylistsTableProps {
  playlists: Playlist[];
  sortField: PlaylistSortField;
  sortDirection: 'asc' | 'desc';
  onSort: (field: PlaylistSortField) => void;
  onToggleEnabled: (playlist: Playlist) => void;
  onToggleAutoTrack: (playlist: Playlist) => void;
  onSyncPlaylist: (playlistId: number) => void;
  onEditPlaylist?: (playlist: Playlist) => void;
  loading?: boolean;
}

export function PlaylistsTable({
  playlists,
  sortField,
  sortDirection,
  onSort,
  onToggleEnabled,
  onToggleAutoTrack,
  onSyncPlaylist,
  onEditPlaylist,
  loading = false,
}: PlaylistsTableProps) {
  if (playlists.length === 0) {
    return (
      <div className='bg-white rounded shadow overflow-hidden'>
        <div className='p-6 text-center text-gray-500'>
          {loading ? 'Loading playlists...' : 'No playlists found.'}
        </div>
      </div>
    );
  }

  return (
    <div className='bg-white rounded shadow overflow-hidden'>
      <div className='overflow-x-auto'>
        <table className='min-w-full divide-y divide-gray-200'>
          <thead className='bg-gray-50'>
            <tr>
              <SortableTableHeader
                field='name'
                currentSortField={sortField}
                currentSortDirection={sortDirection}
                onSort={onSort}
              >
                Playlist
              </SortableTableHeader>
              <SortableTableHeader
                field='enabled'
                currentSortField={sortField}
                currentSortDirection={sortDirection}
                onSort={onSort}
              >
                Status
              </SortableTableHeader>
              <SortableTableHeader
                field='auto_track_artists'
                currentSortField={sortField}
                currentSortDirection={sortDirection}
                onSort={onSort}
              >
                Track Artists
              </SortableTableHeader>
              <SortableTableHeader
                field='last_synced_at'
                currentSortField={sortField}
                currentSortDirection={sortDirection}
                onSort={onSort}
              >
                Last Synced
              </SortableTableHeader>
              <SortableTableHeader
                field={null}
                currentSortField={sortField}
                currentSortDirection={sortDirection}
                onSort={onSort}
              >
                Actions
              </SortableTableHeader>
            </tr>
          </thead>
          <tbody className='bg-white divide-y divide-gray-200'>
            {playlists.map(playlist => (
              <tr key={playlist.id} className='hover:bg-gray-50'>
                <td className='px-6 py-4 whitespace-nowrap'>
                  <div className='text-sm font-medium text-gray-900'>
                    {playlist.name}
                  </div>
                </td>
                <td className='px-6 py-4 whitespace-nowrap'>
                  {/* Mobile: Toggle switch */}
                  <button
                    onClick={() => onToggleEnabled(playlist)}
                    role='switch'
                    aria-checked={playlist.enabled}
                    aria-label={
                      playlist.enabled ? 'Disable playlist' : 'Enable playlist'
                    }
                    className='md:hidden inline-flex items-center w-12 h-6 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 '
                    style={{
                      backgroundColor: playlist.enabled ? '#22c55e' : '#e5e7eb',
                    }}
                  >
                    <span
                      className={`inline-block w-5 h-5 bg-white rounded-full transform transition-transform translate-x-1 ${
                        playlist.enabled ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                    <span className='sr-only'>
                      {playlist.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </button>

                  {/* Desktop: Interactive status pill */}
                  <button
                    onClick={() => onToggleEnabled(playlist)}
                    aria-pressed={playlist.enabled}
                    aria-label={
                      playlist.enabled ? 'Disable playlist' : 'Enable playlist'
                    }
                    className={`group hidden md:inline-flex px-2 py-1 text-xs font-semibold rounded-full transition-colors ${
                      playlist.enabled
                        ? 'bg-green-100 text-green-800 hover:bg-red-100 hover:text-red-800 focus:bg-red-100 focus:text-red-800'
                        : 'bg-red-100 text-red-800 hover:bg-green-100 hover:text-green-800 focus:bg-green-100 focus:text-green-800'
                    }`}
                  >
                    <span className='group-hover:hidden group-focus:hidden'>
                      {playlist.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                    <span className='hidden group-hover:inline group-focus:inline'>
                      {playlist.enabled ? 'Disable' : 'Enable'}
                    </span>
                  </button>
                </td>
                <td className='px-6 py-4 whitespace-nowrap'>
                  {/* Mobile: Toggle switch for auto track */}
                  <button
                    onClick={() => onToggleAutoTrack(playlist)}
                    role='switch'
                    aria-checked={playlist.autoTrackArtists}
                    aria-label={
                      playlist.autoTrackArtists
                        ? 'Disable tracking artists'
                        : 'Enable tracking artists'
                    }
                    className='md:hidden inline-flex items-center w-12 h-6 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 '
                    style={{
                      backgroundColor: playlist.autoTrackArtists
                        ? '#60a5fa'
                        : '#fed7aa',
                    }}
                  >
                    <span
                      className={`inline-block w-5 h-5 bg-white rounded-full transform transition-transform translate-x-1 ${
                        playlist.autoTrackArtists
                          ? 'translate-x-6'
                          : 'translate-x-1'
                      }`}
                    />
                    <span className='sr-only'>
                      {playlist.autoTrackArtists ? 'Enabled' : 'Disabled'}
                    </span>
                  </button>

                  {/* Desktop: Interactive status pill */}
                  <button
                    onClick={() => onToggleAutoTrack(playlist)}
                    aria-pressed={playlist.autoTrackArtists}
                    aria-label={
                      playlist.autoTrackArtists
                        ? 'Disable tracking artists'
                        : 'Enable tracking artists'
                    }
                    className={`group hidden md:inline-flex px-2 py-1 text-xs font-semibold rounded-full transition-colors ${
                      playlist.autoTrackArtists
                        ? 'bg-blue-100 text-blue-800 hover:bg-orange-100 hover:text-orange-800 focus:bg-orange-100 focus:text-orange-800'
                        : 'bg-orange-100 text-orange-800 hover:bg-blue-100 hover:text-blue-800 focus:bg-blue-100 focus:text-blue-800'
                    }`}
                  >
                    <span className='group-hover:hidden group-focus:hidden'>
                      {playlist.autoTrackArtists ? 'Yes' : 'No'}
                    </span>
                    <span className='hidden group-hover:inline group-focus:inline'>
                      {playlist.autoTrackArtists ? 'Disable' : 'Enable'}
                    </span>
                  </button>
                </td>
                <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-500'>
                  {playlist.lastSyncedAt
                    ? new Date(playlist.lastSyncedAt).toLocaleString()
                    : 'Never'}
                </td>
                <td className='px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2'>
                  <button
                    onClick={() => onSyncPlaylist(playlist.id)}
                    className='px-3 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800 hover:bg-blue-200 transition-colors'
                  >
                    Sync Now
                  </button>
                  {onEditPlaylist && (
                    <button
                      onClick={() => onEditPlaylist(playlist)}
                      className='px-3 py-1 rounded text-xs font-medium bg-yellow-100 text-yellow-800 hover:bg-yellow-200 transition-colors'
                    >
                      Edit
                    </button>
                  )}
                  <a
                    href={playlist.url}
                    target='_blank'
                    rel='noopener noreferrer'
                    className='text-indigo-600 hover:text-indigo-900 underline'
                  >
                    Open Spotify
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
