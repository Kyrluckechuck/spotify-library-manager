import { createFileRoute } from '@tanstack/react-router';
import { useQuery } from '@apollo/client';
import { GetArtistsDocument } from '../types/generated/graphql';
import type { Artist } from '../types/generated/graphql';

function Artists() {
  const { data, loading, error } = useQuery(GetArtistsDocument, {
    variables: { limit: 50 }
  });

  if (loading) {
    return (
      <section>
        <h1 className="text-2xl font-semibold mb-4">Artists</h1>
        <div className="bg-white rounded shadow p-6 min-h-[200px] flex items-center justify-center text-gray-400">
          Loading artists...
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section>
        <h1 className="text-2xl font-semibold mb-4">Artists</h1>
        <div className="bg-white rounded shadow p-6 min-h-[200px] flex items-center justify-center text-red-500">
          Error loading artists: {error.message}
        </div>
      </section>
    );
  }

  const artists = data?.artists || [];

  return (
    <section>
      <h1 className="text-2xl font-semibold mb-4">Artists ({artists.length})</h1>
      
      <div className="flex gap-4 mb-6">
        <button className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700">
          Show All
        </button>
        <button className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
          Tracked Only
        </button>
      </div>

      <div className="bg-white rounded shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Artist
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Last Synced
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {artists.map((artist: Artist) => (
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
                    ? new Date(artist.lastSyncedAt).toLocaleDateString()
                    : 'Never'
                  }
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button className="text-indigo-600 hover:text-indigo-900 mr-4">
                    View Albums
                  </button>
                  <button className={`${
                    artist.tracked 
                      ? 'text-red-600 hover:text-red-900' 
                      : 'text-green-600 hover:text-green-900'
                  }`}>
                    {artist.tracked ? 'Untrack' : 'Track'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {artists.length === 0 && (
          <div className="p-6 text-center text-gray-500">
            No artists found.
          </div>
        )}
      </div>
    </section>
  );
}

export const Route = createFileRoute('/artists')({
  component: Artists,
}); 