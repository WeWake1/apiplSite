# ambicapatterns.com

Website of Ambica Patterns India Pvt Ltd, built with [Astro](https://astro.build) as a static site and hosted on Hostinger.

The design is the original Ambica Patterns site (same header, footer, fonts, colours, animations and tabbed product page), rebuilt in Astro with the full 28-model product library, SEO and faster loading. Product images are studio renders made in Blender from each pallet's real dimensions, and every product can also be viewed in 3D (the model only downloads when a visitor taps "3D").

Ambica Patterns does **not** hold an EPAL licence. The Euro-size and CP-type pallets are built to the standard dimensions but carry only the ISPM-15 mark **IN-081 HT**: never add EPAL logos, the EPAL oval or "EPAL licensed" wording to this site.

## Quick start

```bash
npm install          # once
npm run dev          # local preview at http://localhost:4321 with live reload
npm run build        # production build into dist/
npm run preview      # serve dist/ locally
```

Requires Node 22.22 or newer.

## Where things live

| What | Where |
|---|---|
| Company details (phones, address, WhatsApp, certifications, IPPC code, social links, analytics ID) | `src/data/site.ts` |
| Product list: slug, 3D recipe id, code, size, construction, wood | `src/data/products.json` |
| Product descriptions, meta titles, bullet points | `src/content/products/<slug>.md` |
| Product families (tabs, category pages, buying advice, FAQs) | `src/data/categories.ts` |
| Buyer guides / articles | `src/content/guides/<slug>.md` |
| Pages (home, about, products, quality, contact…) | `src/pages/` |
| Header, footer, scripts (smooth scroll, animations, menu) | `src/layouts/Base.astro` |
| Product rows, cards, 3D viewer, FAQ, breadcrumbs | `src/components/` |
| Styles (the old `style.css` plus a short additions section at the end) | `src/styles/legacy.css` |
| Factory photos | `src/assets/photos/` |
| Rendered product images | `src/assets/products/<slug>/1-5.webp` |
| 3D models (loaded on tap) and the 3D viewer script | `public/models/<slug>.glb`, `public/vendor/` |
| Server rules (redirects, caching), quote form handler, robots.txt | `public/.htaccess`, `public/contact.php`, `public/robots.txt` |
| Internal pallet spec-sheet tool (not indexed) | `public/pallet-designer/` |
| Old static site, kept for reference | `legacy-site/` (not deployed) |
| SEO action plan | `docs/seo-plan/` |

## Common edits

**Change a phone number, email or WhatsApp number:** edit `src/data/site.ts`, then rebuild. It updates every page, the footer and Google's structured data.

**Edit a product description:** edit `src/content/products/<slug>.md`. `metaTitle` must stay within 65 characters and `metaDescription` within 170 (the build checks this).

**Add a guide:** copy a file in `src/content/guides/`, change the front matter and text. It appears on /guides/, in the sitemap and on the home page automatically.

**Add a new pallet:**
1. Add a build recipe to `tools/render/pallets.py` (copy a similar pallet; every board, block and stringer is listed in millimetres) and run `python3 tools/render/pallets.py`. Its table must say `ok` for the new pallet: that checks the outside dimensions, overlaps and floating parts.
2. Add an entry to `src/data/products.json` with `"pallet": "<recipe id>"`.
3. Add `src/content/products/<slug>.md` with original text. The build fails if a product has no copy file.
4. Render its images and 3D model: `npm run render -- <slug>` (about 70 seconds).
5. Build and deploy.

Never copy descriptions from other websites: Google shows only the original and hides copies.

## Rendering product images and 3D models

```bash
tools/render/fetch_textures.sh                 # once: downloads the CC0 wood textures (ambientCG)
npm run render                                 # all 28 products (~33 min on an M2 Pro)
npm run render -- cp3-type-pallet-1140x1140    # one product
```

Needs Blender 5.x at `/Applications/Blender.app` (override with `BLENDER=/path/to/blender`).

- `tools/render/pallets.py`: exact component layout of every pallet, checked against the official EPAL / CP drawings where they exist. Corner chamfers cut through every layer at that corner; bottom-board chamfers only where the drawings show them, between the blocks.
- `tools/render/brand.json`: which markings go on the pallets. For Ambica only the IPPC mark `IN-081 HT` (made by `tools/render/make_stamps.py`), and 3D models are switched on (`"glb": true`).
- Output: 5 views per product (collar: 4) on a #F2F2F2 background matching the website's image panels, in `src/assets/products/<slug>/<n>.webp`, plus `public/models/<slug>.glb`. Full-size PNGs stay in `tools/render/out/` (git-ignored).
- Close-up of a marking (used on the quality page): `Blender --background --factory-startup --python tools/render/render_pallet.py -- --recipe epal1 --views 9 --detail-index 0 --out <folder>`.

## Hosting on Hostinger

The built site is plain static files plus one small PHP file for the quote form, so it runs on any Hostinger web hosting plan (Single, Premium, Business). Those plans include PHP and read `.htaccess` (LiteSpeed). If your plan cannot run PHP, the pages still work; switch the form's `action` in `src/pages/contact/index.astro` to a form service such as Formspree.

1. `npm run build`
2. In hPanel → File Manager (or FTP), open `public_html` for **ambicapatterns.com**. Back up the current files, then upload **the contents of `dist/`** (including the hidden `.htaccess` and `_astro/.htaccess`).
3. Make sure the mailbox `website@ambicapatterns.com` exists (hPanel → Emails). The quote form sends from it to `sales@ambicapatterns.in`; change both at the top of `public/contact.php` if needed.
4. hPanel → Performance → CDN → **Purge cache**.
5. Check:
   - https://ambicapatterns.com/ loads the new site, and tapping "3D" on a product shows the model
   - https://ambicapatterns.in/ and https://www.ambicapatterns.com/ redirect to https://ambicapatterns.com/
   - https://ambicapatterns.com/about.html redirects to /about/
   - the quote form delivers a test message
6. Submit `https://ambicapatterns.com/sitemap.xml` in Google Search Console, and run "Test live URL" on the home page. Hostinger's CDN showed a JavaScript challenge page to automated browsers during testing; if Google's live test shows a challenge page instead of the site, turn off bot protection / "under attack" mode in hPanel, or ask Hostinger support to allow verified search engine bots.

If ambicapatterns.in is a separate website (not an alias) in hPanel, either upload the same `.htaccess` there or add a 301 redirect to https://ambicapatterns.com in hPanel → Domains → Redirects.
