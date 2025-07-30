interface SortableTableHeaderProps<T> {
  field: T;
  currentSortField: T;
  currentSortDirection: 'asc' | 'desc';
  onSort: (field: T) => void;
  children: React.ReactNode;
  className?: string;
}

export function SortableTableHeader<T>({
  field,
  currentSortField,
  currentSortDirection,
  onSort,
  children,
  className = '',
}: SortableTableHeaderProps<T>) {
  const getSortIcon = () => {
    if (currentSortField !== field) {
      return '↕️'; // Both arrows when not sorted
    }
    return currentSortDirection === 'asc' ? '↑' : '↓';
  };

  const baseClasses =
    'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider';
  const interactiveClasses = field ? 'cursor-pointer hover:bg-gray-100' : '';

  return (
    <th
      className={`${baseClasses} ${interactiveClasses} ${className}`}
      onClick={field ? () => onSort(field) : undefined}
    >
      <div className='flex items-center gap-1'>
        {children} {field && getSortIcon()}
      </div>
    </th>
  );
}
