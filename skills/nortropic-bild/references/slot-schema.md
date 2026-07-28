# Slot-schema

Slot-id är **semantiskt**, inte arkitekturhärlett. Rollen bär reglerna: `claim` sätts
på prefixet, ersättningsprioritet sätts på prefixet, biblioteksmatchning sker på
prefixet. Ett semantiskt id överlever också en re-plan — slås två tjänstesidor ihop
behåller `proof-03` sin identitet och byter bara `sida`.

## Namnrymd — uttömmande

| Prefix | Roll | Beskärning | Claim | Ersättningsprio | Biblioteksklass |
|---|---|---|---|---|---|
| `hero-*` | Kategorisignal | 2400×1350 | `none` | 4 | miljo, yta |
| `env-*` | Miljö, sektionsavdelare | 1600×1067 | `none` | 4 | miljo, yta |
| `proof-*` | Utfört arbete, före/efter | 1600×1067 | `depicts_client_work` | **1** | — |
| `people-*` | Porträtt, team | 1080×1350 | `depicts_client_people` | **2** | — |
| `detail-*` | Verktyg, material, närbild | 1600×1067 | `illustrative` | 3 | yta, grafisk |

**`og` är inte längre en slot.** Delningsbilden genereras av `app/opengraph-image.tsx`
(Next-konventionen, statisk vid byggtid): ref-versionens hero + logotyp + företagsnamn
via ImageResponse, med `opengraph-image.alt.txt` bredvid — se `behandling.md`
("OG-bilden läser ref/"). Varumärkesmaterial (`brand__*`) är inte heller slots —
det ägs av `scripts/brand.mjs` och går aldrig genom behandlingen.

**Ersättningsprioriteten är det icke-uppenbara.** Sortera inte efter luckor — sortera
efter vad som blir bättre av en riktig bild. En `proof-*`-platshållare är en textur:
den ljuger inte, men bevisar heller ingenting, och där sitter konverteringen. En
`hero-*`-platshållare ur biblioteket slår vad kunden fotar med mobilen. **Vissa
platshållare är permanenta designval, inte skulder.** Bara `proof-*` och `people-*`
är verkliga skulder.

## Filnamn på disk

Källmaterial (kundfoton, opåverkade original) läggs i `raw/`; anskaffningen
(`fetch-images.mjs`) levererar normaliserat material direkt till `ref/` — se
behandlingens trestegsflöde i `behandling.md`. Samma namnkonvention i båda:

    public/images/raw/<slot-id>__<beskrivande-svenska>.<ext>

    raw/proof-01__takbyte-lulea-fore.jpg      ← kundfoto
    raw/people-01__jonas-portratt.jpg         ← kundfoto
    ref/hero-01__genererad.jpg                ← anskaffningens leverans (normaliserad)

Slot-id före dubbla understreck, beskrivande efter. Byggsteget läser prefixet.
Operatören ser vilken slot filen fyller och vad den föreställer på samma rad.

Slot-id syns aldrig i fotouppdraget till kunden.

## SLOTS.json — kontraktet mellan planner och scripten

    {
      "kund": "elkalkyl-konsult",
      "bransch": "elkalkyl och byggkonsult",
      "bildspar": "C",
      "bildbehandling": "duotone",
      "slots": [
        { "id": "hero-01", "prefix": "hero", "sida": "/", "status": "saknas", "luft": "topp" },
        { "id": "proof-01", "prefix": "proof", "sida": "/tjanster/kalkyl", "status": "saknas" }
      ]
    }

`status`: `kundfoto` | `placeholder` | `saknas`. `luft` (`topp`/`vanster`/`hoger`)
styr biblioteksmatchningen så en hero med rubrik uppe till vänster får en bild med
plats där.

## Antalet slots

Härleds ur arkitekturen: en `proof-*` per tjänstesida plus två på Hem, en `people-*`
om §5 planerar porträtt, `env-*`/`detail-*` efter sektionsantal. Blir sannolikt fel
de första gångerna — justeras vid nod 3.
