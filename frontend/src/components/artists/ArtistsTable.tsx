import type { Artist } from '../../types/generated/graphql';
import { SortableTableHeader } from '../ui/SortableTableHeader';
import { Link } from '@tanstack/react-router';

export type SortField = 'name' | 'isTracked' | 'addedAt' | 'lastSynced' | null;

interface ArtistsTableProps {
  artists: Artist[];
  sortField: SortField;
  sortDirection: 'asc' | 'desc';
  onSort: (field: SortField) => void;
  onTrackToggle: (artist: Artist) => void;
  onSyncArtist: (artistId: number) => void;
  loading?: boolean;
  mutatingIds?: Set<number>;
  syncMutatingIds?: Set<number>;
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
  loading = false,
  mutatingIds,
  syncMutatingIds,
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
                  <div className='text-sm font-medium text-gray-900'>
                    {artist.name}
                  </div>
                  <div className='text-sm text-gray-500'>ID: {artist.gid}</div>
                </td>
                <td className='px-6 py-4 whitespace-nowrap'>
                  <button
                    onClick={() => onTrackToggle(artist)}
                    disabled={mutatingIds?.has(artist.id)}
                    role='switch'
                    aria-checked={artist.isTracked}
                    aria-label={
                      artist.isTracked ? 'Untrack artist' : 'Track artist'
                    }
                    className='md:hidden inline-flex items-center w-12 h-6 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 '
                    style={{
                      backgroundColor: artist.isTracked ? '#22c55e' : '#e5e7eb',
                    }}
                  >
                    <span
                      className={`inline-block w-5 h-5 bg-white rounded-full transform transition-transform translate-x-1 ${
                        artist.isTracked ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                    <span className='sr-only'>
                      {artist.isTracked ? 'Tracked' : 'Not Tracked'}
                    </span>
                  </button>

                  <button
                    onClick={() => onTrackToggle(artist)}
                    disabled={mutatingIds?.has(artist.id)}
                    aria-pressed={artist.isTracked}
                    aria-label={
                      artist.isTracked ? 'Untrack artist' : 'Track artist'
                    }
                    className={`group hidden md:inline-flex px-2 py-1 text-xs font-semibold rounded-full transition-colors relative w-28 justify-center ${
                      artist.isTracked
                        ? 'bg-green-100 text-green-800 hover:bg-red-100 hover:text-red-800 focus:bg-red-100 focus:text-red-800'
                        : 'bg-red-100 text-red-800 hover:bg-green-100 hover:text-green-800 focus:bg-green-100 focus:text-green-800'
                    } ${pulseIds?.has(artist.id) ? 'ring-2 ring-green-400 ring-offset-1' : ''}`}
                  >
                    <span className='inline-flex items-center gap-1'>
                      {artist.isTracked ? (
                        <svg
                          className='w-3 h-3 text-green-700'
                          viewBox='0 0 20 20'
                          fill='currentColor'
                          aria-hidden='true'
                        >
                          <path
                            fillRule='evenodd'
                            d='M16.707 5.293a1 1 0 00-1.414 0L8 12.586 4.707 9.293a1 1 0 10-1.414 1.414l4 4a1 1 0 001.414 0l8-8a1 1 0 000-1.414z'
                            clipRule='evenodd'
                          />
                        </svg>
                      ) : (
                        <svg
                          className='w-3 h-3 text-red-700'
                          viewBox='0 0 20 20'
                          fill='currentColor'
                          aria-hidden='true'
                        >
                          <path
                            fillRule='evenodd'
                            d='M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z'
                            clipRule='evenodd'
                          />
                        </svg>
                      )}
                      <span>
                        {artist.isTracked ? 'Tracked' : 'Not Tracked'}
                      </span>
                    </span>
                    {mutatingIds?.has(artist.id) && (
                      <span
                        className='absolute right-1 top-1.5 w-3 h-3 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin'
                        aria-hidden='true'
                      />
                    )}
                  </button>
                </td>
                <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-500'>
                  {artist.lastSynced
                    ? new Date(artist.lastSynced).toLocaleString()
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
                      'Sync Now'
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
