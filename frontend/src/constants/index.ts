export const BRAND_NAME = 'Prakriti';

export const ANNOUNCEMENTS = [
  'Free shipping on orders above ₹999',
  'Handcrafted in India · Plastic-free packaging',
  'Flat 10% off on your first order',
];

export const NAV_LINKS = [
  { label: 'Home', to: '/' },
  { label: 'Shop', to: '/shop' },
  { label: 'Categories', to: '/shop#categories' },
  { label: 'Gift Collections', to: '/shop?category=Gift%20Hampers' },
  { label: 'About Us', to: '/about' },
  { label: 'Contact', to: '/contact' },
] as const;

/**
 * Categories showcased on the home page. The `value` is passed to the
 * backend's `category` query param (matched with ILIKE, case-insensitive).
 */
export const CATEGORIES = [
  {
    name: 'Bamboo Products',
    value: 'Bamboo',
    description: 'Toothbrushes, straws, cutlery & more',
    image:
      'https://images.unsplash.com/photo-1583947215259-38e31be8751f?auto=format&fit=crop&w=800&q=70',
  },
  {
    name: 'Eco-friendly Essentials',
    value: 'Essentials',
    description: 'Everyday zero-waste swaps',
    image:
      'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=800&q=70',
  },
  {
    name: 'Personal Care',
    value: 'Personal Care',
    description: 'Natural soaps, oils & skincare',
    image:
      'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=800&q=70',
  },
  {
    name: 'Gift Hampers',
    value: 'Gift Hampers',
    description: 'Thoughtful, sustainable gifting',
    image:
      'https://images.unsplash.com/photo-1549465220-1a8b9238cd48?auto=format&fit=crop&w=800&q=70',
  },
  {
    name: 'Customized Products',
    value: 'Customized',
    description: 'Personalised just for you',
    image:
      'https://images.unsplash.com/photo-1452860606245-08befc0ff44b?auto=format&fit=crop&w=800&q=70',
  },
] as const;

export const WHY_CHOOSE = [
  {
    title: 'Sustainable Products',
    description: 'Every product is made from renewable, biodegradable or recycled materials.',
    icon: 'Leaf',
  },
  {
    title: 'Eco-conscious Choices',
    description: 'Plastic-free packaging and carbon-aware shipping on every order.',
    icon: 'Recycle',
  },
  {
    title: 'Quality Craftsmanship',
    description: 'Handcrafted by skilled Indian artisans who take pride in every detail.',
    icon: 'Award',
  },
  {
    title: 'Responsible Sourcing',
    description: 'Raw materials sourced ethically from local, fair-trade communities.',
    icon: 'HandHeart',
  },
] as const;

export const TESTIMONIALS = [
  {
    name: 'Ananya Sharma',
    location: 'Bengaluru',
    quote:
      'The bamboo kitchen set is beautiful and sturdy. Love that everything arrived in paper packaging — not a shred of plastic.',
    rating: 5,
  },
  {
    name: 'Rohan Mehta',
    location: 'Mumbai',
    quote:
      'Ordered a customized gift hamper for my parents’ anniversary. The personal touch made it unforgettable.',
    rating: 5,
  },
  {
    name: 'Priya Nair',
    location: 'Kochi',
    quote:
      'Switched our whole household to Prakriti essentials. Great quality, honest pricing, and it feels good to shop consciously.',
    rating: 4,
  },
] as const;

export const CART_STORAGE_KEY = 'prakriti_cart';
export const TOKEN_STORAGE_KEY = 'prakriti_access_token';
