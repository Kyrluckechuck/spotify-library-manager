import { Link } from '@tanstack/react-router';

interface ArtistContextProps {
  artistId: number;
  artistName: string;
  contentType: 'songs' | 'albums';
  totalCount: number;
}

export function ArtistContext({
  artistId,
  artistName,
  contentType,
  totalCount,
}: ArtistContextProps) {
  return (
    <div className='bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg p-4 mb-6'>
      <div className='flex items-center justify-between'>
        <div>
          <h2 className='text-lg font-semibold text-indigo-900'>
            {artistName}
          </h2>
          <p className='text-sm text-indigo-700'>
            {contentType === 'songs'
              ? `${totalCount} songs`
              : `${totalCount} albums`}
          </p>
        </div>
        <div className='flex items-center space-x-3'>
          <Link
            to='/artists'
            className='text-sm text-indigo-600 hover:text-indigo-800 underline'
          >
            ← Back to Artists
          </Link>
          <Link
            to='/albums'
            search={{ artistId }}
            className='text-sm text-indigo-600 hover:text-indigo-800 underline'
          >
            View {contentType === 'songs' ? 'Albums' : 'Songs'}
          </Link>
        </div>
      </div>
    </div>
  );
}
