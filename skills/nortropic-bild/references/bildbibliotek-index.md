# Bildbiblioteket

**Binärerna bor utanför systemrepot.** `.gitignore` är en vitlista och systemrepot
ska aldrig bära bildbinärer. Biblioteket bor i mappen som miljövariabeln
`NORTROPIC_BILDBIBLIOTEK` pekar på; är variabeln inte satt används defaulten:
operatörens hemkatalog, underkatalog `Workflow/bildbibliotek`. Manifestet
(`manifest.json`) ligger i samma mapp.

## Biblioteket är en CACHE, inte ett förarbete

Det byggs inte i förväg. `fetch-images.mjs` skriver **den normaliserade
ref-versionen** av varje godkänd genererad bild till biblioteket med metadata, och
första godkända bilden i en klass blir klassens **ankare** — referensbilden alla
efterföljande genereringar i klassen ärver stil från. Biblioteket växer ur
produktion och konvergerar mot ett kurerat bibliotek, eftersom bara godkända bilder
skrivs in.

**Att det är ref-versionen som lagras är poängen:** en normaliserad bild är
PRESETAGNOSTISK — samma bibliotekspost tjänar en duotone-kund och en ljus-kund.
Looken appliceras alltid nedströms, i kundrepots byggsteg, aldrig i biblioteket.

Första kunden i en klass betalar genereringen. Alla efterföljande får cacheträff.

## Klasser

| Klass | Innehåll | Slot-prefix |
|---|---|---|
| `yta` | Betong, plåt, rost, snöasfalt, trä i motljus, ritningsrutnät | hero, env, detail |
| `miljo` | Anläggning i skymning, kraftledningsgata, hamn, kran mot mörk himmel | hero, env |
| `grafisk` | Ritningsutsnitt, kurvor, rutnät, stiliserad karta | detail, og |

`yta` är mest återanvändbar och billigast — och den enda klass preset `ljus` får
generera utöver `grafisk`.

## manifest.json

    {
      "poster": [
        { "id": "yta-014", "klass": "yta", "kalla": "genererad", "stadie": "ref",
          "modell": "fal-ai/flux-2/pro", "orientering": "landskap",
          "luft": "hoger", "fil": "<bibliotek>/yta-014.jpg",
          "anvandningar": 3, "skapad": "2026-08-02" }
      ],
      "ankare": { "yta": "<bibliotek>/yta-001.jpg", "miljo": "<bibliotek>/miljo-001.jpg" }
    }

`stadie: "ref"` markerar att posten är en normaliserad ref-version — fältet skiljer
framtida format åt. `luft` och `orientering` gör slot-matchningen till ett urval i
stället för slumpdragning. `anvandningar` viktas negativt så samma bild inte
återkommer på var tredje kundsajt.

## Fotografering som komplement

Miljöklassen bör fotograferas när tillfälle ges — riktigt fotografi är starkare och
har noll anspråksfrågor. Praktisk not för Norrbotten: det låga skymningsljus klassen
bygger på finns inte i juni–juli. September–oktober är idealiskt.
