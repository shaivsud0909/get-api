import { discountPercent, formatPrice } from '../../utils/format';

interface PriceTagProps {
  price: number;
  originalPrice?: number | null;
  size?: 'sm' | 'md' | 'lg';
}

const sizes = {
  sm: { price: 'text-sm font-medium', original: 'text-xs', badge: 'text-[10px] px-1.5' },
  md: { price: 'text-lg font-semibold', original: 'text-sm', badge: 'text-xs px-2' },
  lg: { price: 'text-2xl font-semibold', original: 'text-base', badge: 'text-sm px-2.5' },
};

/** Shows the selling price, with the original price struck through when discounted. */
export function PriceTag({ price, originalPrice, size = 'md' }: PriceTagProps) {
  const s = sizes[size];
  const off = discountPercent(price, originalPrice);

  return (
    <span className="inline-flex flex-wrap items-baseline gap-x-2 gap-y-1">
      <span className={`${s.price} text-forest-800`}>{formatPrice(price)}</span>
      {off > 0 && (
        <>
          <s className={`${s.original} text-forest-400`} aria-label={`Original price ${formatPrice(originalPrice!)}`}>
            {formatPrice(originalPrice!)}
          </s>
          <span className={`${s.badge} rounded-full bg-clay-100 py-0.5 font-medium text-clay-700`}>
            {off}% off
          </span>
        </>
      )}
    </span>
  );
}
