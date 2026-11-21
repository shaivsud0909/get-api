import { useAuth } from '../context/AuthContext';
import { AddressBook } from '../components/address/AddressBook';

/** No profile endpoint exists — identity comes from the JWT payload. */
export function ProfilePage() {
  const { user } = useAuth();
  return (
    <div className="container-px max-w-3xl space-y-8 py-12">
      <section className="space-y-2">
        <h1 className="font-display text-3xl font-semibold text-forest-900">Your profile</h1>
        <p className="text-forest-700">
          Signed in as <strong>{user?.email}</strong>
        </p>
      </section>
      <section className="space-y-4">
        <h2 className="font-display text-xl font-semibold text-forest-900">Saved addresses</h2>
        <AddressBook />
      </section>
    </div>
  );
}
