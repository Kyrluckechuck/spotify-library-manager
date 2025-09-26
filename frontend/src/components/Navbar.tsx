import { Link } from '@tanstack/react-router';
import { useDownloadModal } from './ui/useDownloadModal';

const navLinks = [
  { to: '/', label: 'Home' },
  { to: '/artists', label: 'Artists' },
  { to: '/albums', label: 'Albums' },
  { to: '/playlists', label: 'Playlists' },
  { to: '/tasks', label: 'Tasks' },
];

export const Navbar = () => {
  const downloadModal = useDownloadModal();
  const titleClasses =
    'font-extrabold text-2xl tracking-tight text-indigo-700 hover:text-indigo-800';
  const navLinkClasses =
    'px-3 py-1.5 rounded-md transition-colors font-semibold text-gray-800 hover:text-indigo-700 hover:bg-indigo-50';
  const activeNavLinkClasses =
    'bg-indigo-100 text-indigo-700 hover:text-indigo-800';
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
