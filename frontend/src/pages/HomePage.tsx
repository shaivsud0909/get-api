import { Hero } from '../components/home/Hero';
import { CategoryShowcase } from '../components/home/CategoryShowcase';
import { SectionHeading } from '../components/ui/SectionHeading';
import { TESTIMONIALS, WHY_CHOOSE } from '../constants';

export function HomePage() {
  return (
    <>
      <Hero />
      <CategoryShowcase />
      <section className="bg-cream-100 py-16">
        <div className="container-px space-y-10">
          <SectionHeading eyebrow="Why Prakriti" title="Better for you, better for the planet" />
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {WHY_CHOOSE.map((item) => (
              <div key={item.title} className="rounded-3xl bg-white p-6 shadow-sm">
                <h3 className="font-display text-lg font-semibold text-forest-900">{item.title}</h3>
                <p className="mt-2 text-sm text-forest-600">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
      <section className="container-px space-y-10 py-16">
        <SectionHeading eyebrow="Kind words" title="Loved by conscious shoppers" />
        <div className="grid gap-5 md:grid-cols-3">
          {TESTIMONIALS.map((t) => (
            <figure key={t.name} className="rounded-3xl border border-forest-100 p-6">
              <blockquote className="text-sm text-forest-700">“{t.quote}”</blockquote>
              <figcaption className="mt-4 text-sm font-semibold text-forest-900">
                {t.name} · <span className="font-normal text-forest-600">{t.location}</span>
              </figcaption>
            </figure>
          ))}
        </div>
      </section>
    </>
  );
}
