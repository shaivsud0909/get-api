import { Route, Routes } from 'react-router-dom';
import { MainLayout } from './layouts/MainLayout';
import { ProtectedRoute } from './routes/ProtectedRoute';
import { HomePage } from './pages/HomePage';
import { ShopPage } from './pages/ShopPage';
import { ProductDetailPage } from './pages/ProductDetailPage';
import { CartPage } from './pages/CartPage';
import { LoginPage, SignupPage } from './pages/AuthPages';
import { OrdersPage } from './pages/OrdersPage';
import { InfoPage, NotFoundPage } from './pages/InfoPages';

export default function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route index element={<HomePage />} />
        <Route path="shop" element={<ShopPage />} />
        <Route path="products/:id" element={<ProductDetailPage />} />
        <Route path="cart" element={<CartPage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="signup" element={<SignupPage />} />
        <Route
          path="about"
          element={
            <InfoPage
              title="About Prakriti"
              body="Prakriti brings together Indian artisans and conscious shoppers. Every product is plastic-free, ethically sourced and made to last."
            />
          }
        />
        <Route
          path="contact"
          element={
            <InfoPage
              title="Contact us"
              body="Questions about an order or a customised product? Write to hello@prakriti.example and we will get back to you within two working days."
            />
          }
        />
        <Route element={<ProtectedRoute />}>
          <Route path="orders" element={<OrdersPage />} />
          <Route
            path="profile"
            element={<InfoPage title="Your profile" body="Profile management is coming soon." />}
          />
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
