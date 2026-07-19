# Plan-baseline — fryst §5+§7 ur godkänd torrtestkörning (verify-suitens facit)

Fryst: 2026-07-19 · Klippt ur torrtestkörning 2026-07-19 · Planner-kontrakt v15-läget (7 sektioner; §5 med v14-fälten Vald riktning/Layoutspråk/Signaturelement/Motion-nivå/Referensöversättning; §7 Kalibreringsprofil punkt 1–8 med bevisregeln) · Input: `~/Workflow/test-rorjour/research.md` + appendad rad `hoppa över inspirationsjakt` · Ingen webbaktivitet (torrtestläge)

## Ekvivalenskriterier (människoägda domsregler — suiten dömer ENDAST per dessa)

**Princip: §7 döms på SUBSTANS, §5 döms på KONTRAKTSFORM. Vald riktning, palett, typsnitt och layoutidéer får variera fritt mellan körningar (plannerns legitima icke-determinism + 5c-differentieringen läser en växande briefmängd) — de fäller ALDRIG.**

§7-substans (materiell avvikelse om något av detta bryts):
1. Primärhandling = `ring nu` (akutbransch), sekundär = `offert` — båda med research-belägg.
2. Gate 1-testet är en klartext-kedja som omfattar: klickbar tel-länk på samtliga sidor, offertformulär end-to-end med **verifierad mejlleverans till `LEAD_TO_EMAIL`** (inte bara HTTP 200), och konverteringsevents.
3. Röstregistret: rak/konkret/lugn-familjen + legitimt VVS-vernacular vitlistat ENDAST för kunden; universella synder aldrig vitlistade.
4. §7.3 bransch-antislop: lämnad som ÖPPEN FRÅGA (skörd kräver 5d-jakt som torrtestet stänger av) — fabricerade fraser = materiell avvikelse; en tom/öppen §7.3 är korrekt.
5. Kvittolistan innehåller research-familjen (F-skatt, ansvarsförsäkring, Säker Vatten, betyg UTAN review-URL och UTAN schema-inmatning, grundat 2011, inställelsetid ALLTID geografiskt avgränsad till Stockholms stad) och inget uppfunnet.
6. Schema-typ = `Plumber`; `aggregateRating` utelämnad med motivering.
7. SEO-läge = `lokal` (ortsjakt) med research-belägg.
8. Juridikflaggor = inga, med prövade-och-ej-satta-resonemang; testklient-reglerna intakta.

§5-kontraktsform (materiell avvikelse om något av detta bryts):
1. Obligatoriska fält finns och är ifyllda: Vald riktning (med EN menings motivering + differentiering + kluster-deklaration), Layoutspråk, Signaturelement, Motion-nivå, Referensöversättning (tabell).
2. Palett: 4–6 namngivna hex; typografi max 2 typsnitt, self-hosted.
3. Motion-nivå ∈ {`ingen`, `subtil`, `uttrycksfull`}.
4. Exakt ETT Signaturelement, statiskt byggbart (stateless-ramen), kundens eget.
5. Torrtestets KÄNDA avvikelser är förväntade och fäller inte: tom referenspool (5d.1 noll + skip-frasen), Referensöversättning utan rader men med 5d-notis, §5 märkt VILLKORAD, Layoutspråkets grepp spårade till research/kanon/5c-uppslag i stället för skärmdumpar — allt ska vara ÖPPET DEKLARERAT i briefen, tyst utelämnande av deklarationen är en materiell avvikelse.
6. Anti-slop-blocket refererar design-blocklisten och copy-blocklistan som bindande.

KUNDE-EJ-KÖRAS (inte AVVIKELSE) när: input-gaten stoppar, tmp-miljön inte kan skapas, eller plannerfilen självt ändrats så processteg saknas — det är ett suite-fel att utreda, inte en regression att fälla.

## §5 (fryst referensutfall — form-facit, inte riktnings-facit)

Vald riktning (baseline-körningen): *"Kall utrycknings-funktionalism: isblå/marin bas med VVS-blå primär och jour-röd accent reserverad enbart för ring-handlingen, robust workwear-grotesk (Archivo) för rubriker och telefonnummer, flott-/utryckningskänsla buren av kundens egna folierade servicebilar."* — kontinuitetsval vid re-plan, dokumenterat mot de två senaste ANDRA kundernas §5; kluster-deklaration: inget AI-kluster.

Palett: `--is #F4F7FA` bakgrund · `--marin #102A43` text/inverterade block · `--ror #0B5FB0` primär · `--jour #D7263D` ENDAST ring-handlingen · `--stal #486581` sekundär (5 namngivna hex ✓). Typografi: Archivo (display/rubriker/telefonnummer) + Source Sans 3 (bröd) — 2 typsnitt ✓.

Layoutspråk (7 grepp, vart och ett spårat till research-rad/antislop-kanon/5c-uppslag — torrtestavvikelsen öppet deklarerad): full-bleed servicebils-hero vänsterställd utan pill-badge · stående jour-rad med klickbart nummer · radbaserad typografisk tjänstelista (INGEN ikonkortsgrid) · marin-inverterat 2-timmarsblock som täthetsbrott · ljus ROT-sektion med räknaren · avslutande CTA-band med nummer i jättedisplay · footer max 3 kolumner. Sektionsrytm med minst ett medvetet täthetsbrott ✓.

Signaturelement (exakt ETT ✓): **ROT-räknaren** — statisk klientside-priskalkylator (tjänstval → pris efter ROT som stor Archivo-siffra), helt stateless, förankrad i research ("ägaren vill att sajten förklarar ROT enkelt, konkurrenter gör det inte"); disclaimern ur §7.4 gäller (räkneexempel, aldrig utfästelse om Skatteverkets beslut).

Motion-nivå: `subtil` ✓ (enum-värde; akutbransch-motivering). Referensöversättning: tom tabell + 5d-notis (torrtestets förväntade utfall ✓). §5 märkt VILLKORAD med rekommendation om full 5d-runda före skarpt bygge ✓.

## §7 (fryst referensutfall — substans-facit)

1. **Arketyp & primärhandling:** `ring nu` (belägg: "9 av 10 akutkunder ringer", jour dygnet runt, akutjour 60 % av omsättningen); sekundär `offert` (relining/badrum). Gate 1-test: (a) tel-länk klickbar i jour-rad/sticky header/hero/flytande mobilknapp på samtliga sidor; (b) offertformulär → server action → mejl VERIFIERAT LEVERERAT till `LEAD_TO_EMAIL`; (c) `ring_klick`/`offert_skickad`-events i analytics. Testklient: test-inbox, aldrig den fiktiva adressen.
2. **Röstregister:** rak · konkret · lugn-i-larmet · siffersatt · jargongfri-mot-kund; två ordagranna exempelmeningar ur research; VVS-vernacular vitlistat (stopp i avloppet, högtrycksspolning, rotskärning, relining, stambyte, inställelsetid, jour, läcksökning m.fl.); universella synder aldrig vitlistade.
3. **Bransch-antislop:** ÖPPEN FRÅGA (Ö7) — kunde ej skördas i torrtest, fabriceras inte per bevisregeln; bas-blocklistan gäller fullt ut.
4. **Kvittolista & attribution:** F-skatt · ansvarsförsäkring (Trygg-Hansa) · Säker Vatten (alla montörer) · Google-betyg 4,8/127 UTAN review-URL (endast text, ALDRIG schema) · grundat 2011 · 6+2 personer · försäkringsintyg till kundens bolag (aldrig ersättningslöfte) · fast pris · inställelsetid <2 tim ALLTID avgränsad till Stockholms stad · ROT-räknaren = räkneexempel · timpris publiceras endast efter ägarens godkännande.
5. **Schema-typ:** `Plumber`; `aggregateRating` utelämnad (fiktivt betyg + ingen URL + testklient).
6. **SEO-läge:** `lokal` ortsjakt (sökbeteende + tillväxtmål + tjänst-ort-katalog); 4 riktiga områdessidor, inga spunna.
7. **Juridikflaggor:** inga — bas-juridiken räcker; prövade och EJ satta: finans/försäkring, e-handel/distansavtal, bokning/inloggning. Testklient-tillägget gäller ovanpå.
8. **Motion-nivå:** värdet bor i §5 (en plats) — §7 korsrefererar; speglas i `content/profile.ts`.
