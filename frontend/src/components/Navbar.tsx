import { Link } from '@tanstack/react-router';

const navLinks = [
  { to: '/', label: 'Home' },
  { to: '/artists', label: 'Artists' },
  { to: '/albums', label: 'Albums' },
  { to: '/playlists', label: 'Playlists' },
  { to: '/tasks', label: 'Tasks' },
];

export const Navbar = () => {
  const titleClasses =
    'font-extrabold text-2xl tracking-tight text-indigo-700 hover:text-indigo-800';
  const navLinkClasses =
    'px-3 py-1.5 rounded-md transition-colors font-semibold text-gray-800 hover:text-indigo-700 hover:bg-indigo-50';
  const activeNavLinkClasses =
    'bg-indigo-100 text-indigo-700 hover:text-indigo-800';

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
        </div>
      </div>
    </nav>
  );
};
