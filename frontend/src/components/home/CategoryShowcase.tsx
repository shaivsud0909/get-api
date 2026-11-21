import { Link } from 'react-router-dom';
import { CATEGORIES } from '../../constants';
import { SectionHeading } from '../ui/SectionHeading';

export function CategoryShowcase() {
  return (
    <section id="categories" className="container-px space-y-10 py-16 sm:py-20">
      <SectionHeading
        eyebrow="Collections"
        title="Shop by Category"
        description="Every category is a small step away from plastic and a big step towards mindful living."
      />
      <div className="grid grid-cols-2 gap-4 sm:gap-5 lg:grid-cols-5">
        {CATEGORIES.map((category, index) => (
          <Link
            key={category.name}
            to={
              category.value === 'Customized'
                ? '/shop?customisable=true'
                : `/shop?category=${encodeURIComponent(category.value)}`
            }
            className={`group relative overflow-hidden rounded-3xl ${index === 0 ? 'col-span-2 lg:col-span-1' : ''}`}
          >
            <div className="aspect-[4/5] w-full bg-cream-200">
              <img
                src={category.image}
                alt={category.name}
                loading="lazy"
                className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
            </div>
            <div className="absolute inset-0 flex flex-col justify-end bg-gradient-to-t from-forest-950/80 via-forest-950/20 to-transparent p-4">
              <h3 className="font-display text-lg font-semibold text-cream-50">{category.name}</h3>
              <p className="text-xs text-cream-200/90">{category.description}</p>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
