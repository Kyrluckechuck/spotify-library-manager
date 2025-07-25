import type { Album } from '../../types/generated/graphql';
import { SortableTableHeader } from '../ui/SortableTableHeader';

export type AlbumSortField = 'name' | 'wanted' | 'downloaded' | 'album_type' | null;

interface AlbumsTableProps {
  albums: Album[];
  sortField: AlbumSortField;
  sortDirection: 'asc' | 'desc';
  onSort: (field: AlbumSortField) => void;
  onWantedToggle: (album: Album) => void;
  loading?: boolean;
}

export function AlbumsTable({
  albums,
  sortField,
  sortDirection,
  onSort,
  onWantedToggle,
  loading = false
}: AlbumsTableProps) {
  if (albums.length === 0) {
    return (
      <div className="bg-white rounded shadow overflow-hidden">
        <div className="p-6 text-center text-gray-500">
          {loading ? 'Loading albums...' : 'No albums found.'}
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
              Album
            </SortableTableHeader>
            <SortableTableHeader
              field="album_type"
              currentSortField={sortField}
              currentSortDirection={sortDirection}
              onSort={onSort}
            >
              Type
            </SortableTableHeader>
            <SortableTableHeader
              field={null}
              currentSortField={sortField}
              currentSortDirection={sortDirection}
              onSort={onSort}
            >
              Tracks
            </SortableTableHeader>
            <SortableTableHeader
              field="wanted"
              currentSortField={sortField}
              currentSortDirection={sortDirection}
              onSort={onSort}
            >
              Status
            </SortableTableHeader>
            <SortableTableHeader
              field="downloaded"
              currentSortField={sortField}
              currentSortDirection={sortDirection}
              onSort={onSort}
            >
              Downloaded
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
          {albums.map((album) => (
            <tr key={album.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-gray-900">
                  {album.name}
                </div>
                <div className="text-sm text-gray-500">
                  ID: {album.spotifyGid}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                  {album.albumType || 'Unknown'}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {album.totalTracks} tracks
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                  album.wanted
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {album.wanted ? 'Wanted' : 'Not Wanted'}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                  album.downloaded
                    ? 'bg-green-100 text-green-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {album.downloaded ? 'Downloaded' : 'Pending'}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                <button className="text-indigo-600 hover:text-indigo-900 underline">
                  View Songs
                </button>
                <button 
                  onClick={() => onWantedToggle(album)}
                  className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                    album.wanted
                      ? 'bg-red-100 text-red-800 hover:bg-red-200'
                      : 'bg-green-100 text-green-800 hover:bg-green-200'
                  }`}
                >
                  {album.wanted ? 'Mark Unwanted' : 'Mark Wanted'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      </div>
    </div>
  );
} 