import { useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { PackageSearch } from 'lucide-react';
import { useProducts } from '../hooks/useProducts';
import { ProductGrid } from '../components/product/ProductGrid';
import { AuthGateNotice } from '../components/product/AuthGateNotice';
import { EmptyState } from '../components/ui/EmptyState';
import { Spinner } from '../components/ui/Spinner';
import { SectionHeading } from '../components/ui/SectionHeading';
import type { ProductQuery, SortOption } from '../types';

const SORTS: Record<SortOption, Pick<ProductQuery, 'order_by' | 'order'> & { label: string }> = {
  'id-asc': { label: 'Newest', order_by: 'id', order: 'asc' },
  'name-asc': { label: 'Name A–Z', order_by: 'name', order: 'asc' },
  'name-desc': { label: 'Name Z–A', order_by: 'name', order: 'desc' },
  'price-asc': { label: 'Price: low to high', order_by: 'price', order: 'asc' },
  'price-desc': { label: 'Price: high to low', order_by: 'price', order: 'desc' },
};

export function ShopPage() {
  const [params, setParams] = useSearchParams();
  const category = params.get('category') ?? undefined;
  const customisable = params.get('customisable') === 'true' ? true : undefined;
  const q = (params.get('q') ?? '').trim().toLowerCase();
  const sort = (params.get('sort') as SortOption) in SORTS ? (params.get('sort') as SortOption) : 'id-asc';

  const { products, isLoading, error, needsAuth, reload } = useProducts({
    category,
    customisable,
    order_by: SORTS[sort].order_by,
    order: SORTS[sort].order,
  });

  const visible = useMemo(
    () => (q ? products.filter((p) => `${p.name} ${p.description ?? ''}`.toLowerCase().includes(q)) : products),
    [products, q]
  );

  return (
    <div className="container-px space-y-8 py-12">
      <SectionHeading align="left" title={category ?? (customisable ? 'Customised products' : 'Shop all')} />
      {needsAuth ? (
        <AuthGateNotice />
      ) : (
        <>
          <select
            value={sort}
            onChange={(e) => {
              const next = new URLSearchParams(params);
              next.set('sort', e.target.value);
              setParams(next);
            }}
            className="input-field max-w-xs"
            aria-label="Sort products"
          >
            {Object.entries(SORTS).map(([key, s]) => (
              <option key={key} value={key}>
                {s.label}
              </option>
            ))}
          </select>
          {isLoading && <Spinner />}
          {error && (
            <EmptyState
              icon={PackageSearch}
              title="Could not load products"
              description={error}
              action={<button className="btn-primary px-5 py-2 text-sm" onClick={reload}>Try again</button>}
            />
          )}
          {!isLoading && !error && visible.length === 0 && (
            <EmptyState icon={PackageSearch} title="No products found" />
          )}
          {!isLoading && !error && visible.length > 0 && <ProductGrid products={visible} />}
        </>
      )}
    </div>
  );
}
