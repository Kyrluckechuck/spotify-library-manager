import React from 'react';

interface PageContainerProps {
  children: React.ReactNode;
  className?: string;
}

export function PageContainer({
  children,
  className = '',
}: PageContainerProps) {
  return <div className={`space-y-8 ${className}`}>{children}</div>;
}
