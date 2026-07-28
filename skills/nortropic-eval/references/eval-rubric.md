# Nortropic Eval Rubric

**Rubrikversion: v3.0.0**

> Semver. Bump on **any** change to criteria, weights, or thresholds so scores stay comparable over time: PATCH = wording/clarification, MINOR = threshold/guidance change, MAJOR = criteria or weights change. Record the version used in every `EVAL-RESULT.md`. Never compare totals across different MAJOR/MINOR versions without noting it.

100 points across 11 weighted criteria. A criterion's **Status = PASS** when it earns **≥ 70 %** of its weight, otherwise **FAIL**. The site total is the sum of criterion points. **Faktatrohet (criterion 2) is also a hard gate:** any untraceable factual claim → the whole eval is reported **FAIL** regardless of total (see SKILL.md).

Score conservatively and cite `file:line` for every deduction. Testklient placeholders that are correctly gated (empty `certId`, `TODO-FACT`/`TODO-COPY` markers, `aggregateRating` omitted from schema, grayscale SVG photo placeholders) are the **correct** handling of a missing fact — never deduct for them; deduct only for a *false* or *ungated* claim.

---

## 1. Konverteringsarkitektur — 15 p
The site's one job: get a stressed mobile visitor to utföra PRIMÄRHANDLINGEN enligt `content/profile.ts` — omedelbart nåbar, mobilergonomisk, ≤5 formulärfält där formulär ingår. **Offert/samtal-fallet (hantverkar-defaulten) = exakt dessa fem delkrav:**
- tel:-länkar på varje telefonnummer (klickbart på mobil) — 3
- Sticky header med synligt nummer + ring-knapp på alla sidor — 3
- Primär CTA ("Ring" / "Få offert") above the fold på varje sidmall — 3
- Offertformulär ≤ 5 fält, inte gömt bakom modal — 3
- Flytande ringknapp på mobil (≥56px, tumräckvidd), döljs korrekt över formuläret — 3

Annan primärhandling: fem motsvarande delkrav à 3 p härledda ur `primaraktion`/`gate1Test` (t.ex. boka: boka-CTA i sticky header, boka above fold per sidmall, flödet når extern bokning, mobilergonomi ≥56px, felväg med kontaktväg) — samma kravnivå, samma avdragslogik. Full 15 = alla fem finns och fungerar. Deduct per missing/half-working element. **PASS ≥ 11.**

## 2. Faktatrohet — 15 p  · HÅRD GRIND
Every factual claim must trace to `research.md` (the client fact source). Check: certifikat, betyg/omdömen, priser/timpris, garantier, restider/inställelsetid, org.nr, F-skatt, namn, årtal, teamstorlek.
- Fullt 15 = varje påstående spårbart, och osäkra fakta antingen utelämnade eller korrekt gaterade (`TODO-FACT`, tom sträng, schema-utelämning).
- **Any invented or ungated claim, or a `[OSÄKER]`-markerad fakta framställd som säker → criterion FAILs AND the whole eval is reported FAIL.** No partial credit past a real violation.
- Cite the claim verbatim, its `file:line`, and why it is untraceable.

## 3. Svensk copy-kvalitet — 10 p
Röst enligt §7-registret (adjektiv, exempelmeningar, legitimt bransch-vernacular — läses ur briefens §7.2 eller `content/profile.ts` `rostregister` i byggrepot); universella basen alltid: korta meningar, siffror/orter över adjektiv. §7-legitimerat vernacular är inte avdrag; bransch-antislopen drar utöver basen.
- Blocklistan ren — bas (**nortropic-antislop** `references/copy-blocklist.md`) + bransch-antislopen (§7.3 / `content/profile.ts` `branschAntislop`); varje träff drar — up to 5
- Idiomatisk, korrekt svenska; sentence-case rubriker; ≤1 utropstecken/sida — up to 3
- Konkret (tjänst + ort + tid) snarare än generiskt — up to 2

**PASS ≥ 7.**

## 4. NAP-konsistens — 8 p
Name / Address / Phone **identiska** överallt: `src/content/business.ts` (single source), JSON-LD schema, footer, kontaktsida.
- Telefon (visningsformat + E.164 i tel:/schema) konsistent — 3
- Adress + postnummer + ort identiska — 3
- Företagsnamn (AB-namn vs displayName använt rätt) — 2

Any divergence between business.ts and a rendered surface is a deduction (and usually a bug). **PASS ≥ 6.**

## 5. Lokal SEO — 8 p
Uppfyller §7:s SEO-läge (`seoLage` i `content/profile.ts`): ortssidor endast där seoLage kräver dem — då unika.
- Sökstruktur per seoLage: `lokal`/`hybrid` = "[tjänst] i [stad]" på tjänst-/ortssidor; `varumarke` = varumärkes-/tjänstestruktur utan ortsjakt — 2
- Unik `<title>` + meta description per sida (ingen dubblett, ingen keyword-stuffing) — 2
- Ortssidor (endast vid `lokal`/`hybrid`) med genuint unikt innehåll (landmärken, restider, jobb) — INTE mallade; vid `varumarke` ges dessa 4 p när ortssidor korrekt UTELÄMNATS — 4

Templated area pages (samma text, bara ortsnamn utbytt) → deduct the full 4. **PASS ≥ 6.**

## 6. Schema-korrekthet — 8 p
- Schema-typen enligt `content/profile.ts` `schemaTyp` (LocalBusiness-subtyp som `Plumber`, eller `ProfessionalService`/`Restaurant`/...) validerar — 3
- Svensk `PostalAddress` (streetAddress/postalCode/addressLocality/addressCountry=SE) — 2
- `openingHoursSpecification` korrekt; ev. jour/ContactPoint — 3

Placeholdertext får aldrig läcka in i schema (FAQPage ska filtrera `TODO-FACT`/`TODO-COPY`); en läcka = deduction. **PASS ≥ 6.**

## 7. Prestanda — 8 p
Mät mot **nortropic-prelaunch**-skillens `references/lighthouse-targets.md` (mobil, produktionsbygge, median av 3):
- Lighthouse Performance ≥ 90 — 2 · Accessibility/Best-Practices/SEO ≥ 95 — 2
- Core Web Vitals: LCP < 2,5 s, CLS < 0,1, INP < 200 ms — 4

Om live-mätning inte går: bedöm mot viktbudgetarna (total < 1 MB, JS < 200 kB, hero < 150 kB, self-hosted fonts) och notera att det är en statisk bedömning. **PASS ≥ 6.**

## 8. Juridik komplett — 8 p
> Poäng ≠ juridiskt godkännande. Juridik stoppar alltid för människan (governance). Detta mäter bara att bitarna finns.
- Integritetspolicy finns och täcker persondata/lagring — 3
- Företagsuppgifter i footer: org.nr + F-skatt + firmanamn — 2
- Cookie/samtycke stämmer med vad som faktiskt laddas (cookieless analytics vs samtyckeskrav) — 3

**PASS ≥ 6.**

## 9. Visuell distinktion — 10 p
Sajten ska läsas som **handbyggd premium**, aldrig som AI-genererad mall. Döms mot design-blocklisten (**nortropic-antislop** `references/design-blocklist.md`) och design-reviewerns template-test; §5:s Layoutspråk + Signaturelement är facit för vad som skulle byggas. Vad **premium** BETYDER kalibreras mot premium-checklistan (**nortropic-antislop** `references/premium-checklist.md`, PK-1…PK-8) med `references/premium-bevis.md` som tak-bevis — Read båda vid dömningen av detta kriterium; exemplaren KALIBRERAR vad världsklass betyder per drag, aldrig jämförelsemängd eller mall; döm bygget mot PK-DRAGET, aldrig mot exemplar-sajten.
- **10 = kan förväxlas med handbyggd premium på tak-bevisens nivå** — samtliga PK-drag hållna på den nivå `premium-bevis.md` belägger att de kan hållas (PK-7/PK-8 döms mot principtexten — bevis-exemplar saknas ännu, never-invent), i §5:s valda riktning (Referensöversättningen).
- **≤5 om heron följer ett blocklistat mallmönster (sektion A) eller ≥2 sektioner fälls av template-testet.**
- **Ikonkortsrader och zebra-rytm drar alltid ner.**
- Saknat eller urvattnat Signaturelement (mot §5) drar; en hävning som §5 dokumenterat med referensbevis är INTE avdrag (blocklistens sektion C).

**PASS ≥ 7.**

## 10. Förtroendesignaler — 5 p
Förtroendekvitton enligt briefens §7.4 (kvittolistan + attributionsreglerna) nära hero.
- Omdömen med namn + ort (inte anonyma 5-stjärniga stockkort) — 2
- Kundens kvitton per §7.4 (F-skatt/certifikat, utbildningar korrekt attribuerade, portfolio, försäkring...) synliga och äkta — 2
- Riktiga foton (team/lokal/arbete) nära hero — 1

Gaterade platshållare (fiktiva omdömen med `placeholder:true`, grå SVG) = korrekt hantering, ingen avdragning för att de ännu inte är riktiga. **PASS ≥ 4.**

## 11. Teknisk hygien — 5 p
- Inga döda interna länkar — 1
- Fungerande svensk 404-sida — 1
- Sitemap + robots serveras korrekt — 1
- Säkerhet: `npm audit` rent (prod), säkerhetsheaders servas, formulär-endpoint skyddad (honeypot + fast mottagare från env) — 2

**PASS ≥ 4.**

---

## Verdict-band (totalpoäng)
- **90–100** lanseringsklar
- **75–89** åtgärda de listade punkterna
- **50–74** betydande omarbetning
- **< 50** gör om de flaggade sektionerna innan review fortsätter

En **Faktatrohet-FAIL** rapporteras som **FAIL** i EVAL-RESULT-headern oavsett band.

## Changelog
- **v3.0.0** — Q2b drag-kalibrering (MAJOR — kriterium 9:s kravnivå/10-definition ändrad; totaler EJ bakåtjämförbara mot v2.x utan notering): premium-definitionen i kriterium 9 ankras mot premium-checklistan PK-1…PK-8 (tak-princip) med `premium-bevis.md` som tak-bevis — kalibrering av vad världsklass betyder, aldrig jämförelsemängd eller mall; döm bygget mot PK-DRAGET, aldrig mot exemplar-sajten. PK-7/PK-8 döms mot princip (bevis-exemplar saknas, never-invent). Vikter, kriterieantal, delpoäng och PASS-trösklar orörda (summa 100 intakt); kriterierna 1–8, 10–11 oförändrade. Eval-baselinen måste klippas om (mänsklig §A6-handling).
- **v2.0.0** — v14 design-antislop (MAJOR — vikter och kriterieantal ändrade; totaler EJ bakåtjämförbara mot v1.x utan notering): nytt kriterium 9 **Visuell distinktion** (10 p; ankare mot design-blocklisten + template-testet; ≤5 vid blocklistad hero eller ≥2 fällda sektioner) finansierat med kriterierna 4–8 10→8 p (delpoäng ombalanserade, PASS-trösklar 70 %-regeln → ≥6); gamla 9/10 (Förtroendesignaler/Teknisk hygien) omnumrerade till 10/11 oförändrade. Faktatrohet förblir kriterium 2.
- **v1.2.1** — Förtydligande (PATCH): kriterium 3:s datakälla i byggrepot är `content/profile.ts` (`rostregister`/`branschAntislop`) — transportfälten fanns inte i v1.2.0-texten, vilket gjorde kriteriet odömbart utan brief. Inga trösklar/vikter ändrade.
- **v1.2.0** — v13 kalibreringsprofilen: kriterierna 1/3/5/6/9 neutraliserade från hantverkar-antaganden till §7/`content/profile.ts` med OFÖRÄNDRAD kravnivå (offert/samtal-fallet ger exakt v1.1.0:s delkrav — poäng bakåtjämförbara för hantverkarklienter; andra arketyper får härledda delkrav på samma nivå).
- **v1.1.0** — Kriterium 10 utökat med säkerhet (npm audit prod, säkerhetsheaders, skyddad formulär-endpoint) — ombalanserat inom oförändrade 5 p (v6 säkerhetsgrind). Poäng mot v1.0.0 jämförbara med reservation för kriterium 10.
- **v1.0.0** — Initial rubric (v5 mätbarhetslager). 10 criteria, Faktatrohet hard-gate.
