interface ToggleStatusButtonProps {
  enabled: boolean;
  onToggle: () => void;
  mutating?: boolean;
  pulse?: boolean;
  labels?: {
    on: string;
    off: string;
  };
  icons?: {
    on?: React.ReactNode;
    off?: React.ReactNode;
  };
  colors?: {
    on: string;
    off: string;
  };
  variant?: 'switch' | 'badge';
  disabled?: boolean;
  ariaLabel?: string;
}

const CheckIcon = () => (
  <svg
    className='w-3 h-3 text-green-700'
    viewBox='0 0 20 20'
    fill='currentColor'
    aria-hidden='true'
  >
    <path
      fillRule='evenodd'
      d='M16.707 5.293a1 1 0 00-1.414 0L8 12.586 4.707 9.293a1 1 0 10-1.414 1.414l4 4a1 1 0 001.414 0l8-8a1 1 0 000-1.414z'
      clipRule='evenodd'
    />
  </svg>
);

const CrossIcon = () => (
  <svg
    className='w-3 h-3 text-red-700'
    viewBox='0 0 20 20'
    fill='currentColor'
    aria-hidden='true'
  >
    <path
      fillRule='evenodd'
      d='M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z'
      clipRule='evenodd'
    />
  </svg>
);

export function ToggleStatusButton({
  enabled,
  onToggle,
  mutating = false,
  pulse = false,
  labels = { on: 'Enabled', off: 'Disabled' },
  icons = { on: <CheckIcon />, off: <CrossIcon /> },
  colors = { on: 'green', off: 'red' },
  variant = 'badge',
  disabled = false,
  ariaLabel,
}: ToggleStatusButtonProps) {
  if (variant === 'switch') {
    return (
      <button
        onClick={onToggle}
        disabled={disabled || mutating}
        role='switch'
        aria-checked={enabled}
        aria-label={
          ariaLabel ||
          (enabled ? `Disable ${labels.off}` : `Enable ${labels.on}`)
        }
        className='md:hidden inline-flex items-center w-12 h-6 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
        style={{
          backgroundColor: enabled ? '#22c55e' : '#e5e7eb',
        }}
      >
        <span
          className={`inline-block w-5 h-5 bg-white rounded-full transform transition-transform ${
            enabled ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
        <span className='sr-only'>{enabled ? labels.on : labels.off}</span>
      </button>
    );
  }

  // Badge variant
  const colorClasses = {
    green: {
      active:
        'bg-green-100 text-green-800 hover:bg-red-100 hover:text-red-800 focus:bg-red-100 focus:text-red-800',
      inactive:
        'bg-red-100 text-red-800 hover:bg-green-100 hover:text-green-800 focus:bg-green-100 focus:text-green-800',
    },
    blue: {
      active:
        'bg-blue-100 text-blue-800 hover:bg-gray-100 hover:text-gray-800 focus:bg-gray-100 focus:text-gray-800',
      inactive:
        'bg-gray-100 text-gray-800 hover:bg-blue-100 hover:text-blue-800 focus:bg-blue-100 focus:text-blue-800',
    },
    red: {
      active:
        'bg-red-100 text-red-800 hover:bg-green-100 hover:text-green-800 focus:bg-green-100 focus:text-green-800',
      inactive:
        'bg-green-100 text-green-800 hover:bg-red-100 hover:text-red-800 focus:bg-red-100 focus:text-red-800',
    },
  };

  const colorClass =
    colorClasses[colors.on as keyof typeof colorClasses] || colorClasses.green;
  const pulseClass = pulse ? `ring-2 ring-${colors.on}-400 ring-offset-1` : '';

  return (
    <button
      onClick={onToggle}
      disabled={disabled || mutating}
      aria-pressed={enabled}
      aria-label={
        ariaLabel || (enabled ? `Disable ${labels.off}` : `Enable ${labels.on}`)
      }
      className={`group hidden md:inline-flex px-2 py-1 text-xs font-semibold rounded-full transition-colors relative w-28 justify-center ${
        enabled ? colorClass.active : colorClass.inactive
      } ${pulseClass}`}
    >
      <span className='inline-flex items-center gap-1'>
        {enabled ? icons.on : icons.off}
        <span>{enabled ? labels.on : labels.off}</span>
      </span>
    </button>
  );
}
