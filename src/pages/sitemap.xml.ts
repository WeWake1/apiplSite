import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { categories, products, productUrl } from '../lib/catalog';

// Every indexable page (thank-you and 404 are noindex and left out).
export const GET: APIRoute = async ({ site }) => {
  const guides = await getCollection('guides');
  const today = new Date().toISOString().slice(0, 10);
  const paths = [
    '/',
    '/about/',
    '/products/',
    ...categories.map((c) => `/products/${c.slug}/`),
    ...products.map(productUrl),
    '/quality-certifications/',
    '/contact/',
    '/guides/',
    ...guides.map((g) => `/guides/${g.id}/`),
    '/privacy-policy/',
  ];
  const body = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${paths.map((p) => `  <url><loc>${new URL(p, site).href}</loc><lastmod>${today}</lastmod></url>`).join('\n')}
</urlset>
`;
  return new Response(body, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
};
