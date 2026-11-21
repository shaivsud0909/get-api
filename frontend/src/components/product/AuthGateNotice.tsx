import { Link, useLocation } from 'react-router-dom';
import { Lock } from 'lucide-react';
import { EmptyState } from '../ui/EmptyState';

/**
 * The backend guards GET /products behind an authenticated "user" role,
 * so signed-out visitors (and admins) cannot browse the catalogue.
 */
export function AuthGateNotice() {
  const location = useLocation();
  return (
    <EmptyState
      icon={Lock}
      title="Sign in to browse our catalogue"
      description="Our product catalogue is available to signed-in customers. Log in or create a free account to explore sustainable products."
      action={
        <div className="flex gap-3">
          <Link
            to="/login"
            state={{ from: location.pathname + location.search }}
            className="btn-primary px-5 py-2 text-sm"
          >
            Log in
          </Link>
          <Link to="/signup" className="btn-secondary px-5 py-2 text-sm">
            Create account
          </Link>
        </div>
      }
    />
  );
}
