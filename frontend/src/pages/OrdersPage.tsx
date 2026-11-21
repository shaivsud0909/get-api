import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ClipboardList, Loader2 } from 'lucide-react';
import { fetchOrders } from '../services/orderService';
import { getErrorMessage } from '../services/apiClient';
import { useToast } from '../context/ToastContext';
import { usePayment } from '../hooks/usePayment';
import { AddressLines } from '../components/address/AddressForm';
import { EmptyState } from '../components/ui/EmptyState';
import { Spinner } from '../components/ui/Spinner';
import { formatDate, formatPrice } from '../utils/format';
import type { Order, OrderStatus } from '../types';

const STATUS_LABEL: Record<OrderStatus, { text: string; cls: string }> = {
  pending_payment: { text: 'Awaiting payment', cls: 'bg-amber-100 text-amber-800' },
  confirmed: { text: 'Confirmed', cls: 'bg-forest-100 text-forest-800' },
};

export function OrdersPage() {
  const { showToast } = useToast();
  const { state: payment, pay, busy } = usePayment();
  const [orders, setOrders] = useState<Order[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [payingId, setPayingId] = useState<number | null>(null);

  const load = useCallback(() => {
    fetchOrders()
      .then(setOrders)
      .catch((e) => setError(getErrorMessage(e)));
  }, []);

  useEffect(load, [load]);

  useEffect(() => {
    if (payment.phase === 'confirmed') showToast(`Order #${payment.order.id} confirmed`, 'success');
    if (payment.phase === 'error' || payment.phase === 'pending') showToast(payment.message, 'info');
  }, [payment, showToast]);

  const payNow = async (orderId: number) => {
    setPayingId(orderId);
    await pay(orderId);
    setPayingId(null);
    load();
  };

  return (
    <div className="container-px space-y-6 py-12">
      <h1 className="font-display text-3xl font-semibold text-forest-900">Your orders</h1>
      {error && <EmptyState icon={ClipboardList} title="Orders unavailable" description={error} />}
      {!error && !orders && <Spinner />}
      {orders && orders.length === 0 && (
        <EmptyState
          icon={ClipboardList}
          title="No orders yet"
          action={
            <Link to="/shop" className="btn-primary px-5 py-2 text-sm">
              Start shopping
            </Link>
          }
        />
      )}
      {orders && orders.length > 0 && (
        <ul className="space-y-4">
          {orders.map((o) => {
            const status = STATUS_LABEL[o.status] ?? { text: o.status, cls: 'bg-forest-50' };
            return (
              <li key={o.id} className="space-y-3 rounded-2xl border border-forest-100 bg-white p-5">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <p className="font-medium text-forest-900">Order #{o.id}</p>
                    <p className="text-xs text-forest-500">{formatDate(o.created_at)}</p>
                  </div>
                  <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${status.cls}`}>
                    {status.text}
                  </span>
                </div>
                <ul className="space-y-1 text-sm text-forest-700">
                  {o.items.map((i, idx) => (
                    <li key={idx} className="flex justify-between gap-2">
                      <span>
                        {i.product_id !== null ? (
                          <Link to={`/products/${i.product_id}`} className="hover:underline">
                            {i.product_name}
                          </Link>
                        ) : (
                          i.product_name
                        )}{' '}
                        × {i.quantity}
                      </span>
                      <span>{formatPrice(i.price * i.quantity)}</span>
                    </li>
                  ))}
                </ul>
                <details className="text-sm">
                  <summary className="cursor-pointer text-forest-600">Shipping address</summary>
                  <div className="mt-2">
                    <AddressLines address={o.shipping_address} />
                  </div>
                </details>
                <div className="flex flex-wrap items-center justify-between gap-2 border-t border-forest-100 pt-3">
                  <p>
                    Total <strong>{formatPrice(o.total_amount)}</strong>
                  </p>
                  {o.status === 'pending_payment' && (
                    <button
                      className="btn-primary px-5 py-2 text-sm"
                      disabled={busy}
                      onClick={() => payNow(o.id)}
                    >
                      {payingId === o.id && busy && <Loader2 className="h-4 w-4 animate-spin" />}
                      {payingId === o.id && payment.phase === 'confirming' ? 'Confirming…' : 'Pay now'}
                    </button>
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
