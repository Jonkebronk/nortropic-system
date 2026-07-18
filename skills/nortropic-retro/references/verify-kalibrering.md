# Verify-kalibrering — en engångsmätning

**Syfte:** avgöra om det adversariella verify-steget i `nortropic-review.js` (två skeptiker per fynd) är värt sin token-kostnad, eller om det stryker äkta fynd. Detta är ett **kalibreringstest**, inte en del av det normala flödet. Kör det en gång (eller när verify-steget ändras väsentligt), låt sedan stewarden döma i nästa retro.

## Protokoll

Kör på **exakt samma commit** (ingen kodändring emellan), på samma sajt:

1. **Verifierad körning:** `/nortropic-review`
   - Notera: antal CONFIRMED, PLAUSIBLE, DROPPED, samt total token-kostnad för körningen.
2. **Overifierad körning:** `/nortropic-review --no-verify`
   - Rapporten märks automatiskt "⚠️ OVERIFIERAD KÖRNING — endast för kalibrering". Alla fynd är UNVERIFIED. Notera antal fynd och token-kostnad.

Spara båda rapporterna sida vid sida (t.ex. i projektets STEWARD-REPORT-mapp) med commit-hash och datum.

> **Filnamnsnot (v8):** den verifierade körningen skriver `REVIEW-REPORT.md`; `--no-verify`-körningen skriver `REVIEW-REPORT-CALIBRATION.md` och rör därmed ALDRIG launch-freshness-metan i `REVIEW-REPORT.md`. Kopiera ändå undan båda till projektets steward-mapp så de överlever nästa fullständiga granskning.

## Jämför och bedöm

- **(a) Fynd som verify STRÖK (DROPPED):** gå igenom varje ett manuellt — var det faktiskt falskt/redan åtgärdat/pedanteri? Om verify strök äkta fynd → steget är för aggressivt (skeptikern "default refuted=true" är för hård).
- **(b) Fynd som fanns i BÅDA körningarna (överlevde verify):** tillförde verify-steget något, eller bekräftade det bara det som ändå var uppenbart sant? Om verify aldrig ändrar utfallet → steget är dyrt utan effekt.
- **(c) Token-kostnad:** verify fördubblar (2 skeptiker × N fynd) agent-anropen i Verify-fasen. Väg kostnaden mot hur många falska fynd den faktiskt fångade.

## Stewardens beslut (nästa retro)

### Beslutsregler (mekaniska — stewarden dömer efter dessa, inte efter känsla)

| Utfall i jämförelsen | Förslag |
|---|---|
| ≥80 % identiska fynd i båda körningarna OCH inga falska positiver i no-verify-körningen | **EN skeptiker** (halva verify-kostnaden) |
| Verify strök genuint falska fynd (stickprova 3 DROPPED manuellt — minst 2 var äkta strykningar) | **Två skeptiker endast för CRITICAL/HIGH**; MEDIUM overifierat |
| Ingen mätbar skillnad i utfall mellan körningarna | **Verify endast i `/nortropic-launch`**; mellangranskningar overifierade |

Förslaget ska alltid ange **förväntad besparing i % av review-kostnaden**, hämtad från usage-loggen (`~/Workflow/usage-log.md`).

Beslutet är ett vanligt steward-förslag (propose-only) och ska koppla till ett återkommande mönster, inte en enskild körning. Notera vald rubrik-effekt om någon (t.ex. färre falska fynd → mindre onödig omarbetning).
