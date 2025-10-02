import { FilterButtonGroup, type FilterOption } from '../ui/FilterButtonGroup';

interface ArtistFiltersProps {
  currentFilter: 'all' | 'tracked' | 'untracked';
  onFilterChange: (filter: 'all' | 'tracked' | 'untracked') => void;
  onFilterHover?: (filter: 'all' | 'tracked' | 'untracked') => void;
}

const filterOptions: FilterOption<'all' | 'tracked' | 'untracked'>[] = [
  { value: 'all', label: 'Show All', color: 'indigo' },
  { value: 'tracked', label: 'Tracked Only', color: 'green' },
  { value: 'untracked', label: 'Untracked Only', color: 'orange' },
];

export function ArtistFilters({
  currentFilter,
  onFilterChange,
  onFilterHover,
}: ArtistFiltersProps) {
  return (
    <FilterButtonGroup
      value={currentFilter}
      options={filterOptions}
      onChange={onFilterChange}
      onHover={onFilterHover}
      className='mb-6'
    />
  );
}
