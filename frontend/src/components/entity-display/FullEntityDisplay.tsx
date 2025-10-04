interface FullEntityDisplayProps {
  icon: string;
  color: string;
  name: string;
  label: string;
  entityType: string;
  link?: string;
}

export function FullEntityDisplay({
  icon,
  color,
  name,
  label,
  entityType,
  link,
}: FullEntityDisplayProps) {
  return (
    <div className='flex items-center space-x-2'>
      <span className={`text-lg ${color}`}>{icon}</span>
      {link ? (
        <a
          href={link}
          target='_blank'
          rel='noopener noreferrer'
          className='text-blue-600 hover:text-blue-800 hover:underline font-medium'
          title={`View ${entityType.toLowerCase()}: ${name}`}
        >
          {name}
        </a>
      ) : (
        <span className='font-medium text-gray-900'>{name}</span>
      )}
      <span className='text-gray-500 text-xs'>({label})</span>
    </div>
  );
}
