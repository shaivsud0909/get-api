import { Minus, Plus } from 'lucide-react';

interface QuantitySelectorProps {
  value: number;
  min?: number;
  max: number;
  onChange: (value: number) => void;
  disabled?: boolean;
  size?: 'sm' | 'md';
}

export function QuantitySelector({
  value,
  min = 1,
  max,
  onChange,
  disabled = false,
  size = 'md',
}: QuantitySelectorProps) {
  const btn =
    size === 'sm'
      ? 'h-7 w-7'
      : 'h-9 w-9';
  return (
    <div className="inline-flex items-center rounded-full border border-forest-200 bg-white">
      <button
        type="button"
        aria-label="Decrease quantity"
        disabled={disabled || value <= min}
        onClick={() => onChange(value - 1)}
        className={`${btn} flex items-center justify-center rounded-full text-forest-700 transition hover:bg-forest-50 disabled:opacity-40`}
      >
        <Minus className="h-4 w-4" />
      </button>
      <span
        aria-live="polite"
        className={`${size === 'sm' ? 'w-8 text-sm' : 'w-10'} text-center font-medium text-forest-900`}
      >
        {value}
      </span>
      <button
        type="button"
        aria-label="Increase quantity"
        disabled={disabled || value >= max}
        onClick={() => onChange(value + 1)}
        className={`${btn} flex items-center justify-center rounded-full text-forest-700 transition hover:bg-forest-50 disabled:opacity-40`}
      >
        <Plus className="h-4 w-4" />
      </button>
    </div>
  );
}
