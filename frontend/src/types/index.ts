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

export type Role = 'user' | 'admin';

/** Response of POST /signup (raw user object, not wrapped). */
export interface SignupResponse {
  id: number;
  email: string;
  phone_number: string | null;
  country_code: string | null;
  role: Role;
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

export interface ProductFeature {
  id: number;
  product_id: number;
  key: string;
  value: string;
  detailed_description: string | null;
}

/** NOTE: the backend currently stores only a file name in image_url, not a hosted URL. */
export interface ProductImage {
  image_url: string;
  alt_text: string | null;
}

/** GET /products/{id} (plural) — features + images, NOT the product itself. */
export interface ProductDetails {
  features: ProductFeature[];
  images: ProductImage[];
}

export interface Review {
  id: number;
  user_id: number;
  product_id: number;
  rating: number;
  comment: string | null;
  created_at: string;
  updated_at: string;
}

export interface Address {
  id: number;
  user_id: number;
  full_name: string;
  phone: string;
  line1: string;
  line2: string | null;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export type AddressInput = Omit<Address, 'id' | 'user_id' | 'is_default' | 'created_at' | 'updated_at'>;
export type ShippingAddress = AddressInput;

export type OrderStatus = 'pending_payment' | 'confirmed';

export interface OrderItem {
  /** null if the product was deleted after the order was placed. */
  product_id: number | null;
  product_name: string;
  price: number;
  quantity: number;
}

export interface Order {
  id: number;
  /** Major units (rupees). */
  total_amount: number;
  currency: string;
  status: OrderStatus;
  shipping_address: ShippingAddress;
  created_at: string;
  items: OrderItem[];
}

export interface PaymentInit {
  order_id: number;
  payment_id: number;
  gateway: 'razorpay';
  /** Pass as `order_id` to Razorpay Checkout. */
  gateway_order_id: string;
  key_id: string;
  /** MINOR units (paise). */
  amount: number;
  currency: string;
}

export type SortOption = 'id-asc' | 'name-asc' | 'name-desc' | 'price-asc' | 'price-desc';

export interface ProductQuery {
  category?: string;
  customisable?: boolean;
  order_by?: 'id' | 'name' | 'price' | 'stock';
  order?: 'asc' | 'desc';
}
