import { Link } from '@tanstack/react-router';
import { useDownloadModal } from './ui/useDownloadModal';
import { useSpotifySearch } from './ui/useSpotifySearch';

const navLinks = [
  { to: '/', label: 'Home' },
  { to: '/artists', label: 'Artists' },
  { to: '/albums', label: 'Albums' },
  { to: '/playlists', label: 'Playlists' },
  { to: '/songs', label: 'Songs' },
  { to: '/tasks', label: 'Tasks' },
];

export const Navbar = () => {
  const downloadModal = useDownloadModal();
  const spotifySearch = useSpotifySearch();
  const titleClasses =
    'font-extrabold text-2xl tracking-tight text-indigo-700 hover:text-indigo-800';
  const navLinkClasses =
    'px-3 py-1.5 rounded-md transition-colors font-semibold text-gray-800 hover:text-indigo-700 hover:bg-indigo-50';
  const activeNavLinkClasses =
    'bg-indigo-100 text-indigo-700 hover:text-indigo-800';
  const searchButtonClasses =
    'px-3 py-1.5 border border-gray-300 text-gray-600 rounded-md hover:border-indigo-400 hover:text-indigo-600 transition-colors flex items-center gap-2 text-sm';
  const downloadButtonClasses =
    'px-4 py-1.5 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors font-semibold flex items-center gap-2';

  return (
    <nav className='bg-white border-b border-gray-300 px-6 py-3 shadow-sm sticky top-0 z-10'>
      <div className='flex items-center justify-between w-full mx-auto'>
        <Link
          to='/'
          className={titleClasses}
          activeProps={{ className: titleClasses }}
        >
          Spotify Library Manager
        </Link>
        <div className='flex items-center gap-4'>
          {navLinks.map(link => (
            <Link
              key={link.to}
              to={link.to}
              className={navLinkClasses}
              activeProps={{
                className: `${navLinkClasses} ${activeNavLinkClasses}`,
              }}
              activeOptions={{ exact: true }}
            >
              {link.label}
            </Link>
          ))}
          <button
            onClick={spotifySearch.open}
            className={searchButtonClasses}
            title='Search Spotify (Ctrl+K)'
          >
            <svg
              className='w-4 h-4'
              fill='none'
              stroke='currentColor'
              viewBox='0 0 24 24'
            >
              <path
                strokeLinecap='round'
                strokeLinejoin='round'
                strokeWidth={2}
                d='M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z'
              />
            </svg>
            <span className='hidden sm:inline'>Search</span>
            <kbd className='hidden md:inline-flex items-center gap-0.5 px-1.5 py-0.5 text-xs font-medium text-gray-500 bg-gray-100 rounded'>
              <span className='text-xs'>⌘</span>K
            </kbd>
          </button>
          <button
            onClick={downloadModal.open}
            className={downloadButtonClasses}
            title='Download Spotify content'
          >
            <svg
              className='w-4 h-4'
              fill='none'
              stroke='currentColor'
              viewBox='0 0 24 24'
            >
              <path
                strokeLinecap='round'
                strokeLinejoin='round'
                strokeWidth={2}
                d='M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
              />
            </svg>
            Download
          </button>
        </div>
      </div>
    </nav>
  );
};
