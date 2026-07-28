# Behandling — trestegs

`skills/nortropic-bild/references/behandling.md`

## Innehåll

1. [Varför trestegs](#varför-trestegs)
2. [Varför looken är en parameter](#varför-looken-är-en-parameter)
3. [Steg 1 — Normalisering](#steg-1--normalisering) (vitbalans, exponering, tak, känd begränsning: blandat ljus)
4. [Steg 2 — Referensutrymmet ref/](#steg-2--referensutrymmet-ref)
5. [Steg 3 — De tre presetsen](#steg-3--de-tre-presetsen) (`duotone` · `dokumentar` · `ljus`)
6. [Presetval](#presetval)
7. [Paletten — kanoniska tokens](#paletten--kanoniska-tokens)
8. [Byggtidskontraktet](#byggtidskontraktet) (beskärningar, utdata)
9. [Versionering](#versionering)
10. [Testprotokollet](#testprotokollet)

---

## Varför trestegs

En look mappar färg- och luminansvärden men är blind för exponering. Genereras den
mot en korrekt exponerad referens förväntar den sig korrekt exponerad input —
appliceras den på en underexponerad mobilbild träffar mappningen fel tonområden och
ger grumliga skuggor och skeva färger. Det är samma fel som
färggraderingslitteraturen varnar för. Ordningen är därför: **normalisera först,
gradera sen.**

Och mellanformen ska LAGRAS, inte bara beräknas — prior art från OpenColorIO (film)
och Cloudinary (webb): OCIO transformerar indata till ett referensutrymme innan
looks appliceras; Cloudinary skiljer "incoming transformations" (transformera
originalet före lagring) från derivat.

```
public/images/raw/     källmaterial, orört
      ↓ 1. NORMALISERING — körs EN gång per bild, resultatet lagras
public/images/ref/     referensutrymme: neutral vitpunkt, målexponering
      ↓ 2–3. LOOK + BESKÄRNING — körs vid varje bygge
public/images/         levererat
```

Att referensutrymmet lagras köper tre saker: normaliseringen körs en gång per bild
i stället för varje bygge (idempotent, snabbare ombyggen) · gallringen kan
poängsätta normaliserat material så alla kandidater bedöms mot samma skala ·
**biblioteket kan lagra ref-versionen, som är PRESETAGNOSTISK** — samma bild tjänar
en duotone-kund och en ljus-kund, i stället för att vara låst till det preset som
råkade generera den.

Steg 1 är samma för varje kund i varje bransch. Looken är det enda som varierar.

## Varför looken är en parameter

Ring 1 delar sig i två kluster som beter sig olika:

| | Bildfattiga | Bildrika |
|---|---|---|
| Branscher | El, bygg, konsult, mark, transport | Blomster, frisör, hunddagis, café, fotograf |
| Källa | Ingen Instagram, kanske en GBP-bild | 200 mobilbilder, aktivt konto |
| Problem | För få bilder | För **spretiga** bilder |
| Bildspår | B eller C | Nästan alltid A |
| Bär mest vikt | Biblioteket + looken | **Normaliseringen** |

Monokrom duotone på en blomsterhandel är inte suboptimalt — det är fel, för
blommorna *är* färgen. Och spår A i det bildrika klustret betyder inte att problemet
är löst: tvåhundra mobilbilder i blandat ljus är "fem källor"-problemet i ren form.

**Invarianten är inte duotone. Invarianten är ett preset per sajt, applicerat på
allt.** Det är det som gör PK-5:3 sann, och det gäller lika i alla tre presets.

---

## Steg 1 — Normalisering

Målet är att en mobilbild inomhus i gult ljus och en utomhusbild i skugga ska landa
på samma vitpunkt och samma exponering innan looken läggs på.

### Vitbalans — hybrid

Två metoder, viktade mot varandra:

**Vitpunkt (percentil 98).** Mäter färgsticket i de ljusaste pixlarna. Robust mot
färgstarka motiv: ett färgstick färgar även högdagrarna, medan ett rött blomsterhav
lämnar dem neutrala. Det här är metoden som gör att `ljus`-presetet inte
neutraliserar bort blommorna.

**Gråvärld.** Antar att bildens genomsnitt ska vara neutralt. Enkel och stabil, men
neutraliserar färgdominerade motiv — den skulle göra rosorna grå.

**Vikten** styrs av andelen klippta pixlar. Är högdagrarna urblåsta döljs sticket
där, och vitpunkten blir opålitlig → vikten flyttas mot gråvärld. Rena högdagrar →
full tilltro till vitpunkten.

### Exponering

Efter vitbalans skalas bilden mot `TARGET_LUMA = 132` (sRGB 8-bit).

### Tak

`WB_CAP = 0.45`, `EXP_CAP = 0.60`. En bild som kräver mer korrigering än taket blir
hellre delvis rättad än förvriden. Det är avsiktligt: en kraftigt underexponerad
kvällsbild ska inte lyftas till dagsljus, den ska bara flyttas närmare.

### Känd begränsning — blandat ljus

Blandat ljus (två ljuskällor med olika färgtemperatur i samma bild) kan inte lösas
av en global vitbalans — den rumsliga tudelningen består genom normaliseringen.
Mätt utfall: helheten flyttas mot neutral, uppdelningen kvarstår. Konsekvens:
blandljusbilder sitter aldrig helt i en serie. Åtgärd är beskärning eller
uteslutning, inte parameterjustering.

### Uppmätt beteende

Kontrollerad testkörning (falsifieringstestet 2026-07-27, tio ljuslägen på samma
motiv) genom normaliseringssteget:

| Bild | RGB-medel före | RGB-medel efter |
|---|---|---|
| Varm tungsten, underexponerad | 90 / 68 / 46 | 108 / 108 / 105 |
| Kall skugga | 87 / 105 / 143 | 131 / 132 / 131 |
| Hård sol, ljus | 183 / 178 / 167 | 131 / 132 / 131 |
| Färgdominerad röd, neutralt ljus | 131 / 107 / 108 | 154 / 125 / 127 |
| Kraftigt underexponerad | 39 / 38 / 42 | 63 / 63 / 64 |

Neutrala scener konvergerar mot samma vitpunkt. Det färgstarka motivet **behåller
sin färgrelation** — hybriden neutraliserar inte bort rödheten. Kraftigt felexponerade
bilder landar delvis rättade, takbegränsat.

Notera att detta är kontrollerat/syntetiskt material. Riktiga foton beter sig
annorlunda, särskilt vid blandat ljus (se Känd begränsning ovan). Kör `--compare`
på eget dokumentärt material innan parametrarna låses.

---

## Steg 2 — Referensutrymmet ref/

`treatment.mjs --stage=normalise` skriver normaliserade versioner av allt i `raw/`
till `public/images/ref/` (JPEG, hög kvalitet, ursprunglig upplösning — beskärning
sker först i look-steget). Filer där ref-versionen är nyare än råfilen HOPPAS —
steget är idempotent och ombyggen blir snabbare.

`ref/` är internt mellanmaterial och läggs i `.vercelignore` — deployas aldrig,
samma behandling som `design-referenser/`.

Anskaffningen (`fetch-images.mjs`) levererar sitt material direkt som ref-versioner:
genererade kandidater normaliseras FÖRE gallringen (score-måtten är
exponeringskänsliga — allt bedöms mot samma skala), och vinnaren skrivs som
ref-version till både bildbiblioteket och projektets `ref/`. Kundfoton läggs alltid
i `raw/` och normaliseras av prebuild.

---

## Steg 3 — De tre presetsen

### `duotone`

**Branscher:** el, bygg, industri, konsult, mark, anläggning
**Princip:** färgen är irrelevant → tas bort. Formen och ytan bär.

```
greyscale → linear(1.12, -14) → tint(accent) → saturation 0.55
overlay: hero 55%, övrigt 30%
```

Detta är originalpresetet, kalibrerat mot branschspaningen för teknisk konsult. Det
gör tre saker samtidigt: konsistens över blandade källor, döljning av detaljfel i
genererat material, och anspråkssänkning — en hårt behandlad monokrom abstraktion
gör inte anspråk på att vara autentisk dokumentärbild.

### `dokumentar`

**Branscher:** hantverkare generellt, transport, fastighet, verkstad
**Princip:** färgen är verklig → normaliseras, inte tas bort. Sakligt, inte stiliserat.

```
linear(1.06, -8) → saturation 0.85
overlay: hero 42%, övrigt 12%
```

Nästan all koherens kommer från normaliseringen här. Looken lägger bara på en mild
kontrastkurva och klämmer mättnaden så att en översaturerad mobilbild inte sticker
ut mot en dämpad. Det här är default när plannern är osäker.

### `ljus`

**Branscher:** blomster, frisör, café, hunddagis, terapeut, fotograf
**Princip:** färgen ÄR innehållet → bevaras. Koherensen kommer ur ljus och luft.

```
linear(0.92, 22) → saturation 1.04, brightness 1.02 → gamma 1.05
overlay: hero 28%, övrigt 6%
```

Lyfta skuggor, sänkt kontrast, luftigt. Overlayn är nästan borta — en mörk
multiply-yta över en blomsterbild är fel signal. Läsbarhet i heron löses här med
textplatta eller gradient bakom rubriken, inte med global nedtoning.

---

## Presetval

Sätts av plannern i briefens §5 bredvid Bildspår, härlett ur den trade-anchored
palett §5 redan producerar.

| §5-palett | Preset |
|---|---|
| el/energi → amber/warm, bygg → earthy/robust | `duotone` |
| VVS/rör → blues | `dokumentar` |
| städ → greens/fresh | `dokumentar` eller `ljus` |
| Övriga konsumentnära (blomster, frisör, djur, café) | `ljus` |

Vid osäkerhet: `dokumentar`. Det är det minst stiliserade och därmed det som gör
minst skada om valet är fel.

---

## Paletten — kanoniska tokens

Paletten har ETT hem: byggrepots `globals.css`. Behandlingen får aldrig ett eget
hex-hem — två hex-hemvister är precis den drift systemet förbjuder på andra ställen
(NAP-regeln, Motion-nivåns "en plats").

Init skriver två kanoniska CSS-custom-properties i varje nytt repo, som **alias
till befintliga värden** (aldrig nya färger); stack-builder sätter dem ur briefens
§5-palett samtidigt som övriga tokens skrivs:

```css
:root {
  --nortropic-ink: #0B0E11;      /* mörkaste ytan i paletten */
  --nortropic-accent: #C97B4A;   /* trade-anchored accent ur §5 */
}
```

`treatment.mjs` läser dem med enkel regex, i denna ordning:

1. `--nortropic-ink` / `--nortropic-accent` i `app/globals.css` — normalfallet
2. `tokens`-fältet i SLOTS.json — ENDAST bakåtkompatibilitet för äldre repon;
   nya SLOTS.json får aldrig ett tokens-fält
3. Ingen träff → degradering

**Degradering (aldrig hårt fel — bygget stoppas inte av en färg):** ink saknas →
`#000000`, overlay-alpha sänks 20 %, WARNING i loggen. Accent saknas och preset =
`duotone` → tint-steget hoppas helt (ren normaliserad gråskala), WARNING i
versaler. **Gissa ALDRIG en defaultpalett** — en felaktig accent ändrar tyst
varenda bild på sajten, och det är värre än en gråskalig sajt med en varning i
loggen. `dokumentar` och `ljus` använder inte accent alls — bara ink för overlayn.

---

## Byggtidskontraktet

```
public/images/raw/     ← källmaterial (kundfoto; opåverkade original)
public/images/ref/     ← referensutrymme (normaliserat; anskaffningens leveransmål)
         ↓ prebuild: node scripts/treatment.mjs   (kör --stage=both)
public/images/         ← behandlade varianter, ENDA vägen hit
```

Filnamn i `raw/` och `ref/` bär slot-id som prefix (`proof-01__takbyte-lulea.jpg`);
skriptet läser prefixet för beskärning, ignorerar resten.

**Bieffekten är den viktigaste egenskapen:** när kunden skickar in ett riktigt foto
efter lansering droppas det i `raw/`, bygget körs, och bilden landar automatiskt i
samma look som resten. Ingen manuell efterbehandling, ingen risk att en sen kundbild
sticker ut.

### Beskärningar

| Slot-prefix | Format |
|---|---|
| `hero-*` | 2400 × 1350 (16:9) |
| `env-*`, `proof-*`, `detail-*` | 1600 × 1067 (3:2) |
| `people-*` | 1080 × 1350 (4:5) |
| `og-*` | 1200 × 630 |

`fit: cover`, `position: attention` — sharp beskär mot bildens entropitäta område i
stället för mitten.

### Utdata

AVIF q55 + WebP q72 fallback, enhetligt för alla tre presets. **q55 är ett TAK av
kompressionsskäl, inte en smakinställning:** uppmätt på högentropisk källa i
2400×1350 ligger en klippa mellan q55 och q60 (dokumentar 59→206 kB, ljus
71→278 kB). q60+ sätts aldrig utan ny mätning. Preset-kostnaden är dessutom inte
den intuitiva — vid q55 är `duotone` dyrast (86 kB mot dokumentar 59, ljus 71):
tint återinför kroma och kontrastlyftet förstärker brus. Därför antas storlek
aldrig per preset — den mäts per bild:

**Budgetloop:** skriptet mäter varje producerad avif mot budgeten per slot-prefix
(tabellen bor i `lighthouse-targets.md` — en plats; hero 150 kB). Över budget →
avif-kvaliteten sänks i steg om 5 och kodas om, golv q35. Nås golvet utan att
budgeten hålls skrivs en WARN-rad i `BILDRAPPORT.json` (filnamn, slot, faktisk
storlek) — bygget felar aldrig på en bildstorlek. Explicit width/height och
`priority` endast på hero gäller oförändrat.

---

## Versionering

Presetnamnen bär versionen implicit via skriptets git-historik. Vill du köra om
äldre kunder på en senare look räcker det att uppdatera `treatment.mjs` och bygga
om — källmaterialet i `raw/` och referensutrymmet i `ref/` är orörda.

Ändras ett preset efter att kunder byggts: notera det i `docs/05-beslutslogg.md`,
eftersom sajternas uttryck då förändras utan att någon copy eller layout rörts.

---

## Testprotokollet

Kör detta innan parametrarna låses mot nytt material.

```bash
mkdir -p raw ut && npm install sharp
# lägg 8–10 riktiga bilder i raw/ — medvetet spretiga:
#   inomhus, utomhus, blixt, skugga, kvällsljus, en översaturerad,
#   en underexponerad, en från GBP, en genererad
node treatment.mjs --compare
```

Du får en kontaktkarta per bild med fem kolumner: **original · normaliserad ·
duotone · dokumentar · ljus**. Kolumn två motsvarar exakt innehållet i `ref/` —
det referensutrymme som lagras och som biblioteket bygger på.

**Det som ska avgöras:** titta bara på kolumn två först. Hänger de normaliserade
bilderna ihop *utan* look? Om ja är hela systemet bevisat för båda klustren, för
det är normaliseringen som bär det bildrika fallet. Om nej — justera `TARGET_LUMA`
och taken innan du bryr dig om presetsen.

Testa på bilder med drastiskt olika ljus innan en batch körs skarpt. Det är hela
poängen med jämförelseläget.
