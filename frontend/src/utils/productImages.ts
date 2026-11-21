/**
 * The backend Product model has no image field, so product imagery is
 * derived client-side: a curated pool per category keyword, picked
 * deterministically by product id so a product always shows the same photo.
 */
const IMAGE_POOLS: Record<string, string[]> = {
  bamboo: [
    'https://images.unsplash.com/photo-1583947215259-38e31be8751f?auto=format&fit=crop&w=800&q=70',
    'https://images.unsplash.com/photo-1605092676920-8ac5ae40c7c8?auto=format&fit=crop&w=800&q=70',
    'https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?auto=format&fit=crop&w=800&q=70',
  ],
  'personal care': [
    'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=800&q=70',
    'https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?auto=format&fit=crop&w=800&q=70',
    'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?auto=format&fit=crop&w=800&q=70',
  ],
  gift: [
    'https://images.unsplash.com/photo-1549465220-1a8b9238cd48?auto=format&fit=crop&w=800&q=70',
    'https://images.unsplash.com/photo-1513201099705-a9746e1e201f?auto=format&fit=crop&w=800&q=70',
  ],
  custom: [
    'https://images.unsplash.com/photo-1452860606245-08befc0ff44b?auto=format&fit=crop&w=800&q=70',
    'https://images.unsplash.com/photo-1606722590583-6951b5ea92ad?auto=format&fit=crop&w=800&q=70',
  ],
  default: [
    'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=800&q=70',
    'https://images.unsplash.com/photo-1545165375-1b744b9ed444?auto=format&fit=crop&w=800&q=70',
    'https://images.unsplash.com/photo-1536939459926-301728717817?auto=format&fit=crop&w=800&q=70',
    'https://images.unsplash.com/photo-1610701596007-11502861dcfa?auto=format&fit=crop&w=800&q=70',
  ],
};

export function productImage(productId: number, category: string): string {
  const key = Object.keys(IMAGE_POOLS).find(
    (k) => k !== 'default' && category.toLowerCase().includes(k)
  );
  const pool = IMAGE_POOLS[key ?? 'default'];
  return pool[productId % pool.length];
}
