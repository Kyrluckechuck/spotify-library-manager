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
}

export function ArtistsTable({
  artists,
  sortField,
  sortDirection,
  onSort,
  onTrackToggle,
  onSyncArtist,
  loading = false,
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
                    aria-pressed={artist.isTracked}
                    aria-label={
                      artist.isTracked ? 'Untrack artist' : 'Track artist'
                    }
                    className={`group hidden md:inline-flex px-2 py-1 text-xs font-semibold rounded-full transition-colors ${
                      artist.isTracked
                        ? 'bg-green-100 text-green-800 hover:bg-red-100 hover:text-red-800 focus:bg-red-100 focus:text-red-800'
                        : 'bg-red-100 text-red-800 hover:bg-green-100 hover:text-green-800 focus:bg-green-100 focus:text-green-800'
                    }`}
                  >
                    <span className='group-hover:hidden group-focus:hidden'>
                      {artist.isTracked ? 'Tracked' : 'Not Tracked'}
                    </span>
                    <span className='hidden group-hover:inline group-focus:inline'>
                      {artist.isTracked ? 'Untrack' : 'Track'}
                    </span>
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
                    className='px-3 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800 hover:bg-blue-200 transition-colors'
                  >
                    Sync Now
                  </button>
                  <Link
                    to='/albums'
                    search={{ artistId: artist.id }}
                    className='text-indigo-600 hover:text-indigo-900 underline'
                  >
                    View Albums
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
