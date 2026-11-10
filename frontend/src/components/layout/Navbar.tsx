import { useEffect, useRef, useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { Leaf, Menu, Search, ShoppingBag, User, X, LogOut, Package } from 'lucide-react';
import { BRAND_NAME, NAV_LINKS } from '../../constants';
import { useAuth } from '../../context/AuthContext';
import { useCart } from '../../context/CartContext';

export function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const { itemCount } = useCart();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [accountOpen, setAccountOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const accountRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    function onClickOutside(event: MouseEvent) {
      if (accountRef.current && !accountRef.current.contains(event.target as Node)) {
        setAccountOpen(false);
      }
    }
    document.addEventListener('mousedown', onClickOutside);
    return () => document.removeEventListener('mousedown', onClickOutside);
  }, []);

  useEffect(() => {
    if (searchOpen) searchInputRef.current?.focus();
  }, [searchOpen]);

  function submitSearch(event: React.FormEvent) {
    event.preventDefault();
    const term = searchTerm.trim();
    setSearchOpen(false);
    setMobileOpen(false);
    navigate(term ? `/shop?q=${encodeURIComponent(term)}` : '/shop');
    setSearchTerm('');
  }

  function handleLogout() {
    logout();
    setAccountOpen(false);
    setMobileOpen(false);
    navigate('/');
  }

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `text-sm font-medium transition hover:text-forest-600 ${
      isActive ? 'text-forest-700' : 'text-forest-900'
    }`;

  return (
    <header className="sticky top-0 z-50 border-b border-forest-100 bg-cream-50/95 backdrop-blur">
      <nav className="container-px flex h-16 items-center justify-between gap-4" aria-label="Main navigation">
        {/* Mobile menu button */}
        <button
          className="rounded-lg p-2 text-forest-800 hover:bg-forest-100 lg:hidden"
          onClick={() => setMobileOpen((open) => !open)}
          aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={mobileOpen}
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>

        {/* Logo */}
        <Link to="/" className="flex items-center gap-2" aria-label={`${BRAND_NAME} home`}>
          <span className="rounded-full bg-forest-700 p-1.5 text-cream-50">
            <Leaf className="h-4 w-4" />
          </span>
          <span className="font-display text-2xl font-semibold tracking-tight text-forest-900">
            {BRAND_NAME}
          </span>
        </Link>

        {/* Desktop links */}
        <div className="hidden items-center gap-7 lg:flex">
          {NAV_LINKS.map((link) => (
            <NavLink key={link.label} to={link.to} className={navLinkClass} end={link.to === '/'}>
              {link.label}
            </NavLink>
          ))}
        </div>

        {/* Icons */}
        <div className="flex items-center gap-1 sm:gap-2">
          <button
            className="rounded-lg p-2 text-forest-800 hover:bg-forest-100"
            onClick={() => setSearchOpen((open) => !open)}
            aria-label="Search products"
            aria-expanded={searchOpen}
          >
            <Search className="h-5 w-5" />
          </button>

          <div className="relative" ref={accountRef}>
            <button
              className="rounded-lg p-2 text-forest-800 hover:bg-forest-100"
              onClick={() => setAccountOpen((open) => !open)}
              aria-label="Account"
              aria-expanded={accountOpen}
            >
              <User className="h-5 w-5" />
            </button>
            {accountOpen && (
              <div className="absolute right-0 mt-2 w-56 rounded-2xl border border-forest-100 bg-white p-2 shadow-xl animate-fade-in">
                {isAuthenticated ? (
                  <>
                    <p className="truncate px-3 py-2 text-xs text-forest-500">{user?.email}</p>
                    <Link
                      to="/profile"
                      onClick={() => setAccountOpen(false)}
                      className="flex items-center gap-2 rounded-xl px-3 py-2 text-sm text-forest-800 hover:bg-forest-50"
                    >
                      <User className="h-4 w-4" /> My Profile
                    </Link>
                    <Link
                      to="/orders"
                      onClick={() => setAccountOpen(false)}
                      className="flex items-center gap-2 rounded-xl px-3 py-2 text-sm text-forest-800 hover:bg-forest-50"
                    >
                      <Package className="h-4 w-4" /> My Orders
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm text-red-700 hover:bg-red-50"
                    >
                      <LogOut className="h-4 w-4" /> Log out
                    </button>
                  </>
                ) : (
                  <>
                    <Link
                      to="/login"
                      onClick={() => setAccountOpen(false)}
                      className="block rounded-xl px-3 py-2 text-sm text-forest-800 hover:bg-forest-50"
                    >
                      Log in
                    </Link>
                    <Link
                      to="/signup"
                      onClick={() => setAccountOpen(false)}
                      className="block rounded-xl px-3 py-2 text-sm text-forest-800 hover:bg-forest-50"
                    >
                      Create account
                    </Link>
                  </>
                )}
              </div>
            )}
          </div>

          <Link
            to="/cart"
            className="relative rounded-lg p-2 text-forest-800 hover:bg-forest-100"
            aria-label={`Cart, ${itemCount} item${itemCount === 1 ? '' : 's'}`}
          >
            <ShoppingBag className="h-5 w-5" />
            {itemCount > 0 && (
              <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-clay-500 px-1 text-[10px] font-bold text-white">
                {itemCount > 99 ? '99+' : itemCount}
              </span>
            )}
          </Link>
        </div>
      </nav>

      {/* Search bar */}
      {searchOpen && (
        <div className="border-t border-forest-100 bg-cream-50 animate-fade-in">
          <form onSubmit={submitSearch} className="container-px flex items-center gap-2 py-3">
            <Search className="h-4 w-4 shrink-0 text-forest-500" />
            <input
              ref={searchInputRef}
              type="search"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search bamboo products, gift hampers, personal care…"
              className="w-full bg-transparent text-sm text-forest-900 placeholder:text-forest-400 focus:outline-none"
              aria-label="Search products"
            />
            <button type="submit" className="btn-primary px-4 py-1.5 text-sm">
              Search
            </button>
          </form>
        </div>
      )}

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="border-t border-forest-100 bg-cream-50 lg:hidden animate-fade-in">
          <div className="container-px flex flex-col gap-1 py-4">
            {NAV_LINKS.map((link) => (
              <NavLink
                key={link.label}
                to={link.to}
                end={link.to === '/'}
                onClick={() => setMobileOpen(false)}
                className={({ isActive }) =>
                  `rounded-xl px-3 py-2.5 text-sm font-medium ${
                    isActive ? 'bg-forest-100 text-forest-800' : 'text-forest-900 hover:bg-forest-50'
                  }`
                }
              >
                {link.label}
              </NavLink>
            ))}
            <div className="mt-2 border-t border-forest-100 pt-3">
              {isAuthenticated ? (
                <button
                  onClick={handleLogout}
                  className="flex w-full items-center gap-2 rounded-xl px-3 py-2.5 text-sm font-medium text-red-700 hover:bg-red-50"
                >
                  <LogOut className="h-4 w-4" /> Log out
                </button>
              ) : (
                <div className="flex gap-2 px-1">
                  <Link
                    to="/login"
                    onClick={() => setMobileOpen(false)}
                    className="btn-secondary flex-1 px-4 py-2 text-sm"
                  >
                    Log in
                  </Link>
                  <Link
                    to="/signup"
                    onClick={() => setMobileOpen(false)}
                    className="btn-primary flex-1 px-4 py-2 text-sm"
                  >
                    Sign up
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
