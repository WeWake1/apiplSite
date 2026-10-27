// @ts-check
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://ambicapatterns.com',
  trailingSlash: 'always',
  // keep HTML-aware whitespace (Astro 7 defaults to JSX rules, which glue inline words together)
  compressHTML: true,
  build: {
    format: 'directory',
    inlineStylesheets: 'auto',
  },
  prefetch: { prefetchAll: false, defaultStrategy: 'hover' },
});
