# Design-blocklisten — layoutspråkets negativyta (v14)

> Copy-blocklisten förbjuder FRASER; den här filen förbjuder LAYOUTMÖNSTER. Samma logik: mönstren nedan är igenkännbara som "AI-genererad 2020-mallsajt" och kostar trovärdighet oavsett hur snyggt de exekveras. Blocklisten är **default-lag** för alla marknadssidor — hävningsregeln står i sektion C. Läses av stack-builder och content-designer FÖRE bygge, av design-reviewern i template-testet.

## A. Förbjudna/ransonerade layoutmönster (marknadssidor)

- **Centrerad hero** (rubrik + underrubrik + 2 knappar i mitten, ev. bild under) — **FÖRBJUDEN som default.** Tillåten endast om en verklig referens i Referensöversättningen bevisar mönstret för denna kund. Default-riktning: asymmetrisk/vänsterställd komposition eller full-bleed foto med typografi över.
- **Ikonkortsrad** (3–4 kolumner kort med ikon + rubrik + text) — **max EN kortsektion per SAJT.** Tjänster/fördelar uttrycks hellre radbaserat, typografiskt, med stora siffror eller foto.
- **Zebra-sektioner** (bild vänster/text höger alternerande ≥3 ggr i rad) — **FÖRBJUDET.** Variera kompositionen.
- **Kort-på-allt**: vita kort med rounded-xl + mjuk skugga på grå/ljus bakgrund som genomgående sektionsspråk — **FÖRBJUDET som default.** Ytor skiljs hellre med bakgrundsskiften, linjer, luft.
- **Gradient-blobbar/mesh-bakgrunder, lila-blå SaaS-gradienter, pill-badges ovanför H1 ("Nyhet ✨"), emoji i rubriker** — **FÖRBJUDET.**
- **Ikonbibliotek** (Lucide m.fl.) som bärande sektionsgrafik — ikoner endast funktionellt (UI-kontroller, listmarkörer i undantagsfall); innehåll bärs av foto, siffror och typografi.
- **Enhetlig sektionsrytm** (samma vertikala luft mellan alla sektioner) — sektionsrytmen ska varieras medvetet; **minst ett medvetet täta/luftiga-brott per sida.**
- **Numrerade markörer** (01/02/03, eyebrows, dividers) **ENDAST** när innehållet faktiskt är en sekvens där ordningen bär information — struktur ska koda något sant, aldrig dekorera.
- **AI-kluster-paletterna** (2026 års tre igenkännbara AI-looks — endast som dokumenterat val med referensbevis, **ALDRIG som default**):
  1. Varm cream-bakgrund + högkontrast-serif + terrakotta/lera-accent nära `#D97757` (läses som Claude-signatur av designkunniga).
  2. Nära-svart + en enda syragrön/vermilion-accent.
  3. Broadsheet-stil med hairlines, noll radius och täta tidningskolumner.

  **Differentieringsregeln (5c, skärpt):** två på varandra följande ANDRA kunder får aldrig båda landa i samma kluster.
- **Modell-default-genrer/typsnitt** (namngivna konvergens-vektorer bortom paletten — endast som dokumenterat val med referensbevis i §5, ALDRIG som default): **(a) serif-display + sans SOM GENRE** — arkitektonisk/editorial serif-display-rubrik + neutral sans-brödtext är modellens reflexmässiga premium-grepp; det konvergerar mot sig själv OCH mot tidigare kunder OBEROENDE av palett. Differentieringen gäller GENREN, inte typsnittsnamnet: byta serif-typsnitt (t.ex. Libre Caslon → Newsreader) eller justera hex flyr inte genren. **(b) Space Grotesk** som rubrik-default — modellens signatur-grotesk; välj rubriktypsnitt medvetet, aldrig Space Grotesk på autopilot. **Hävning (som paletterna):** ett referensbevisat §5-val i en av dessa riktningar tillåts — en kund KAN förtjäna serif-display-genren med belägg; reflexdefault utan belägg är förbjuden. Skyddar mot att ANDRA kunder tyst konvergerar mot KLASSEN (och därmed mot varandra + mot tidigare kunder som förtjänat greppet), aldrig mot en enskild kunds palett.
- **shadcn/ui-gränsen:** shadcn används för formulär och interaktiva kontroller — **ALDRIG som sektions-/layoutspråk på marknadssidor.** Sektioner byggs custom enligt §5-layoutspråket.

## B. Token-regler (de-templating)

- **Radius:** väljs medvetet i §5 (redaktionell riktning ofta 0–6 px); aldrig stora radier + mjuka skuggor som omedveten default.
- **Skuggor:** nära noll; djup skapas med bakgrund, border, överlapp.
- **Typskala:** VERKLIG kontrast — display-rubrik i clamp-klass (~2.75–5 rem efter riktning), tydlig sekundär röst (etiketter/small-caps/mono om referens stödjer); H1 nära brödtextstorlek = varningstecken.
- **Luft:** ojämnt fördelad med avsikt; generositet där innehållet ska andas, täthet där det ska driva.
- **Yta:** paletten per §5 (cream/ink-klass hellre än vitt/grå-50); grain/texturdetalj om §5 anger.

## C. Tillämpningsregel — och riktningsdeklarationen

Blocklisten är ett förbud mot **KLICHÉER**, aldrig ett påbud om minimalism — motsatsen till mall är **särart, inte tomhet** (spartansk-som-default är kluster-look 3 och lika förbjuden som gradient-korten). Ambitionen är **LEVANDE, påkostade sajter** som driver segmentet framåt: rikedom koncentrerad i signaturelementet och detaljerna, disciplin runtom.

- Blocklisten är **default-lag**; en verklig referens i Referensöversättningen kan medvetet häva **ENSKILT mönster för ENSKILD kund** (dokumenteras i §5 med motivering).
- Bas-antislopens auktoritetsordning gäller: **§5/§7 kan aldrig häva sektion A:s förbjudna-rader utan referensbevis.**
- **Guard mot kopiering (referenstrohet):** trohet mot en referens avser KOMPOSITION och kvalitetsnivå — aldrig pixelkopiering av annans varumärke. Kundens tokens (§5-palett/typo) gäller alltid; att lyfta en referens unika signaturelement rakt av är förbjudet — signaturen ska vara kundens egen (per §5-fältet Signaturelement).
