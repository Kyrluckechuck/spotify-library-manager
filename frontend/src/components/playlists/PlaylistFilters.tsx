import { FilterButtonGroup, type FilterOption } from '../ui/FilterButtonGroup';

interface PlaylistFiltersProps {
  currentEnabledFilter: 'all' | 'enabled' | 'disabled';
  onEnabledFilterChange: (filter: 'all' | 'enabled' | 'disabled') => void;
  onFilterHover?: (filter: 'all' | 'enabled' | 'disabled') => void;
}

const filterOptions: FilterOption<'all' | 'enabled' | 'disabled'>[] = [
  { value: 'all', label: 'All Playlists', color: 'indigo' },
  { value: 'enabled', label: 'Enabled Only', color: 'green' },
  { value: 'disabled', label: 'Disabled Only', color: 'gray' },
];

export function PlaylistFilters({
  currentEnabledFilter,
  onEnabledFilterChange,
  onFilterHover,
}: PlaylistFiltersProps) {
  return (
    <FilterButtonGroup
      value={currentEnabledFilter}
      options={filterOptions}
      onChange={onEnabledFilterChange}
      onHover={onFilterHover}
      label='Status'
      className='mb-6'
    />
  );
}
