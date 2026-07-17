---
name: nortropic-seo-lokal
description: Swedish local SEO playbook for Nortropic local service business websites. Use when optimizing a Swedish trades/service site for local search — "[tjänst] i [stad]" keyword strategy, Swedish citations (eniro, hitta.se, reco), LocalBusiness schema with Swedish conventions, Nordic hreflang, service-area pages per kommun, Google Företagsprofil checklist, and Google Search Console launch steps. Trigger with /nortropic-seo-lokal [url-or-business], or for "lokal SEO", "rank in Swedish local search", "GBP optimization", "Google Företagsprofil".
argument-hint: "[url-or-business]"
---

# Nortropic Lokal SEO — Swedish Market Playbook

Local SEO for a Swedish trades business has three legs: **the site** (this skill's on-page rules), **Google Företagsprofil** (checklist a human executes — `references/gbp-checklist.md`), and **citations/omdömen** (`references/swedish-directories.md`). NAP consistency across all three is the foundation: name, address, phone **exactly** as written in `content/business.ts`.

## Keyword Strategy: the "[tjänst] i [stad]" formula

Swedes search `elektriker uppsala`, `stopp i avloppet täby`, `flyttstädning västerås pris`. Structure:
- **One service page per tjänst**: targets `[tjänst]` + `[tjänst] [huvudort]` — `/tjanster/avloppsrensning`
- **One area page per ort/kommun**: targets `[huvudtjänst] i [ort]` — `/omraden/taby`
- **Hem**: targets `[yrke/kategori] [huvudort]` ("Rörmokare Stockholm")
- Long-tail lives in FAQ blocks: "vad kostar avloppsrensning", "rörmokare jour pris", "gäller rot-avdrag för..."

Rules: å/ä/ö transliterate in slugs (`/omraden/taby`), keep å/ä/ö in titles/H1/copy. Never spin area pages — each needs genuinely local content (local landmarks, real jobs done there, restider) or it's thin-content risk. Start with the orter where the business actually works; 5 real area pages beat 25 spun ones.

## Meta templates (per page type)
| Page | Title (≤60 chars) | Description (≤155 chars) |
|---|---|---|
| Hem | `[Yrke] [Stad] — [USP kort] \| [Företag]` | yrke + områden + proof (betyg, jour, fast pris) + phone |
| Tjänst | `[Tjänst] i [Stad] \| [Företag]` | what+where+price signal+CTA "Ring 08-..." |
| Område | `[Tjänst] i [Ort] — [respons-USP] \| [Företag]` | local promise + proof + phone |
| Om oss | `Om [Företag] — [yrke] sedan [år]` | history + certifikat + area |

Never superlatives in meta; numbers and place names win the click.

## Schema (JSON-LD — full patterns in `references/nordic-schema-patterns.md`)
- Root: `LocalBusiness` (use the specific subtype: `Plumber`, `Electrician`, `HousePainter`, `MovingCompany`, `HVACBusiness`...) with Swedish `PostalAddress`, `openingHoursSpecification` (incl. avvikande helgdagar), `telephone` E.164, `areaServed`, `priceRange` in SEK, `aggregateRating` ONLY from real Google data
- Service pages: `Service` + `FAQPage` (drives rich snippets — the FAQ block is mandatory on service pages)
- Area pages: `Service` with `areaServed` → the specific `City`/`AdministrativeArea`
- Validate every page in Rich Results Test before launch

## On-page rules
- H1 = target keyword naturally phrased, ONE per page
- Phone number in crawlable text (not image/JS-injected) on every page
- Internal linking: Hem → all services; every service ↔ related services; every area → services offered there; footer links all areas (that's the NAP+area crawl path)
- Bilder: filenames in Swedish (`avloppsrensning-taby-fore.webp`), alt text descriptive Swedish
- `hreflang` only when the site truly has language variants (see `references/nordic-schema-patterns.md` §hreflang) — a Swedish-only site needs NONE (self-referencing optional). Never fake sv-FI/nb-NO variants for SEO.

## Citations & omdömen (execution list: `references/swedish-directories.md`)
Priority order: Google Företagsprofil → hitta.se → eniro.se → reco.se → trustpilot.se (if client wants) → merinfo/allabolag (auto-listed from Bolagsverket — verify correctness, don't create). Same NAP everywhere. Omdömen strategy: ask EVERY happy customer for a Google review with a direct review link (QR on faktura works); respond to every review in Swedish within a week.

## Launch & post-launch (execution list: `references/gsc-launch-steps.md`)
DNS TXT verification BEFORE launch → sitemap submitted at cutover → URL-inspect Hem + top service pages → watch Page indexing report for 2 weeks → then monthly: Performance query mining (new FAQ/area page ideas from real queries).

## On-Demand Escalation
`seo-local` (general local SEO) · `seo-schema` (schema deep work) · `seo-technical` (crawl/index issues) · `seo-sitemap` · `seo-page` (per-page optimization) · `seo-content` (content briefs) · `seo-images` · `seo-hreflang` (only if multi-language actually exists) · `local-seo-manager` (GBP management practices) · `seo-google` / `seo-maps` (Google surface specifics)
