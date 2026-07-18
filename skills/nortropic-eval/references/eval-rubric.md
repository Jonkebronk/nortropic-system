# Nortropic Eval Rubric

**Rubrikversion: v1.2.0**

> Semver. Bump on **any** change to criteria, weights, or thresholds so scores stay comparable over time: PATCH = wording/clarification, MINOR = threshold/guidance change, MAJOR = criteria or weights change. Record the version used in every `EVAL-RESULT.md`. Never compare totals across different MAJOR/MINOR versions without noting it.

100 points across 10 weighted criteria. A criterion's **Status = PASS** when it earns **≥ 70 %** of its weight, otherwise **FAIL**. The site total is the sum of criterion points. **Faktatrohet (criterion 2) is also a hard gate:** any untraceable factual claim → the whole eval is reported **FAIL** regardless of total (see SKILL.md).

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
Röst enligt briefens §7-register (adjektiv, exempelmeningar, legitimt bransch-vernacular); universella basen alltid: korta meningar, siffror/orter över adjektiv. §7-legitimerat vernacular är inte avdrag; §7:s bransch-antislop drar utöver basen.
- Blocklistan ren — bas (**nortropic-antislop** `references/copy-blocklist.md`) + briefens bransch-antislop (§7.3); varje träff drar — up to 5
- Idiomatisk, korrekt svenska; sentence-case rubriker; ≤1 utropstecken/sida — up to 3
- Konkret (tjänst + ort + tid) snarare än generiskt — up to 2

**PASS ≥ 7.**

## 4. NAP-konsistens — 10 p
Name / Address / Phone **identiska** överallt: `src/content/business.ts` (single source), JSON-LD schema, footer, kontaktsida.
- Telefon (visningsformat + E.164 i tel:/schema) konsistent — 4
- Adress + postnummer + ort identiska — 3
- Företagsnamn (AB-namn vs displayName använt rätt) — 3

Any divergence between business.ts and a rendered surface is a deduction (and usually a bug). **PASS ≥ 7.**

## 5. Lokal SEO — 10 p
Uppfyller §7:s SEO-läge (`seoLage` i `content/profile.ts`): ortssidor endast där seoLage kräver dem — då unika.
- Sökstruktur per seoLage: `lokal`/`hybrid` = "[tjänst] i [stad]" på tjänst-/ortssidor; `varumarke` = varumärkes-/tjänstestruktur utan ortsjakt — 3
- Unik `<title>` + meta description per sida (ingen dubblett, ingen keyword-stuffing) — 3
- Ortssidor (endast vid `lokal`/`hybrid`) med genuint unikt innehåll (landmärken, restider, jobb) — INTE mallade; vid `varumarke` ges dessa 4 p när ortssidor korrekt UTELÄMNATS — 4

Templated area pages (samma text, bara ortsnamn utbytt) → deduct the full 4. **PASS ≥ 7.**

## 6. Schema-korrekthet — 10 p
- Schema-typen enligt `content/profile.ts` `schemaTyp` (LocalBusiness-subtyp som `Plumber`, eller `ProfessionalService`/`Restaurant`/...) validerar — 4
- Svensk `PostalAddress` (streetAddress/postalCode/addressLocality/addressCountry=SE) — 3
- `openingHoursSpecification` korrekt; ev. jour/ContactPoint — 3

Placeholdertext får aldrig läcka in i schema (FAQPage ska filtrera `TODO-FACT`/`TODO-COPY`); en läcka = deduction. **PASS ≥ 7.**

## 7. Prestanda — 10 p
Mät mot **nortropic-prelaunch**-skillens `references/lighthouse-targets.md` (mobil, produktionsbygge, median av 3):
- Lighthouse Performance ≥ 90 — 3 · Accessibility/Best-Practices/SEO ≥ 95 — 3
- Core Web Vitals: LCP < 2,5 s, CLS < 0,1, INP < 200 ms — 4

Om live-mätning inte går: bedöm mot viktbudgetarna (total < 1 MB, JS < 200 kB, hero < 150 kB, self-hosted fonts) och notera att det är en statisk bedömning. **PASS ≥ 7.**

## 8. Juridik komplett — 10 p
> Poäng ≠ juridiskt godkännande. Juridik stoppar alltid för människan (governance). Detta mäter bara att bitarna finns.
- Integritetspolicy finns och täcker persondata/lagring — 4
- Företagsuppgifter i footer: org.nr + F-skatt + firmanamn — 3
- Cookie/samtycke stämmer med vad som faktiskt laddas (cookieless analytics vs samtyckeskrav) — 3

**PASS ≥ 7.**

## 9. Förtroendesignaler — 5 p
Förtroendekvitton enligt briefens §7.4 (kvittolistan + attributionsreglerna) nära hero.
- Omdömen med namn + ort (inte anonyma 5-stjärniga stockkort) — 2
- Kundens kvitton per §7.4 (F-skatt/certifikat, utbildningar korrekt attribuerade, portfolio, försäkring...) synliga och äkta — 2
- Riktiga foton (team/lokal/arbete) nära hero — 1

Gaterade platshållare (fiktiva omdömen med `placeholder:true`, grå SVG) = korrekt hantering, ingen avdragning för att de ännu inte är riktiga. **PASS ≥ 4.**

## 10. Teknisk hygien — 5 p
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
- **v1.2.0** — v13 kalibreringsprofilen: kriterierna 1/3/5/6/9 neutraliserade från hantverkar-antaganden till §7/`content/profile.ts` med OFÖRÄNDRAD kravnivå (offert/samtal-fallet ger exakt v1.1.0:s delkrav — poäng bakåtjämförbara för hantverkarklienter; andra arketyper får härledda delkrav på samma nivå).
- **v1.1.0** — Kriterium 10 utökat med säkerhet (npm audit prod, säkerhetsheaders, skyddad formulär-endpoint) — ombalanserat inom oförändrade 5 p (v6 säkerhetsgrind). Poäng mot v1.0.0 jämförbara med reservation för kriterium 10.
- **v1.0.0** — Initial rubric (v5 mätbarhetslager). 10 criteria, Faktatrohet hard-gate.
