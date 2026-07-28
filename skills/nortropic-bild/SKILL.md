---
name: nortropic-bild
description: >-
  Bildlagrets kontrakt för Nortropic-sajter — spårval A/B/C, behandlingspresets
  (duotone/dokumentar/ljus), claim-regler, slot-schema och anskaffningskedjan.
  Använd den ALLTID när arbetet rör bilder på en kundsajt: bildinventering och
  spårval i briefens §5, val av behandlingspreset, namngivning av bildslots,
  anskaffning eller generering av saknat bildmaterial, behandling vid byggtid,
  fotouppdrag till kund, eller granskning av genererade bilder — även när bilder
  bara nämns i förbigående och användaren inte uttryckligen ber om bildreglerna.
  Läses av project-planner, stack-builder, content-designer och design-reviewer.
---

# Bildlagret

Fyra regler bär skillen.

**R1 — Anspråk avgör, inte medium.** Frågan är aldrig "är bilden genererad?" utan
"påstår bilden något om kunden?". En behandlad miljöbild i en hero säger *det här är
vår värld* — stämning, inget anspråk. Samma bild i ett referensgalleri säger *det här
är vårt jobb* — ett osant påstående om verksamheten. Regeln i prosa bor i
`agents/content-designer.md` (Images) — peka, återge inte.

**R2 — Behandlingen är tillgången, inte motiven.** Ett konsekvent efterbehandlings-
system gör att fem bilder läser som ett system i stället för fem bilder. Behandlingen
är kod (`scripts/treatment.mjs`, byggtid), inte prompt, och appliceras på ALLT:
kundfoton, biblioteksmaterial, genererat. Så blir PK-5:3 sann per konstruktion i
stället för kontrollerad med ögat.

**R3 — Avstånd är säkerhet.** Ju närmare och mer tekniskt specifikt motivet, desto
större risk att det blir fel på ett sätt målgruppen ser — en genererad kabelstege med
stegar som inte går ihop läses av en elentreprenör som inkompetens. Ju mer avstånd
och abstraktion, desto mindre anspråk OCH desto bättre bär bilden hård behandling.
Den säkraste bilden är också den snyggaste.

**R4 — En blind pass är farligare än en röd.** Gallringen (`score.mjs`) är ett
FILTER, inte en domare: den ser tomt, rusigt och saknad rubrikzon, aldrig att något
är strukturellt fel. Varje publicerad genererad bild passerar dessutom bildlinsen i
design-reviewer, med tri-state-utfall. Regeln ärvs ordagrant från
kluster-differentieringslinsen.

## Var skripten bor

**BYGGTID kopieras, ANSKAFFNINGSTID gör det inte.** `treatment.mjs` körs som
prebuild i kundrepot och måste finnas där — sajten ska gå att bygga om utan
systemrepot. `fetch-images.mjs`, `score.mjs` och `models.json` körs en gång, av en
agent som redan har systemrepot laddat, och bor kvar i skillen: doctor #13 vaktar EN
`models.json`, och kopior i kundrepon gör vakten verkningslös för de exemplar som
faktiskt används. Anskaffningsskripten kräver `sharp` upplösbart från skillens träd
(Nodes uppåtvandring — installerat en gång i systemrepots rot eller operatörens
hemkatalog), aldrig i kundrepon för anskaffningens skull.

Alla CLI-skript använder `pathToFileURL` för main-detektering:

    import { pathToFileURL } from 'node:url'
    if (import.meta.url === pathToFileURL(process.argv[1]).href) { ... }

Den naiva `file://`-jämförelsen matchar ALDRIG på Windows och gör CLI:t till en
tyst no-op. Gäller varje nytt skript i skillen, inklusive framtida.

## De två klustren

Ring 1 delar sig, och skillnaden styr allt nedströms.

| | Bildfattiga | Bildrika |
|---|---|---|
| Branscher | El, bygg, konsult, mark, transport | Blomster, frisör, hunddagis, café, fotograf |
| Källa | Ingen Instagram, kanske en GBP-bild | 200 mobilbilder, aktivt konto |
| Problem | För få bilder | För **spretiga** bilder |
| Bildspår | B eller C | Nästan alltid A |
| Bär mest vikt | Biblioteket + looken | Normaliseringen |

Spår A i det bildrika klustret betyder inte att problemet är löst: tvåhundra
mobilbilder i blandat ljus är "fem källor"-problemet i ren form.

Klustren sammanfaller dessutom med genererbarhet: det bildfattiga klustret är också
det säkert genererbara. En genererad bukett på en blomsterhandels sajt läser som
"så här ser våra buketter ut" — motivet ÄR påståendet. Därför spärrar
`fetch-images.mjs` produktklasser under preset `ljus`.

## Claim-tabellen

| `claim` | Betydelse | Slot-prefix |
|---|---|---|
| `none` | Stämning, kategorisignal, dekor | `hero-*`, `env-*` |
| `illustrative` | Generisk situation, inte ett specifikt uppdrag | `detail-*` |
| `depicts_client_work` | Påstår att kunden utfört detta | `proof-*` |
| `depicts_client_people` | Påstår att detta är kundens personal | `people-*` |

### Hårda regler

    genererad OCH claim ∈ (depicts_client_work, depicts_client_people)  → FÖRBJUDET
    claim = depicts_client_people OCH samtycke ej dokumenterat          → FÖRBJUDET
    tredjepartskälla OCH rättigheter okända                             → FÖRBJUDET

Mekaniskt genomdrivet i `fetch-images.mjs` (`SLOT_KLASS[...].genererbar = false`
för `proof` och `people`) och verifierat av bildlinsens fråga 6.

Strängare än lagkravet, av kommersiella skäl: en ny firma har inte råd med det
förtroendetapp som uppstår om en fiktiv anläggning visar sig vara fiktiv.

## Spårval

Beräknas ur bildinventeringen i briefens §5. Ingen fri sättning.

| Spår | Villkor | Uttryck |
|---|---|---|
| **A — foto-först** | ≥1 hero-grade OCH ≥6 användbara över ≥3 kategorier | Fotoledd layout, galleri, ansikten |
| **B — bevis-först** | 3–5 användbara | Foto endast där det bär bevis |
| **C — typografi-först** | 0–2 användbara | Hero obligatorisk (bibliotek/genererad, `claim: none`). Inga dokumentära foton i övrigt |

**Hero är obligatorisk i alla tre spåren.** Kategorisignal: en stressad besökare som
jämför tre flikar ska på en halv sekund veta vilken bransch sajten gäller. Typografi
klarar det, men långsammare. Kostnaden är noll — heron kommer ur biblioteket.

**Spår C har EGEN mall.** Aldrig spår A med bilderna borttagna. En sektion byggd för
ett foto som står tom är en lucka, inte typografi-först. Mallen bärs av förstorad
typskala, färgblock, rutnät, siffror som grafik, urklippta objekt och texturer som
sektionsavdelare. Förenligt med `design-checklist.md` §1, som redan tillåter "clean
solid/soft tone" som hero-alternativ till foto.

## Hero-grade — kriterier

Samtliga måste uppfyllas: ≥2400 px på längsta sidan · 16:9-beskärning möjlig utan
att motivet förstörs · ingen vattenstämpel eller synlig socialmediekomprimering ·
motivet läsbart efter overlay · inga identifierbara ansikten utan dokumenterat
samtycke · inga tredjepartsvarumärken i förgrunden utan tillstånd.

## Vad som får genereras

| Motiv | Tillåtet |
|---|---|
| Texturer, betong, plåt, rutnät, ritningsutsnitt | Ja, fritt |
| Anläggning/industrifasad, skymning, tung overlay | Ja (ej under preset `ljus`) |
| Stiliserad täckningskarta, processikoner | Ja |
| Teknisk närbild med avläsbara komponenter | Nej — R3 |
| Personer med ansikte | Nej |
| Allt i `proof-*` och `people-*` | Nej — mekaniskt spärrat |
| Produkten under preset `ljus` (bukett, frisyr, tårta, djur) | Nej — motivet ÄR påståendet |

## Varumärkeslagret

Logotyp, favicon och manifest-ikoner ägs av `scripts/brand.mjs` — körs av
content-designer i nod 5, EFTER `fetch-images.mjs`, med byggrepots rot som cwd
(kopieras aldrig — anskaffningstid). Indata: `public/images/raw/brand__*` —
**går ALDRIG genom treatment.mjs** (fotobehandling är aktivt skadlig på en
logotyp; stageNormalise hoppar prefixet explicit). Kedjan, utdatauppsättningen
(exakt åtta filer via Next 15:s filkonventioner — aldrig handskrivna
ikon-`<link>`), favicon-märkets dokumenterade beslut (symbol/monogram —
agentens ögon avgör, skriptet verkställer och journalför via `--marke`),
degraderingarna (rembg/vtracer saknas → rastern behålls + fotouppdragsflagga;
ingen logotyp → monogramvägen, som kräver noll binärer) och gatesen (i
rapporten, aldrig launch.js) bor i skriptets huvudkommentar. OG-bilden är inte
en slot: `app/opengraph-image.tsx` komponerar ref-versionens hero + logotyp +
företagsnamn — se `behandling.md`.

## Checklista — bildanskaffning

- [ ] Läst briefens §5: Bildspår, Bildbehandling, slot-tabell
- [ ] Kundfoton i raw/ identifierade och orörda
- [ ] fetch-images.mjs kört, BILDRAPPORT.json läst
- [ ] Platshållare kvar redovisade med skäl per slot
- [ ] Svensk alt-text skriven för varje slot
- [ ] Fotouppdrag skrivet om prio 1–2 saknas
- [ ] Inga proof-*/people-* med källa genererad

## Referensfiler

`slot-schema.md` · `behandling.md` · `fotouppdrag-mall.md` · `bildbibliotek-index.md` ·
`models.json` (roll → modell, med avvecklingsfält)
