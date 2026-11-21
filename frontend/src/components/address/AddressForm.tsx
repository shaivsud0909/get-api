import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { FormField } from '../ui/FormField';
import type { Address, AddressInput } from '../../types';

const required = (label: string) => z.string().trim().min(1, `${label} is required`);

const addressSchema = z.object({
  full_name: required('Full name'),
  phone: z.string().trim().min(5, 'At least 5 characters').max(20, 'At most 20 characters'),
  line1: required('Address line 1'),
  line2: z.string().optional(),
  city: required('City'),
  state: required('State'),
  postal_code: required('Postal code'),
  country: required('Country'),
});

type AddressValues = z.infer<typeof addressSchema>;

interface AddressFormProps {
  initial?: Address | null;
  submitLabel?: string;
  onSubmit: (input: AddressInput) => Promise<void>;
  onCancel?: () => void;
}

export function AddressForm({ initial, submitLabel = 'Save address', onSubmit, onCancel }: AddressFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<AddressValues>({
    resolver: zodResolver(addressSchema),
    defaultValues: {
      full_name: initial?.full_name ?? '',
      phone: initial?.phone ?? '',
      line1: initial?.line1 ?? '',
      line2: initial?.line2 ?? '',
      city: initial?.city ?? '',
      state: initial?.state ?? '',
      postal_code: initial?.postal_code ?? '',
      country: initial?.country ?? 'India',
    },
  });

  const submit = handleSubmit((values) =>
    onSubmit({ ...values, line2: values.line2?.trim() ? values.line2.trim() : null })
  );

  return (
    <form onSubmit={submit} className="grid gap-4 sm:grid-cols-2" noValidate>
      <FormField label="Full name" {...register('full_name')} error={errors.full_name?.message} />
      <FormField label="Phone" type="tel" {...register('phone')} error={errors.phone?.message} />
      <div className="sm:col-span-2">
        <FormField label="Address line 1" {...register('line1')} error={errors.line1?.message} />
      </div>
      <div className="sm:col-span-2">
        <FormField label="Address line 2 (optional)" {...register('line2')} />
      </div>
      <FormField label="City" {...register('city')} error={errors.city?.message} />
      <FormField label="State" {...register('state')} error={errors.state?.message} />
      <FormField label="Postal code" {...register('postal_code')} error={errors.postal_code?.message} />
      <FormField label="Country" {...register('country')} error={errors.country?.message} />
      <div className="flex gap-2 sm:col-span-2">
        <button className="btn-primary px-5 py-2 text-sm" disabled={isSubmitting}>
          {isSubmitting ? 'Saving…' : submitLabel}
        </button>
        {onCancel && (
          <button type="button" className="btn-ghost px-5 py-2 text-sm" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}

export function AddressLines({ address }: { address: AddressInput }) {
  return (
    <div className="text-sm text-forest-700">
      <p className="font-medium text-forest-900">{address.full_name}</p>
      <p>
        {address.line1}
        {address.line2 ? `, ${address.line2}` : ''}
      </p>
      <p>
        {address.city}, {address.state} {address.postal_code}, {address.country}
      </p>
      <p>{address.phone}</p>
    </div>
  );
}
