import { apiClient } from './apiClient';
import type { ApiEnvelope, Order, PaymentInit } from '../types';

/**
 * Checkout flow (see CLAUDE.md):
 *   1. POST /checkout { address_id }      → Order (pending_payment)
 *   2. POST /payments/initiate { order_id } → PaymentInit (safe to retry)
 *   3. Open Razorpay Checkout
 *   4. Poll GET /orders/{id} until "confirmed" (set by Razorpay's webhook —
 *      the frontend never calls /payments/webhook).
 */

/** POST /checkout — turns the whole server-side cart into an order. */
export async function checkout(addressId: number): Promise<Order> {
  const { data } = await apiClient.post<ApiEnvelope<Order>>('/checkout', { address_id: addressId });
  return data.data;
}

/** GET /orders — newest first. */
export async function fetchOrders(): Promise<Order[]> {
  const { data } = await apiClient.get<ApiEnvelope<Order[]>>('/orders');
  return data.data;
}

/** GET /orders/{id} */
export async function fetchOrder(orderId: number): Promise<Order> {
  const { data } = await apiClient.get<ApiEnvelope<Order>>(`/orders/${orderId}`);
  return data.data;
}

/** POST /payments/initiate — returns the same Razorpay order for an unpaid order. */
export async function initiatePayment(orderId: number): Promise<PaymentInit> {
  const { data } = await apiClient.post<ApiEnvelope<PaymentInit>>('/payments/initiate', {
    order_id: orderId,
  });
  return data.data;
}

/** Poll GET /orders/{id} until confirmed or the timeout passes. */
export async function pollOrderUntilConfirmed(
  orderId: number,
  { intervalMs = 2000, timeoutMs = 30000 } = {}
): Promise<Order> {
  const deadline = Date.now() + timeoutMs;
  let order = await fetchOrder(orderId);
  while (order.status !== 'confirmed' && Date.now() < deadline) {
    await new Promise((r) => setTimeout(r, intervalMs));
    order = await fetchOrder(orderId);
  }
  return order;
}

// ---------------------------------------------------------------------------
// Razorpay Checkout
// ---------------------------------------------------------------------------

interface RazorpayOptions {
  key: string;
  amount: number;
  currency: string;
  order_id: string;
  name?: string;
  description?: string;
  prefill?: { email?: string };
  handler: () => void;
  modal?: { ondismiss?: () => void };
}

interface RazorpayInstance {
  open: () => void;
  on: (event: 'payment.failed', cb: (resp: { error?: { description?: string } }) => void) => void;
}

declare global {
  interface Window {
    Razorpay?: new (options: RazorpayOptions) => RazorpayInstance;
  }
}

const RAZORPAY_SRC = 'https://checkout.razorpay.com/v1/checkout.js';
let razorpayPromise: Promise<void> | null = null;

function loadRazorpay(): Promise<void> {
  if (window.Razorpay) return Promise.resolve();
  if (!razorpayPromise) {
    razorpayPromise = new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = RAZORPAY_SRC;
      script.async = true;
      script.onload = () => resolve();
      script.onerror = () => {
        razorpayPromise = null;
        reject(new Error('Could not load the payment gateway. Please try again.'));
      };
      document.body.appendChild(script);
    });
  }
  return razorpayPromise;
}

export type PaymentOutcome = 'paid' | 'dismissed' | 'failed';

/**
 * Open Razorpay Checkout for a PaymentInit. Resolves when the handler fires
 * ("paid" — still needs webhook confirmation via polling), the modal is closed,
 * or the payment fails.
 */
export async function openRazorpayCheckout(
  init: PaymentInit,
  opts: { name?: string; email?: string } = {}
): Promise<{ outcome: PaymentOutcome; reason?: string }> {
  await loadRazorpay();
  const Razorpay = window.Razorpay;
  if (!Razorpay) throw new Error('Payment gateway unavailable.');

  return new Promise((resolve) => {
    let settled = false;
    const settle = (outcome: PaymentOutcome, reason?: string) => {
      if (settled) return;
      settled = true;
      resolve({ outcome, reason });
    };
    const rzp = new Razorpay({
      key: init.key_id,
      amount: init.amount, // paise
      currency: init.currency,
      order_id: init.gateway_order_id,
      name: opts.name,
      description: `Order #${init.order_id}`,
      prefill: opts.email ? { email: opts.email } : undefined,
      handler: () => settle('paid'),
      modal: {
        ondismiss: () => (lastFailure !== null ? settle('failed', lastFailure) : settle('dismissed')),
      },
    });
    // Razorpay keeps the modal open after a failed attempt so the user can retry;
    // remember the reason and report it only if they close the modal.
    let lastFailure: string | null = null;
    rzp.on('payment.failed', (resp) => {
      lastFailure = resp.error?.description ?? 'Payment failed';
    });
    rzp.open();
  });
}
