# Pallet catalogue handoff (for the EPAL-licensed company's new website)

Give this file to Claude Code in the new project, together with the short assets brief. It lists all 28 pallets, what is reusable from the Ambica Patterns project (`~/VSC/APIPL/apiplSite`), and what must change because this company holds the EPAL licence and Ambica does not.

## 1. The 28 pallets

Dimensions are L × W × H in mm. **L is the direction the top deck boards run; W runs across them.** The source of truth is `src/data/products.json` and `tools/render/pallets.py` in the Ambica repo. "Recipe" is the id used by the render pipeline.

### Euro / EPAL family (3)
| Code | Recipe | Size (mm) | Entry | Construction |
|---|---|---|---|---|
| EU-1 (**EPAL 1**) | epal1 | 1200 × 800 × 144 | 4-way | 11 boards, 9 blocks; double deck; chamfered corners |
| EU-2 (**EPAL 2**) | epal2 | 1200 × 1000 × 162 | 4-way | 17 boards, 9 blocks; single-layer perimeter base |
| EU-3 (**EPAL 3**) | epal3 | 1000 × 1200 × 144 | 4-way | 13 boards, 9 blocks; double deck |

### CP chemical pallets (9)
| Code | Recipe | Size (mm) | Entry | Construction |
|---|---|---|---|---|
| CP1 | cp1 | 1000 × 1200 × 138 | 4-way | 15 boards, 9 blocks; 3 bottom boards |
| CP2 | cp2 | 800 × 1200 × 138 | 4-way | 13 boards, 9 blocks; 3 bottom boards |
| CP3 | cp3 | 1140 × 1140 × 138 | 4-way | 15 boards, 9 blocks; 3 bottom boards |
| CP4 | cp4 | 1100 × 1300 × 138 | 4-way | 15 boards, 9 blocks; deck overhangs a 1200 × 1000 base |
| CP5 | cp5 | 760 × 1140 × 138 | 4-way | 13 boards, 9 blocks; 3 bottom boards; square corners |
| CP6 | cp6 | 1200 × 1000 × 156 | 4-way | 20 boards, 9 blocks; two-layer base |
| CP7 | cp7 | 1300 × 1100 × 156 | 4-way | 22 boards, 9 blocks; two-layer base |
| CP8 | cp8 | 1140 × 1140 × 156 | 4-way | 12 blocks, 4 stringer boards; two-layer base, open deck centre |
| CP9 | cp9 | 1140 × 1140 × 156 | 4-way | 9 blocks; two-layer base |

Typical use: CP1 bagged goods and cartons; CP2 retail chains on the Euro footprint; CP3 drums, casks, octabins; CP4 polymer granule bags; CP5 cartons and crates; CP6/CP7 bagged bulk; CP8 large containers with a bottom outlet; CP9 casks and FIBCs.

### Pinewood (8): not EPAL
| Code | Recipe | Size (mm) | Entry | Construction |
|---|---|---|---|---|
| PW-01 | pw01 | 800 × 1200 × 130 | 4-way | 11 boards, 9 blocks; double deck, non-reversible |
| PW-02 | pw02 | 1000 × 1200 × 130 | 4-way | 17 boards, 9 blocks; perimeter base |
| PW-03 | pw03 | 1120 × 1120 × 130 | 4-way | 13 boards, 9 blocks; double deck |
| PW-04 | pw04 | 1120 × 1120 × 150 | 4-way | 20 boards, 9 blocks; two-layer base, full bottom deck |
| PW-05 | pw05 | 1100 × 1100 × 130 | 2-way | 7 deck boards, 3 runners; skid, single face, flush |
| PW-06 | pw06 | 1140 × 1140 × 130 | 2-way | 12 boards, 4 stringers; flush (owner confirmed 1140, not 1100) |
| PW-07 | pw07 | 1000 × 1000 × 146 | 4-way | 17 boards, 9 blocks; perimeter base |
| PW-08 | pw08 | 1100 × 1100 × 146 | 4-way | 17 boards, 9 blocks; perimeter base, chamfered bottom boards |

### Hardwood (6): not EPAL
| Code | Recipe | Size (mm) | Entry | Construction |
|---|---|---|---|---|
| HW-01 | hw01 | 1000 × 1200 × 161 | 4-way | 18 boards, 9 blocks; perimeter base, double face |
| HW-02 | hw02 | 1200 × 1000 × 161 | 4-way | 14 boards, 9 blocks; double face, chamfered bottom boards |
| HW-03 | hw03 | 1200 × 1200 × 144 | 2-way | 12 boards, 3 stringers; double face, flush |
| HW-04 | hw04 | 1235 × 1200 × 122 | 2-way | 10 deck boards, 4 runners; near-solid deck, single face skid |
| HW-05 | hw05 | 1275 × 1275 × 161 | 4-way | 18 boards, 9 blocks; chamfered corners and bottom boards |
| HW-06 | hw06 | 1200 × 1200 × 144 | 2-way | 16 boards, 4 stringers; double face, flush |

### GMA (1) and collar (1): not EPAL
| Code | Recipe | Size (mm) | Entry | Construction |
|---|---|---|---|---|
| GMA | gma | 1220 × 1016 × 132 (48 × 40 in) | 4-way (partial) | 10 boards, 3 notched stringers; notches ~230 × 38 mm, radius ~32 mm |
| PC-1208 | collar | 1200 × 800 × 195 | n/a | Planed softwood, 4 boards, 4 galvanised steel hinges; folds flat |

Wood: EPAL 1–3 and CP1–CP9 are softwood (pine / spruce). PW is pinewood, heat treatable to ISPM-15. HW is seasoned hardwood.

## 2. What can be reused from the Ambica repo

- **3D layouts:** `tools/render/pallets.py` lists every board, block and stringer in mm and prints a check table (every row must say `ok`).
- **Renderer:** `tools/render/render_pallet.py` (Blender 5.x headless, Cycles on METAL GPU only), `render_all.sh`, `make_stamps.py`, `fetch_textures.sh`, `brand.json`. Command: `npm run render` for everything (about 33 min on an M2 Pro for 28), or `npm run render -- <slug>` for one product.
- **Renders:** WebP files in `src/assets/products/<slug>/` (5 views; collar 4). **GLB models** in `public/models/<slug>.glb`.
- **Catalogue data:** `src/data/products.json`, `src/data/categories.ts`.
- Needs `brew install webp` (cwebp) before rendering, because the script deletes the old images first.
- The existing Pallet Euro repo (`github.com/WeWake1/PalletEuro`, 13 products, EPAL-licensed, same owner) already has the EPAL marking setup. If the new site is that company, extend that repo to 28 instead of starting again.

## 3. What MUST change: the existing renders and GLBs carry Ambica's marking

Every render and GLB in the Ambica repo has the **IPPC mark "IN-083 HT"** (Ambica's heat-treatment registration) baked into the blocks, and none has the EPAL oval. Do not publish them on this company's site as they are.

1. Set this company's `brand.json` (`"epal": true`, its own IPPC `country`/`code`/`treatment`, and the `marks` layout below), then re-render. Never invent the code, licence number or company details; leave placeholders and `noindex` until the owner supplies them.
2. Re-export the GLBs too, because the stamps are baked into the textures. `web_gain` was calibrated for `<model-viewer>` with `environment-image="legacy"` on a white viewer; recalibrate if the look changes.

### Where the marks go (from EPAL's own sheets; EPAL-licensed pallets only)
- **EPAL 1, 2, 3:** EPAL oval on the left AND right corner blocks. IPPC mark (plus licence number, year and month) on the centre block.
- **CP1–CP9:** IPPC mark on the left-hand corner block, the CP type and EPAL ID on the centre block, EPAL oval on the right-hand corner block.
- **PW, HW, GMA, collar are NOT EPAL pallets.** They get the IPPC mark only, with no EPAL oval and no EPAL claims.
- Never stamp the company name on the pallets.

## 4. Render rules from the owner (do not break)

- **Chamfers only where the official drawing has them.** No generic bevels.
- **Corner chamfer** cuts through every layer at that corner (top board, cross board, block, bottom board): EPAL 1 = 17 mm, EPAL 2/3 = 24 mm, CP = 20 mm, all at 45°.
- **Outer bottom boards of EPAL-type pallets:** chamfered only between the blocks, on the outer top edge, about 11 mm deep with curved run-outs. The pinewood middle bottom board has no chamfer.
- **GMA notches** are rounded, not rectangles.
- **Dimensions** were checked against the official EPAL and CP drawings (free at epal-pallets.org). Board and block counts match for EPAL 1–3 and CP1–CP7.
- **Look (approved 5 Nov 2026):** high-key studio, white background, overhead softbox, camera at 24°, 3 mm eased edges, pale straight-grain spruce, small bright nails, a few knots on one deck board per pallet, CC0 wood textures from ambientCG (Wood096 pine, Wood060 hardwood). Do not use Wood095 (rejected). Never open the `.blend` files inside the texture zips.
- If the look is changed, test **one pallet first** and get the owner's OK before re-rendering all 28.

## 5. Open issues to settle

- **CP8 / CP9 board counts:** EPAL's sheets say 28 and 24 boards, but the drawings give 21 and 18, and the renders follow the drawings. The Ambica spec tables show EPAL's numbers. Settle it with the licence documents (a licensed company will have them).
- **PW / HW / GMA / collar** have no public standard. Their layouts were measured from a reference range, so this company should check them against its real production drawings. The owner says it makes these exact pallets, so its own drawings win.
- **EPAL load ratings** may be published only for licensed pallets, so they can go on EPAL 1/2/3 and CP pages here (they were removed from Ambica).

## 6. Content and site rules

- **Specs match Jay Wood's product range, but all text must be original.** Never copy descriptions and never publish Jay Wood's images or text.
- **Naming:** on this site use the real names (EPAL 1/2/3, CP1–CP9, "pallet collar"). Ambica's "Euro-size" naming was only there because Ambica is unlicensed.
- **Do not copy Ambica's page text.** It says things like "we do not hold an EPAL licence" and contains Ambica's address, phones and certifications.
- **Do not reuse Ambica's photos.** Use renders only until real factory photos arrive.
- **Tech:** Astro static site for Hostinger, one PHP file for the quote form, LiteSpeed `.htaccess`. Product image first; the GLB loads only when the visitor taps "3D".
- **Phones:** no scroll-driven animation (pinned or pop-out motion was laggy on a real phone), no dot-grid background, no Lenis smooth scroll. Keep the 3D model off the first load on touch devices (the 1 MB viewer script dropped mobile Lighthouse from 100 to 69). Taps use an `.is-pressed` tint, not the browser's square flash.
- **Reference scores to beat:** Lighthouse mobile 99–100 across the board.
- **Go-live gate:** a `site.launchReady = false` flag in `src/data/site.ts` puts `noindex` on every page until the real company name, address, phones, WhatsApp, email, EPAL licence number and IPPC code are filled in.

## 7. Working style with this owner

Offer options and get approval at each design decision, and don't choose silently. For motion or visual choices, show a working demo. Put the owner's answers in a handoff file so they are not asked twice.
