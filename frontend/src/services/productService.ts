import { apiClient } from './apiClient';
import type { ApiEnvelope, Product, ProductQuery } from '../types';

/**
 * GET /products — requires an authenticated user (role "user").
 * Supports category (ILIKE match), customisable, order_by and order params.
 */
export async function fetchProducts(query: ProductQuery = {}): Promise<Product[]> {
  const { data } = await apiClient.get<ApiEnvelope<Product[]>>('/products', {
    params: query,
  });
  return data.data;
}

/** GET /customisable-products — customisable products only. */
export async function fetchCustomisableProducts(): Promise<Product[]> {
  const { data } = await apiClient.get<ApiEnvelope<Product[]>>('/customisable-products');
  return data.data;
}

/**
 * MISSING BACKEND ENDPOINT: there is no customer-facing
 * GET /products/{id} (it exists only on the admin router).
 * Product detail is resolved by fetching the list and matching the id.
 */
export async function fetchProductById(id: number): Promise<Product | null> {
  const products = await fetchProducts();
  return products.find((p) => p.id === id) ?? null;
}
