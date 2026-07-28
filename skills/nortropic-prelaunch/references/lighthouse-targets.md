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

### Bildbudget per slot-prefix (enforced av treatment.mjs budgetloop)
| Slot-prefix | Budget (avif) |
|---|---|
| `hero-*` | 150 kB |
| `people-*` | 100 kB |
| övriga (`env`/`proof`/`detail`/`og`) | 120 kB |

Behandlingen kodar avif q55 och sänker i steg om 5 (golv q35) tills budgeten hålls;
golv nått utan budget → WARN-rad i `BILDRAPPORT.json`, aldrig byggfel. **q55 är ett
TAK av kompressionsskäl, inte en smakinställning** — uppmätt klippa q55→q60
(dokumentar 59→206 kB, ljus 71→278 kB, 2400×1350 högentropisk källa); q60+ sätts
aldrig utan ny mätning. Preset-kostnaden är inte intuitiv (duotone dyrast vid q55 —
tint återinför kroma), därför mäts storleken per bild, aldrig antas per preset.
**Spår A + preset `ljus` är kundprofilen närmast LCP-gränsen** (flest foton, minst
overlay) — extra uppmärksamhet på hero-storleken där.

## Common Nortropic failure patterns
1. **Map embed loaded eagerly on Kontakt** → lazy-load below fold, `loading="lazy"`, or facade pattern (static image → iframe on click)
2. **Team photos straight from phone camera (4MB JPEG)** → mekaniskt löst av behandlingssteget: filen läggs i `public/images/raw/` med slot-id-prefix och prebuild (`scripts/treatment.mjs`) normaliserar, beskär och budgetkodar den — aldrig manuell nedskalning
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
