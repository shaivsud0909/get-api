import { useCallback, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import axios from 'axios';
import { PackageSearch, Star, Trash2, Pencil } from 'lucide-react';
import { fetchProductById, fetchProductDetails } from '../services/productService';
import * as reviewService from '../services/reviewService';
import { getErrorMessage } from '../services/apiClient';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';
import { useToast } from '../context/ToastContext';
import { AuthGateNotice } from '../components/product/AuthGateNotice';
import { EmptyState } from '../components/ui/EmptyState';
import { QuantitySelector } from '../components/ui/QuantitySelector';
import { Spinner } from '../components/ui/Spinner';
import { StockBadge } from '../components/ui/StockBadge';
import { PriceTag } from '../components/ui/PriceTag';
import { formatDate } from '../utils/format';
import { productImage } from '../utils/productImages';
import type { Product, ProductDetails, Review } from '../types';

export function ProductDetailPage() {
  const { id } = useParams();
  const productId = Number(id);
  const { isAuthenticated, user } = useAuth();
  const { addItem } = useCart();
  const { showToast } = useToast();
  const [product, setProduct] = useState<Product | null>(null);
  const [details, setDetails] = useState<ProductDetails | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    if (!isAuthenticated || !Number.isFinite(productId)) {
      setLoading(false);
      return;
    }
    let cancelled = false;
    setLoading(true);
    // Shared routes (users and admins): /product/{id}, /products/{id} and reviews.
    Promise.all([
      fetchProductById(productId),
      fetchProductDetails(productId).catch(() => null),
      reviewService.fetchReviews(productId).catch(() => [] as Review[]),
    ])
      .then(([p, d, r]) => {
        if (cancelled) return;
        setProduct(p);
        setDetails(d);
        setReviews(r);
      })
      .catch((err) => {
        if (cancelled) return;
        setProduct(null);
        if (!(axios.isAxiosError(err) && err.response?.status === 404)) {
          showToast(getErrorMessage(err), 'error');
        }
      })
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [productId, isAuthenticated, showToast]);

  if (!isAuthenticated || !user) {
    return (
      <div className="container-px py-12">
        <AuthGateNotice />
      </div>
    );
  }
  if (loading) return <Spinner />;
  if (!product) {
    return (
      <div className="container-px py-12">
        <EmptyState
          icon={PackageSearch}
          title="Product not found"
          action={
            <Link to="/shop" className="btn-primary px-5 py-2 text-sm">
              Back to shop
            </Link>
          }
        />
      </div>
    );
  }

  const handleAdd = async () => {
    try {
      await addItem(product, quantity);
      showToast(`${product.name} added to cart`, 'success');
    } catch (err) {
      showToast(getErrorMessage(err), 'error');
    }
  };

  const isAdmin = user.role === 'admin';
  const features = details?.features ?? [];
  const avgRating = reviews.length
    ? reviews.reduce((s, r) => s + r.rating, 0) / reviews.length
    : null;

  return (
    <div className="container-px space-y-12 py-12">
      <div className="grid gap-10 md:grid-cols-2">
        {/* The backend stores only image file names (not hosted URLs), so
            product imagery still comes from the client-side pool. */}
        <img
          src={productImage(product.id, product.category)}
          alt={details?.images[0]?.alt_text || product.name}
          className="aspect-square w-full rounded-3xl object-cover"
        />
        <div className="space-y-4">
          <p className="text-xs uppercase tracking-widest text-clay-500">{product.category}</p>
          <h1 className="font-display text-3xl font-semibold text-forest-900">{product.name}</h1>
          {avgRating !== null && (
            <p className="flex items-center gap-1 text-sm text-forest-700">
              <Stars value={Math.round(avgRating)} /> {avgRating.toFixed(1)} · {reviews.length}{' '}
              review{reviews.length === 1 ? '' : 's'}
            </p>
          )}
          <PriceTag price={product.price} originalPrice={product.original_price} size="lg" />
          <StockBadge stock={product.stock} />
          {product.customisable && (
            <p className="text-sm text-clay-700">This product can be customised.</p>
          )}
          {product.description && <p className="text-forest-600">{product.description}</p>}
          {isAdmin ? null : product.stock > 0 ? (
            <div className="flex items-center gap-4">
              <QuantitySelector value={quantity} onChange={setQuantity} max={product.stock} />
              <button className="btn-primary px-6 py-2.5" onClick={handleAdd}>
                Add to cart
              </button>
            </div>
          ) : (
            <p className="font-medium text-red-600">Out of stock</p>
          )}

          {features.length > 0 && (
            <div className="pt-4">
              <h2 className="mb-2 font-display text-lg font-semibold text-forest-900">Specifications</h2>
              <dl className="divide-y divide-forest-100 rounded-2xl border border-forest-100 bg-white">
                {features.map((f) => (
                  <div key={f.id} className="grid grid-cols-3 gap-4 px-4 py-2.5 text-sm">
                    <dt className="font-medium text-forest-800">{f.key}</dt>
                    <dd className="col-span-2 text-forest-700">
                      {f.value}
                      {f.detailed_description && (
                        <p className="mt-1 text-xs text-forest-500">{f.detailed_description}</p>
                      )}
                    </dd>
                  </div>
                ))}
              </dl>
            </div>
          )}
        </div>
      </div>

      <ReviewsSection
        productId={product.id}
        userId={user.id}
        isAdmin={isAdmin}
        reviews={reviews}
        onChange={setReviews}
      />
    </div>
  );
}

function Stars({ value }: { value: number }) {
  return (
    <span className="inline-flex" aria-label={`${value} out of 5 stars`}>
      {[1, 2, 3, 4, 5].map((n) => (
        <Star
          key={n}
          className={`h-4 w-4 ${n <= value ? 'fill-amber-400 text-amber-400' : 'text-forest-200'}`}
        />
      ))}
    </span>
  );
}

function ReviewsSection({
  productId,
  userId,
  isAdmin,
  reviews,
  onChange,
}: {
  productId: number;
  userId: number;
  isAdmin: boolean;
  reviews: Review[];
  onChange: (reviews: Review[]) => void;
}) {
  const { showToast } = useToast();
  // Admins cannot write reviews, so "own" only applies to customers.
  const own = isAdmin ? null : reviews.find((r) => r.user_id === userId) ?? null;
  const [editing, setEditing] = useState(false);

  // Users delete their own review; admins can delete any review (same endpoint).
  const handleDelete = useCallback(
    async (review: Review) => {
      const mine = review.user_id === userId && !isAdmin;
      if (!window.confirm(mine ? 'Delete your review?' : 'Delete this review?')) return;
      try {
        await reviewService.deleteReview(review.id);
        onChange(reviews.filter((r) => r.id !== review.id));
        if (mine) setEditing(false);
        showToast('Review deleted', 'success');
      } catch (err) {
        showToast(getErrorMessage(err), 'error');
      }
    },
    [userId, isAdmin, reviews, onChange, showToast]
  );

  return (
    <section className="space-y-6">
      <h2 className="font-display text-2xl font-semibold text-forest-900">Reviews</h2>

      {/* One review per user per product: hide the form once the user has one. */}
      {!isAdmin && (!own || editing) && (
        <ReviewForm
          initial={editing ? own : null}
          onCancel={editing ? () => setEditing(false) : undefined}
          onSubmit={async (input) => {
            if (editing && own) {
              const updated = await reviewService.updateReview(own.id, input);
              onChange(reviews.map((r) => (r.id === updated.id ? updated : r)));
              setEditing(false);
              showToast('Review updated', 'success');
            } else {
              const created = await reviewService.createReview(productId, input);
              onChange([created, ...reviews]);
              showToast('Thanks for your review!', 'success');
            }
          }}
        />
      )}

      {reviews.length === 0 ? (
        <p className="text-sm text-forest-600">No reviews yet.</p>
      ) : (
        <ul className="space-y-3">
          {reviews.map((r) => (
            <li key={r.id} className="rounded-2xl border border-forest-100 bg-white p-4">
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <Stars value={r.rating} />
                  <span className="text-xs text-forest-500">
                    {!isAdmin && r.user_id === userId ? 'You' : isAdmin ? `Customer #${r.user_id}` : 'Verified customer'} · {formatDate(r.created_at)}
                  </span>
                </div>
                {isAdmin ? (
                  <button onClick={() => handleDelete(r)} aria-label="Delete this review">
                    <Trash2 className="h-4 w-4 text-red-500" />
                  </button>
                ) : (
                  r.user_id === userId &&
                  !editing && (
                    <div className="flex gap-2">
                      <button onClick={() => setEditing(true)} aria-label="Edit your review">
                        <Pencil className="h-4 w-4 text-forest-600" />
                      </button>
                      <button onClick={() => handleDelete(r)} aria-label="Delete your review">
                        <Trash2 className="h-4 w-4 text-red-500" />
                      </button>
                    </div>
                  )
                )}
              </div>
              {r.comment && <p className="mt-2 text-sm text-forest-700">{r.comment}</p>}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function ReviewForm({
  initial,
  onSubmit,
  onCancel,
}: {
  initial: Review | null;
  onSubmit: (input: reviewService.ReviewInput) => Promise<void>;
  onCancel?: () => void;
}) {
  const { showToast } = useToast();
  const [rating, setRating] = useState(initial?.rating ?? 0);
  const [comment, setComment] = useState(initial?.comment ?? '');
  const [submitting, setSubmitting] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (rating < 1) {
      showToast('Please choose a rating.', 'error');
      return;
    }
    setSubmitting(true);
    try {
      const trimmed = comment.trim();
      await onSubmit({ rating, ...(trimmed ? { comment: trimmed } : {}) });
      if (!initial) {
        setRating(0);
        setComment('');
      }
    } catch (err) {
      showToast(getErrorMessage(err), 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={submit} className="space-y-3 rounded-2xl border border-forest-100 bg-white p-4">
      <p className="text-sm font-medium text-forest-800">
        {initial ? 'Edit your review' : 'Write a review'}
      </p>
      <div className="flex gap-1" role="radiogroup" aria-label="Rating">
        {[1, 2, 3, 4, 5].map((n) => (
          <button
            key={n}
            type="button"
            role="radio"
            aria-checked={rating === n}
            aria-label={`${n} star${n > 1 ? 's' : ''}`}
            onClick={() => setRating(n)}
          >
            <Star
              className={`h-6 w-6 ${n <= rating ? 'fill-amber-400 text-amber-400' : 'text-forest-200'}`}
            />
          </button>
        ))}
      </div>
      <textarea
        className="input-field min-h-24"
        maxLength={500}
        placeholder="Share your thoughts (optional)"
        value={comment}
        onChange={(e) => setComment(e.target.value)}
      />
      <div className="flex gap-2">
        <button className="btn-primary px-5 py-2 text-sm" disabled={submitting}>
          {submitting ? 'Saving…' : initial ? 'Save' : 'Submit review'}
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
