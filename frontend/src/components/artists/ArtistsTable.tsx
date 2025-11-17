import type { Artist } from '../../types/generated/graphql';
import { SortableTableHeader } from '../ui/SortableTableHeader';
import { ToggleStatusButton } from '../ui/ToggleStatusButton';
import { Link } from '@tanstack/react-router';

export type SortField =
  | 'name'
  | 'isTracked'
  | 'addedAt'
  | 'lastSynced'
  | 'lastDownloaded'
  | null;

interface ArtistsTableProps {
  artists: Artist[];
  sortField: SortField;
  sortDirection: 'asc' | 'desc';
  onSort: (field: SortField) => void;
  onTrackToggle: (artist: Artist) => void;
  onSyncArtist: (artistId: number) => void;
  onDownloadArtist: (artistId: number) => void;
  loading?: boolean;
  mutatingIds?: Set<number>;
  syncMutatingIds?: Set<number>;
  downloadMutatingIds?: Set<number>;
  errorById?: Record<number, string>;
  pulseIds?: Set<number>;
}

export function ArtistsTable({
  artists,
  sortField,
  sortDirection,
  onSort,
  onTrackToggle,
  onSyncArtist,
  onDownloadArtist,
  loading = false,
  mutatingIds,
  syncMutatingIds,
  downloadMutatingIds,
  errorById,
  pulseIds,
}: ArtistsTableProps) {
  if (artists.length === 0) {
    return (
      <div className='bg-white rounded shadow overflow-hidden'>
        <div className='p-6 text-center text-gray-500'>
          {loading ? 'Loading artists...' : 'No artists found.'}
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
                Artist
              </SortableTableHeader>
              <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'>
                ID
              </th>
              <SortableTableHeader
                field='isTracked'
                currentSortField={sortField}
                currentSortDirection={sortDirection}
                onSort={onSort}
              >
                Status
              </SortableTableHeader>
              <SortableTableHeader
                field='lastSynced'
                currentSortField={sortField}
                currentSortDirection={sortDirection}
                onSort={onSort}
              >
                Last Synced
              </SortableTableHeader>
              <SortableTableHeader
                field='lastDownloaded'
                currentSortField={sortField}
                currentSortDirection={sortDirection}
                onSort={onSort}
              >
                Last Downloaded
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
            {artists.map(artist => (
              <tr key={artist.id} className='hover:bg-gray-50'>
                <td className='px-6 py-4 whitespace-nowrap'>
                  <div className='text-sm font-medium'>
                    <a
                      href={`https://open.spotify.com/artist/${artist.gid}`}
                      target='_blank'
                      rel='noopener noreferrer'
                      className='text-green-600 hover:text-green-800 hover:underline'
                      title={`Open ${artist.name} on Spotify`}
                    >
                      {artist.name}
                    </a>
                  </div>
                </td>
                <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-500'>
                  {artist.id}
                </td>
                <td className='px-6 py-4 whitespace-nowrap'>
                  <ToggleStatusButton
                    variant='switch'
                    enabled={artist.isTracked}
                    onToggle={() => onTrackToggle(artist)}
                    mutating={mutatingIds?.has(artist.id)}
                    pulse={pulseIds?.has(artist.id)}
                    labels={{ on: 'Tracked', off: 'Not Tracked' }}
                    ariaLabel={
                      artist.isTracked ? 'Untrack artist' : 'Track artist'
                    }
                  />
                  <ToggleStatusButton
                    variant='badge'
                    enabled={artist.isTracked}
                    onToggle={() => onTrackToggle(artist)}
                    mutating={mutatingIds?.has(artist.id)}
                    pulse={pulseIds?.has(artist.id)}
                    labels={{ on: 'Tracked', off: 'Not Tracked' }}
                    colors={{ on: 'green', off: 'red' }}
                    ariaLabel={
                      artist.isTracked ? 'Untrack artist' : 'Track artist'
                    }
                  />
                </td>
                <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-500'>
                  {artist.lastSynced
                    ? new Date(artist.lastSynced).toLocaleString()
                    : 'Never'}
                </td>
                <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-500'>
                  {artist.lastDownloaded
                    ? new Date(artist.lastDownloaded).toLocaleString()
                    : 'Never'}
                </td>
                <td className='px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2'>
                  <button
                    onClick={() => onSyncArtist(artist.id)}
                    disabled={syncMutatingIds?.has(artist.id)}
                    className='px-3 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800 hover:bg-blue-200 transition-colors disabled:opacity-60'
                  >
                    {syncMutatingIds?.has(artist.id) ? (
                      <span className='inline-flex items-center gap-2'>
                        <span className='w-3 h-3 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin' />
                        <span>Syncing…</span>
                      </span>
                    ) : (
                      '📄 Sync Library'
                    )}
                  </button>
                  <button
                    onClick={() => onDownloadArtist(artist.id)}
                    disabled={
                      downloadMutatingIds?.has(artist.id) ||
                      artist.undownloadedCount === 0
                    }
                    className='px-3 py-1 rounded text-xs font-medium bg-green-100 text-green-800 hover:bg-green-200 transition-colors disabled:opacity-60'
                    title={
                      artist.undownloadedCount === 0
                        ? 'No undownloaded albums'
                        : `Download ${artist.undownloadedCount} missing albums/singles`
                    }
                  >
                    {downloadMutatingIds?.has(artist.id) ? (
                      <span className='inline-flex items-center gap-2'>
                        <span className='w-3 h-3 border-2 border-gray-300 border-t-green-500 rounded-full animate-spin' />
                        <span>Downloading…</span>
                      </span>
                    ) : (
                      `⬇️ Download (${artist.undownloadedCount})`
                    )}
                  </button>
                  <Link
                    to='/albums'
                    search={{ artistId: artist.id }}
                    className='text-indigo-600 hover:text-indigo-900 underline'
                  >
                    View Albums
                  </Link>
                  {errorById?.[artist.id] && (
                    <div className='text-xs text-red-600 mt-1'>
                      {errorById[artist.id]}
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
