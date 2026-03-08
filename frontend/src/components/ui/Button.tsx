/**
 * 按钮组件
 */
import React from 'react';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  children,
  className = '',
  disabled,
  ...props
}) => {
  const baseClass = 'font-medium rounded-md transition-all duration-fast inline-flex items-center justify-center gap-2';
  
  const variantClasses = {
    primary: 'bg-primary-500 text-white hover:bg-primary-600 hover:-translate-y-0.5',
    secondary: 'bg-bg-tertiary text-text-primary border border-border-default hover:bg-border-default',
    ghost: 'bg-transparent text-primary-500 hover:bg-primary-500/10',
    danger: 'bg-error-500 text-white hover:bg-error-600',
  };
  
  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  };
  
  const disabledClass = disabled || loading ? 'opacity-50 cursor-not-allowed hover:translate-y-0' : '';

  return (
    <button
      className={`${baseClass} ${variantClasses[variant]} ${sizeClasses[size]} ${disabledClass} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Loader2 size={16} className="animate-spin" />}
      {children}
    </button>
  );
};

export default Button;
