import type { LucideIcon } from 'lucide-react';
import type { ReactNode } from 'react';

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-3xl border border-dashed border-forest-200 bg-cream-50 px-6 py-16 text-center">
      <div className="rounded-full bg-forest-100 p-4 text-forest-600">
        <Icon className="h-8 w-8" />
      </div>
      <h3 className="font-display text-xl font-semibold text-forest-900">{title}</h3>
      {description && <p className="max-w-md text-sm text-forest-600">{description}</p>}
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}
