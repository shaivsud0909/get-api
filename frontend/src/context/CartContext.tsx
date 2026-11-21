import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import type { CartLine, Product } from '../types';
import * as cartService from '../services/cartService';
import { getErrorMessage } from '../services/apiClient';
import { useAuth } from './AuthContext';
import { CART_STORAGE_KEY } from '../constants';

/**
 * The backend cannot return a cart with its items (see cartService), so the
 * cart of record lives here, persisted per-user in localStorage. Mutations
 * are synced to the backend where endpoints exist:
 *   - add       → POST /add-to-cart (authenticated users)
 *   - quantity  → PATCH /cart-item/{id} (when the line has a server id)
 *   - remove    → local only (no DELETE endpoint on the backend), so a
 *                 removed line may still be in the server cart at checkout.
 *                 The checkout page shows the server's order before payment.
 * The server empties its cart after a confirmed payment; call clearCart then.
 */

interface CartContextValue {
  lines: CartLine[];
  itemCount: number;
  subtotal: number;
  addItem: (product: Product, quantity: number) => Promise<void>;
  updateQuantity: (productId: number, quantity: number) => Promise<void>;
  removeItem: (productId: number) => void;
  clearCart: () => void;
  /** Push lines added while signed out to the server cart (needed before /checkout). */
  syncUnsyncedLines: () => Promise<void>;
}

const CartContext = createContext<CartContextValue | null>(null);

function storageKey(userId: number | null): string {
  return userId === null ? `${CART_STORAGE_KEY}_guest` : `${CART_STORAGE_KEY}_${userId}`;
}

function loadLines(userId: number | null): CartLine[] {
  try {
    const raw = localStorage.getItem(storageKey(userId));
    return raw ? (JSON.parse(raw) as CartLine[]) : [];
  } catch {
    return [];
  }
}

export function CartProvider({ children }: { children: ReactNode }) {
  const { user, isAuthenticated } = useAuth();
  const userId = user?.id ?? null;
  const [lines, setLines] = useState<CartLine[]>(() => loadLines(userId));

  // Swap carts when the signed-in user changes (login/logout).
  useEffect(() => {
    setLines(loadLines(userId));
  }, [userId]);

  useEffect(() => {
    try {
      localStorage.setItem(storageKey(userId), JSON.stringify(lines));
    } catch {
      // Storage unavailable (private mode etc.) — the in-memory cart still works.
    }
  }, [lines, userId]);

  const addItem = useCallback(
    async (product: Product, quantity: number) => {
      if (!Number.isInteger(quantity) || quantity < 1) {
        // The server doesn't validate this and returns 500 for 0 / negatives.
        throw new Error('Quantity must be at least 1.');
      }
      const existing = lines.find((l) => l.product.id === product.id);
      const nextQuantity = (existing?.quantity ?? 0) + quantity;
      if (nextQuantity > product.stock) {
        throw new Error('Requested quantity exceeds available stock.');
      }

      let serverItemId = existing?.serverItemId ?? null;
      if (isAuthenticated && user?.role === 'user') {
        try {
          const item = await cartService.addToCart(product.id, quantity);
          serverItemId = item.id;
        } catch (error) {
          throw new Error(getErrorMessage(error));
        }
      }

      setLines((prev) => {
        const idx = prev.findIndex((l) => l.product.id === product.id);
        if (idx === -1) {
          return [...prev, { product, quantity, serverItemId }];
        }
        return prev.map((l, i) =>
          i === idx ? { ...l, quantity: l.quantity + quantity, serverItemId } : l
        );
      });
    },
    [lines, isAuthenticated, user]
  );

  const updateQuantity = useCallback(
    async (productId: number, quantity: number) => {
      const line = lines.find((l) => l.product.id === productId);
      if (!line || quantity < 1) return;
      if (quantity > line.product.stock) {
        throw new Error('Requested quantity exceeds available stock.');
      }

      if (isAuthenticated && line.serverItemId !== null) {
        try {
          await cartService.updateCartItem(line.serverItemId, quantity);
        } catch (error) {
          throw new Error(getErrorMessage(error));
        }
      }

      setLines((prev) =>
        prev.map((l) => (l.product.id === productId ? { ...l, quantity } : l))
      );
    },
    [lines, isAuthenticated]
  );

  // Local only: the backend exposes no endpoint to delete a cart item.
  const removeItem = useCallback((productId: number) => {
    setLines((prev) => prev.filter((l) => l.product.id !== productId));
  }, []);

  const clearCart = useCallback(() => setLines([]), []);

  const syncUnsyncedLines = useCallback(async () => {
    if (!isAuthenticated || user?.role !== 'user') return;
    const pending = lines.filter((l) => l.serverItemId === null);
    for (const line of pending) {
      try {
        const item = await cartService.addToCart(line.product.id, line.quantity);
        setLines((prev) =>
          prev.map((l) => (l.product.id === line.product.id ? { ...l, serverItemId: item.id } : l))
        );
      } catch (error) {
        throw new Error(`${line.product.name}: ${getErrorMessage(error)}`);
      }
    }
  }, [lines, isAuthenticated, user]);

  const { itemCount, subtotal } = useMemo(
    () => ({
      itemCount: lines.reduce((sum, l) => sum + l.quantity, 0),
      subtotal: lines.reduce((sum, l) => sum + l.quantity * l.product.price, 0),
    }),
    [lines]
  );

  const value = useMemo(
    () => ({
      lines,
      itemCount,
      subtotal,
      addItem,
      updateQuantity,
      removeItem,
      clearCart,
      syncUnsyncedLines,
    }),
    [lines, itemCount, subtotal, addItem, updateQuantity, removeItem, clearCart, syncUnsyncedLines]
  );

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart(): CartContextValue {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error('useCart must be used within CartProvider');
  return ctx;
}
