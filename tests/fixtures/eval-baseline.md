# Eval-baseline — fryst preview (verify-suitens facit)

Fryst: 2026-07-19 · **Rubrikversion: v2.0.0** · Preview: https://rorjour-stockholm.vercel.app (fryst publikt alias; ALDRIG en levande kunds rörliga preview) · Faktakälla: `~/Workflow/test-rorjour/research.md` · Byggrepo: `~/Workflow/rorjour-stockholm` @ commit `07c1d0d`

**Toleransregeln (§B6):** total får inte vara >2 p under baseline-totalen; inget kriterium får bli FAIL som är PASS här; Faktatrohet måste vara PASS. **Rubrikversion ≠ v2.0.0 ⇒ baselinen OGILTIG** — människan klipper om (en eval-körning).

Kontext som ska läsas MED siffrorna: sajten är byggd FÖRE v14 och repot saknar `content/profile.ts` (pre-v13-brief) — evalen faller tillbaka på hantverkar-defaulten; kriterium 9 finns inte i sajtens byggkontrakt. Föregående committade eval var 98/100 på rubrik v1.1.0 — EJ bakåtjämförbar (MAJOR-bump: nytt kriterium 9, kriterierna 4–8 omviktade 10→8).

## Totalpoäng (baseline)

**95/100 — lanseringsklar (band 90–100)** · Faktatrohetsgrinden: **PASS**

## Per-kriterium (baseline-status som "nya FAIL" döms mot)

| # | Kriterium | Vikt | Poäng | PASS/FAIL |
|---|---|---|---|---|
| 1 | Konverteringsarkitektur | 15 | 15 | PASS |
| 2 | Faktatrohet | 15 | 15 | PASS |
| 3 | Svensk copy-kvalitet | 10 | 8 | PASS |
| 4 | NAP-konsistens | 8 | 8 | PASS |
| 5 | Lokal SEO | 8 | 8 | PASS |
| 6 | Schema-korrekthet | 8 | 8 | PASS |
| 7 | Prestanda | 8 | 7 | PASS |
| 8 | Juridik komplett | 8 | 8 | PASS |
| 9 | Visuell distinktion | 10 | 8 | PASS |
| 10 | Förtroendesignaler | 5 | 5 | PASS |
| 11 | Teknisk hygien | 5 | 5 | PASS |

## Kända avdrag (accepterad utgångspunkt — får inte räknas som regression)

- Kriterium 3 (−2): blocklistnära fras "oavsett om det är rotskärning eller relining" (`areas.ts:36`); tankstrecks-paret "— inte ett callcenter —" (`services.ts:48`).
- Kriterium 7 (−1): LCP/CLS/INP ej live-bekräftade (statisk viktbudget-bedömning; JS ~154 kB gzip, CSS 11 kB, noll tredjepartsrequests vid load).
- Kriterium 9 (−2): enhetlig sektionsrytm (py-14/16 utan täta/luftiga-brott) + kort som återkommande sektionsspråk; inget Signaturelement (fanns ej i pre-v14-briefen).

## Kända gated testklient-platshållare (INTE faktatrohetsbrott)

Tom `certId` · `rating.url:""` · omdömen `placeholder:true` märkta "exempelomdöme" · TODO-FACT-markörer · aggregateRating/geo utelämnade ur schema · `robots.txt Disallow: /` (noindex-gaten är ett KRAV för testklient).
