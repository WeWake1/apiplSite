# Search Console exports (ambicapatterns.com)

Raw exports from Google Search Console, one dated folder per export. The original zip files are in `originals/`. Each new export goes in a new folder named `YYYY-MM-DD-<report>`; old ones are never overwritten, so they can be compared over time.

## 2026-11-11-page-indexing

Indexing > Pages report. Google's data was last updated 6 Nov 2026, the day before the sitemap was submitted.

- **18 indexed, 15 not indexed.** Of the 18, 14 are real pages of the new site. The other 4 are two old addresses (`www…/about.html`, `www…/contact.html`, crawled in Sep/Oct) and two quote links (`/contact/?product=cp3-…`, `…pw06-…`).
- The other 30 of the 44 sitemap pages had not been processed yet when the report was made.
- Not indexed, by reason (URLs read in Search Console on 11 Nov 2026):

| Reason | Pages | URLs | Verdict |
|---|---|---|---|
| Alternate page with proper canonical tag | 7 | `/contact/?product=<product>` quote links | Correct behaviour: they point Google to `/contact/` |
| Page with redirect | 5 | `http://`, `http://www.`, `https://www.`, `/index.html`, `www…/index.html` | Intended 301s to the home page |
| Not found (404) | 2 | `/index.php` and `www…/index.php` | Old-site address with no redirect: fix |
| Crawled - currently not indexed | 1 | `www…/products.html` (crawled 31 Jul 2026) | Old address, redirects now; will move to "Page with redirect" |

## 2026-11-11-performance

Performance report, web search, "last 3 months" (data only starts 4 Nov 2026).

- 4–9 Nov: **3 clicks, 238 impressions, average position about 6.**
- Pages: `http://www.ambicapatterns.com/` (the old address) still got 171 impressions. Google will swap it for `https://ambicapatterns.com/` as it re-processes the site.
- Clicks came from the ISPM-15 guide, the home page and the pallet-collars page.
- Countries: India 189 impressions, USA 30, then 15 other countries with 1–3 each.
- Devices: desktop 123, mobile 112, tablet 3.
- Queries include several about pallet furniture ("pallet bed bangalore", "pallet bed near me") that are not buyers. Keyword research (step 4) will steer the site away from these.
