import { apiClient } from './apiClient';
import type { ApiEnvelope, Review } from '../types';

export interface ReviewInput {
  rating: number;
  comment?: string;
}

/** GET /products/{id}/reviews — shared: users and admins. */
export async function fetchReviews(productId: number): Promise<Review[]> {
  const { data } = await apiClient.get<ApiEnvelope<Review[]>>(`/products/${productId}/reviews`);
  return data.data;
}

/**
 * POST /products/{id}/reviews. One review per user per product — a second one
 * returns 500, so the UI hides the form when the user already has a review.
 */
export async function createReview(productId: number, input: ReviewInput): Promise<Review> {
  const { data } = await apiClient.post<ApiEnvelope<Review>>(
    `/products/${productId}/reviews`,
    stripEmpty(input)
  );
  return data.data;
}

/** PUT /reviews/{id} — partial update. Never send null fields (null rating → 500). */
export async function updateReview(reviewId: number, input: Partial<ReviewInput>): Promise<Review> {
  const { data } = await apiClient.put<ApiEnvelope<Review>>(`/reviews/${reviewId}`, stripEmpty(input));
  return data.data;
}

/**
 * DELETE /reviews/{id} — shared route. Users may delete only their own review;
 * admins may delete any review.
 */
export async function deleteReview(reviewId: number): Promise<void> {
  await apiClient.delete(`/reviews/${reviewId}`);
}

function stripEmpty<T extends object>(obj: T): Partial<T> {
  return Object.fromEntries(
    Object.entries(obj).filter(([, v]) => v !== undefined && v !== null)
  ) as Partial<T>;
}
