// Company facts used across pages, structured data (schema.org) and the footer.
// Anything left empty ('') is simply not shown.

export const site = {
  url: 'https://ambicapatterns.com',
  name: 'Ambica Patterns',
  legalName: 'Ambica Patterns India Pvt Ltd',
  tagline: 'Perfection is Our Habit !!',
  founded: 2001,
  description:
    'Wooden pallet manufacturer in Bengaluru since 2001: Euro-size and CP-type pallets, GMA, pinewood and hardwood pallets and pallet collars. ISPM-15 heat treatment (IN-081), ISO 9001, PEFC / FSC.',

  address: {
    street: 'No. 6/7, Hesarghatta Main Road, Near Railway Station, Chikkabanavara',
    locality: 'Bengaluru',
    region: 'Karnataka',
    postalCode: '560090',
    country: 'IN',
    countryName: 'India',
  },
  geo: { lat: 13.0777036, lng: 77.5053038 },
  mapsUrl: 'https://maps.app.goo.gl/jrj59N63ReEidAKp8',
  mapsEmbed:
    'https://www.google.com/maps?q=Ambica+Patterns+(INDIA)+Pvt+Ltd,+Chikkabanavara,+Bengaluru&ll=13.0777036,77.5053038&z=15&output=embed',

  phones: [
    { display: '+91 988-683-7016', tel: '+919886837016' },
    { display: '+91 812-332-9333', tel: '+918123329333' },
  ],
  // TODO(owner): confirm which number is on WhatsApp
  whatsapp: '919886837016',
  email: 'sales@ambicapatterns.in',

  hours: {
    label: 'Monday - Saturday: 9:00 AM - 6:00 PM',
    closed: 'Sunday: Closed',
    schema: ['Mo-Sa 09:00-18:00'],
  },

  // Plant protection registration printed in the ISPM-15 mark on every heat-treated pallet
  ippc: 'IN-081',

  // TODO(owner): add profile URLs to show the icons in the footer
  social: {
    linkedin: '',
    facebook: '',
  },

  // Shown in the footer "Licenses" column and on the Quality page. Only what the company holds.
  certifications: [
    {
      id: 'ispm15',
      badge: 'ISPM-15',
      sub: 'IN-081',
      name: 'ISPM-15 heat treatment',
      icon: 'fire-flame-curved',
      text: 'Registered heat-treatment provider IN-081. Export pallets are heat treated and stamped with the IPPC mark "IN-081 HT", accepted by customs worldwide.',
    },
    {
      id: 'iso9001',
      badge: 'ISO 9001',
      sub: '',
      name: 'ISO 9001 quality system',
      icon: 'clipboard-check',
      text: 'Certified quality management system covering timber intake, cutting, assembly, inspection and dispatch.',
    },
    {
      id: 'pefc',
      badge: 'PEFC/FSC',
      sub: '',
      name: 'PEFC / FSC chain of custody',
      icon: 'tree',
      text: 'Certified timber from responsibly managed forests, available on request for customers with sustainability requirements.',
    },
  ],

  googleSiteVerification: '',
  ga4Id: '',
} as const;

export const yearsInBusiness = new Date().getFullYear() - site.founded;

export const fullAddress = `${site.address.street}, ${site.address.locality} - ${site.address.postalCode}, ${site.address.region}, ${site.address.countryName}`;

export const whatsappLink = (text = 'Hello Ambica Patterns, I would like a quote for wooden pallets.') =>
  `https://wa.me/${site.whatsapp}?text=${encodeURIComponent(text)}`;
