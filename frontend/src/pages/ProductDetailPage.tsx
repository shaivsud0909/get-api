import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { PackageSearch } from 'lucide-react';
import { fetchProductById } from '../services/productService';
import { getErrorMessage } from '../services/apiClient';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';
import { useToast } from '../context/ToastContext';
import { AuthGateNotice } from '../components/product/AuthGateNotice';
import { EmptyState } from '../components/ui/EmptyState';
import { QuantitySelector } from '../components/ui/QuantitySelector';
import { Spinner } from '../components/ui/Spinner';
import { formatPrice } from '../utils/format';
import type { Product } from '../types';

export function ProductDetailPage() {
  const { id } = useParams();
  const { isAuthenticated } = useAuth();
  const { addItem } = useCart();
  const { showToast } = useToast();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    if (!isAuthenticated) return;
    setLoading(true);
    fetchProductById(Number(id))
      .then(setProduct)
      .catch((err) => showToast(getErrorMessage(err), 'error'))
      .finally(() => setLoading(false));
  }, [id, isAuthenticated, showToast]);

  if (!isAuthenticated) return <div className="container-px py-12"><AuthGateNotice /></div>;
  if (loading) return <Spinner />;
  if (!product) {
    return (
      <div className="container-px py-12">
        <EmptyState
          icon={PackageSearch}
          title="Product not found"
          action={<Link to="/shop" className="btn-primary px-5 py-2 text-sm">Back to shop</Link>}
        />
      </div>
    );
  }

  const handleAdd = async () => {
    try {
      await addItem(product, quantity);
      showToast(`${product.name} added to cart`, 'success');
    } catch (err) {
      showToast(getErrorMessage(err), 'error');
    }
  };

  return (
    <div className="container-px max-w-2xl space-y-4 py-12">
      <p className="text-xs uppercase tracking-widest text-clay-500">{product.category}</p>
      <h1 className="font-display text-3xl font-semibold text-forest-900">{product.name}</h1>
      <p className="text-2xl text-forest-800">{formatPrice(product.price)}</p>
      <p className="text-forest-600">{product.description}</p>
      {product.stock > 0 ? (
        <div className="flex items-center gap-4">
          <QuantitySelector value={quantity} onChange={setQuantity} max={product.stock} />
          <button className="btn-primary px-6 py-2.5" onClick={handleAdd}>Add to cart</button>
        </div>
      ) : (
        <p className="font-medium text-red-600">Out of stock</p>
      )}
    </div>
  );
}
