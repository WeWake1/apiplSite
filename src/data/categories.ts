export interface Faq {
  q: string;
  a: string;
}

export interface Category {
  slug: string;
  name: string;
  tab: string; // label on the products page tabs
  heroProduct: string;
  metaTitle: string;
  metaDescription: string;
  summary: string; // one paragraph under the heading (products page + cards)
  intro: string[];
  sections: { heading: string; paragraphs?: string[]; bullets?: string[] }[];
  faqs: Faq[];
}

export const categories: Category[] = [
  {
    slug: 'euro-pallets',
    name: 'Euro-Size Pallets',
    tab: 'Euro-Size',
    heroProduct: 'euro-pallet-1200x800',
    metaTitle: 'Euro-Size Wooden Pallets 1200 × 800 & 1200 × 1000 | Bangalore',
    metaDescription:
      'Euro-size wooden pallets made in Bengaluru: 1200 × 800 × 144, 1200 × 1000 perimeter base and 1000 × 1200 industrial pallets. 4-way, chamfered corners, ISPM-15 heat treated.',
    summary:
      'Pallets built to the Euro pallet family dimensions and construction: 1200 × 800 and two 1200 × 1000 industrial formats, 4-way entry, chamfered corners, heat treated for export.',
    intro: [
      'The 1200 × 800 mm pallet and its 1200 × 1000 mm industrial cousins are the most widely used pallet sizes in Europe, and the default for many Indian exporters. Racking, trucks and containers on export routes are planned around these footprints, so building to them saves re-palletising at the destination.',
      'We build all three formats to the familiar construction: deck boards over cross boards and nine blocks, 45° chamfered corners through every layer, and outer bottom boards chamfered between the blocks so hand pallet trucks roll in easily.',
    ],
    sections: [
      {
        heading: 'Which size do you need?',
        bullets: [
          'EU-1, 1200 × 800 × 144 mm: the Euro footprint for European retail, FMCG and most shipments into the EU.',
          'EU-2, 1200 × 1000 × 162 mm: a heavier industrial pallet with a single-layer perimeter base, good on roller conveyors.',
          'EU-3, 1000 × 1200 × 144 mm: the industrial format for chemicals, bagged goods and larger cartons.',
        ],
      },
      {
        heading: 'Export ready',
        paragraphs: [
          'Every pallet for export is heat treated in our registered facility and stamped with the IPPC mark "IN-081 HT", so it clears customs in all countries that follow ISPM-15 without fumigation certificates.',
        ],
      },
    ],
    faqs: [
      {
        q: 'Are these EPAL pallets?',
        a: 'No. Ambica Patterns does not hold an EPAL licence, so these pallets do not carry the EPAL mark and cannot be exchanged in the EPAL pallet pool. They are built to the same Euro footprint and construction for one-way export shipments and domestic use.',
      },
      {
        q: 'Are your Euro-size pallets heat treated?',
        a: 'Yes, for export. They are heat treated to ISPM-15 and marked "IN-081 HT" with the IPPC symbol on two opposite sides.',
      },
      {
        q: 'How many 1200 × 800 pallets fit in a container?',
        a: 'As a rule of thumb, about 11 in a single layer in a 20 ft container and about 24 in a 40 ft container. The exact number depends on how you load them.',
      },
    ],
  },
  {
    slug: 'cp-pallets',
    name: 'CP-Type Pallets',
    tab: 'CP-Type',
    heroProduct: 'cp3-type-pallet-1140x1140',
    metaTitle: 'CP1–CP9 Type Chemical Pallets | Manufacturer in Bangalore',
    metaDescription:
      'CP-type chemical pallets in all nine CP sizes, CP1 to CP9 (1000 × 1200 to 1140 × 1140), built to the standard CP dimensions and layouts in Bengaluru. ISPM-15 heat treated.',
    summary:
      'All nine chemical-industry formats, CP1 to CP9, built to the standard CP dimensions and board layouts for drums, sacks, octabins and bulk containers.',
    intro: [
      'The nine CP (chemical pallet) formats were created by the European chemical and plastics industry so that drums, sacks, octabins and bulk bags could move through automated filling lines and high-bay stores. Each format has a fixed size, height, board layout and block position, and plants size their conveyors around them.',
      'We build every CP format to those standard dimensions: CP1 to CP5 at 138 mm high with three bottom boards, CP6 to CP9 at 156 mm with a two-layer base.',
    ],
    sections: [
      {
        heading: 'Choosing the right CP format',
        bullets: [
          'CP1 (1000 × 1200): bagged goods, cartons and boxes.',
          'CP2 (800 × 1200): retail-type flows on the Euro footprint.',
          'CP3 (1140 × 1140): square pallet for drums, casks and octabins.',
          'CP4 (1100 × 1300): bagged goods such as polymer granules; the deck overhangs the base.',
          'CP5 (760 × 1140): narrow pallet for cartons and crates.',
          'CP6 (1200 × 1000) and CP7 (1300 × 1100): two-layer base for bagged bulk materials.',
          'CP8 (1140 × 1140): 12 blocks and an open deck centre for containers with a bottom outlet.',
          'CP9 (1140 × 1140): two-layer base for casks and flexible bulk containers (FIBCs).',
        ],
      },
      {
        heading: 'Made for automated plants',
        paragraphs: [
          'A pallet a few millimetres out, or one with a loose board, can stop a filling line. We cut boards and blocks to the CP layout, place blocks and stringer boards at the standard positions and check every batch before it leaves the plant.',
        ],
      },
    ],
    faqs: [
      {
        q: 'What does CP mean on a pallet?',
        a: 'CP means chemical pallet: a family of nine standard sizes, CP1 to CP9, used by the chemical, polymer and plastics industries for drums, sacks and bulk containers.',
      },
      {
        q: 'Are your CP pallets EPAL CP pallets?',
        a: 'No. We build CP-type pallets to the standard CP dimensions and layouts, but we do not hold an EPAL licence, so they carry our ISPM-15 mark and not the EPAL or CP type markings.',
      },
      {
        q: 'Which CP pallet is used for drums?',
        a: 'CP3 (1140 × 1140 × 138 mm) is the usual drum and octabin pallet. CP9 has a two-layer base for heavier casks and FIBCs.',
      },
    ],
  },
  {
    slug: 'pinewood-pallets',
    name: 'Pinewood Pallets',
    tab: 'Pinewood',
    heroProduct: 'pw03-pinewood-pallet-1120x1120',
    metaTitle: 'Pinewood Pallets Manufacturer in Bangalore | 4-Way & 2-Way',
    metaDescription:
      'Pinewood pallets made in Bengaluru: 4-way block, 2-way stringer and skid pallets in 800 × 1200, 1000 × 1200, 1100 × 1100, 1120 × 1120 and custom sizes. ISPM-15 on request.',
    summary:
      'Versatile, cost-effective pinewood block, stringer and skid pallets with an excellent strength-to-weight ratio, in popular sizes or built to yours.',
    intro: [
      'Pinewood is the everyday workhorse of Indian manufacturing and export. It is light, strong for its weight, takes nails without splitting and heat treats well, which keeps freight weight down and suits most export destinations.',
      'Our range covers 4-way block pallets for warehouses and hand pallet trucks, 2-way stringer pallets and simple skids for in-plant use. Every model can be adjusted to your load and handling.',
    ],
    sections: [
      {
        heading: 'Block, stringer or skid?',
        bullets: [
          '4-way block pallets (PW-01, 02, 03, 04, 07, 08): forklifts and hand pallet trucks enter from all four sides.',
          '2-way stringer pallet (PW-06): solid stringers give a stiff pallet for heavier loads moved by forklift.',
          'Skid pallet (PW-05): deck boards on runners, no bottom deck; economical for machinery and one-way shipments.',
        ],
      },
      {
        heading: 'Heat treatment',
        paragraphs: [
          'Any pinewood pallet can be heat treated to ISPM-15 in our registered facility and stamped "IN-081 HT" for export. For domestic use we can supply untreated pallets to keep costs down.',
        ],
      },
    ],
    faqs: [
      {
        q: 'Can you make pinewood pallets in a custom size?',
        a: 'Yes. Many of our orders are built to the customer’s size, load and handling. Send the dimensions or a drawing and we will quote.',
      },
      {
        q: 'Is a 2-way or 4-way pallet better?',
        a: 'A 4-way pallet can be lifted from any side and works with hand pallet trucks. A 2-way stringer pallet is stiffer and often cheaper, which suits heavier loads moved by forklift.',
      },
    ],
  },
  {
    slug: 'hardwood-pallets',
    name: 'Hardwood Pallets',
    tab: 'Hardwood',
    heroProduct: 'hw05-hardwood-pallet-1275x1275',
    metaTitle: 'Heavy-Duty Hardwood Pallets | Manufacturer in Bangalore',
    metaDescription:
      'Heavy-duty hardwood pallets made in Bengaluru: 4-way block, 2-way stringer and skid pallets from 1000 × 1200 to 1275 × 1275 mm for machinery, metals and heavy industrial loads.',
    summary:
      'Dense, heavy-duty hardwood block, stringer and skid pallets for machinery, metal and other heavy or concentrated loads.',
    intro: [
      'When the load is heavy, concentrated or likely to be dropped onto the deck, hardwood is the safer choice. Dense boards resist crushing, hold nails tighter and survive rough handling far longer than softwood.',
      'We build hardwood pallets as 4-way block pallets, 2-way stringer pallets and flush skids, in the sizes below or to your drawing.',
    ],
    sections: [
      {
        heading: 'Where hardwood makes sense',
        bullets: [
          'Heavy machinery, motors, gearboxes and castings',
          'Steel, aluminium and copper products',
          'Returnable pallets used for many trips in one supply chain',
          'Loads placed by crane or dropped onto the deck by forklift',
        ],
      },
    ],
    faqs: [
      {
        q: 'Are hardwood pallets stronger than pinewood pallets?',
        a: 'Board for board, yes: hardwood is denser, resists crushing and holds nails better. It is also heavier, so for light loads pinewood is usually more economical.',
      },
      {
        q: 'Can hardwood pallets be exported?',
        a: 'Yes. They can be heat treated to ISPM-15 and stamped with the IPPC mark like any other wooden pallet.',
      },
    ],
  },
  {
    slug: 'gma-pallets',
    name: 'GMA Pallets',
    tab: 'GMA',
    heroProduct: 'gma-pallet-1220x1016',
    metaTitle: 'GMA Pallet 48 × 40 (1220 × 1016 mm) Manufacturer in India',
    metaDescription:
      'GMA 48 × 40 inch (1220 × 1016 mm) stringer pallets with notched stringers for exports to the USA and Canada. Made in Bengaluru, ISPM-15 heat treated.',
    summary:
      'The 48 × 40 inch North American standard pallet with three notched stringers, for shipments to the USA and Canada.',
    intro: [
      'The GMA pallet, 48 × 40 inches (1220 × 1016 mm), is the most common pallet in North America. Its footprint matches the racking, trailers and warehouses of the USA and Canada, so shipping on GMA pallets avoids re-palletising at the destination.',
    ],
    sections: [
      {
        heading: 'Construction',
        paragraphs: [
          'Seven deck boards sit on three stringers running the 48-inch length, with three bottom boards underneath. Each stringer has two notches with rounded ends, so forklift tines can also enter from the 40-inch sides.',
        ],
      },
    ],
    faqs: [
      {
        q: 'What size is a GMA pallet in millimetres?',
        a: 'A GMA pallet is 48 × 40 inches, about 1220 × 1016 mm.',
      },
      {
        q: 'Do GMA pallets need heat treatment for the USA?',
        a: 'Yes. The USA and Canada require wooden packaging to meet ISPM-15. We heat treat and IPPC-stamp GMA pallets for export.',
      },
    ],
  },
  {
    slug: 'pallet-collars',
    name: 'Pallet Collars',
    tab: 'Collars',
    heroProduct: 'pallet-collar-1200x800',
    metaTitle: 'Wooden Pallet Collars 1200 × 800 | Hinged & Stackable',
    metaDescription:
      'Hinged wooden pallet collars for 1200 × 800 pallets, 195 mm high, with galvanised steel corner hinges. Stack to build a crate, fold flat when empty. Made in Bengaluru.',
    summary: 'Hinged wooden collars that turn a 1200 × 800 pallet into a stackable crate and fold flat when not in use.',
    intro: [
      'A pallet collar is a hinged wooden frame that sits on a pallet to form an open crate. Add one collar for low items or stack several for a deeper box, then fold them flat when the job is done.',
    ],
    sections: [
      {
        heading: 'Common uses',
        bullets: [
          'Turning a pallet into a crate for loose parts, castings or bagged goods',
          'Stackable warehouse storage',
          'Collapsible returnable packaging that folds flat for the return trip',
        ],
      },
    ],
    faqs: [
      {
        q: 'Can pallet collars be stacked?',
        a: 'Yes. The corner hinges locate each collar on the one below, so you can stack several to build the depth you need.',
      },
    ],
  },
];

export const categoryBySlug: Record<string, Category> = Object.fromEntries(categories.map((c) => [c.slug, c]));
