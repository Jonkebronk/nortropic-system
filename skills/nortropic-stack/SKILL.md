---
name: nortropic-stack
description: Nortropic tech stack conventions and GitHub-first workflow for Swedish local service business websites. Use when scaffolding, structuring, or reviewing a Nortropic project — Next.js 15 App Router, TypeScript strict, Tailwind CSS 4, shadcn/ui, Vercel, pnpm, static-first with no database, leads via server action + Resend email. Trigger with /nortropic-stack [project-name], or when starting a new client site, deciding file structure, or asking "how do we build sites at Nortropic".
argument-hint: "[project-name]"
---

# Nortropic Stack & Conventions

How every Nortropic site is built. Deviations require an explicit reason written into PROJECT-BRIEF.md.

## The Stack (fixed)

| Layer | Choice | Notes |
|---|---|---|
| Framework | **Next.js 15, App Router** | Static-first: every page statically rendered |
| Language | **TypeScript, strict** | `"strict": true`, no `any` without comment |
| Styling | **Tailwind CSS 4** | Design tokens in `@theme`; no CSS modules, no styled-components |
| Components | **shadcn/ui** | Install via MCP/CLI per component, never fork the whole registry. shadcn now emits **Base UI** primitives (`@base-ui/react`), not Radix — style link-buttons with `buttonVariants()` (no `asChild`); see `references/component-patterns.md` |
| Email (leads) | **Resend** | The ONLY server code on the site |
| Analytics | **Vercel Analytics** (default) | Cookieless → no consent banner needed for it. GA4 + Consent Mode v2 only if the brief demands |
| Hosting | **Vercel** | Linked at scaffold time, deploys from `main` |
| Package manager | **pnpm** | Never npm/yarn in a Nortropic repo |

**NO DATABASE.** Services, service areas, testimonials, FAQ — all typed TS/MDX content in the repo. The quote form posts to one server action that emails the lead. If a client ever needs lead history or bookings, that is a brief-level decision, not a default.

## GitHub-First Workflow (never local-only)

```bash
gh repo create <kebab-name> --private --clone   # 1. repo FIRST
cd <kebab-name>                                  # 2. scaffold INSIDE the clone
pnpm create next-app@15 . --ts --tailwind --app --src-dir --use-pnpm   # pin @15 — @latest now resolves past Next 15
vercel link                                      # 3. Vercel from day one
git add -A && git commit -m "chore: scaffold" && git push -u origin main
```

**Pin `create-next-app@15`.** `@latest` now resolves to a newer major than the Next 15 the stack targets (`package.json` pins `next` 15.x; App Router config, Tailwind 4 tokens and shadcn/Base UI are written for 15). `@latest` scaffolds an unsupported version.

Repo naming: `<client>-<trade>` kebab-case, ASCII only (`rorjour-stockholm`, not `rörjour`). Branch model: `main` deploys; feature branches for anything after first launch.

## File Structure (canonical — full version in `references/file-structure.md`)

```
src/
  app/
    layout.tsx                    # html lang="sv", header/footer/phone, Analytics
    page.tsx                      # Hem
    tjanster/[slug]/page.tsx      # one per service, generateStaticParams
    omraden/[slug]/page.tsx       # one per stad/kommun
    om-oss/page.tsx
    omdomen/page.tsx
    kontakt/page.tsx
    faq/page.tsx
    integritetspolicy/page.tsx
    not-found.tsx                 # Swedish 404 — keeps chrome + phone
    error.tsx                     # Swedish error — keeps chrome + phone
    actions/lead.ts               # THE server action (Zod-validated → Resend)
    sitemap.ts / robots.ts
  components/
    site/                         # header, footer, hero, cta-banner, quote-form...
    ui/                           # shadcn primitives (generated)
  content/
    business.ts                   # NAP, org.nr, öppettider, phone — SINGLE SOURCE
    services.ts / areas.ts / testimonials.ts / faq.ts
  lib/
```

No `(site)` route group — header/footer/phone live in the root `app/layout.tsx` so `not-found.tsx` and `error.tsx` inherit full chrome and the phone number. Matches `references/file-structure.md` and the shipped build.

**`content/business.ts` is sacred**: name, address, phone, org.nr, öppettider live ONLY here and must exactly match the client's Google Företagsprofil (NAP consistency). Header, footer, schema, and copy all import from it.

`content/business.ts` also carries `testklient: boolean` (from the brief's Klienttyp). When `true`, the site is built non-indexable: `robots.ts` reads a `noindex` flag (driven by `NEXT_PUBLIC_NOINDEX=1` in Vercel) and disallows all crawling, and page metadata sets `robots: { index: false, follow: false }`. A fictional/demo business must never be indexable or claimable. This flag + env var are the canonical way any agent detects a TESTKLIENT.

## URL Conventions
- Swedish slugs, å/ä/ö transliterated: `tjanster/varmepumpar`, `omraden/taby`
- Service pages: `/tjanster/<tjänst>` · Area pages: `/omraden/<ort>`
- No trailing slashes, no uppercase, no dates in URLs

## Component Patterns (full version in `references/component-patterns.md`)
- Server Components by default; `"use client"` only for the quote form, mobile nav, and anything with handlers
- Every page composes: `<Hero>` → content sections → `<CtaBanner>` (closing CTA is a shared component, phone from `business.ts`)
- `<PhoneLink>` component wraps every phone number occurrence (renders `tel:` + tracks click as conversion)
- Images through `next/image` with explicit sizes; hero images `priority`
- Schema markup (`LocalBusiness`, `Service`, `FAQPage`) as JSON-LD components fed from `content/*`

## Lead Server Action (the only backend)
`app/actions/lead.ts`: Zod schema (namn, telefon, epost?, tjanst, meddelande, honeypot) → validate → send via Resend to the business owner (subject: "Ny offertförfrågan — <tjänst> i <ort>") → return typed result. Rules:
- Honeypot field + submission-time check for spam (no CAPTCHA — friction kills leads)
- On email failure: return error state telling the visitor to CALL, with the number — a lead must never dead-end
- `RESEND_API_KEY` + `LEAD_TO_EMAIL` via Vercel env vars; never committed

## Quality Baseline (enforced by /nortropic-review and /nortropic-launch)
- Lighthouse: Performance ≥90, Accessibility ≥95, Best Practices ≥95, SEO ≥95 (mobile)
- Zero TypeScript errors, zero ESLint errors at commit
- Prettier formatting via project PostToolUse hook
- Every page exports `generateMetadata` with Swedish title/description per `nortropic-seo-lokal` templates

## On-Demand Escalation
- `spec-to-repo` / `saas-scaffolder` — scaffold mechanics beyond this skill
- `react-best-practices` / `composition-patterns` — component architecture decisions
- `senior-frontend` — hard frontend problems
- `vercel-geist-design` — Vercel platform conventions
- `shadcn-ui` MCP + `context7` MCP — component installs and current library docs
