import { apiClient } from './apiClient';
import type { ApiEnvelope, ServerCartItem } from '../types';

/**
 * Cart API surface actually provided by the backend:
 *   POST  /add-to-cart          — add a product (creates the cart if needed)
 *   PATCH /cart-item/{item_id}  — set a line's quantity (min 1)
 *
 * MISSING BACKEND ENDPOINTS (documented integration boundary):
 *   - GET a cart with its items (GET /cart *creates* a cart and returns no
 *     items, and fails once a cart already exists for the user)
 *   - DELETE a cart item
 * The cart is therefore mirrored in CartContext/localStorage and synced to
 * the backend through the two endpoints above.
 */

export async function addToCart(productId: number, quantity: number): Promise<ServerCartItem> {
  const { data } = await apiClient.post<ApiEnvelope<ServerCartItem>>('/add-to-cart', {
    product_id: productId,
    quantity,
  });
  return data.data;
}

export async function updateCartItem(itemId: number, quantity: number): Promise<ServerCartItem> {
  const { data } = await apiClient.patch<ApiEnvelope<ServerCartItem>>(`/cart-item/${itemId}`, {
    quantity,
  });
  return data.data;
}
