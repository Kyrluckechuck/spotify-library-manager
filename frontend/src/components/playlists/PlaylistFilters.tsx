interface PlaylistFiltersProps {
  currentEnabledFilter: 'all' | 'enabled' | 'disabled';
  onEnabledFilterChange: (filter: 'all' | 'enabled' | 'disabled') => void;
  onFilterHover?: (filter: 'all' | 'enabled' | 'disabled') => void;
}

export function PlaylistFilters({
  currentEnabledFilter,
  onEnabledFilterChange,
  onFilterHover,
}: PlaylistFiltersProps) {
  return (
    <div className='mb-6'>
      <h3 className='text-sm font-medium text-gray-700 mb-2'>Status</h3>
      <div className='flex gap-4'>
        <button
          onClick={() => onEnabledFilterChange('all')}
          onMouseEnter={() => onFilterHover?.('all')}
          className={`px-4 py-2 rounded transition-colors font-medium border ${
            currentEnabledFilter === 'all'
              ? 'bg-indigo-700 border-indigo-700 shadow-md ring-2 ring-indigo-300'
              : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300'
          }`}
          style={{
            backgroundColor:
              currentEnabledFilter === 'all' ? '#3730a3' : 'white',
            color: currentEnabledFilter === 'all' ? 'white' : '#374151',
          }}
        >
          All Playlists
        </button>
        <button
          onClick={() => onEnabledFilterChange('enabled')}
          onMouseEnter={() => onFilterHover?.('enabled')}
          className={`px-4 py-2 rounded transition-colors font-medium border ${
            currentEnabledFilter === 'enabled'
              ? 'bg-green-700 border-green-700 shadow-md ring-2 ring-green-300'
              : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300'
          }`}
          style={{
            backgroundColor:
              currentEnabledFilter === 'enabled' ? '#15803d' : 'white',
            color: currentEnabledFilter === 'enabled' ? 'white' : '#374151',
          }}
        >
          Enabled Only
        </button>
        <button
          onClick={() => onEnabledFilterChange('disabled')}
          onMouseEnter={() => onFilterHover?.('disabled')}
          className={`px-4 py-2 rounded transition-colors font-medium border ${
            currentEnabledFilter === 'disabled'
              ? 'bg-gray-700 border-gray-700 shadow-md ring-2 ring-gray-300'
              : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300'
          }`}
          style={{
            backgroundColor:
              currentEnabledFilter === 'disabled' ? '#374151' : 'white',
            color: currentEnabledFilter === 'disabled' ? 'white' : '#374151',
          }}
        >
          Disabled Only
        </button>
      </div>
    </div>
  );
}
