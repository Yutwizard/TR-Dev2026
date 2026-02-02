/**
 * Reusable UI Components for Treasury Management System
 */

'use client';

import { ReactNode, ButtonHTMLAttributes, InputHTMLAttributes, forwardRef } from 'react';
import { Loader2 } from 'lucide-react';

// =============================================================================
// Button Component
// =============================================================================
interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
    loading?: boolean;
    icon?: ReactNode;
    children: ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
    ({ variant = 'primary', size = 'md', loading, icon, children, disabled, className = '', ...props }, ref) => {
        const baseStyles = 'inline-flex items-center justify-center gap-2 font-medium rounded-lg transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

        const variants = {
            primary: 'bg-primary-500 text-white hover:bg-primary-600 focus:ring-primary-500',
            secondary: 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600 focus:ring-gray-400',
            success: 'bg-green-500 text-white hover:bg-green-600 focus:ring-green-500',
            danger: 'bg-red-500 text-white hover:bg-red-600 focus:ring-red-500',
            ghost: 'bg-transparent hover:bg-gray-100 dark:hover:bg-gray-800 focus:ring-gray-400',
        };

        const sizes = {
            sm: 'px-3 py-1.5 text-xs',
            md: 'px-4 py-2 text-sm',
            lg: 'px-6 py-3 text-base',
        };

        return (
            <button
                ref={ref}
                className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
                disabled={disabled || loading}
                {...props}
            >
                {loading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                ) : icon ? (
                    icon
                ) : null}
                {children}
            </button>
        );
    }
);

Button.displayName = 'Button';

// =============================================================================
// Input Component
// =============================================================================
interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
    helperText?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
    ({ label, error, helperText, className = '', ...props }, ref) => {
        return (
            <div className="space-y-1">
                {label && (
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        {label}
                    </label>
                )}
                <input
                    ref={ref}
                    className={`
            w-full px-3 py-2 text-sm border rounded-lg 
            bg-white dark:bg-gray-800 
            ${error
                            ? 'border-red-500 focus:ring-red-500'
                            : 'border-gray-300 dark:border-gray-600 focus:ring-primary-500'
                        }
            focus:outline-none focus:ring-2 focus:border-transparent
            placeholder:text-gray-400 dark:placeholder:text-gray-500
            disabled:bg-gray-50 dark:disabled:bg-gray-900 disabled:cursor-not-allowed
            ${className}
          `}
                    {...props}
                />
                {error && <p className="text-xs text-red-600 dark:text-red-400">{error}</p>}
                {helperText && !error && (
                    <p className="text-xs text-gray-500 dark:text-gray-400">{helperText}</p>
                )}
            </div>
        );
    }
);

Input.displayName = 'Input';

// =============================================================================
// Select Component
// =============================================================================
interface SelectOption {
    value: string;
    label: string;
}

interface SelectProps {
    label?: string;
    options: SelectOption[];
    value?: string;
    onChange?: (value: string) => void;
    error?: string;
    placeholder?: string;
    disabled?: boolean;
}

export function Select({ label, options, value, onChange, error, placeholder, disabled }: SelectProps) {
    return (
        <div className="space-y-1">
            {label && (
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {label}
                </label>
            )}
            <select
                value={value}
                onChange={(e) => onChange?.(e.target.value)}
                disabled={disabled}
                className={`
          w-full px-3 py-2 text-sm border rounded-lg 
          bg-white dark:bg-gray-800 
          ${error
                        ? 'border-red-500 focus:ring-red-500'
                        : 'border-gray-300 dark:border-gray-600 focus:ring-primary-500'
                    }
          focus:outline-none focus:ring-2 focus:border-transparent
          disabled:bg-gray-50 dark:disabled:bg-gray-900 disabled:cursor-not-allowed
        `}
            >
                {placeholder && (
                    <option value="" disabled>
                        {placeholder}
                    </option>
                )}
                {options.map((option) => (
                    <option key={option.value} value={option.value}>
                        {option.label}
                    </option>
                ))}
            </select>
            {error && <p className="text-xs text-red-600 dark:text-red-400">{error}</p>}
        </div>
    );
}

// =============================================================================
// Card Component
// =============================================================================
interface CardProps {
    children: ReactNode;
    className?: string;
    hover?: boolean;
    padding?: 'sm' | 'md' | 'lg';
}

export function Card({ children, className = '', hover = false, padding = 'md' }: CardProps) {
    const paddings = {
        sm: 'p-3',
        md: 'p-5',
        lg: 'p-6',
    };

    return (
        <div
            className={`
        bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-card
        ${hover ? 'transition-all duration-200 hover:shadow-card-hover hover:border-primary-200 dark:hover:border-primary-700' : ''}
        ${paddings[padding]}
        ${className}
      `}
        >
            {children}
        </div>
    );
}

// =============================================================================
// Badge Component
// =============================================================================
type BadgeVariant = 'success' | 'warning' | 'danger' | 'info' | 'neutral';

interface BadgeProps {
    children: ReactNode;
    variant?: BadgeVariant;
    size?: 'sm' | 'md';
}

export function Badge({ children, variant = 'neutral', size = 'md' }: BadgeProps) {
    const variants = {
        success: 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-400',
        warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-400',
        danger: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-400',
        info: 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-400',
        neutral: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
    };

    const sizes = {
        sm: 'px-2 py-0.5 text-xs',
        md: 'px-2.5 py-0.5 text-xs',
    };

    return (
        <span className={`inline-flex items-center rounded-full font-medium ${variants[variant]} ${sizes[size]}`}>
            {children}
        </span>
    );
}

// =============================================================================
// Status Badge with specific status mappings
// =============================================================================
interface StatusBadgeProps {
    status: string;
}

export function StatusBadge({ status }: StatusBadgeProps) {
    const statusMap: Record<string, { label: string; variant: BadgeVariant }> = {
        // Trade/Deal statuses
        DRAFT: { label: 'Draft', variant: 'neutral' },
        PENDING_APPROVAL: { label: 'Pending Approval', variant: 'warning' },
        APPROVED: { label: 'Approved', variant: 'info' },
        ACTIVE: { label: 'Active', variant: 'success' },
        SETTLED: { label: 'Settled', variant: 'success' },
        MATURED: { label: 'Matured', variant: 'neutral' },
        CANCELLED: { label: 'Cancelled', variant: 'danger' },
        REJECTED: { label: 'Rejected', variant: 'danger' },
        // Settlement statuses
        PENDING: { label: 'Pending', variant: 'warning' },
        PROCESSING: { label: 'Processing', variant: 'info' },
        SENT: { label: 'Sent', variant: 'info' },
        CONFIRMED: { label: 'Confirmed', variant: 'success' },
        FAILED: { label: 'Failed', variant: 'danger' },
        // Repo
        NEAR_LEG_SETTLED: { label: 'Near Leg Settled', variant: 'info' },
        FAR_LEG_SETTLED: { label: 'Far Leg Settled', variant: 'success' },
        EARLY_TERMINATED: { label: 'Early Terminated', variant: 'warning' },
    };

    const config = statusMap[status] || { label: status, variant: 'neutral' as BadgeVariant };

    return <Badge variant={config.variant}>{config.label}</Badge>;
}

// =============================================================================
// Loading Spinner
// =============================================================================
interface SpinnerProps {
    size?: 'sm' | 'md' | 'lg';
}

export function Spinner({ size = 'md' }: SpinnerProps) {
    const sizes = {
        sm: 'w-4 h-4',
        md: 'w-6 h-6',
        lg: 'w-8 h-8',
    };

    return (
        <div className="flex items-center justify-center">
            <Loader2 className={`${sizes[size]} animate-spin text-primary-500`} />
        </div>
    );
}

// =============================================================================
// Empty State
// =============================================================================
interface EmptyStateProps {
    icon?: ReactNode;
    title: string;
    description?: string;
    action?: ReactNode;
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
    return (
        <div className="flex flex-col items-center justify-center py-12 text-center">
            {icon && <div className="mb-4 text-gray-400 dark:text-gray-500">{icon}</div>}
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">{title}</h3>
            {description && (
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400 max-w-sm">
                    {description}
                </p>
            )}
            {action && <div className="mt-4">{action}</div>}
        </div>
    );
}

// =============================================================================
// Currency Display
// =============================================================================
interface CurrencyDisplayProps {
    value: number;
    currency?: string;
    showSign?: boolean;
    className?: string;
}

export function CurrencyDisplay({ value, currency = 'THB', showSign = false, className = '' }: CurrencyDisplayProps) {
    const isNegative = value < 0;
    const absValue = Math.abs(value);

    // Format with Thai Baht style
    const formatted = new Intl.NumberFormat('th-TH', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(absValue);

    const colorClass = showSign
        ? isNegative
            ? 'text-red-600 dark:text-red-400'
            : value > 0
                ? 'text-green-600 dark:text-green-400'
                : ''
        : '';

    const sign = showSign && value > 0 ? '+' : '';
    const prefix = currency === 'THB' ? '฿' : currency + ' ';

    return (
        <span className={`font-mono ${colorClass} ${className}`}>
            {sign}{isNegative ? '-' : ''}{prefix}{formatted}
        </span>
    );
}

// =============================================================================
// Percentage Display
// =============================================================================
interface PercentageDisplayProps {
    value: number;
    showSign?: boolean;
    decimals?: number;
    className?: string;
}

export function PercentageDisplay({ value, showSign = false, decimals = 2, className = '' }: PercentageDisplayProps) {
    const formatted = value.toFixed(decimals);
    const isNegative = value < 0;
    const colorClass = showSign
        ? isNegative
            ? 'text-red-600 dark:text-red-400'
            : value > 0
                ? 'text-green-600 dark:text-green-400'
                : ''
        : '';

    const sign = showSign && value > 0 ? '+' : '';

    return (
        <span className={`font-mono ${colorClass} ${className}`}>
            {sign}{formatted}%
        </span>
    );
}
