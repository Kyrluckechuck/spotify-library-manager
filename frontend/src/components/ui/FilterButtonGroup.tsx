/**
 * FilterButtonGroup - Reusable filter button component
 *
 * Provides consistent filter UI across the application with:
 * - Active/inactive state styling
 * - Customizable colors per button
 * - Optional hover handlers for prefetching
 * - Flexible layout options
 */

export interface FilterOption<T extends string> {
  value: T;
  label: string;
  color?: 'indigo' | 'green' | 'orange' | 'yellow' | 'red' | 'gray' | 'blue';
}

interface FilterButtonGroupProps<T extends string> {
  /** Current active filter value */
  value: T;
  /** Available filter options */
  options: FilterOption<T>[];
  /** Called when filter changes */
  onChange: (value: T) => void;
  /** Optional hover handler for prefetching */
  onHover?: (value: T) => void;
  /** Optional label/heading for the filter group */
  label?: string;
  /** Additional CSS classes for the container */
  className?: string;
}

const colorStyles = {
  indigo: {
    active: 'bg-indigo-700 border-indigo-700 shadow-md ring-2 ring-indigo-300',
    activeBg: '#3730a3',
  },
  green: {
    active: 'bg-green-700 border-green-700 shadow-md ring-2 ring-green-300',
    activeBg: '#15803d',
  },
  orange: {
    active: 'bg-orange-700 border-orange-700 shadow-md ring-2 ring-orange-300',
    activeBg: '#c2410c',
  },
  yellow: {
    active: 'bg-yellow-700 border-yellow-700 shadow-md ring-2 ring-yellow-300',
    activeBg: '#a16207',
  },
  red: {
    active: 'bg-red-700 border-red-700 shadow-md ring-2 ring-red-300',
    activeBg: '#b91c1c',
  },
  gray: {
    active: 'bg-gray-700 border-gray-700 shadow-md ring-2 ring-gray-300',
    activeBg: '#374151',
  },
  blue: {
    active: 'bg-blue-700 border-blue-700 shadow-md ring-2 ring-blue-300',
    activeBg: '#1d4ed8',
  },
};

export function FilterButtonGroup<T extends string>({
  value,
  options,
  onChange,
  onHover,
  label,
  className = '',
}: FilterButtonGroupProps<T>) {
  return (
    <div className={className}>
      {label && (
        <h3 className='text-sm font-medium text-gray-700 mb-2'>{label}</h3>
      )}
      <div className='flex gap-4'>
        {options.map(option => {
          const isActive = value === option.value;
          const color = option.color || 'indigo';
          const colorStyle = colorStyles[color];

          return (
            <button
              key={option.value}
              onClick={() => onChange(option.value)}
              onMouseEnter={() => onHover?.(option.value)}
              className={`px-4 py-2 rounded transition-colors font-medium border ${
                isActive
                  ? colorStyle.active
                  : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300'
              }`}
              style={{
                backgroundColor: isActive ? colorStyle.activeBg : 'white',
                color: isActive ? 'white' : '#374151',
              }}
            >
              {option.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
