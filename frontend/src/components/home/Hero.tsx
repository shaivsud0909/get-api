import { Link } from 'react-router-dom';
import { ArrowRight, Leaf } from 'lucide-react';

export function Hero() {
  return (
    <section className="relative overflow-hidden bg-forest-900">
      <img
        src="https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=1800&q=75"
        alt="Lush green forest canopy"
        className="absolute inset-0 h-full w-full object-cover opacity-40"
      />
      <div className="absolute inset-0 bg-gradient-to-r from-forest-950/80 via-forest-950/50 to-transparent" />

      <div className="container-px relative flex min-h-[480px] flex-col justify-center py-20 sm:min-h-[560px]">
        <div className="max-w-xl space-y-6 animate-fade-up">
          <span className="inline-flex items-center gap-2 rounded-full border border-cream-200/30 bg-cream-50/10 px-4 py-1.5 text-xs font-medium uppercase tracking-[0.2em] text-cream-100 backdrop-blur">
            <Leaf className="h-3.5 w-3.5" /> Sustainably handcrafted in India
          </span>
          <h1 className="font-display text-4xl font-semibold leading-tight text-cream-50 sm:text-5xl lg:text-6xl">
            Live gently.
            <br />
            Choose products the Earth would pick.
          </h1>
          <p className="max-w-md text-base text-cream-200/90 sm:text-lg">
            From bamboo essentials to personalised eco-gifts — everything at Prakriti is
            plastic-free, planet-kind and made to last.
          </p>
          <div className="flex flex-wrap gap-3 pt-2">
            <Link to="/shop" className="btn-primary px-7 py-3 text-base">
              Shop Now <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              to="/shop?category=Gift%20Hampers"
              className="btn border border-cream-200/40 px-7 py-3 text-base text-cream-50 hover:bg-cream-50/10"
            >
              Explore Gifting
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
