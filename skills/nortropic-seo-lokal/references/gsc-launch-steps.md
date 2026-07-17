# Google Search Console — Launch Steps Reference

## Before launch (during build — do NOT wait for launch day)
1. **Verify the domain early**: GSC → Add property → **Domain property** (covers www/non-www, http/https) → DNS **TXT record** at the registrar (Loopia/one.com/Cloudflare — client's registrar). Propagation can take hours; doing this pre-launch means indexing starts day one
2. Confirm `sitemap.ts` outputs all pages (services + areas included) at `/sitemap.xml`
3. Confirm `robots.ts`: allow all, `Sitemap:` line present
4. If the domain previously hosted an old site: crawl the old URLs, prepare 301 redirects in `next.config.ts` for any URL with traffic/backlinks (check GSC of the old property if accessible)

## Launch day (cutover)
1. Deploy to production domain, confirm SSL
2. GSC → Sitemaps → submit `https://domain.se/sitemap.xml`
3. **URL Inspection** → inspect + "Begär indexering" for: Hem, top 2 service pages, Kontakt
4. Link GA4 property ↔ GSC (if GA4 in use); Vercel Analytics needs no linking

## Weeks 1–2 (the watch — part of handover)
- **Pages report** (Indexering → Sidor) every 2–3 days:
  - "Upptäckt – för närvarande inte indexerad" → normal first days; if stuck >2 veckor on money pages → request indexing again, strengthen internal links
  - "Genomsökt – för närvarande inte indexerad" on area pages → thin content signal: deepen the local content on those pages
  - Excluded by `noindex` → BUG, fix immediately (leftover from staging)
- Performance report: first impressions typically day 2–7 for brand queries, weeks 2–6 for "[tjänst] [stad]"

## Monthly (retainer/handover routine)
1. Performance → Queries, filter position 5–20: each is a page-improvement candidate (add the query's exact phrasing to the page/FAQ)
2. Queries with impressions but no clicks → meta description rewrite candidates
3. Query mining for NEW pages: recurring "[tjänst] [ny ort]" queries justify a new area page; recurring questions justify FAQ entries
4. Check Core Web Vitals report (field data appears after enough traffic) + Manual actions (should always be empty)

## Ownership
Property owner = client's Google account (their asset), Nortropic added as **Full user** — mirrors GBP ownership so offboarding never loses data.
