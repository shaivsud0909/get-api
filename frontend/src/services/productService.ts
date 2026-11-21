import { apiClient } from './apiClient';
import type { ApiEnvelope, Product, ProductDetails, ProductQuery } from '../types';

/**
 * GET /products — requires role "user".
 * Supports category (case-insensitive exact match), customisable, order_by and order params.
 */
export async function fetchProducts(query: ProductQuery = {}): Promise<Product[]> {
  const { data } = await apiClient.get<ApiEnvelope<Product[]>>('/products', {
    params: query,
  });
  return data.data;
}

/** GET /customisable-products — same params as /products; customisable defaults to true. */
export async function fetchCustomisableProducts(query: ProductQuery = {}): Promise<Product[]> {
  const { data } = await apiClient.get<ApiEnvelope<Product[]>>('/customisable-products', {
    params: query,
  });
  return data.data;
}

/** GET /product/{id} (singular) — the product itself. */
export async function fetchProductById(id: number): Promise<Product> {
  const { data } = await apiClient.get<ApiEnvelope<Product>>(`/product/${id}`);
  return data.data;
}

/** GET /products/{id} (plural) — features and images only. */
export async function fetchProductDetails(id: number): Promise<ProductDetails> {
  const { data } = await apiClient.get<ApiEnvelope<ProductDetails>>(`/products/${id}`);
  return data.data;
}
