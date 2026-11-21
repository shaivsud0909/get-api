import { Link } from 'react-router-dom';
import { EmptyState } from '../components/ui/EmptyState';
import { Compass } from 'lucide-react';

export function InfoPage({ title, body }: { title: string; body: string }) {
  return (
    <div className="container-px max-w-2xl space-y-4 py-16">
      <h1 className="font-display text-3xl font-semibold text-forest-900">{title}</h1>
      <p className="text-forest-700">{body}</p>
    </div>
  );
}

export function NotFoundPage() {
  return (
    <div className="container-px py-16">
      <EmptyState
        icon={Compass}
        title="Page not found"
        action={<Link to="/" className="btn-primary px-5 py-2 text-sm">Go home</Link>}
      />
    </div>
  );
}
