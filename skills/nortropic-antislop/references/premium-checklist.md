# Premium-känsla-checklistan (PK-1…PK-8)

Antislop-gaten är **negativytan** (vad som inte får finnas). Den här checklistan är **positivytan**: vad som ska finnas för att en Nortropic-sajt ska kännas dyr, avsiktlig och mänskligt formgiven — inte genererad.

> **Punktnumren är stabila ID:n.** Fynd taggas `[PK-n]` i granskningsrapporter. Kategorierna grupperar punkterna icke-sammanhängande (Substans = 4, 5, 7; Upplevd kvalitet = 6, 8) — **ändra aldrig numren**, historiska taggar bygger på dem.

**Ingen egen poängskala.** Checklistan informerar fynd som redan flödar in i eval-kriterierna 1 (Konverteringsarkitektur), 3 (Svensk copy-kvalitet), 9 (Förtroendesignaler) och 10 (Teknisk hygien).

---

## Taste

### PK-1 — Point of view, inte mall
Sajten har en beskrivbar hållning, inte ett genererat medelvärde.
- [ ] Riktningen ur PROJECT-BRIEF §5 går att beskriva i EN mening — och sajten följer den meningen
- [ ] Ingenting på sajten "kunde vara vilken bransch som helst" — byt ut företagsnamnet i huvudet: känns sidan fortfarande som VVS/städ/el i just den här orten?
- [ ] Minst ett medvetet avsteg från default (layoutgrepp, bildbeskärning, sektionsordning) som är motiverat av branschen — inte dekoration

### PK-2 — Typografi som arbetar
- [ ] Medvetet typsnittspar valt ur `ui-ux-pro-max`-uppslaget (inte Next-defaulten), max 2 typsnitt
- [ ] Tydlig typografisk skala: rubriknivåer skiljer sig i mer än storlek (vikt, spärrning eller färg)
- [ ] Radlängd i brödtext 45–75 tecken på desktop; ingen rubrik bryter till ensamt ord på mobil hjälten

### PK-3 — Återhållet färgsystem
- [ ] Briefens palett används — EN accentfärg bär alla CTA:er
- [ ] Inga dekorativa gradienter utan syfte; en tonad yta måste svara på "vad gör den för konverteringen?"
- [ ] Neutraler är varma/kalla i linje med paletten (inte default-grå rakt av)

## Substans

### PK-4 — Hierarki som andas
- [ ] EN primär handling per vy — allt annat är visuellt underordnat
- [ ] Vertikal rytm: konsekvent spacing-skala mellan sektioner (inte slumpvisa py-värden)
- [ ] Whitespace används som verktyg: det viktigaste elementet har mest luft omkring sig

### PK-5 — Bildspråk med avsikt
- [ ] Prioritetsordning hålls: kundfoton > genererade brand-bilder > stock — och stock med människor undviks helt
- [ ] Varje bild svarar på "varför just här?" — bilden stödjer sektionens budskap, inte fyller yta
- [ ] Bildbeskärning och ljus är konsekventa över sajten (ser ut som EN fotograf, inte fem källor)

## Upplevd kvalitet

### PK-6 — Rörelse som viskar
- [ ] Motion-nivån ur PROJECT-BRIEF §5 respekteras exakt (`ingen` = noll rörelse; `subtil` = entrances/mikrorörelser; `uttrycksfull` = fritt inom reglerna)
- [ ] `prefers-reduced-motion` respekteras av varje animation
- [ ] Rörelse kostar noll Lighthouse-poäng och orsakar ingen layoutförskjutning

## Substans (forts.)

### PK-7 — Mobil som är designad, inte krympt
- [ ] Touch-ytor ≥44 px; primär-CTA i tumzonen (nedre halvan) på mobil
- [ ] Mobilhero är komponerad för porträtt — inte desktop skalad ner (bildbeskärning, radbrytningar och CTA-placering är mobilspecifika)
- [ ] Ingen horisontell scroll, inga element som kolliderar med flytande ringknappen

## Upplevd kvalitet (forts.)

### PK-8 — De osynliga dyra detaljerna
- [ ] Synliga fokusramar på alla interaktiva element (tangentbordsnavigering ser avsiktlig ut)
- [ ] Svenska felmeddelanden och formulär-microcopy (inte "This field is required"); felstate visar telefonnumret
- [ ] Laddning utan layoutskift (dimensionerade bilder, ingen FOUC); favicon + OG-bild satta; 404-sida med personlighet och telefonnummer
