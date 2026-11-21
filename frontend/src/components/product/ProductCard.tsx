import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ShoppingBag, Sparkles, Loader2 } from 'lucide-react';
import type { Product } from '../../types';
import { formatPrice } from '../../utils/format';
import { productImage } from '../../utils/productImages';
import { StockBadge } from '../ui/StockBadge';
import { useCart } from '../../context/CartContext';
import { useToast } from '../../context/ToastContext';

interface ProductCardProps {
  product: Product;
}

export function ProductCard({ product }: ProductCardProps) {
  const { addItem } = useCart();
  const { showToast } = useToast();
  const [isAdding, setIsAdding] = useState(false);
  const outOfStock = product.stock <= 0;

  async function handleAdd() {
    setIsAdding(true);
    try {
      await addItem(product, 1);
      showToast(`${product.name} added to cart`, 'success');
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'Could not add to cart', 'error');
    } finally {
      setIsAdding(false);
    }
  }

  return (
    <article className="group flex flex-col overflow-hidden rounded-3xl border border-forest-100 bg-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
      <Link
        to={`/products/${product.id}`}
        className="relative block aspect-square overflow-hidden bg-cream-200"
        aria-label={`View ${product.name}`}
      >
        <img
          src={productImage(product.id, product.category)}
          alt={product.name}
          loading="lazy"
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
        />
        {product.customisable && (
          <span className="absolute left-3 top-3 inline-flex items-center gap-1 rounded-full bg-clay-500/95 px-2.5 py-1 text-xs font-medium text-white">
            <Sparkles className="h-3 w-3" /> Customisable
          </span>
        )}
      </Link>

      <div className="flex flex-1 flex-col gap-2 p-4">
        <div className="flex items-start justify-between gap-2">
          <span className="text-xs font-medium uppercase tracking-wide text-clay-500">
            {product.category}
          </span>
          <StockBadge stock={product.stock} />
        </div>
        <Link to={`/products/${product.id}`} className="hover:underline">
          <h3 className="font-display text-lg font-semibold leading-snug text-forest-900">
            {product.name}
          </h3>
        </Link>
        {product.description && (
          <p className="line-clamp-2 text-sm text-forest-600">{product.description}</p>
        )}
        <div className="mt-auto flex items-center justify-between gap-2 pt-2">
          <span className="text-lg font-semibold text-forest-800">{formatPrice(product.price)}</span>
          <button
            onClick={handleAdd}
            disabled={outOfStock || isAdding}
            className="btn-primary px-4 py-2 text-sm"
            aria-label={`Add ${product.name} to cart`}
          >
            {isAdding ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <ShoppingBag className="h-4 w-4" />
            )}
            {outOfStock ? 'Sold out' : 'Add'}
          </button>
        </div>
      </div>
    </article>
  );
}
