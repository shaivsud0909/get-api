import { useEffect, useState } from 'react';
import { ANNOUNCEMENTS } from '../../constants';

export function AnnouncementBar() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(
      () => setIndex((i) => (i + 1) % ANNOUNCEMENTS.length),
      4500
    );
    return () => window.clearInterval(timer);
  }, []);

  return (
    <div className="bg-forest-900 text-cream-100">
      <div className="container-px flex h-9 items-center justify-center">
        <p key={index} className="animate-fade-in text-center text-xs font-medium tracking-wide sm:text-sm">
          {ANNOUNCEMENTS[index]}
        </p>
      </div>
    </div>
  );
}
