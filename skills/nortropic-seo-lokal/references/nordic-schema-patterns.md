# Nordic Schema & hreflang Patterns — Full Reference

## LocalBusiness (root layout, every page) — Swedish conventions

Use the MOST specific @type: `Plumber`, `Electrician`, `HVACBusiness`, `HousePainter`, `RoofingContractor`, `MovingCompany`, `LockSmith`, or fallback `HomeAndConstructionBusiness` / `LocalBusiness` (cleaning: `LocalBusiness` + `"knowsAbout"`).

```json
{
  "@context": "https://schema.org",
  "@type": "Plumber",
  "@id": "https://www.rorjourstockholm.se/#business",
  "name": "Rörjour Stockholm AB",
  "url": "https://www.rorjourstockholm.se",
  "telephone": "+46812345678",
  "email": "info@rorjourstockholm.se",
  "vatID": "SE556677889901",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Exempelgatan 12",
    "postalCode": "112 34",
    "addressLocality": "Stockholm",
    "addressCountry": "SE"
  },
  "geo": { "@type": "GeoCoordinates", "latitude": 59.3293, "longitude": 18.0686 },
  "openingHoursSpecification": [
    { "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
      "opens": "07:00", "closes": "17:00" }
  ],
  "areaServed": [
    { "@type": "City", "name": "Stockholm" },
    { "@type": "City", "name": "Solna" },
    { "@type": "City", "name": "Sundbyberg" }
  ],
  "priceRange": "$$",
  "image": "https://www.rorjourstockholm.se/images/team/teamet.webp",
  "sameAs": [
    "https://www.hitta.se/...", "https://www.eniro.se/...", "https://www.reco.se/..."
  ]
}
```

Swedish specifics:
- `telephone` in E.164 (`+46...`) — display format stays in visible HTML
- Jour dygnet runt → single spec `"opens": "00:00", "closes": "23:59"` all seven days; avvikande helgdagar via `specialOpeningHoursSpecification` if hours genuinely differ
- `aggregateRating` ONLY with real Google data and only if those reviews are surfaced on the page: `{ "@type": "AggregateRating", "ratingValue": 4.8, "reviewCount": 127 }` — fabricated ratings risk manual action
- `sameAs` → the citation profiles (hitta, eniro, reco, GBP short URL, socials)
- Payment methods NOT in schema (acceptedPaymentMethod is for offers) — put "Swish, kort, faktura" in visible copy instead

## Service (service + area pages)
```json
{
  "@context": "https://schema.org",
  "@type": "Service",
  "serviceType": "Avloppsrensning",
  "provider": { "@id": "https://www.rorjourstockholm.se/#business" },
  "areaServed": { "@type": "City", "name": "Täby" },
  "offers": { "@type": "Offer", "priceCurrency": "SEK", "price": "1495",
              "description": "Fast pris efter ROT-avdrag" }
}
```
Only include `offers` when a real fast-pris exists; omit rather than invent.

## FAQPage (service pages — mandatory FAQ block)
```json
{ "@context": "https://schema.org", "@type": "FAQPage",
  "mainEntity": [
    { "@type": "Question", "name": "Vad kostar avloppsrensning?",
      "acceptedAnswer": { "@type": "Answer",
        "text": "Fast pris från 1 495 kr efter ROT-avdrag för villor i Stockholm..." } }
  ] }
```
Questions must match the visible FAQ text exactly. 3–6 real customer questions per service.

## BreadcrumbList (service + area pages)
Hem → Tjänster → [Tjänst] as `BreadcrumbList` with positions; matches visible breadcrumb.

## hreflang — the honest rules
- **Swedish-only site (Nortropic default): NO hreflang needed.** Do not fabricate variants.
- Real language variants (e.g. `/en` for anglophone customers in Sverige):
```html
<link rel="alternate" hreflang="sv-SE" href="https://site.se/" />
<link rel="alternate" hreflang="en" href="https://site.se/en/" />
<link rel="alternate" hreflang="x-default" href="https://site.se/" />
```
- Rules: bidirectional (every variant lists all, incl. itself) · absolute URLs · `x-default` → the Swedish page (primary market) · Nordic expansion (sv-FI/nb-NO/da-DK) only when real translated content for that market exists — never as an SEO trick
- In Next.js: `alternates.languages` in `generateMetadata`

## Validation gate
Every template validates in Google Rich Results Test + Schema.org validator before launch; re-validate after any content-shape change. JSON-LD only (no microdata), one script per schema object, rendered server-side.
