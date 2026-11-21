import { apiClient } from './apiClient';
import type { Address, AddressInput, ApiEnvelope } from '../types';

/** GET /addresses — default first, then newest. */
export async function fetchAddresses(): Promise<Address[]> {
  const { data } = await apiClient.get<ApiEnvelope<Address[]>>('/addresses');
  return data.data;
}

/** POST /addresses — the first address becomes the default automatically. */
export async function createAddress(input: AddressInput): Promise<Address> {
  const { data } = await apiClient.post<ApiEnvelope<Address>>('/addresses', normalise(input));
  return data.data;
}

/** PUT /addresses/{id} — partial update despite the verb. */
export async function updateAddress(id: number, input: Partial<AddressInput>): Promise<Address> {
  const { data } = await apiClient.put<ApiEnvelope<Address>>(`/addresses/${id}`, normalise(input));
  return data.data;
}

/** PATCH /addresses/{id}/select — make this the default address. */
export async function selectDefaultAddress(id: number): Promise<Address> {
  const { data } = await apiClient.patch<ApiEnvelope<Address>>(`/addresses/${id}/select`);
  return data.data;
}

/** DELETE /addresses/{id} */
export async function deleteAddress(id: number): Promise<void> {
  await apiClient.delete(`/addresses/${id}`);
}

function normalise<T extends Partial<AddressInput>>(input: T): T {
  return { ...input, line2: input.line2?.trim() ? input.line2 : null };
}
