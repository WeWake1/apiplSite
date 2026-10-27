import type { ImageMetadata } from 'astro';
import productsData from '../data/products.json';
import { categories, categoryBySlug, type Category } from '../data/categories';
import placeholder from '../assets/brand/render-placeholder.webp';

export interface Product {
  slug: string;
  pallet: string; // 3D recipe id (tools/render/pallets.py)
  category: string;
  code: string;
  name: string;
  dims: { l: number; w: number; h: number };
  entry: string;
  style: string;
  wood: string;
  components?: string;
  use?: string;
  loadKg?: number;
}

export const products = productsData as unknown as Product[];
export const productBySlug: Record<string, Product> = Object.fromEntries(products.map((p) => [p.slug, p]));

// Blender studio renders: src/assets/products/<slug>/<view>.webp (tools/render)
const renders = import.meta.glob<{ default: ImageMetadata }>('/src/assets/products/*/*.webp', { eager: true });
const VIEW_LABELS = ['front three-quarter view', 'opposite three-quarter view', 'fork-entry side view', 'top view', 'underside view'];
const COLLAR_LABELS = ['collar on a pallet', 'three collars stacked', 'single collar', 'top view'];

export function productImages(p: Product): { src: ImageMetadata; alt: string }[] {
  const prefix = `/src/assets/products/${p.slug}/`;
  const files = Object.keys(renders)
    .filter((k) => k.startsWith(prefix))
    .sort((a, b) => parseInt(a.slice(prefix.length)) - parseInt(b.slice(prefix.length)));
  const labels = p.category === 'pallet-collars' ? COLLAR_LABELS : VIEW_LABELS;
  if (!files.length) return [{ src: placeholder, alt: `${p.name}` }];
  return files.map((f, i) => ({ src: renders[f].default, alt: `${p.name}, ${sizeLabel(p, true)}: ${labels[i] ?? 'view ' + (i + 1)}` }));
}

export const mainImage = (p: Product) => productImages(p)[0];

/** Web 3D model (public/models/<slug>.glb), loaded only when the visitor taps "3D". */
export const modelUrl = (p: Product) => `/models/${p.slug}.glb`;

export const productUrl = (p: Product) => `/products/${p.category}/${p.slug}/`;
export const categoryUrl = (slug: string) => `/products/${slug}/`;

export function sizeLabel(p: Product, withHeight = false) {
  const { l, w, h } = p.dims;
  return withHeight ? `${l} × ${w} × ${h} mm` : `${l} × ${w} mm`;
}

export const productsIn = (category: string) => products.filter((p) => p.category === category);
export const categoryOf = (p: Product): Category => categoryBySlug[p.category];

/** Spec rows in display order: only facts we actually have. */
export function specRows(p: Product): [string, string][] {
  const rows: [string, string][] = [['Dimensions', `${p.dims.l} × ${p.dims.w} × ${p.dims.h} mm (L × W × H)`]];
  rows.push(['Construction', p.style]);
  if (p.entry && p.entry !== '-') rows.push(['Fork entry', p.entry]);
  if (p.components) rows.push(['Components', p.components]);
  rows.push(['Material', p.wood]);
  if (p.loadKg) rows.push(['Load capacity', `${p.loadKg.toLocaleString('en-IN')} kg`]);
  if (p.use) rows.push(['Typical use', p.use]);
  rows.push(['Treatment', 'ISPM-15 heat treatment, IPPC mark IN-081 HT']);
  return rows;
}

export function relatedProducts(p: Product, n = 3): Product[] {
  const same = productsIn(p.category).filter((x) => x.slug !== p.slug);
  const area = (x: Product) => x.dims.l * x.dims.w;
  same.sort((a, b) => Math.abs(area(a) - area(p)) - Math.abs(area(b) - area(p)));
  const picks = same.slice(0, n);
  for (const x of products) {
    if (picks.length >= n) break;
    if (x.category !== p.category && !picks.includes(x)) picks.push(x);
  }
  return picks;
}

export { categories, categoryBySlug };
