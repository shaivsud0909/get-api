/** Product as returned by GET /products and GET /customisable-products. */
export interface Product {
  id: number;
  name: string;
  price: number;
  stock: number;
  category: string;
  customisable: boolean;
  description: string | null;
}

/** Standard wrapper used by the backend's @api_response decorator. */
export interface ApiEnvelope<T> {
  status: 'success';
  message: string;
  data: T;
}

/** Response of POST /login. */
export interface LoginResponse {
  access_token: string;
  token_type: string;
}

/** Response of POST /signup (raw user object, not wrapped). */
export interface SignupResponse {
  id: number;
  email: string;
  phone_number: string | null;
  country_code: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
  last_login_at: string | null;
}

/** Claims encoded in the backend's JWT access token. */
export interface TokenPayload {
  sub: string;
  email: string;
  role: 'user' | 'admin';
  exp: number;
}

/** Authenticated user derived from the JWT (backend has no profile endpoint). */
export interface AuthUser {
  id: number;
  email: string;
  role: 'user' | 'admin';
}

/** Cart item as returned by POST /add-to-cart and PATCH /cart-item/{id}. */
export interface ServerCartItem {
  id: number;
  cart_id: number;
  product_id: number;
  quantity: number;
  created_at: string;
  updated_at: string;
}

/**
 * Local cart line. The backend has no "fetch cart with items" endpoint,
 * so the cart is mirrored locally and synced where endpoints exist.
 * `serverItemId` is set once the backend acknowledges the line.
 */
export interface CartLine {
  product: Product;
  quantity: number;
  serverItemId: number | null;
}

export type SortOption = 'id-asc' | 'name-asc' | 'name-desc' | 'price-asc' | 'price-desc';

export interface ProductQuery {
  category?: string;
  customisable?: boolean;
  order_by?: 'id' | 'name' | 'price' | 'stock';
  order?: 'asc' | 'desc';
}
