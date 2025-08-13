import React from 'react';
import { Link } from '@tanstack/react-router';

export type SortField =
  | 'name'
  | 'primaryArtist'
  | 'createdAt'
  | 'downloaded'
  | null;

interface Song {
  id: number;
  name: string;
  gid: string;
  primaryArtist: string;
  primaryArtistId: number;
  createdAt: string;
  failedCount: number;
  bitrate: number;
  unavailable: boolean;
  filePath: string | null;
  downloaded: boolean;
  spotifyUri: string;
}

interface SongsTableProps {
  songs: Song[];
  sortField: SortField;
  sortDirection: 'asc' | 'desc';
  onSort: (field: SortField) => void;
  loading?: boolean;
  mutatingIds?: Set<number>;
  errorById?: Record<number, string>;
}

export const SongsTable: React.FC<SongsTableProps> = ({
  songs,
  sortField,
  sortDirection,
  onSort,
  loading = false,
}) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatBitrate = (bitrate: number) => {
    if (bitrate === 0) return 'N/A';
    return `${Math.round(bitrate / 1000)} kbps`;
  };

  const getStatusIcon = (song: Song) => {
    if (song.unavailable) {
      return (
        <span className='text-red-500' title='Unavailable'>
          ⚠️
        </span>
      );
    }
    if (song.downloaded) {
      return (
        <span className='text-green-500' title='Downloaded'>
          ✓
        </span>
      );
    }
    if (song.failedCount > 0) {
      return (
        <span
          className='text-yellow-500'
          title={`Failed ${song.failedCount} times`}
        >
          ⚠️
        </span>
      );
    }
    return (
      <span className='text-gray-400' title='Not downloaded'>
        ○
      </span>
    );
  };

  const getStatusText = (song: Song) => {
    if (song.unavailable) {
      return 'Unavailable';
    }
    if (song.downloaded) {
      return 'Downloaded';
    }
    if (song.failedCount > 0) {
      return `Failed (${song.failedCount})`;
    }
    return 'Not downloaded';
  };

  const SortableTableHeader: React.FC<{
    field: SortField;
    children: React.ReactNode;
    className?: string;
  }> = ({ field, children, className = '' }) => (
    <th
      className={`px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-50 ${className}`}
      onClick={() => onSort(field)}
    >
      <div className='flex items-center gap-1'>
        {children}
        {sortField === field && (
          <span className='text-gray-400'>
            {sortDirection === 'asc' ? '↑' : '↓'}
          </span>
        )}
      </div>
    </th>
  );

  if (loading && songs.length === 0) {
    return (
      <div className='bg-white shadow overflow-hidden sm:rounded-md'>
        <div className='px-6 py-4 text-center text-gray-500'>
          Loading songs...
        </div>
      </div>
    );
  }

  if (songs.length === 0) {
    return (
      <div className='bg-white shadow overflow-hidden sm:rounded-md'>
        <div className='px-6 py-4 text-center text-gray-500'>
          No songs found.
        </div>
      </div>
    );
  }

  return (
    <div className='bg-white shadow overflow-hidden sm:rounded-md'>
      <table className='min-w-full divide-y divide-gray-200'>
        <thead className='bg-gray-50'>
          <tr>
            <SortableTableHeader field='downloaded' className='w-24'>
              Status
            </SortableTableHeader>
            <SortableTableHeader field='name'>Song Name</SortableTableHeader>
            <SortableTableHeader field='primaryArtist'>
              Artist
            </SortableTableHeader>
            <SortableTableHeader field='createdAt'>Added</SortableTableHeader>
            <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'>
              Bitrate
            </th>
            <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'>
              File Path
            </th>
          </tr>
        </thead>
        <tbody className='bg-white divide-y divide-gray-200'>
          {songs.map(song => (
            <tr key={song.id} className='hover:bg-gray-50'>
              <td className='px-6 py-4 whitespace-nowrap'>
                <div className='flex items-center gap-2'>
                  {getStatusIcon(song)}
                  <span className='text-sm text-gray-900'>
                    {getStatusText(song)}
                  </span>
                </div>
              </td>
              <td className='px-6 py-4 whitespace-nowrap'>
                <div className='text-sm font-medium text-gray-900'>
                  {song.name}
                </div>
                <div className='text-sm text-gray-500'>{song.gid}</div>
              </td>
              <td className='px-6 py-4 whitespace-nowrap'>
                <Link
                  to='/artists'
                  className='text-sm font-medium text-blue-600 hover:text-blue-900'
                >
                  {song.primaryArtist}
                </Link>
              </td>
              <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-500'>
                {formatDate(song.createdAt)}
              </td>

              <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-500'>
                {formatBitrate(song.bitrate)}
              </td>
              <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-500'>
                {song.filePath ? (
                  <span
                    className='truncate max-w-xs block'
                    title={song.filePath}
                  >
                    {song.filePath}
                  </span>
                ) : (
                  '-'
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
