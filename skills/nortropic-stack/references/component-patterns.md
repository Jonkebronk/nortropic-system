# Nortropic Component Patterns — Full Reference

## Server-first split
Server Components by default. `"use client"` ONLY for: `quote-form.tsx`, `mobile-nav.tsx`, `faq-accordion.tsx`, `floating-call.tsx` (scroll listener), and analytics event wrappers. Everything else — heroes, cards, footers, schema — stays server-rendered.

## The conversion trio (exists on every page)

**1. `<PhoneLink>`** — the ONLY way a phone number appears anywhere:
```tsx
// server-safe; tracking via a tiny client child
export function PhoneLink({ className, children }: Props) {
  return (
    <a href={`tel:${business.phone}`} className={className}
       aria-label={`Ring ${business.name}, ${business.phoneDisplay}`}>
      {children ?? business.phoneDisplay}
    </a>
  )
}
```
Click = primary conversion event (fire `phone_click` to analytics in a client wrapper).

**2. `<QuoteForm>`** — client component, posts to the server action:
- Fields: namn, telefon, epost (optional), tjanst (select from `services`), meddelande + hidden honeypot
- `useActionState` for pending/success/error states
- Error state ALWAYS renders: "Det gick inte att skicka — ring oss direkt på {PhoneLink}" 
- Success: "Tack {namn}! Vi ringer dig inom {promise}." + `quote_submit` event

**3. `<CtaBanner>`** — closing section of every page:
```tsx
<section className="bg-primary text-primary-foreground">
  <h2>Behöver du {service ?? "hjälp"} i {area ?? business.address.city}?</h2>
  <PhoneLink /> <Link href="/kontakt#offert" className={buttonVariants()}>Få kostnadsfri offert</Link>
</section>
```

## Page composition recipes

**Hem**: `Hero` (pain headline + phone + CTA + `TrustRow`) → services grid (`ServiceCard`×N) → how-it-works (3 steps max) → `Testimonials` (3, named + ort) → area coverage (`AreaList`) → `CtaBanner`

**Service page** (`tjanster/[slug]`): `Hero` (service-specific problem headline) → what's included → `priceHint` + ROT/RUT callout → process → service-specific FAQ (also as `FAQPage` schema) → related areas → `CtaBanner service={name}`

**Area page** (`omraden/[slug]`): H1 "「Tjänst」 i 「Ort」" → local intro (genuine local references, no spun text) → services offered there → testimonials filtered by ort when available → `CtaBanner area={ort}`

**Kontakt**: phone + hours FIRST (above form), `QuoteForm`, **consent-gated map facade**, address + org.nr

> **Never embed a live Google Maps `<iframe>` on render.** It fires ~35 requests to Google/US hosts on page load, transfers the visitor's IP to a third country without consent, and contradicts the cookieless "no banner needed" claim (a CRITICAL legal finding). Use a small `"use client"` facade: a self-hosted placeholder (map-pin + address + a "Visa karta" button) that injects the `google.com/maps?...&output=embed` iframe **only on explicit click**, with a factual line ("Kartan laddas från Google först när du klickar"). Google then loads only after consent, so the cookieless-on-load promise stays true. Keep `frame-src https://www.google.com` in the CSP (needed for the post-click iframe). Reference implementation: `map-embed.tsx`.

## shadcn/ui usage
- Install per component: `button`, `card`, `input`, `label`, `select`, `textarea`, `accordion`, `sheet` (mobile nav) — nothing speculative
- Theme via Tailwind 4 `@theme` tokens: `--color-primary` = trade anchor color, `--color-accent` = CTA only
- Never restyle shadcn internals per-usage; extend via `cn()` + variants (cva)
- shadcn now scaffolds **Base UI** primitives (`@base-ui/react`), **not Radix**. The Base UI `Button` has **no `asChild` prop** — to render a link that looks like a button, put `buttonVariants({ variant, size })` on the `<Link>`/`<a>` (import `buttonVariants` from `@/components/ui/button`), never `<Button asChild>`.

## Schema components
`<SchemaMarkup>` renders JSON-LD `<script>` from content:
- Root layout: `LocalBusiness` (from `business.ts`: NAP, geo, öppettider, rating as `aggregateRating` only if real)
- Service pages: `Service` + `FAQPage`
- Area pages: `Service` with `areaServed`
- **Escape before injecting.** Serialize each JSON-LD block and replace every `<` with its Unicode escape `\u003c`: `JSON.stringify(data).replace(/</g, "\u003c")`, then inject via React's dangerous inner-HTML prop (the only SSR way to emit JSON-LD). A raw `<` is blocked by the repo security hook and risks a `</script>` breakout; the `\u003c` escape is valid JSON and renders identically. Do **not** use the HTML entity `&lt;` — it corrupts the JSON.
- **FAQPage marker guard (do not remove).** `FaqSchema` must filter out any answer containing `TODO-FACT`/`TODO-COPY` (`items.filter(i => !i.a.includes("TODO-FACT") && !i.a.includes("TODO-COPY"))`) and return `null` if none remain. This keeps unfinished placeholders out of JSON-LD — intentional, not dead code.
See `nortropic-seo-lokal` skill for the exact Swedish field patterns.

## Accessibility defaults
- Landmark structure: single `<main>`, `<nav aria-label="Huvudmeny">`, skip-link first in DOM
- Focus rings never removed; forms with visible labels + `aria-describedby` errors
- Accordion/nav from shadcn keep their keyboard behavior — don't rebuild primitives by hand
- Swedish `lang="sv"` on `<html>`; `aria-label`s in Swedish

## Performance defaults
- Hero image: `priority`, AVIF/WebP, exact `sizes`
- Fonts: `next/font` self-hosted, `display: swap`, max 2 families/4 weights total
- Map embeds + any video: lazy, below fold, `loading="lazy"`
- No client-side data fetching anywhere — content is imported at build time
