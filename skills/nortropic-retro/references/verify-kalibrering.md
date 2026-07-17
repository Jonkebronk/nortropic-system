# Verify-kalibrering — en engångsmätning

**Syfte:** avgöra om det adversariella verify-steget i `nortropic-review.js` (två skeptiker per fynd) är värt sin token-kostnad, eller om det stryker äkta fynd. Detta är ett **kalibreringstest**, inte en del av det normala flödet. Kör det en gång (eller när verify-steget ändras väsentligt), låt sedan stewarden döma i nästa retro.

## Protokoll

Kör på **exakt samma commit** (ingen kodändring emellan), på samma sajt:

1. **Verifierad körning:** `/nortropic-review`
   - Notera: antal CONFIRMED, PLAUSIBLE, DROPPED, samt total token-kostnad för körningen.
2. **Overifierad körning:** `/nortropic-review --no-verify`
   - Rapporten märks automatiskt "⚠️ OVERIFIERAD KÖRNING — endast för kalibrering". Alla fynd är UNVERIFIED. Notera antal fynd och token-kostnad.

Spara båda rapporterna sida vid sida (t.ex. i projektets STEWARD-REPORT-mapp) med commit-hash och datum.

## Jämför och bedöm

- **(a) Fynd som verify STRÖK (DROPPED):** gå igenom varje ett manuellt — var det faktiskt falskt/redan åtgärdat/pedanteri? Om verify strök äkta fynd → steget är för aggressivt (skeptikern "default refuted=true" är för hård).
- **(b) Fynd som fanns i BÅDA körningarna (överlevde verify):** tillförde verify-steget något, eller bekräftade det bara det som ändå var uppenbart sant? Om verify aldrig ändrar utfallet → steget är dyrt utan effekt.
- **(c) Token-kostnad:** verify fördubblar (2 skeptiker × N fynd) agent-anropen i Verify-fasen. Väg kostnaden mot hur många falska fynd den faktiskt fångade.

## Stewardens beslut (nästa retro)

Utifrån (a)–(c), föreslå ETT av:
- **Behåll** verify som det är (fångar falska fynd, kostnaden motiverad).
- **Tunna** till en skeptiker (halva kostnaden; räcker om andra rösten sällan ändrar utfallet).
- **Reservera** verify för `/nortropic-launch` (där fel kostar mest) och kör `/nortropic-review` overifierat under bygget för snabbare loopar.

Beslutet är ett vanligt steward-förslag (propose-only) och ska koppla till ett återkommande mönster, inte en enskild körning. Notera vald rubrik-effekt om någon (t.ex. färre falska fynd → mindre onödig omarbetning).
