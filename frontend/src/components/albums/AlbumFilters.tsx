interface AlbumFiltersProps {
  currentWantedFilter: 'all' | 'wanted' | 'unwanted';
  currentDownloadFilter: 'all' | 'downloaded' | 'pending';
  onWantedFilterChange: (filter: 'all' | 'wanted' | 'unwanted') => void;
  onDownloadFilterChange: (filter: 'all' | 'downloaded' | 'pending') => void;
}

export function AlbumFilters({
  currentWantedFilter,
  currentDownloadFilter,
  onWantedFilterChange,
  onDownloadFilterChange,
}: AlbumFiltersProps) {
  return (
    <div className='space-y-4 mb-6'>
      {/* Wanted Status Filter */}
      <div>
        <h3 className='text-sm font-medium text-gray-700 mb-2'>
          Wanted Status
        </h3>
        <div className='flex gap-4'>
          <button
            onClick={() => onWantedFilterChange('all')}
            className={`px-4 py-2 rounded transition-colors font-medium border ${
              currentWantedFilter === 'all'
                ? 'bg-indigo-700 border-indigo-700 shadow-md ring-2 ring-indigo-300'
                : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300'
            }`}
            style={{
              backgroundColor:
                currentWantedFilter === 'all' ? '#3730a3' : 'white',
              color: currentWantedFilter === 'all' ? 'white' : '#374151',
            }}
          >
            All Albums
          </button>
          <button
            onClick={() => onWantedFilterChange('wanted')}
            className={`px-4 py-2 rounded transition-colors font-medium border ${
              currentWantedFilter === 'wanted'
                ? 'bg-green-700 border-green-700 shadow-md ring-2 ring-green-300'
                : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300'
            }`}
            style={{
              backgroundColor:
                currentWantedFilter === 'wanted' ? '#15803d' : 'white',
              color: currentWantedFilter === 'wanted' ? 'white' : '#374151',
            }}
          >
            Wanted Only
          </button>
          <button
            onClick={() => onWantedFilterChange('unwanted')}
            className={`px-4 py-2 rounded transition-colors font-medium border ${
              currentWantedFilter === 'unwanted'
                ? 'bg-orange-700 border-orange-700 shadow-md ring-2 ring-orange-300'
                : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300'
            }`}
            style={{
              backgroundColor:
                currentWantedFilter === 'unwanted' ? '#c2410c' : 'white',
              color: currentWantedFilter === 'unwanted' ? 'white' : '#374151',
            }}
          >
            Unwanted Only
          </button>
        </div>
      </div>

      {/* Download Status Filter */}
      <div>
        <h3 className='text-sm font-medium text-gray-700 mb-2'>
          Download Status
        </h3>
        <div className='flex gap-4'>
          <button
            onClick={() => onDownloadFilterChange('all')}
            className={`px-4 py-2 rounded transition-colors font-medium border ${
              currentDownloadFilter === 'all'
                ? 'bg-indigo-700 border-indigo-700 shadow-md ring-2 ring-indigo-300'
                : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300'
            }`}
            style={{
              backgroundColor:
                currentDownloadFilter === 'all' ? '#3730a3' : 'white',
              color: currentDownloadFilter === 'all' ? 'white' : '#374151',
            }}
          >
            All Status
          </button>
          <button
            onClick={() => onDownloadFilterChange('downloaded')}
            className={`px-4 py-2 rounded transition-colors font-medium border ${
              currentDownloadFilter === 'downloaded'
                ? 'bg-green-700 border-green-700 shadow-md ring-2 ring-green-300'
                : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300'
            }`}
            style={{
              backgroundColor:
                currentDownloadFilter === 'downloaded' ? '#15803d' : 'white',
              color:
                currentDownloadFilter === 'downloaded' ? 'white' : '#374151',
            }}
          >
            Downloaded
          </button>
          <button
            onClick={() => onDownloadFilterChange('pending')}
            className={`px-4 py-2 rounded transition-colors font-medium border ${
              currentDownloadFilter === 'pending'
                ? 'bg-yellow-700 border-yellow-700 shadow-md ring-2 ring-yellow-300'
                : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300'
            }`}
            style={{
              backgroundColor:
                currentDownloadFilter === 'pending' ? '#a16207' : 'white',
              color: currentDownloadFilter === 'pending' ? 'white' : '#374151',
            }}
          >
            Pending
          </button>
        </div>
      </div>
    </div>
  );
}
