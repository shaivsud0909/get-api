import { useEffect, useState } from 'react';
import { ClipboardList } from 'lucide-react';
import { fetchOrders } from '../services/orderService';
import type { OrderSummary } from '../services/orderService';
import { getErrorMessage } from '../services/apiClient';
import { EmptyState } from '../components/ui/EmptyState';
import { Spinner } from '../components/ui/Spinner';
import { formatDate, formatPrice } from '../utils/format';

export function OrdersPage() {
  const [orders, setOrders] = useState<OrderSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchOrders().then(setOrders).catch((e) => setError(getErrorMessage(e)));
  }, []);

  return (
    <div className="container-px space-y-6 py-12">
      <h1 className="font-display text-3xl font-semibold text-forest-900">Your orders</h1>
      {error && <EmptyState icon={ClipboardList} title="Orders unavailable" description={error} />}
      {!error && !orders && <Spinner />}
      {orders && orders.length === 0 && <EmptyState icon={ClipboardList} title="No orders yet" />}
      {orders && orders.length > 0 && (
        <ul className="space-y-3">
          {orders.map((o) => (
            <li key={o.id} className="rounded-2xl border border-forest-100 bg-white p-4">
              #{o.id} · {formatDate(o.created_at)} · {formatPrice(o.total)} · {o.status}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
