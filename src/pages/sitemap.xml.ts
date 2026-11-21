import type { APIRoute } from 'astro';
import { execFileSync } from 'node:child_process';
import { getCollection } from 'astro:content';
import { categories, products, productUrl } from '../lib/catalog';

// Every indexable page (thank-you and 404 are noindex and left out).
//
// <lastmod> is the date the page's own content last changed: the newest Git commit that touched the files
// listed for it (its page file, text, data and pictures). Site-wide code such as the layout or styles is left
// out on purpose: Google wants lastmod to change only for real content changes, and ignores sitemaps whose
// dates are always "today". Commit content changes before building, or the dates stay at the last commit.
// If Git history is unavailable, the page is listed without a date.

const lastCommit = (files: string[]): string | undefined => {
  try {
    const out = execFileSync('git', ['log', '-1', '--format=%cs', '--', ...files], { encoding: 'utf8' }).trim();
    return out || undefined;
  } catch {
    return undefined;
  }
};

const PRODUCT_DATA = 'src/data/products.json';
const CATEGORIES = 'src/data/categories.ts';

export const GET: APIRoute = async ({ site }) => {
  const guides = await getCollection('guides');
  const guideFiles = guides.map((g) => `src/content/guides/${g.id}.md`);

  const pages: [string, string[]][] = [
    ['/', ['src/pages/index.astro', CATEGORIES]],
    ['/about/', ['src/pages/about.astro']],
    ['/products/', ['src/pages/products/index.astro', CATEGORIES, PRODUCT_DATA]],
    ...categories.map((c): [string, string[]] => [
      `/products/${c.slug}/`,
      ['src/pages/products/[category]/index.astro', CATEGORIES, PRODUCT_DATA],
    ]),
    ...products.map((p): [string, string[]] => [
      productUrl(p),
      ['src/pages/products/[category]/[slug].astro', `src/content/products/${p.slug}.md`, `src/assets/products/${p.slug}`, PRODUCT_DATA],
    ]),
    ['/quality-certifications/', ['src/pages/quality-certifications.astro']],
    ['/contact/', ['src/pages/contact/index.astro']],
    ['/guides/', ['src/pages/guides/index.astro', ...guideFiles]],
    ...guides.map((g): [string, string[]] => [`/guides/${g.id}/`, ['src/pages/guides/[slug].astro', `src/content/guides/${g.id}.md`]]),
    ['/privacy-policy/', ['src/pages/privacy-policy.astro']],
  ];

  const urls = pages.map(([path, files]) => {
    const date = lastCommit(files);
    return `  <url><loc>${new URL(path, site).href}</loc>${date ? `<lastmod>${date}</lastmod>` : ''}</url>`;
  });

  const body = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.join('\n')}
</urlset>
`;
  return new Response(body, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
};
