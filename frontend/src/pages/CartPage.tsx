import { Link } from 'react-router-dom';
import { ShoppingBag, Trash2 } from 'lucide-react';
import { useCart } from '../context/CartContext';
import { useToast } from '../context/ToastContext';
import { getErrorMessage } from '../services/apiClient';
import { placeOrder } from '../services/orderService';
import { EmptyState } from '../components/ui/EmptyState';
import { QuantitySelector } from '../components/ui/QuantitySelector';
import { formatPrice } from '../utils/format';

export function CartPage() {
  const { lines, subtotal, updateQuantity, removeItem } = useCart();
  const { showToast } = useToast();

  if (lines.length === 0) {
    return (
      <div className="container-px py-12">
        <EmptyState
          icon={ShoppingBag}
          title="Your cart is empty"
          action={<Link to="/shop" className="btn-primary px-5 py-2 text-sm">Start shopping</Link>}
        />
      </div>
    );
  }

  const checkout = async () => {
    try {
      await placeOrder();
    } catch (err) {
      showToast(getErrorMessage(err), 'info');
    }
  };

  return (
    <div className="container-px space-y-6 py-12">
      <h1 className="font-display text-3xl font-semibold text-forest-900">Your cart</h1>
      <ul className="divide-y divide-forest-100 rounded-3xl border border-forest-100 bg-white">
        {lines.map(({ product, quantity }) => (
          <li key={product.id} className="flex flex-wrap items-center gap-4 p-4">
            <div className="min-w-0 flex-1">
              <Link to={`/products/${product.id}`} className="font-medium text-forest-900 hover:underline">
                {product.name}
              </Link>
              <p className="text-sm text-forest-600">{formatPrice(product.price)}</p>
            </div>
            <QuantitySelector
              size="sm"
              value={quantity}
              max={Math.max(product.stock, 1)}
              onChange={(q) => updateQuantity(product.id, q).catch((e) => showToast(getErrorMessage(e), 'error'))}
            />
            <span className="w-24 text-right font-medium">{formatPrice(product.price * quantity)}</span>
            <button onClick={() => removeItem(product.id)} aria-label={`Remove ${product.name}`}>
              <Trash2 className="h-4 w-4 text-red-500" />
            </button>
          </li>
        ))}
      </ul>
      <div className="flex items-center justify-between">
        <p className="text-lg">Subtotal: <strong>{formatPrice(subtotal)}</strong></p>
        <button className="btn-primary px-6 py-2.5" onClick={checkout}>Checkout</button>
      </div>
    </div>
  );
}
