import { useCallback, useEffect, useState } from 'react';
import type { Product, ProductQuery } from '../types';
import { fetchProducts } from '../services/productService';
import { getErrorMessage } from '../services/apiClient';
import { useAuth } from '../context/AuthContext';

interface UseProductsResult {
  products: Product[];
  isLoading: boolean;
  error: string | null;
  /** True when the failure is a 401/403 — products require a signed-in user. */
  needsAuth: boolean;
  reload: () => void;
}

/**
 * Fetches products from GET /products. Note: the backend guards this route
 * with role "user", so visitors must sign in before the catalogue loads.
 */
export function useProducts(query: ProductQuery = {}): UseProductsResult {
  const { isAuthenticated, user } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [needsAuth, setNeedsAuth] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);

  const { category, customisable, order_by, order } = query;

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'user') {
      setProducts([]);
      setNeedsAuth(true);
      setError(null);
      setIsLoading(false);
      return;
    }

    let cancelled = false;
    setIsLoading(true);
    setNeedsAuth(false);
    setError(null);

    fetchProducts({ category, customisable, order_by, order })
      .then((data) => {
        if (!cancelled) setProducts(data);
      })
      .catch((err) => {
        if (!cancelled) setError(getErrorMessage(err));
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [isAuthenticated, user?.role, category, customisable, order_by, order, reloadKey]);

  const reload = useCallback(() => setReloadKey((k) => k + 1), []);

  return { products, isLoading, error, needsAuth, reload };
}
