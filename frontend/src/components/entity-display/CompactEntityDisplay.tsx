interface CompactEntityDisplayProps {
  icon: string;
  color: string;
  displayName: string;
  fullName: string;
  label: string;
  entityType: string;
  link?: string;
}

export function CompactEntityDisplay({
  icon,
  color,
  displayName,
  fullName,
  label,
  entityType,
  link,
}: CompactEntityDisplayProps) {
  return (
    <div className='flex items-center space-x-1 min-w-0 w-full'>
      <span className={`text-sm flex-shrink-0 ${color}`}>{icon}</span>
      {link ? (
        <a
          href={link}
          target='_blank'
          rel='noopener noreferrer'
          className='text-blue-600 hover:text-blue-800 hover:underline text-xs truncate flex-1 min-w-0'
          title={`View ${entityType.toLowerCase()}: ${fullName}`}
        >
          {displayName}
        </a>
      ) : (
        <span
          className='text-xs text-gray-900 truncate flex-1 min-w-0 font-medium'
          title={fullName}
        >
          {displayName}
        </span>
      )}
      <span className='text-gray-500 text-xs flex-shrink-0'>({label})</span>
    </div>
  );
}
