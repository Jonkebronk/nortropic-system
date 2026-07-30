# Google Search Console — Launch Steps Reference

> **Endast skarpa klienter.** För en TESTKLIENT körs INGET av dessa steg — ingen verifiering, ingen sitemap-submit, ingen indexeringsbegäran; testsajten förblir noindex. `scripts/gsc-setup.mjs` avbryter dessutom själv på TESTKLIENT-flaggan i `business.ts`.

## Before launch (during build — förbered mekaniken; `verify` hör till cutover)
1. **Förbered META-verifieringen** (inte DNS TXT) — detta är beredskapen prelaunch **Gate 5** kontrollerar: mekaniken finns, kanonisk variant vald, kund-ägaradress i `business.ts`. META-taggen är en fil i ett repo du äger; DNS TXT kräver kundens registrar (kundens zon ligger normalt hos **Oderland**), så META är standard.
   - **Hämta token + rendera + skeppa till preview:** `node scripts/gsc-setup.mjs token <domän.se> <klientrepo>` hämtar tokenet och skriver `src/content/verification.ts` (bredvid `business.ts`; skriptet letar `src/content/` och faller tillbaka till `content/`). Rendera `<meta name="google-site-verification" content={googleSiteVerification} />` i layouten så taggen skeppas med varje deploy.
   - **`verify` körs INTE här.** META-verifiering kräver att taggen är live på den **kanoniska produktionsdomänen** — och den domänen finns inte förrän kunden lagt DNS vid cutover. Att köra `verify` mot preview är samma omöjliga steg som den gamla DNS-raden, bara åt andra hållet. `verify` hör uteslutande till cutover (Launch day fas 3).
   - **Välj kanonisk variant nu.** URL-prefix: `www` och apex är **skilda properties**. Bestäm vilken som är kanonisk och se till att den andra **301:a** till den. Servar båda `200` utan redirect = delade properties + dubblettinnehåll. `gsc-setup verify` avbryter senare om redirecten pekar bort från den domän du angav.
   - **Kund-ägaradress i `business.ts`.** `GSC_CLIENT_OWNER` fylls ur kundens Google-adress — ha den på plats (eller medvetet noterat att den saknas), så cutover kan lägga kunden som ägare.
   - **Taggen ligger kvar för alltid.** Tas `verification.ts` bort tappas verifieringen och datan slutar komma in, tyst. Den genererade filens kommentar finns för att någon inte ska städa bort den.
   - **DNS TXT kvarstår som dokumenterat undantag** — ENDAST för kunder där du tagit över zonen. Då är Domain property att föredra (täcker www/non-www + båda protokollen i en property). Undantag, inte standard.
2. Confirm `sitemap.ts` outputs all pages (services + areas included) at `/sitemap.xml`
3. Confirm `robots.ts`: allow all, `Sitemap:` line present, **AI-crawlers inte blockerade** på skarp klient
4. If the domain previously hosted an old site: crawl the old URLs, prepare 301 redirects in `next.config.ts` for any URL with traffic/backlinks (check GSC of the old property if accessible)

## Launch day (cutover) — mekaniserat av `/nortropic-cutover` (fas 1–3)
1. Deploy to production domain, confirm SSL (fas 1: domänen i Vercel + verifierad, sajten svarar, sitemap 200)
2. **Verifiera att `noindex` är BORTA** innan GSC-verifieringen (fas 2, före fas 3) — verifierar du en property vars sidor är noindexade får du en som ser korrekt ut men aldrig samlar data. `noindexCutover` i `profile.ts` styr flaggan.
3. **GSC** (fas 3): `gsc-setup.mjs verify` verifierar via META, lägger till ägare, `sites.add` + skickar in `https://domän.se/sitemap.xml`
4. **URL Inspection** → inspektera + "Begär indexering" för: Hem, topp-2 tjänstesidor, Kontakt
5. **Bing Webmaster Tools** (manuellt cutover-steg, ännu ej mekaniserat): importera propertyn **från GSC** (ett klick — ärver verifieringen), skicka in sitemap. Motiv: **Bings index är hämtningslagret för ChatGPT Search och Copilot** — utan Bing är kunden osynlig där, inte bara i Bing self.
6. **IndexNow** (manuellt cutover-steg): nyckelfil svarar `200` i webbroten, deploy-hook aktiv — pushar ändringar till Bing/Yandex direkt i stället för att vänta på crawl.
7. Link GA4 property ↔ GSC (if GA4 in use); Vercel Analytics needs no linking

## Weeks 1–2 (the watch — part of handover)
- **Pages report** (Indexering → Sidor) every 2–3 days:
  - "Upptäckt – för närvarande inte indexerad" → normal first days; if stuck >2 veckor on money pages → request indexing again, strengthen internal links
  - "Genomsökt – för närvarande inte indexerad" on area pages → thin content signal: deepen the local content on those pages
  - Excluded by `noindex` → on a **skarp klient** this is a BUG (staging leftover), fix immediately — UNLESS `profile.ts` deklarerar `noindexCutover.avsiktlig` och `cutoverSenast` ligger i framtiden (avsiktlig pre-cutover, t.ex. Railway→DNS): väntat till cutover, men MÅSTE bort senast `cutoverSenast` (passerad deadline → åter en BUG). On a **TESTKLIENT** noindex is REQUIRED — leave it.
- Performance report: first impressions typically day 2–7 for brand queries, weeks 2–6 for "[tjänst] [stad]"
- **Lighthouse är labbdata, inte det Google rankar på.** Fältmåttet är **CrUX** (Core Web Vitals-rapporten i GSC), men det saknas ofta vid låg trafik — då finns ingen fältdata, inte en dålig sådan. Rapportera **aldrig** en Lighthouse-poäng till kund som "Googles betyg"; den är ett labbverktyg för att hitta regressioner, inte ett omdöme Google fällt.

## Monthly (retainer/handover routine)
1. Performance → Queries, filter position 5–20: each is a page-improvement candidate (add the query's exact phrasing to the page/FAQ)
2. Queries with impressions but no clicks → meta description rewrite candidates
3. Query mining for NEW pages: recurring "[tjänst] [ny ort]" queries justify a new area page; recurring questions justify FAQ entries
4. Check Core Web Vitals report (field data appears after enough traffic) + Manual actions (should always be empty)

> **Söktermslistan är ofullständig.** Google döljer termer med för få användare — totalerna är pålitliga, tabellen är ett urval, och summan av raderna matchar aldrig totalen. Presentera söktermer som exempel, aldrig som facit.

## Ownership — kunden äger, service-kontot behåller åtkomst
Propertyn är **kundens tillgång** — den principen står kvar. Mekaniken (via `gsc-setup.mjs`): service-kontot verifierar via META och blir ägare, lägger sedan till **kunden** (`GSC_CLIENT_OWNER`, kundens Google-adress ur `business.ts`) och **dig** (`GSC_HUMAN_OWNER`) som ägare. Vid offboarding tas service-kontot och du bort; kunden behåller property och historik. Ägarskap i GSC är inte exklusivt, så automation och kundägande går att förena.

- `GSC_CLIENT_OWNER` inte alltid känd vid cutover — skriptet **varnar då, avbryter inte**. Fyll i så snart kundens Google-adress är känd; tills dess äger kunden inte formellt sin property.
