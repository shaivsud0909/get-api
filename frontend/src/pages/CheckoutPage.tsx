import { useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, CheckCircle2, Loader2, ShoppingBag } from 'lucide-react';
import { useCart } from '../context/CartContext';
import { useToast } from '../context/ToastContext';
import { getErrorMessage } from '../services/apiClient';
import * as orderService from '../services/orderService';
import { usePayment } from '../hooks/usePayment';
import { AddressBook } from '../components/address/AddressBook';
import { AddressLines } from '../components/address/AddressForm';
import { EmptyState } from '../components/ui/EmptyState';
import { formatPrice } from '../utils/format';
import type { Address, Order } from '../types';

export function CheckoutPage() {
  const { lines, subtotal, syncUnsyncedLines } = useCart();
  const { showToast } = useToast();
  const { state: payment, pay, busy } = usePayment();
  const [address, setAddress] = useState<Address | null>(null);
  const [order, setOrder] = useState<Order | null>(null);
  const [placing, setPlacing] = useState(false);

  if (payment.phase === 'confirmed') {
    return (
      <div className="container-px py-12">
        <EmptyState
          icon={CheckCircle2}
          title={`Order #${payment.order.id} confirmed`}
          description={`Thank you! We've received ${formatPrice(payment.order.total_amount)}.`}
          action={
            <Link to="/orders" className="btn-primary px-5 py-2 text-sm">
              View orders
            </Link>
          }
        />
      </div>
    );
  }

  if (lines.length === 0 && !order) {
    return (
      <div className="container-px py-12">
        <EmptyState
          icon={ShoppingBag}
          title="Your cart is empty"
          action={
            <Link to="/shop" className="btn-primary px-5 py-2 text-sm">
              Start shopping
            </Link>
          }
        />
      </div>
    );
  }

  const placeOrder = async () => {
    if (!address) {
      showToast('Choose a delivery address first.', 'error');
      return;
    }
    setPlacing(true);
    try {
      await syncUnsyncedLines();
      setOrder(await orderService.checkout(address.id));
    } catch (err) {
      showToast(getErrorMessage(err), 'error');
    } finally {
      setPlacing(false);
    }
  };

  // The server builds the order from its own cart, which can differ from the
  // local mirror (e.g. items removed locally — there's no delete endpoint).
  const mismatch =
    order !== null && Math.abs(order.total_amount - subtotal) > 0.009 && lines.length > 0;

  return (
    <div className="container-px grid gap-10 py-12 lg:grid-cols-[1fr_380px]">
      <section className="space-y-4">
        <h1 className="font-display text-3xl font-semibold text-forest-900">Checkout</h1>
        <h2 className="font-display text-xl font-semibold text-forest-900">Delivery address</h2>
        {order ? (
          <div className="rounded-2xl border border-forest-100 bg-white p-4">
            <AddressLines address={order.shipping_address} />
          </div>
        ) : (
          <AddressBook selectedId={address?.id ?? null} onSelect={setAddress} />
        )}
      </section>

      <aside className="h-fit space-y-4 rounded-3xl border border-forest-100 bg-white p-6">
        <h2 className="font-display text-xl font-semibold text-forest-900">
          {order ? `Order #${order.id}` : 'Order summary'}
        </h2>
        <ul className="space-y-2 text-sm">
          {order
            ? order.items.map((i, idx) => (
                <li key={idx} className="flex justify-between gap-2">
                  <span>
                    {i.product_name} × {i.quantity}
                  </span>
                  <span>{formatPrice(i.price * i.quantity)}</span>
                </li>
              ))
            : lines.map(({ product, quantity }) => (
                <li key={product.id} className="flex justify-between gap-2">
                  <span>
                    {product.name} × {quantity}
                  </span>
                  <span>{formatPrice(product.price * quantity)}</span>
                </li>
              ))}
        </ul>
        <p className="flex justify-between border-t border-forest-100 pt-3 text-lg">
          <span>Total</span>
          <strong>{formatPrice(order ? order.total_amount : subtotal)}</strong>
        </p>

        {mismatch && (
          <p className="flex gap-2 rounded-xl bg-amber-50 p-3 text-xs text-amber-800">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            This order was built from your saved server cart and differs from the cart shown
            on this device. Please review the items above before paying.
          </p>
        )}

        {(payment.phase === 'error' || payment.phase === 'pending') && (
          <p
            className={`rounded-xl p-3 text-sm ${
              payment.phase === 'error' ? 'bg-red-50 text-red-700' : 'bg-cream-100 text-clay-900'
            }`}
            role="alert"
          >
            {payment.message}
          </p>
        )}

        {!order ? (
          <button
            className="btn-primary w-full py-2.5"
            onClick={placeOrder}
            disabled={placing || !address}
          >
            {placing ? 'Placing order…' : 'Place order'}
          </button>
        ) : (
          <button className="btn-primary w-full py-2.5" onClick={() => pay(order.id)} disabled={busy}>
            {busy && <Loader2 className="h-4 w-4 animate-spin" />}
            {payment.phase === 'confirming'
              ? 'Confirming payment…'
              : busy
                ? 'Opening payment…'
                : `Pay ${formatPrice(order.total_amount)}`}
          </button>
        )}
        {order && (
          <p className="text-xs text-forest-500">
            Unpaid orders stay in <Link to="/orders" className="underline">your orders</Link> — you
            can pay for them later.
          </p>
        )}
      </aside>
    </div>
  );
}
