import type { Album } from '../../types/generated/graphql';
import { SortableTableHeader } from '../ui/SortableTableHeader';
import { ToggleStatusButton } from '../ui/ToggleStatusButton';
import { Link } from '@tanstack/react-router';

export type AlbumSortField =
  | 'name'
  | 'artist'
  | 'downloaded'
  | 'wanted'
  | 'totalTracks'
  | 'createdAt'
  | 'albumType'
  | 'albumGroup'
  | null;

interface AlbumsTableProps {
  albums: Album[];
  sortField: AlbumSortField;
  sortDirection: 'asc' | 'desc';
  onSort: (field: AlbumSortField) => void;
  onToggleWanted: (albumId: number, wanted: boolean) => void;
  onDownloadAlbum?: (albumId: number) => void;
  loading?: boolean;
  mutatingIds?: Set<number>;
  pulseIds?: Set<number>;
}

// Helper function to format album type/group values
function formatAlbumValue(value: string | null | undefined): string {
  if (!value) return 'Album';

  return value
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

export function AlbumsTable({
  albums,
  sortField,
  sortDirection,
  onSort,
  onToggleWanted,
  onDownloadAlbum,
  loading = false,
  mutatingIds,
  pulseIds,
}: AlbumsTableProps) {
  if (albums.length === 0) {
    return (
      <div className='bg-white rounded shadow overflow-hidden'>
        <div className='p-6 text-center text-gray-500'>
          {loading ? 'Loading albums...' : 'No albums found.'}
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
                Album
              </SortableTableHeader>
              <SortableTableHeader
                field='artist'
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
                field='albumType'
                currentSortField={sortField}
                currentSortDirection={sortDirection}
                onSort={onSort}
              >
                Type
              </SortableTableHeader>
              <SortableTableHeader
                field='albumGroup'
                currentSortField={sortField}
                currentSortDirection={sortDirection}
                onSort={onSort}
              >
                Group
              </SortableTableHeader>
              <SortableTableHeader
                field='totalTracks'
                currentSortField={sortField}
                currentSortDirection={sortDirection}
                onSort={onSort}
              >
                Tracks
              </SortableTableHeader>
              <SortableTableHeader
                field='downloaded'
                currentSortField={sortField}
                currentSortDirection={sortDirection}
                onSort={onSort}
              >
                Downloaded
              </SortableTableHeader>
              <SortableTableHeader
                field='wanted'
                currentSortField={sortField}
                currentSortDirection={sortDirection}
                onSort={onSort}
              >
                Wanted
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
            {albums.map(album => (
              <tr key={album.id} className='hover:bg-gray-50'>
                <td className='px-6 py-4 whitespace-nowrap'>
                  <div className='text-sm font-medium'>
                    <a
                      href={`https://open.spotify.com/album/${album.spotifyGid}`}
                      target='_blank'
                      rel='noopener noreferrer'
                      className='text-green-600 hover:text-green-800 hover:underline'
                      title={`Open ${album.name} on Spotify`}
                    >
                      {album.name}
                    </a>
                  </div>
                </td>
                <td className='px-6 py-4 whitespace-nowrap'>
                  <div className='text-sm font-medium'>
                    {album.artist && album.artistId ? (
                      <Link
                        to='/artists'
                        search={{ search: String(album.artistId) }}
                        className='text-blue-600 hover:text-blue-900 hover:underline'
                      >
                        {album.artist}
                      </Link>
                    ) : (
                      <span className='text-gray-500'>
                        {album.artist || 'Unknown Artist'}
                      </span>
                    )}
                  </div>
                </td>
                <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-500'>
                  {album.id}
                </td>
                <td className='px-6 py-4 whitespace-nowrap'>
                  <div className='text-sm text-gray-500'>
                    {formatAlbumValue(album.albumType)}
                  </div>
                </td>
                <td className='px-6 py-4 whitespace-nowrap'>
                  <div className='text-sm text-gray-500'>
                    {formatAlbumValue(album.albumGroup)}
                  </div>
                </td>
                <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-500'>
                  {album.totalTracks}
                </td>
                <td className='px-6 py-4 whitespace-nowrap'>
                  <span
                    className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      album.downloaded
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}
                  >
                    {album.downloaded ? 'Yes' : 'No'}
                  </span>
                </td>
                <td className='px-6 py-4 whitespace-nowrap'>
                  <ToggleStatusButton
                    variant='badge'
                    enabled={album.wanted}
                    onToggle={() => onToggleWanted(album.id, !album.wanted)}
                    mutating={mutatingIds?.has(album.id)}
                    pulse={pulseIds?.has(album.id)}
                    labels={{ on: 'Yes', off: 'No' }}
                    colors={{ on: 'blue', off: 'red' }}
                  />
                </td>
                <td className='px-6 py-4 whitespace-nowrap text-sm font-medium'>
                  <div className='flex items-center gap-3'>
                    {onDownloadAlbum && (
                      <button
                        onClick={() => onDownloadAlbum(album.id)}
                        disabled={mutatingIds?.has(album.id)}
                        className='text-blue-600 hover:text-blue-900 disabled:text-gray-400 disabled:cursor-not-allowed'
                        title='Download album'
                      >
                        <svg
                          xmlns='http://www.w3.org/2000/svg'
                          className='h-5 w-5'
                          viewBox='0 0 20 20'
                          fill='currentColor'
                        >
                          <path
                            fillRule='evenodd'
                            d='M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z'
                            clipRule='evenodd'
                          />
                        </svg>
                      </button>
                    )}
                    <Link
                      to='/songs'
                      search={{
                        artistId: album.artistId || undefined,
                        search: undefined,
                      }}
                      className='text-green-600 hover:text-green-900 underline'
                    >
                      View Songs
                    </Link>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
