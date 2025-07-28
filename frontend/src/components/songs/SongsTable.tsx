import type { Song } from '../../types/generated/graphql';
import { SortableTableHeader } from '../ui/SortableTableHeader';

export type SongSortField = 'name' | 'artist' | 'downloaded' | 'unavailable' | 'created_at' | null;

interface SongsTableProps {
  songs: Song[];
  sortField: SongSortField;
  sortDirection: 'asc' | 'desc';
  onSort: (field: SongSortField) => void;
  loading?: boolean;
  showArtist?: boolean; // Add prop to conditionally show artist column
}

export function SongsTable({
  songs,
  sortField,
  sortDirection,
  onSort,
  loading = false,
  showArtist = false
}: SongsTableProps) {
  if (songs.length === 0) {
    return (
      <div className="bg-white rounded shadow overflow-hidden">
        <div className="p-6 text-center text-gray-500">
          {loading ? 'Loading songs...' : 'No songs found.'}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded shadow overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <SortableTableHeader
                field="name"
                currentSortField={sortField}
                currentSortDirection={sortDirection}
                onSort={onSort}
              >
                Song
              </SortableTableHeader>
              {showArtist && (
                <SortableTableHeader
                  field="artist"
                  currentSortField={sortField}
                  currentSortDirection={sortDirection}
                  onSort={onSort}
                >
                  Artist
                </SortableTableHeader>
              )}
              <SortableTableHeader
                field="downloaded"
                currentSortField={sortField}
                currentSortDirection={sortDirection}
                onSort={onSort}
              >
                Status
              </SortableTableHeader>
              <SortableTableHeader
                field="unavailable"
                currentSortField={sortField}
                currentSortDirection={sortDirection}
                onSort={onSort}
              >
                Availability
              </SortableTableHeader>
              <SortableTableHeader
                field="created_at"
                currentSortField={sortField}
                currentSortDirection={sortDirection}
                onSort={onSort}
              >
                Added
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
          <tbody className="bg-white divide-y divide-gray-200">
            {songs.map((song) => (
              <tr key={song.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {song.name}
                  </div>
                  <div className="text-sm text-gray-500">
                    ID: {song.gid}
                  </div>
                </td>
                {showArtist && (
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{song.artist}</div>
                  </td>
                )}
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    song.downloaded
                      ? 'bg-green-100 text-green-800'
                      : song.unavailable
                      ? 'bg-red-100 text-red-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {song.downloaded ? 'Downloaded' : song.unavailable ? 'Unavailable' : 'Pending'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    song.unavailable
                      ? 'bg-red-100 text-red-800'
                      : 'bg-green-100 text-green-800'
                  }`}>
                    {song.unavailable ? 'Unavailable' : 'Available'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(song.createdAt).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                  <a 
                    href={song.spotifyUri}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-indigo-600 hover:text-indigo-900 underline"
                  >
                    Open Spotify
                  </a>
                  {song.filePath && (
                    <button className="text-green-600 hover:text-green-900 underline">
                      Play Local
                    </button>
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