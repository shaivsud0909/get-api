import { Link } from 'react-router-dom';
import { Leaf, Mail, MapPin, Phone, Facebook, Instagram, Twitter } from 'lucide-react';
import { BRAND_NAME } from '../../constants';

const SHOP_LINKS = [
  { label: 'All Products', to: '/shop' },
  { label: 'Bamboo Products', to: '/shop?category=Bamboo' },
  { label: 'Personal Care', to: '/shop?category=Personal%20Care' },
  { label: 'Gift Hampers', to: '/shop?category=Gift%20Hampers' },
  { label: 'Customized Products', to: '/shop?customisable=true' },
];

const COMPANY_LINKS = [
  { label: 'About Us', to: '/about' },
  { label: 'Contact Us', to: '/contact' },
  { label: 'My Orders', to: '/orders' },
  { label: 'My Profile', to: '/profile' },
];

const POLICY_LINKS = [
  'Shipping Policy',
  'Returns & Refunds',
  'Privacy Policy',
  'Terms of Service',
];

export function Footer() {
  return (
    <footer className="bg-forest-950 text-cream-200">
      <div className="container-px grid gap-10 py-14 sm:grid-cols-2 lg:grid-cols-4">
        {/* Brand */}
        <div className="space-y-4">
          <Link to="/" className="flex items-center gap-2">
            <span className="rounded-full bg-forest-700 p-1.5 text-cream-50">
              <Leaf className="h-4 w-4" />
            </span>
            <span className="font-display text-2xl font-semibold text-cream-50">{BRAND_NAME}</span>
          </Link>
          <p className="text-sm leading-relaxed text-cream-300/80">
            Thoughtfully handcrafted, earth-friendly products from India. Every purchase plants a
            step towards a plastic-free tomorrow.
          </p>
          <div className="flex gap-3">
            {[
              { icon: Instagram, label: 'Instagram' },
              { icon: Facebook, label: 'Facebook' },
              { icon: Twitter, label: 'Twitter' },
            ].map(({ icon: Icon, label }) => (
              <a
                key={label}
                href="#"
                aria-label={label}
                className="rounded-full border border-forest-700 p-2 text-cream-200 transition hover:bg-forest-800"
              >
                <Icon className="h-4 w-4" />
              </a>
            ))}
          </div>
        </div>

        {/* Shop */}
        <nav aria-label="Shop links" className="space-y-3">
          <h3 className="font-display text-lg font-semibold text-cream-50">Shop</h3>
          <ul className="space-y-2">
            {SHOP_LINKS.map((link) => (
              <li key={link.label}>
                <Link to={link.to} className="text-sm text-cream-300/80 transition hover:text-cream-50">
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        {/* Company */}
        <nav aria-label="Company links" className="space-y-3">
          <h3 className="font-display text-lg font-semibold text-cream-50">Company</h3>
          <ul className="space-y-2">
            {COMPANY_LINKS.map((link) => (
              <li key={link.label}>
                <Link to={link.to} className="text-sm text-cream-300/80 transition hover:text-cream-50">
                  {link.label}
                </Link>
              </li>
            ))}
            {POLICY_LINKS.map((label) => (
              <li key={label}>
                <span className="cursor-default text-sm text-cream-300/60">{label}</span>
              </li>
            ))}
          </ul>
        </nav>

        {/* Contact */}
        <div className="space-y-3">
          <h3 className="font-display text-lg font-semibold text-cream-50">Get in touch</h3>
          <ul className="space-y-3 text-sm text-cream-300/80">
            <li className="flex items-start gap-2">
              <MapPin className="mt-0.5 h-4 w-4 shrink-0" />
              <span>Patiala, Punjab, India</span>
            </li>
            <li className="flex items-center gap-2">
              <Phone className="h-4 w-4 shrink-0" />
              <a href="tel:+911234567890" className="hover:text-cream-50">+91 12345 67890</a>
            </li>
            <li className="flex items-center gap-2">
              <Mail className="h-4 w-4 shrink-0" />
              <a href="mailto:hello@prakriti.example" className="hover:text-cream-50">
                hello@prakriti.example
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div className="border-t border-forest-800">
        <div className="container-px flex flex-col items-center justify-between gap-2 py-5 text-xs text-cream-300/60 sm:flex-row">
          <p>© {new Date().getFullYear()} {BRAND_NAME}. All rights reserved.</p>
          <p>Made with care for the planet 🌱</p>
        </div>
      </div>
    </footer>
  );
}
