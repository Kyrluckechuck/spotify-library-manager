interface ArtistFiltersProps {
  currentFilter: 'all' | 'tracked' | 'untracked';
  onFilterChange: (filter: 'all' | 'tracked' | 'untracked') => void;
  onFilterHover?: (filter: 'all' | 'tracked' | 'untracked') => void;
}

export function ArtistFilters({
  currentFilter,
  onFilterChange,
  onFilterHover,
}: ArtistFiltersProps) {
  return (
    <div className='flex gap-4 mb-6'>
      <button
        onClick={() => onFilterChange('all')}
        onMouseEnter={() => onFilterHover?.('all')}
        className={`px-4 py-2 rounded transition-colors font-medium border ${
          currentFilter === 'all'
            ? 'bg-indigo-700 border-indigo-700 shadow-md ring-2 ring-indigo-300'
            : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300'
        }`}
        style={{
          backgroundColor: currentFilter === 'all' ? '#3730a3' : 'white',
          color: currentFilter === 'all' ? 'white' : '#374151',
        }}
      >
        Show All
      </button>
      <button
        onClick={() => onFilterChange('tracked')}
        onMouseEnter={() => onFilterHover?.('tracked')}
        className={`px-4 py-2 rounded transition-colors font-medium border ${
          currentFilter === 'tracked'
            ? 'bg-green-700 border-green-700 shadow-md ring-2 ring-green-300'
            : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300'
        }`}
        style={{
          backgroundColor: currentFilter === 'tracked' ? '#15803d' : 'white',
          color: currentFilter === 'tracked' ? 'white' : '#374151',
        }}
      >
        Tracked Only
      </button>
      <button
        onClick={() => onFilterChange('untracked')}
        onMouseEnter={() => onFilterHover?.('untracked')}
        className={`px-4 py-2 rounded transition-colors font-medium border ${
          currentFilter === 'untracked'
            ? 'bg-orange-700 border-orange-700 shadow-md ring-2 ring-orange-300'
            : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300'
        }`}
        style={{
          backgroundColor: currentFilter === 'untracked' ? '#c2410c' : 'white',
          color: currentFilter === 'untracked' ? 'white' : '#374151',
        }}
      >
        Untracked Only
      </button>
    </div>
  );
}
