# Arbetslogg — konvention (Z1)

Varje skrivande agent (planner, stack-builder, content-designer, seo-optimizer) lägger EN post i `AGENT-LOG.md` i kund-repots rot. Loggen svarar på **en** fråga: *varför gjorde agenten det den gjorde?* Den är inte en statusrapport — sex sådana finns redan (AUTO-DIGEST, usage-log, STEWARD-REPORT, VERIFY-SUITE-RESULT, AUTOBYGG-LOG, FINAL-TOUCHES).

## Lag 0 — anti-brus (styr allt annat)
Kan raden härledas ur agentens output — koden, sajten, eller den rapport agenten redan skriver? → Den är **BRUS**. Ta bort den. En rad som bara upprepar vad som syns i resultatet hör inte hemma här.

## Asymmetri
- `utfall=success` → logga BARA det essentiella: de icke-uppenbara valen, ev. en `var förfina`-rad. Några rader, inte fler.
- `utfall=friktion` (agenten fastnade, gissade, tvingades avvika, en grind small) → logga FULLSTÄNDIGT. Det är här spåret behövs.
- `utfall=kunde-ej-koras` → loggen kunde inte skrivas (ingen kund-repo — t.ex. plan-torrtestets scratch, eller innan repot finns). Skriv EN rad med orsak. **Fela ALDRIG bygget eller verify-suiten för att loggen inte gick att skriva.**

## Referera — duplicera ALDRIG
Finns tracen redan i en artefakt agenten producerar? → PEKA dit, återge den inte. Två kopior = två sanningar om samma bygge, och omstrukturering riskerar frysta baslinjer.
- planner `källa→beslut` = pekare till `PROJECT-BRIEF §Referensöversättning`.
- stack-builder `friktion` = pekare till byggrapportens §7-read-back-sektion + endast netto-nytt.

## Läge A — fil-block (de fyra byggarna)
Append till `AGENT-LOG.md`. Meta-block för Z2-aggregering (samma HTML-kommentar-konvention som AUTOBYGG-LOG.md):

```
<!-- nortropic-agent-log agent=<namn> bygge=<kund-slug> utfall=success|friktion|kunde-ej-koras -->
### <agent> — <utfall>
- **beslut:** valde X över Y för Z          (endast val som INTE syns i output)
- **källa→beslut:** <faktisk trace, eller PEKARE om den redan finns>
- **friktion:** <var den fastnade/gissade — utelämna helt vid ren success>
- **var förfina:** <en rad: här kan agenten finjusteras — utelämna om inget verkligt>
```

De fyra fälten ovan är dashboardens kontrakt (`Verkstadsgolvet/components/AgentPanel.tsx`: beslut / källa→beslut / friktion / var förfina) — och de är **hela mallen**. Den växer bara om ett verkligt block bevisar att något saknas, aldrig "för säkerhets skull". Att börja brett och beskära är vägen till en sjunde statusrapport.

Skriv blocket **i agentkroppen** (orkestratorn ser aldrig ditt VARFÖR, och det bemannade flödet går inte via autobygg.js). Committa + pusha till `kund-<slug>`-repot — dashboarden läser via GitHub-API, endast `kund-*`-repon.

## Läge B — rapportsektion (granskarna, read-only)
*(Finaliseras med proposals 05/06 — design-reviewer + qa-launcher.)* Ingen fil, inga skrivrättigheter: en mager `## Arbetslogg (varför)`-sektion sist i den rapport de redan producerar. Får ALDRIG återlista fynd (= output = brus): bara vad granskningen prioriterade & varför, var granskaren var osäker, och `var förfina`.
