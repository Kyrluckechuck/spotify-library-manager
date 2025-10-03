import type { Album } from '../../types/generated/graphql';
import { SortableTableHeader } from '../ui/SortableTableHeader';
import { ToggleStatusButton } from '../ui/ToggleStatusButton';
import { Link } from '@tanstack/react-router';

export type AlbumSortField =
  | 'name'
  | 'artist'
  | 'downloaded'
  | 'wanted'
  | 'total_tracks'
  | 'created_at'
  | 'album_type'
  | 'album_group'
  | null;

interface AlbumsTableProps {
  albums: Album[];
  sortField: AlbumSortField;
  sortDirection: 'asc' | 'desc';
  onSort: (field: AlbumSortField) => void;
  onToggleWanted: (albumId: number, wanted: boolean) => void;
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
                field='album_type'
                currentSortField={sortField}
                currentSortDirection={sortDirection}
                onSort={onSort}
              >
                Type
              </SortableTableHeader>
              <SortableTableHeader
                field='album_group'
                currentSortField={sortField}
                currentSortDirection={sortDirection}
                onSort={onSort}
              >
                Group
              </SortableTableHeader>
              <SortableTableHeader
                field='total_tracks'
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
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
