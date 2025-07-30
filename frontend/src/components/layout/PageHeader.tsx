import React from 'react';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  children?: React.ReactNode;
  className?: string;
}

export function PageHeader({
  title,
  subtitle,
  children,
  className = '',
}: PageHeaderProps) {
  return (
    <div className={`flex items-center justify-between ${className}`}>
      <div>
        <h1 className='text-3xl font-bold text-gray-900'>{title}</h1>
        {subtitle && <p className='text-gray-600 mt-2'>{subtitle}</p>}
      </div>
      {children && <div className='flex items-center gap-4'>{children}</div>}
    </div>
  );
}
