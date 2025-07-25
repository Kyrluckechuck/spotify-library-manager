import { createFileRoute } from '@tanstack/react-router';
import { useQuery, useMutation } from '@apollo/client';
import { GetArtistsDocument, TrackArtistDocument, UntrackArtistDocument } from '../types/generated/graphql';
import type { Artist } from '../types/generated/graphql';
import { useState } from 'react';

type SortField = 'name' | 'tracked' | 'added_at' | 'last_synced_at' | null;
type SortDirection = 'asc' | 'desc';

function Artists() {
  const [filter, setFilter] = useState<'all' | 'tracked' | 'untracked'>('all');
  const [pageSize, setPageSize] = useState(50);
  const [sortField, setSortField] = useState<SortField>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  
  const { data, loading, error, refetch, fetchMore } = useQuery(GetArtistsDocument, {
    variables: { 
      tracked: filter === 'all' ? undefined : filter === 'tracked',
      first: pageSize,
      sortBy: sortField,
      sortDirection: sortDirection
    },
    notifyOnNetworkStatusChange: true,
    fetchPolicy: 'cache-and-network'
  });

  const [trackArtist] = useMutation(TrackArtistDocument, {
    onCompleted: (data) => {
      if (data.trackArtist.success) {
        refetch();
      }
    }
  });

  const [untrackArtist] = useMutation(UntrackArtistDocument, {
    onCompleted: (data) => {
      if (data.untrackArtist.success) {
        refetch();
      }
    }
  });

  const handleFilterChange = (newFilter: 'all' | 'tracked' | 'untracked') => {
    setFilter(newFilter);
    refetch({
      tracked: newFilter === 'all' ? undefined : newFilter === 'tracked',
      first: pageSize,
      after: undefined,
      sortBy: sortField,
      sortDirection: sortDirection
    });
  };

  const handleSort = (field: SortField) => {
    let newDirection: SortDirection = 'asc';
    
    if (sortField === field && sortDirection === 'asc') {
      newDirection = 'desc';
    }
    
    setSortField(field);
    setSortDirection(newDirection);
    
    refetch({
      tracked: filter === 'all' ? undefined : filter === 'tracked',
      first: pageSize,
      after: undefined,
      sortBy: field,
      sortDirection: newDirection
    });
  };

  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize);
    refetch({
      tracked: filter === 'all' ? undefined : filter === 'tracked',
      first: newPageSize,
      after: undefined,
      sortBy: sortField,
      sortDirection: sortDirection
    });
  };

  const handleTrackToggle = async (artist: Artist) => {
    try {
      if (artist.tracked) {
        await untrackArtist({ variables: { artistId: artist.id } });
      } else {
        await trackArtist({ variables: { artistId: artist.id } });
      }
    } catch (error) {
      console.error('Error toggling artist tracking:', error);
    }
  };

  const handleLoadMore = () => {
    if (data?.artists.pageInfo.hasNextPage) {
      fetchMore({
        variables: {
          after: data.artists.pageInfo.endCursor,
        },
        updateQuery: (prevResult, { fetchMoreResult }) => {
          if (!fetchMoreResult) return prevResult;
          
          return {
            artists: {
              ...fetchMoreResult.artists,
              edges: [
                ...prevResult.artists.edges,
                ...fetchMoreResult.artists.edges,
              ],
            },
          };
        },
      });
    }
  };

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) {
      return '↕️'; // Both arrows when not sorted
    }
    return sortDirection === 'asc' ? '↑' : '↓';
  };

  if (loading && !data) {
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

  const artists = data?.artists.edges || [];
  const totalCount = data?.artists.totalCount || 0;
  const pageInfo = data?.artists.pageInfo;

  console.log('Current filter:', filter); // Debug logging

  return (
    <section>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold">
          Artists ({artists.length} of {totalCount})
        </h1>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <label htmlFor="pageSize" className="text-sm text-gray-600">Show:</label>
            <select
              id="pageSize"
              value={pageSize}
              onChange={(e) => handlePageSizeChange(Number(e.target.value))}
              className="border border-gray-300 rounded px-2 py-1 text-sm"
            >
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
              <option value={200}>200</option>
            </select>
          </div>
          {totalCount > artists.length && (
            <span className="text-sm text-gray-500">
              Showing first {artists.length} artists
            </span>
          )}
        </div>
      </div>

      <div className="flex gap-4 mb-6">
        <button 
          onClick={() => handleFilterChange('all')}
          className={`px-4 py-2 rounded transition-colors font-medium border ${
            filter === 'all' 
              ? 'bg-indigo-700 border-indigo-700 shadow-md ring-2 ring-indigo-300' 
              : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300'
          }`}
          style={{ 
            backgroundColor: filter === 'all' ? '#3730a3' : 'white',
            color: filter === 'all' ? 'white' : '#374151'
          }}
        >
          Show All
        </button>
        <button 
          onClick={() => handleFilterChange('tracked')}
          className={`px-4 py-2 rounded transition-colors font-medium border ${
            filter === 'tracked' 
              ? 'bg-green-700 border-green-700 shadow-md ring-2 ring-green-300' 
              : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300'
          }`}
          style={{ 
            backgroundColor: filter === 'tracked' ? '#15803d' : 'white',
            color: filter === 'tracked' ? 'white' : '#374151'
          }}
        >
          Tracked Only
        </button>
        <button 
          onClick={() => handleFilterChange('untracked')}
          className={`px-4 py-2 rounded transition-colors font-medium border ${
            filter === 'untracked' 
              ? 'bg-orange-700 border-orange-700 shadow-md ring-2 ring-orange-300' 
              : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300'
          }`}
          style={{ 
            backgroundColor: filter === 'untracked' ? '#c2410c' : 'white',
            color: filter === 'untracked' ? 'white' : '#374151'
          }}
        >
          Untracked Only
        </button>
      </div>

      <div className="bg-white rounded shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('name')}
              >
                <div className="flex items-center gap-1">
                  Artist {getSortIcon('name')}
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('tracked')}
              >
                <div className="flex items-center gap-1">
                  Status {getSortIcon('tracked')}
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('last_synced_at')}
              >
                <div className="flex items-center gap-1">
                  Last Synced {getSortIcon('last_synced_at')}
                </div>
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
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                  <button className="text-indigo-600 hover:text-indigo-900 underline">
                    View Albums
                  </button>
                  <button 
                    onClick={() => handleTrackToggle(artist)}
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

        {artists.length === 0 && (
          <div className="p-6 text-center text-gray-500">
            No artists found.
          </div>
        )}

        {pageInfo?.hasNextPage && (
          <div className="p-4 text-center border-t border-gray-200">
            <button
              onClick={handleLoadMore}
              disabled={loading}
              className="px-6 py-3 rounded font-medium transition-colors"
              style={{
                backgroundColor: loading ? '#6b7280' : '#3730a3',
                color: 'white',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              {loading ? 'Loading...' : `Load More (${totalCount - artists.length} remaining)`}
            </button>
          </div>
        )}
      </div>
    </section>
  );
}

export const Route = createFileRoute('/artists')({
  component: Artists,
}); 