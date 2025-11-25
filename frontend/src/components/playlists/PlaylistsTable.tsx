import type { Playlist } from '../../types/generated/graphql';
import { SortableTableHeader } from '../ui/SortableTableHeader';
import { ToggleStatusButton } from '../ui/ToggleStatusButton';

export type PlaylistSortField =
  | 'name'
  | 'enabled'
  | 'autoTrackArtists'
  | 'lastSyncedAt'
  | null;

interface PlaylistsTableProps {
  playlists: Playlist[];
  sortField: PlaylistSortField;
  sortDirection: 'asc' | 'desc';
  onSort: (field: PlaylistSortField) => void;
  onToggleEnabled: (playlist: Playlist) => void;
  onToggleAutoTrack: (playlist: Playlist) => void;
  onSyncPlaylist: (playlistId: number) => void;
  onForceSyncPlaylist?: (playlistId: number) => void;
  onEditPlaylist?: (playlist: Playlist) => void;
  onDeletePlaylist?: (playlistId: number, playlistName: string) => void;
  loading?: boolean;
  enabledMutatingIds?: Set<number>;
  autoMutatingIds?: Set<number>;
  syncMutatingIds?: Set<number>;
  forceSyncMutatingIds?: Set<number>;
  deleteMutatingIds?: Set<number>;
  enabledPulseIds?: Set<number>;
  autoPulseIds?: Set<number>;
  errorById?: Record<number, string>;
}

export function PlaylistsTable({
  playlists,
  sortField,
  sortDirection,
  onSort,
  onToggleEnabled,
  onToggleAutoTrack,
  onSyncPlaylist,
  onForceSyncPlaylist,
  onEditPlaylist,
  onDeletePlaylist,
  loading = false,
  enabledMutatingIds,
  autoMutatingIds,
  syncMutatingIds,
  forceSyncMutatingIds,
  deleteMutatingIds,
  enabledPulseIds,
  autoPulseIds,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  errorById,
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
                field='autoTrackArtists'
                currentSortField={sortField}
                currentSortDirection={sortDirection}
                onSort={onSort}
              >
                Track Artists
              </SortableTableHeader>
              <SortableTableHeader
                field='lastSyncedAt'
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
                  <ToggleStatusButton
                    variant='switch'
                    enabled={playlist.enabled}
                    onToggle={() => onToggleEnabled(playlist)}
                    mutating={enabledMutatingIds?.has(playlist.id)}
                    pulse={enabledPulseIds?.has(playlist.id)}
                    labels={{ on: 'Enabled', off: 'Disabled' }}
                    ariaLabel={
                      playlist.enabled ? 'Disable playlist' : 'Enable playlist'
                    }
                  />
                  <ToggleStatusButton
                    variant='badge'
                    enabled={playlist.enabled}
                    onToggle={() => onToggleEnabled(playlist)}
                    mutating={enabledMutatingIds?.has(playlist.id)}
                    pulse={enabledPulseIds?.has(playlist.id)}
                    labels={{ on: 'Enabled', off: 'Disabled' }}
                    colors={{ on: 'green', off: 'red' }}
                    ariaLabel={
                      playlist.enabled ? 'Disable playlist' : 'Enable playlist'
                    }
                  />
                </td>
                <td className='px-6 py-4 whitespace-nowrap'>
                  <ToggleStatusButton
                    variant='switch'
                    enabled={playlist.autoTrackArtists}
                    onToggle={() => onToggleAutoTrack(playlist)}
                    mutating={autoMutatingIds?.has(playlist.id)}
                    pulse={autoPulseIds?.has(playlist.id)}
                    labels={{ on: 'Yes', off: 'No' }}
                    ariaLabel={
                      playlist.autoTrackArtists
                        ? 'Disable tracking artists'
                        : 'Enable tracking artists'
                    }
                  />
                  <ToggleStatusButton
                    variant='badge'
                    enabled={playlist.autoTrackArtists}
                    onToggle={() => onToggleAutoTrack(playlist)}
                    mutating={autoMutatingIds?.has(playlist.id)}
                    pulse={autoPulseIds?.has(playlist.id)}
                    labels={{ on: 'Yes', off: 'No' }}
                    colors={{ on: 'blue', off: 'red' }}
                    ariaLabel={
                      playlist.autoTrackArtists
                        ? 'Disable tracking artists'
                        : 'Enable tracking artists'
                    }
                  />
                </td>
                <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-500'>
                  {playlist.lastSyncedAt
                    ? new Date(playlist.lastSyncedAt).toLocaleString()
                    : 'Never'}
                </td>
                <td className='px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2'>
                  <button
                    onClick={() => onSyncPlaylist(playlist.id)}
                    disabled={
                      syncMutatingIds?.has(playlist.id) ||
                      forceSyncMutatingIds?.has(playlist.id)
                    }
                    className='px-3 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800 hover:bg-blue-200 transition-colors'
                  >
                    {syncMutatingIds?.has(playlist.id) ? (
                      <span className='inline-flex items-center gap-2'>
                        <span className='w-3 h-3 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin' />
                        <span>Syncing…</span>
                      </span>
                    ) : (
                      'Sync Now'
                    )}
                  </button>
                  {onForceSyncPlaylist && (
                    <button
                      onClick={() => onForceSyncPlaylist(playlist.id)}
                      disabled={
                        syncMutatingIds?.has(playlist.id) ||
                        forceSyncMutatingIds?.has(playlist.id)
                      }
                      className='px-3 py-1 rounded text-xs font-medium bg-orange-100 text-orange-800 hover:bg-orange-200 transition-colors'
                      title='Force sync will re-download all tracks, ignoring existing ones'
                    >
                      {forceSyncMutatingIds?.has(playlist.id) ? (
                        <span className='inline-flex items-center gap-2'>
                          <span className='w-3 h-3 border-2 border-gray-300 border-t-orange-500 rounded-full animate-spin' />
                          <span>Force Syncing…</span>
                        </span>
                      ) : (
                        'Force Sync'
                      )}
                    </button>
                  )}
                  {onEditPlaylist && (
                    <button
                      onClick={() => onEditPlaylist(playlist)}
                      className='px-3 py-1 rounded text-xs font-medium bg-yellow-100 text-yellow-800 hover:bg-yellow-200 transition-colors'
                    >
                      Edit
                    </button>
                  )}
                  {onDeletePlaylist && (
                    <button
                      onClick={() =>
                        onDeletePlaylist(playlist.id, playlist.name)
                      }
                      disabled={deleteMutatingIds?.has(playlist.id)}
                      className='px-3 py-1 rounded text-xs font-medium bg-red-100 text-red-800 hover:bg-red-200 transition-colors disabled:opacity-50'
                    >
                      {deleteMutatingIds?.has(playlist.id) ? (
                        <span className='inline-flex items-center gap-2'>
                          <span className='w-3 h-3 border-2 border-gray-300 border-t-red-500 rounded-full animate-spin' />
                          <span>Deleting…</span>
                        </span>
                      ) : (
                        'Delete'
                      )}
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
