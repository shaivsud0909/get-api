/**
 * MISSING BACKEND FUNCTIONALITY — integration boundary.
 *
 * The FastAPI backend currently exposes no order, checkout or payment
 * endpoints. This module defines the boundary the UI talks to, so that
 * wiring in the real endpoints later only requires changes here.
 */

export class BackendNotImplementedError extends Error {
  constructor(feature: string) {
    super(
      `${feature} is not available yet — the backend does not expose this endpoint. ` +
        'Your cart has been saved.'
    );
    this.name = 'BackendNotImplementedError';
  }
}

export interface OrderSummary {
  id: number;
  created_at: string;
  total: number;
  status: string;
  payment_status: string;
}

/** Placeholder for a future POST /checkout (or similar) endpoint. */
export async function placeOrder(): Promise<never> {
  throw new BackendNotImplementedError('Order placement');
}

/** Placeholder for a future GET /orders endpoint. */
export async function fetchOrders(): Promise<OrderSummary[]> {
  throw new BackendNotImplementedError('Order history');
}
