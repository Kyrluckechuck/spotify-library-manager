import type { Artist } from '../../types/generated/graphql';
import { SortableTableHeader } from '../ui/SortableTableHeader';

export type SortField = 'name' | 'tracked' | 'added_at' | 'last_synced_at' | null;

interface ArtistsTableProps {
  artists: Artist[];
  sortField: SortField;
  sortDirection: 'asc' | 'desc';
  onSort: (field: SortField) => void;
  onTrackToggle: (artist: Artist) => void;
  loading?: boolean;
}

export function ArtistsTable({
  artists,
  sortField,
  sortDirection,
  onSort,
  onTrackToggle,
  loading = false
}: ArtistsTableProps) {
  if (artists.length === 0) {
    return (
      <div className="bg-white rounded shadow overflow-hidden">
        <div className="p-6 text-center text-gray-500">
          {loading ? 'Loading artists...' : 'No artists found.'}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded shadow overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <SortableTableHeader
              field="name"
              currentSortField={sortField}
              currentSortDirection={sortDirection}
              onSort={onSort}
            >
              Artist
            </SortableTableHeader>
            <SortableTableHeader
              field="tracked"
              currentSortField={sortField}
              currentSortDirection={sortDirection}
              onSort={onSort}
            >
              Status
            </SortableTableHeader>
            <SortableTableHeader
              field="last_synced_at"
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
        <tbody className="bg-white divide-y divide-gray-200">
          {artists.map((artist) => (
            <tr key={artist.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-gray-900">
                  {artist.name}
                </div>
                <div className="text-sm text-gray-500">
                  ID: {artist.gid}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                  artist.tracked
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {artist.tracked ? 'Tracked' : 'Not Tracked'}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {artist.lastSyncedAt
                  ? new Date(artist.lastSyncedAt).toLocaleString()
                  : 'Never'
                }
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                <button className="text-indigo-600 hover:text-indigo-900 underline">
                  View Albums
                </button>
                <button 
                  onClick={() => onTrackToggle(artist)}
                  className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                    artist.tracked
                      ? 'bg-red-100 text-red-800 hover:bg-red-200'
                      : 'bg-green-100 text-green-800 hover:bg-green-200'
                  }`}
                >
                  {artist.tracked ? 'Untrack' : 'Track'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 