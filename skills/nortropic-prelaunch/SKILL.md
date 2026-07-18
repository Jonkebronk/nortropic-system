---
name: nortropic-prelaunch
description: Pre-launch QA gate for Nortropic Swedish local service websites. Use before launching or deploying any client site — performance gates (Lighthouse, Core Web Vitals), lead-generation gates (click-to-call, quote form email delivery, CTA visibility, conversion tracking), responsive checks, security gate (npm audit, säkerhetsheaders, formulärmissbruk, hemligheter), and Swedish/EU legal compliance (GDPR/Integritetspolicy, cookie consent, Företagsuppgifter). Trigger with /nortropic-prelaunch [url-or-path], or when the user says "are we ready to launch", "prelaunch check", "kan vi lansera", or before /vercel:deploy.
argument-hint: "[url-or-path]"
---

# Nortropic Pre-Launch Gate

Run against `$ARGUMENTS` (preview URL preferred, else local build). **Every gate is PASS/FAIL — no "mostly done".** A site that loses one lead per week because of a broken form costs the client more than a week's delay. Legal findings are NEVER auto-fixed — report them and stop for human judgment.

## Gate 0 — Build Integrity
- [ ] `pnpm build` completes: zero TS errors, zero ESLint errors
- [ ] No `console.log`/`TODO`/lorem ipsum/placeholder images in shipped code
- [ ] `.env.local.example` documents every env var; real values exist in Vercel (`RESEND_API_KEY`, `LEAD_TO_EMAIL`)

## Gate 1 — Lead Generation (THE gate — full targets in this file)
- [ ] **Click-to-call works**: every phone number is a `tel:` link; tap on 375px viewport opens dialer
- [ ] **Phone visible in sticky header** on every page, mobile and desktop
- [ ] **Floating call button** on mobile after scroll, ≥56px target
- [ ] **Quote form end-to-end**: submit a real test lead → **the email ARRIVES at `LEAD_TO_EMAIL`** (check via Resend dashboard/API status or confirmed receipt). Delivery is the test — a 200 response is not
- [ ] Form error state shows the phone number as fallback
- [ ] CTA above the fold on every page at 375×667
- [ ] **Conversion tracking fires**: `phone_click` and `quote_submit` events visible in analytics debug
- [ ] 404 and error pages render the phone number

## Gate 2 — Performance (details: `references/lighthouse-targets.md`)
- [ ] Lighthouse mobile: **Performance ≥90, Accessibility ≥95, Best Practices ≥95, SEO ≥95**
- [ ] **LCP < 2.5s · CLS < 0.1 · INP < 200ms** on 4G-throttled mobile
- [ ] Images WebP/AVIF with explicit dimensions; hero `priority`; total page weight < 1MB on Hem

## Gate 3 — Responsive & Robustness
- [ ] Layouts correct at **375 / 390 / 768 / 1280 / 1920** px — no horizontal scroll, no overlapping header, thumb-reachable CTAs on mobile widths
- [ ] All internal links resolve (crawl for 404s); no mixed content; SSL valid on the production domain
- [ ] `not-found.tsx` + `error.tsx` in Swedish, styled, with phone
- [ ] Favicon + OG images render (test a share preview)

## Gate 4 — Accessibility (escalate to `a11y-audit` for the deep pass)
- [ ] Every image has meaningful Swedish alt text (empty `alt=""` only for decorative)
- [ ] Form labels visible + programmatically associated; error messages announced
- [ ] Keyboard-only pass: nav, accordion, form all operable; focus visible; skip-link works
- [ ] Contrast ≥4.5:1 body, ≥3:1 large text; `prefers-reduced-motion` respected
- [ ] `<html lang="sv">`; heading order sane (one `h1`/page)

## Gate 5 — SEO Launch Readiness (deep pass via `nortropic-seo-lokal`)
- [ ] Unique Swedish title + meta description on every page (`[Tjänst] i [Stad] | Företag` pattern)
- [ ] `sitemap.xml` + `robots.txt` served and correct; canonical URLs set
- [ ] `LocalBusiness` JSON-LD validates (Rich Results Test), NAP matches `content/business.ts` = Google Företagsprofil
- [ ] GSC: domain verified via DNS TXT **before** launch; sitemap ready to submit at cutover

## Gate 6 — Swedish/EU Legal (details: `references/legal-requirements-se.md`) — REPORT ONLY, human decides
- [ ] **Integritetspolicy** page: what data the quote form collects, purpose, legal basis, retention, rights, contact — in Swedish
- [ ] **Cookie consent**: if ONLY Vercel Analytics (cookieless) + necessary cookies → banner not required, but policy still mentions it. Any GA4/pixel/embed cookies → opt-in consent (Consent Mode v2) BEFORE they load
- [ ] **Företagsuppgifter** in footer: company name, org.nr, address, contact
- [ ] Google Maps embed → covered in policy; fonts self-hosted (no Google Fonts CDN — Schrems II practice)
- [ ] If prices shown: inkl. moms for consumers; ROT/RUT claims accurate
- [ ] Marketing claims verifiable (betyg real, "auktoriserad" backed by registration)

## Gate 7 — Säkerhet (details: `references/security-checklist.md`)
- [ ] **Beroenden rena**: `npm audit --omit=dev` — FAIL on any high/critical in production dependencies. Fix: upgrade or replace the package; `npm audit fix` only if the lockfile diff is reviewed
- [ ] **Säkerhetsheaders servas** (verify what is ACTUALLY served: `curl -sI` against the preview URL): Content-Security-Policy (baseline in the reference — copy-paste `headers()` facit for `next.config.ts`), `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `frame-ancestors 'none'` (or `X-Frame-Options: DENY`). Fix: `headers()` in `next.config.ts` — not `vercel.json` when next.config already owns config
- [ ] **Formulärmissbruk** (the quote endpoint): honeypot → silent 200 without email · time-trap rejects an implausibly fast submit — elapsed time measured on ONE clock (client mount→submit, submitted as an `elapsedMs` duration; NEVER a raw timestamp the server compares to its own `Date.now()`, whose client/server skew silently drops real leads — see H1), missing/0 fails open · server-side validation of every field (length caps, email format) · **recipient hardcoded from env `LEAD_TO_EMAIL` — NEVER read from request body** (otherwise the endpoint is an open spam relay) · client-facing errors are generic — no env names, stacks, or Resend responses leak. Rate limiting: platform-level (Vercel WAF/challenge) as optional note — **no DB-based limiter** (breaks static-first)
- [ ] **Hemligheter**: no keys in the client bundle — `grep -r "re_" .next/static` and grep the env var names; `.env*` git-ignored and absent from git history; all API keys only in server code/route handlers

## Verdict Format

```
# Launch Readiness — <site> — <PASS ✅ / BLOCKED ❌>
| Gate | Status | Blockers |
|------|--------|----------|
| 0 Build | ✅/❌ | ... |
| 1 Lead-gen | ✅/❌ | ... |
| 2 Performance | ✅/❌ | ... |
| 3 Responsive | ✅/❌ | ... |
| 4 A11y | ✅/❌ | ... |
| 5 SEO | ✅/❌ | ... |
| 6 Legal | ⚠️ HUMAN REVIEW | findings listed, never auto-fixed |
| 7 Säkerhet | ✅/❌ | ... |
Launch only when 0–5 and 7 all ✅ and a human has signed off 6.
```

## On-Demand Escalation
`a11y-audit` (WCAG deep scan) · `ship-gate` (generic launch gate) · `pw` (Playwright E2E for the form flow) · `seo-technical` / `seo-page` (SEO deep checks) · `security-review` (deep security pass) · `dependency-auditor` (dependency deep-dive) · chrome-devtools/playwright MCP for live viewport + network testing.
