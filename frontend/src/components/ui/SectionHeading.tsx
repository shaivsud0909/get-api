interface SectionHeadingProps {
  eyebrow?: string;
  title: string;
  description?: string;
  align?: 'left' | 'center';
}

export function SectionHeading({ eyebrow, title, description, align = 'center' }: SectionHeadingProps) {
  const alignment = align === 'center' ? 'items-center text-center' : 'items-start text-left';
  return (
    <div className={`flex flex-col gap-2 ${alignment}`}>
      {eyebrow && (
        <span className="text-xs font-semibold uppercase tracking-[0.2em] text-clay-500">
          {eyebrow}
        </span>
      )}
      <h2 className="font-display text-3xl font-semibold text-forest-900 sm:text-4xl">{title}</h2>
      {description && <p className="max-w-2xl text-sm text-forest-600 sm:text-base">{description}</p>}
    </div>
  );
}
