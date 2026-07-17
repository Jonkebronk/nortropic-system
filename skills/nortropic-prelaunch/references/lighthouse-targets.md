# Lighthouse & Core Web Vitals Targets — Full Reference

## Score gates (Lighthouse, MOBILE, production build)
| Category | Gate | Notes |
|---|---|---|
| Performance | **≥90** | Measured on the deployed preview URL, not localhost |
| Accessibility | **≥95** | Automated only catches ~40% — Gate 4 manual checks still required |
| Best Practices | **≥95** | Usually breaks on console errors or mixed content |
| SEO | **≥95** | Usually breaks on missing meta description or illegible font sizes |

Run: chrome-devtools MCP `lighthouse_audit`, or `npx lighthouse <url> --preset=mobile --view`. Run **3 times, take the median** — single runs vary ±5 points.

## Core Web Vitals (lab, mobile 4G throttle)
| Metric | Gate | Typical Nortropic fix when failing |
|---|---|---|
| **LCP** < 2.5s | Hero renders fast | Hero `next/image` with `priority` + AVIF + correct `sizes`; no hero carousels; fonts `display: swap` |
| **CLS** < 0.1 | Nothing jumps | Explicit width/height on ALL images; reserve space for map embeds; no late-loading banners above content |
| **INP** < 200ms | Taps respond | Static site should pass by default — if failing, look for heavy client components that should be server components |

## Weight budgets (Hem, mobile)
- Total transfer < 1 MB · JS < 200 kB gzipped · Hero image < 150 kB (AVIF) · Fonts ≤ 2 families / 4 weights, self-hosted via `next/font`

## Common Nortropic failure patterns
1. **Map embed loaded eagerly on Kontakt** → lazy-load below fold, `loading="lazy"`, or facade pattern (static image → iframe on click)
2. **Team photos straight from phone camera (4MB JPEG)** → run through Next image pipeline, cap at display size ×2
3. **shadcn accordion/sheet pulling client JS into every page** → import only where used
4. **Google Fonts CDN** → forbidden anyway (GDPR practice) — `next/font` self-hosted fixes both
5. **Testimonial/logo carousels** → replace with static grid; carousels hurt LCP and nobody swipes them

## Verification commands
```bash
pnpm build && pnpm start                 # prod build locally
npx lighthouse http://localhost:3000 --preset=mobile --output=json --output-path=./lh.json
node -e "const r=require('./lh.json').categories;console.table(Object.fromEntries(Object.entries(r).map(([k,v])=>[k,Math.round(v.score*100)])))"
```
On Vercel: check the deployment's Speed Insights tab after launch; lab gates above still decide.
