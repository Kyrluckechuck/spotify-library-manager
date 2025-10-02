import { FilterButtonGroup, type FilterOption } from '../ui/FilterButtonGroup';

interface AlbumFiltersProps {
  currentWantedFilter: 'all' | 'wanted' | 'unwanted';
  currentDownloadFilter: 'all' | 'downloaded' | 'pending';
  onWantedFilterChange: (filter: 'all' | 'wanted' | 'unwanted') => void;
  onDownloadFilterChange: (filter: 'all' | 'downloaded' | 'pending') => void;
}

const wantedFilterOptions: FilterOption<'all' | 'wanted' | 'unwanted'>[] = [
  { value: 'all', label: 'All Albums', color: 'indigo' },
  { value: 'wanted', label: 'Wanted Only', color: 'green' },
  { value: 'unwanted', label: 'Unwanted Only', color: 'orange' },
];

const downloadFilterOptions: FilterOption<'all' | 'downloaded' | 'pending'>[] =
  [
    { value: 'all', label: 'All Status', color: 'indigo' },
    { value: 'downloaded', label: 'Downloaded', color: 'green' },
    { value: 'pending', label: 'Pending', color: 'yellow' },
  ];

export function AlbumFilters({
  currentWantedFilter,
  currentDownloadFilter,
  onWantedFilterChange,
  onDownloadFilterChange,
}: AlbumFiltersProps) {
  return (
    <div className='space-y-4 mb-6'>
      <FilterButtonGroup
        value={currentWantedFilter}
        options={wantedFilterOptions}
        onChange={onWantedFilterChange}
        label='Wanted Status'
      />
      <FilterButtonGroup
        value={currentDownloadFilter}
        options={downloadFilterOptions}
        onChange={onDownloadFilterChange}
        label='Download Status'
      />
    </div>
  );
}
