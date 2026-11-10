import { Loader2 } from 'lucide-react';

export function Spinner({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-forest-600" role="status">
      <Loader2 className="h-8 w-8 animate-spin" />
      <span className="text-sm">{label}</span>
    </div>
  );
}
