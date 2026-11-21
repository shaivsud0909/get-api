# Backend API reference (get-api)

This frontend talks to the **get-api** backend: a FastAPI + PostgreSQL e-commerce API
(products, cart, addresses, orders, Razorpay payments, reviews). This file is the
contract the frontend codes against. It was written from the backend source on
2026-11-21. If something here disagrees with live behaviour, the live
OpenAPI spec at `GET /openapi.json` (or the Swagger UI at `/docs`) wins.

## Connection

- Base URL (local): `http://localhost:8000` (`python app.py` or `docker compose up`)
- All paths are at the root; there is **no `/api` or version prefix**, except `/config/*`.
- CORS allows any origin, method and header.
- Request bodies are JSON (`Content-Type: application/json`) unless noted.
  The one exception is the admin image upload, which takes `multipart/form-data`.

## Authentication

- `POST /signup` creates a normal user. Admins can't sign up through the API;
  they are created server-side with `scripts/create_admin.py`.
- `POST /login` takes a **JSON body** `{ email, password }`, not a form, and returns
  `{ access_token, token_type: "bearer" }`.
- Send the token on every protected call: `Authorization: Bearer <access_token>`.
- The token is a JWT (HS256). Its payload is
  `{ sub: "<user id as string>", email, role: "user" | "admin", exp }`.
  Decode it client-side (for example with `jwt-decode`) to read the role and the expiry.
  Don't verify it on the client.
- Tokens expire after **30 minutes** by default. **There's no refresh endpoint**:
  on a 401, clear the token and send the user to login.
- Roles are **exclusive**. User routes reject admin tokens with 403 and admin routes reject
  user tokens with 403. An admin can't use the shop endpoints, and the reverse is also true.
- Emails are lower-cased by the server. Passwords are 8–128 characters at signup.

## Response envelope

Most endpoints wrap their result:

```json
{ "status": "success", "message": "Products fetched successfully", "data": <payload> }
```

**Exceptions (not wrapped):** `POST /signup` and `POST /login` return their payload directly.

### Errors

Errors are not wrapped. Read `detail`:

| Status | When | Body |
|---|---|---|
| 400 | Business rule failed (stock, empty cart, no fields to update, order not payable) | `{ "detail": "Insufficient product stock" }` |
| 401 | Missing, invalid or expired token; bad login | `{ "detail": "Not authenticated" }` / `"Invalid or expired token"` / `"Invalid email or password"` |
| 403 | Wrong role, or the account is inactive | `{ "detail": "User access only" }` / `"Admin only access"` / `"Account is inactive"` |
| 404 | Resource missing, or not owned by the current user | `{ "detail": "Order not found" }` |
| 409 | Signup with an email that is already registered | `{ "detail": "Email already registered" }` |
| 422 | Request validation failed | `{ "detail": [ { "loc": [...], "msg": "...", "type": "..." } ] }` (array) |
| 500 | Unhandled error | `{ "detail": { "error": "<exception text>", "message": "Failed to ..." } }` (object) |
| 502 / 503 | Razorpay rejected the request / isn't configured | `{ "detail": "..." }` |

`detail` can be a **string, an array (422) or an object (500)**. Normalise it in one place:

```ts
function errorMessage(body: any): string {
  const d = body?.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) return d.map((e) => e.msg).join(", ");
  if (d && typeof d === "object") return d.message ?? "Something went wrong";
  return "Something went wrong";
}
```

## Types

```ts
type Envelope<T> = { status: "success"; message: string; data: T };

type Role = "user" | "admin";

interface User {               // returned by /signup
  id: number; email: string; phone_number: string | null; country_code: string | null;
  role: Role; is_active: boolean; is_verified: boolean;
  created_at: string; updated_at: string; last_login_at: string | null; // ISO 8601 timestamps
}

interface Product {
  id: number; name: string; price: number; stock: number;
  category: string;            // default "Uncategorized"
  description: string | null; customisable: boolean;
}

interface ProductFeature {     // a key/value spec row, e.g. { key: "Material", value: "Cotton" }
  id: number; product_id: number; key: string; value: string; detailed_description: string | null;
}

interface ProductImage { image_url: string; alt_text: string | null }

interface ProductDetails { features: ProductFeature[]; images: ProductImage[] }

interface CartItem {
  id: number; cart_id: number; product_id: number; quantity: number;
  created_at: string; updated_at: string;
}

interface Address {
  id: number; user_id: number;
  full_name: string; phone: string; line1: string; line2: string | null;
  city: string; state: string; postal_code: string; country: string;
  is_default: boolean; created_at: string; updated_at: string;
}

type ShippingAddress = Omit<Address, "id" | "user_id" | "is_default" | "created_at" | "updated_at">;

type OrderStatus = "pending_payment" | "confirmed";

interface Order {
  id: number; total_amount: number;      // major units, e.g. 499.50 rupees
  currency: string;                      // "INR"
  status: OrderStatus;
  shipping_address: ShippingAddress;     // a snapshot taken at checkout
  created_at: string;
  items: { product_id: number | null; product_name: string; price: number; quantity: number }[];
}

interface PaymentInit {
  order_id: number; payment_id: number; gateway: "razorpay";
  gateway_order_id: string;              // pass as `order_id` to Razorpay Checkout
  key_id: string;                        // Razorpay public key
  amount: number;                        // MINOR units (paise): 49950 = ₹499.50
  currency: string;
}

interface Review {
  id: number; user_id: number; product_id: number;
  rating: number;                        // 1–5
  comment: string | null;
  created_at: string; updated_at: string;
}
```

Order item `product_id` is `null` if the product was deleted later. `product_name` and `price` are
snapshots taken when the order was placed.

## Endpoints

Columns: **Auth** is `—` (public), `user` or `admin`. **Returns** is the type of the envelope's `data`.

### Auth (public)

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/signup` | `{ email, password (8–128), phone_number?, country_code? }` | `User` (no envelope) |
| POST | `/login` | `{ email, password }` | `{ access_token, token_type }` (no envelope) |

### Shop: products and reviews (role `user`)

| Method | Path | Body / query | Returns |
|---|---|---|---|
| GET | `/products` | query: `category?` (case-insensitive exact match), `customisable?` (bool), `order_by?` = `id`\|`name`\|`price`\|`stock` (default `id`), `order?` = `asc`\|`desc` | `Product[]` |
| GET | `/customisable-products` | same query params; `customisable` defaults to `true` | `Product[]` |
| GET | `/product/{product_id}` (**singular**) | — | `Product` |
| GET | `/products/{product_id}` (**plural**) | — | `ProductDetails` (features + images, **not** the product itself) |
| GET | `/products/{product_id}/reviews` | — | `Review[]` |
| POST | `/products/{product_id}/reviews` | `{ rating: 1–5, comment?: ≤500 chars }` | `Review` |
| GET | `/reviews/{review_id}` | — | `Review` |
| PUT | `/reviews/{review_id}` | `{ rating?, comment? }` (only fields you send are changed; own reviews only) | `Review` |
| DELETE | `/reviews/{review_id}` | — (own reviews only) | `{ id }` |

There is no pagination, text search or price filter. Lists return every matching row.
A product page needs **two calls**: `/product/{id}` for the product and `/products/{id}` for its
features and images.

### Cart (role `user`)

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/add-to-cart` | `{ product_id, quantity }` | `CartItem` |
| PATCH | `/cart-item/{item_id}` | `{ quantity ≥ 1 }` (sets an absolute quantity) | `CartItem` |
| GET | `/cart` | — | Cart row `{ id, user_id, created_at, updated_at }` (see warning) |

- `/add-to-cart` **creates the cart automatically** and **adds to** the existing quantity if the
  product is already in the cart. It fails with 400 if the total would exceed stock.
- ⚠️ `GET /cart` doesn't read the cart: it **creates** one. The first call works. After that it
  fails with 500, because each user can only have one cart. **Don't call it.**
- ⚠️ No endpoint lists the cart's items, and none removes an item. Until the backend adds
  them, keep cart state on the client: store the `CartItem` returned by each add/update and
  join it with `Product` data. The server clears the cart after a successful payment.
- Send `quantity ≥ 1` to `/add-to-cart`. The server doesn't validate it, so 0 or a negative
  number gives a 500.

### Addresses (role `user`)

| Method | Path | Body | Returns |
|---|---|---|---|
| GET | `/addresses` | — | `Address[]` (default first, then newest) |
| POST | `/addresses` | `{ full_name, phone (5–20), line1, line2?, city, state, postal_code, country }` | `Address` |
| PUT | `/addresses/{address_id}` | any subset of the create fields (partial update, despite PUT) | `Address` |
| PATCH | `/addresses/{address_id}/select` | — | `Address` (now `is_default: true`) |
| DELETE | `/addresses/{address_id}` | — | `{ id }` |

A user's first address becomes the default automatically. If the default is deleted, the newest
remaining address becomes the default.

### Orders and payments (role `user`)

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/checkout` | `{ address_id }` | `Order` (status `pending_payment`) |
| GET | `/orders` | — | `Order[]` (newest first) |
| GET | `/orders/{order_id}` | — | `Order` |
| POST | `/payments/initiate` | `{ order_id }` | `PaymentInit` |

**Checkout flow:**

1. `POST /checkout { address_id }`. The server turns the whole server-side cart into an order.
   It fails with 400 `"Cart is empty"` or `"Insufficient stock for <name>"`. Stock isn't reserved
   at this point, and the cart isn't cleared yet.
2. `POST /payments/initiate { order_id }` returns `PaymentInit`. Calling it again for the same
   unpaid order returns the same Razorpay order, so retrying is safe.
3. Open Razorpay Checkout (`https://checkout.razorpay.com/v1/checkout.js`):
   ```js
   new Razorpay({
     key: init.key_id, amount: init.amount, currency: init.currency,
     order_id: init.gateway_order_id,
     handler: () => pollOrder(init.order_id),
   }).open();
   ```
4. **The order is confirmed only by Razorpay's server-to-server webhook**
   (`POST /payments/webhook`). The frontend must never call that endpoint. No endpoint verifies
   the Checkout handler's response. After the handler fires, **poll `GET /orders/{id}`**
   (for example every 2 s for about 30 s) until `status === "confirmed"`. Confirmation also
   reduces stock and empties the cart.
5. If a payment fails, the order stays `pending_payment` and the user can retry from step 2.

`Order.total_amount` is in rupees. `PaymentInit.amount` is in paise. Don't mix them up when
displaying prices.

### Admin (role `admin`)

| Method | Path | Body / query | Returns |
|---|---|---|---|
| GET | `/fetch-products` | same query params as `/products` | `Product[]` |
| POST | `/add-products` | `{ name (1–100), price ≥ 0, stock? ≥ 0, category? ≤ 50, description? ≤ 300, customisable? }` | `Product` |
| PATCH | `/products/{product_id}` | any subset of the fields above (at least one, or 400) | `Product` |
| DELETE | `/products/{product_id}` | — | `null` (cascades to features, images, reviews and cart items) |
| GET | `/products-feature/{product_id}` | — | `ProductDetails` |
| POST | `/products-feature/{product_id}` | `{ key (1–100), value (1–300), detailed_description? ≤ 1000 }` | `ProductFeature` |
| PUT | `/products-feature/{product_id}/{feature_id}` | same body (replaces all three fields) | `ProductFeature` |
| DELETE | `/products-feature/{product_id}?feature_id=<id>` | `feature_id` is a **query param** here | `{ detail }` |
| POST | `/product-images/{product_id}?alt_text=&is_primary=&sort_order=` | multipart form, field `image` (file) | image row |

Admin notes:

- ⚠️ **These admin paths don't work.** Matching user routes are registered first, so an admin
  token gets **403 "User access only"** on:
  `GET /products/{id}`, `GET /products/{id}/reviews`, `GET /reviews/{id}`, `DELETE /reviews/{id}`.
  Workarounds: get one product from the `/fetch-products` list, and get features with
  `GET /products-feature/{id}`. Admins currently can't read or moderate reviews.
- ⚠️ **The image upload is broken right now.** It returns 500 because of a parameter mismatch in
  the backend. It also stores only the file **name** in `image_url`, not a hosted URL, so you can't
  render images from it yet. `alt_text` is a required query param, even if empty.
- A feature `key` must be unique per product. A duplicate gives 500, not 409.

### Ops (public, `/config` prefix)

`GET /config/health` returns `{ "status": "ok" }`. The other `/config/*` routes are
server debugging tools, and the UI shouldn't use them.

## Known server-side gotchas that affect the UI

- Expect 500 instead of a friendly 4xx for:
  - a second review of the same product by the same user (one review per user per product)
  - a review on a product id that doesn't exist
  - a duplicate feature key
  - `GET /cart` called twice

  Check for the first two in the UI where possible: hide "write a review" if the user already
  has one.
- `PUT /reviews/{id}` with `"rating": null` gives 500. Leave the field out instead of sending null.
- Reviews don't include the reviewer's name or email, only `user_id`.
- Nothing returns the current user's profile. Use the JWT payload: `sub`, `email`, `role`.
- No logout endpoint. Logging out means dropping the token on the client.
- Product prices are floats. Format them with `Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" })`.
