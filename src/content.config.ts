import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// Marketing copy for each product. File name = product slug in src/data/products.json.
const products = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/products' }),
  schema: z.object({
    metaTitle: z.string().max(65),
    metaDescription: z.string().max(170),
    summary: z.string(),
    highlights: z.array(z.string()),
    applications: z.array(z.string()),
    handling: z.array(z.string()).default([]),
  }),
});

// Long-form buyer guides (SEO articles).
const guides = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/guides' }),
  schema: z.object({
    title: z.string(),
    metaTitle: z.string().max(65),
    metaDescription: z.string().max(170),
    summary: z.string(),
    published: z.coerce.date(),
    updated: z.coerce.date().optional(),
    heroProduct: z.string(),
    related: z.array(z.string()).default([]),
  }),
});

export const collections = { products, guides };
