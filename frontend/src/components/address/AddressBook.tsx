import { useCallback, useEffect, useState } from 'react';
import { MapPin, Pencil, Plus, Trash2 } from 'lucide-react';
import * as addressService from '../../services/addressService';
import { getErrorMessage } from '../../services/apiClient';
import { useToast } from '../../context/ToastContext';
import { Spinner } from '../ui/Spinner';
import { AddressForm, AddressLines } from './AddressForm';
import type { Address } from '../../types';

interface AddressBookProps {
  /** When set, addresses become selectable (checkout). */
  selectedId?: number | null;
  onSelect?: (address: Address) => void;
}

/** Lists, creates, edits, deletes and sets the default address. */
export function AddressBook({ selectedId, onSelect }: AddressBookProps) {
  const { showToast } = useToast();
  const [addresses, setAddresses] = useState<Address[] | null>(null);
  const [editing, setEditing] = useState<Address | 'new' | null>(null);

  const reload = useCallback(async () => {
    try {
      const list = await addressService.fetchAddresses();
      setAddresses(list);
      if (list.length === 0) setEditing('new');
      return list;
    } catch (err) {
      showToast(getErrorMessage(err), 'error');
      setAddresses([]);
      return [];
    }
  }, [showToast]);

  useEffect(() => {
    reload().then((list) => {
      // Preselect the default address (the server returns it first).
      if (onSelect && selectedId == null && list[0]) onSelect(list[0]);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const run = async (fn: () => Promise<unknown>, success: string) => {
    try {
      await fn();
      showToast(success, 'success');
      await reload();
    } catch (err) {
      showToast(getErrorMessage(err), 'error');
    }
  };

  if (!addresses) return <Spinner label="Loading addresses…" />;

  return (
    <div className="space-y-3">
      {addresses.map((a) =>
        editing !== 'new' && editing?.id === a.id ? (
          <div key={a.id} className="rounded-2xl border border-forest-200 bg-white p-4">
            <AddressForm
              initial={a}
              onCancel={() => setEditing(null)}
              onSubmit={async (input) => {
                try {
                  await addressService.updateAddress(a.id, input);
                  setEditing(null);
                  showToast('Address updated', 'success');
                  await reload();
                } catch (err) {
                  showToast(getErrorMessage(err), 'error');
                }
              }}
            />
          </div>
        ) : (
          <div
            key={a.id}
            className={`flex items-start gap-3 rounded-2xl border bg-white p-4 ${
              selectedId === a.id ? 'border-forest-600 ring-2 ring-forest-200' : 'border-forest-100'
            }`}
          >
            {onSelect ? (
              <input
                type="radio"
                name="address"
                className="mt-1"
                checked={selectedId === a.id}
                onChange={() => onSelect(a)}
                aria-label={`Ship to ${a.full_name}, ${a.line1}`}
              />
            ) : (
              <MapPin className="mt-0.5 h-4 w-4 text-forest-500" />
            )}
            <div className="flex-1">
              <AddressLines address={a} />
              {a.is_default ? (
                <span className="mt-2 inline-block rounded-full bg-forest-100 px-2 py-0.5 text-xs text-forest-700">
                  Default
                </span>
              ) : (
                <button
                  className="mt-2 text-xs font-medium text-forest-700 underline"
                  onClick={() => run(() => addressService.selectDefaultAddress(a.id), 'Default address updated')}
                >
                  Make default
                </button>
              )}
            </div>
            <div className="flex gap-2">
              <button onClick={() => setEditing(a)} aria-label="Edit address">
                <Pencil className="h-4 w-4 text-forest-600" />
              </button>
              <button
                onClick={() =>
                  window.confirm('Delete this address?') &&
                  run(() => addressService.deleteAddress(a.id), 'Address deleted')
                }
                aria-label="Delete address"
              >
                <Trash2 className="h-4 w-4 text-red-500" />
              </button>
            </div>
          </div>
        )
      )}

      {editing === 'new' ? (
        <div className="rounded-2xl border border-forest-200 bg-white p-4">
          <AddressForm
            submitLabel="Add address"
            onCancel={addresses.length > 0 ? () => setEditing(null) : undefined}
            onSubmit={async (input) => {
              try {
                const created = await addressService.createAddress(input);
                setEditing(null);
                showToast('Address added', 'success');
                await reload();
                onSelect?.(created);
              } catch (err) {
                showToast(getErrorMessage(err), 'error');
              }
            }}
          />
        </div>
      ) : (
        <button className="btn-secondary px-4 py-2 text-sm" onClick={() => setEditing('new')}>
          <Plus className="h-4 w-4" /> Add a new address
        </button>
      )}
    </div>
  );
}
