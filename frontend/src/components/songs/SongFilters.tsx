interface SongFiltersProps {
  currentDownloadFilter: 'all' | 'downloaded' | 'failed' | 'unavailable';
  onDownloadFilterChange: (
    filter: 'all' | 'downloaded' | 'failed' | 'unavailable'
  ) => void;
}

export function SongFilters({
  currentDownloadFilter,
  onDownloadFilterChange,
}: SongFiltersProps) {
  return (
    <div className='mb-6'>
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
          All Songs
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
            color: currentDownloadFilter === 'downloaded' ? 'white' : '#374151',
          }}
        >
          Downloaded
        </button>
        <button
          onClick={() => onDownloadFilterChange('failed')}
          className={`px-4 py-2 rounded transition-colors font-medium border ${
            currentDownloadFilter === 'failed'
              ? 'bg-yellow-700 border-yellow-700 shadow-md ring-2 ring-yellow-300'
              : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300'
          }`}
          style={{
            backgroundColor:
              currentDownloadFilter === 'failed' ? '#a16207' : 'white',
            color: currentDownloadFilter === 'failed' ? 'white' : '#374151',
          }}
        >
          Failed
        </button>
        <button
          onClick={() => onDownloadFilterChange('unavailable')}
          className={`px-4 py-2 rounded transition-colors font-medium border ${
            currentDownloadFilter === 'unavailable'
              ? 'bg-red-700 border-red-700 shadow-md ring-2 ring-red-300'
              : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300'
          }`}
          style={{
            backgroundColor:
              currentDownloadFilter === 'unavailable' ? '#dc2626' : 'white',
            color:
              currentDownloadFilter === 'unavailable' ? 'white' : '#374151',
          }}
        >
          Unavailable
        </button>
      </div>
    </div>
  );
}
