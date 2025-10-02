import type { ButtonHTMLAttributes } from 'react';
import { InlineSpinner } from './InlineSpinner';

interface ActionButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean;
  loadingText?: string;
  variant?:
    | 'primary'
    | 'secondary'
    | 'danger'
    | 'success'
    | 'blue'
    | 'green'
    | 'red'
    | 'gray';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

const variantClasses = {
  primary: 'bg-blue-600 hover:bg-blue-700 text-white',
  secondary: 'bg-gray-600 hover:bg-gray-700 text-white',
  danger: 'bg-red-600 hover:bg-red-700 text-white',
  success: 'bg-green-600 hover:bg-green-700 text-white',
  blue: 'bg-blue-600 hover:bg-blue-700 text-white',
  green: 'bg-green-600 hover:bg-green-700 text-white',
  red: 'bg-red-600 hover:bg-red-700 text-white',
  gray: 'bg-gray-600 hover:bg-gray-700 text-white',
};

const sizeClasses = {
  sm: 'px-2 py-1 text-xs',
  md: 'px-3 py-1.5 text-sm',
  lg: 'px-4 py-2 text-base',
};

export function ActionButton({
  loading = false,
  loadingText,
  variant = 'primary',
  size = 'sm',
  disabled,
  className = '',
  children,
  ...props
}: ActionButtonProps) {
  const baseClasses =
    'rounded font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5';
  const finalClassName = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`;

  return (
    <button
      {...props}
      disabled={disabled || loading}
      className={finalClassName}
    >
      {loading && <InlineSpinner size={size === 'sm' ? 'xs' : 'sm'} />}
      {loading && loadingText ? loadingText : children}
    </button>
  );
}
