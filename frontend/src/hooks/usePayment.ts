import { useCallback, useState } from 'react';
import * as orderService from '../services/orderService';
import { getErrorMessage } from '../services/apiClient';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';
import { BRAND_NAME } from '../constants';
import type { Order } from '../types';

export type PaymentState =
  | { phase: 'idle' }
  | { phase: 'starting' }
  | { phase: 'awaiting_gateway' }
  | { phase: 'confirming' }
  | { phase: 'confirmed'; order: Order }
  | { phase: 'pending'; message: string }
  | { phase: 'error'; message: string };

/**
 * Runs steps 2–4 of the checkout flow for an existing order:
 * initiate → Razorpay Checkout → poll GET /orders/{id} until the webhook confirms it.
 */
export function usePayment() {
  const { user } = useAuth();
  const { clearCart } = useCart();
  const [state, setState] = useState<PaymentState>({ phase: 'idle' });

  const pay = useCallback(
    async (orderId: number): Promise<Order | null> => {
      setState({ phase: 'starting' });
      try {
        const init = await orderService.initiatePayment(orderId);
        setState({ phase: 'awaiting_gateway' });
        const { outcome, reason } = await orderService.openRazorpayCheckout(init, {
          name: BRAND_NAME,
          email: user?.email,
        });
        if (outcome === 'dismissed') {
          setState({ phase: 'idle' });
          return null;
        }
        if (outcome === 'failed') {
          setState({ phase: 'error', message: reason ?? 'Payment failed. You can try again.' });
          return null;
        }

        setState({ phase: 'confirming' });
        const order = await orderService.pollOrderUntilConfirmed(orderId);
        if (order.status === 'confirmed') {
          // The server empties its cart on confirmation; mirror that locally.
          clearCart();
          setState({ phase: 'confirmed', order });
          return order;
        }
        setState({
          phase: 'pending',
          message:
            'We received your payment but are still waiting for confirmation. Check your orders in a minute.',
        });
        return order;
      } catch (err) {
        setState({ phase: 'error', message: getErrorMessage(err) });
        return null;
      }
    },
    [user?.email, clearCart]
  );

  const busy =
    state.phase === 'starting' || state.phase === 'awaiting_gateway' || state.phase === 'confirming';

  return { state, pay, busy, reset: () => setState({ phase: 'idle' }) };
}
