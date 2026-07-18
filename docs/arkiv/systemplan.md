# Systemplanen — designhistorik (fryst)

Senast verifierad mot systemet: 2026-07-18 · b68252e

> **Fryst historik.** Den här filen berättar hur systemet blev det det är, era för era, med commit-hashar som belägg. Den uppdateras inte och är undantagen doctor-kontrollen av `Senast verifierad`-datum. Det levande beslutsunderlaget är [../05-beslutslogg.md](../05-beslutslogg.md); det levande systemet är filerna i `agents/`, `skills/` och `workflows/`.

## Före git — det som inte finns i historiken

Git-historiken börjar 2026-07-17 med rotcommiten `1a1b57f`, som innehåller hela det då redan fungerande systemet: sju agenter, pipeline-skillsen, antislop-gaten, prelaunch-grindarna och de två workflowsen. Versionerna v1–v4 och beslutet v5 D1 hände före versionskontrollen och finns bara som referenser i senare commit-texter. Det är en medveten ärlighet i den här filen: allt före `1a1b57f` är förhistoria utan belägg i repot.

## v5 — mätbarhet (2026-07-17)

v5:s tema var att göra kvalitet och granskningskostnad mätbara. Eval-skillen kopplades in i launch och retro (`1a1b57f`): grindarna blockerar, evalen mäter, och varje steward-förslag måste sedan dess namnge sitt rubrikkriterium. Verify-steget fick en kalibreringsväg (`--no-verify`, `545f19e`) så att dess kostnad kan A/B-mätas i stället för antas. Granskningslinserna fick explicita INGÅR/INGÅR INTE-gränser och dedup över linser (`2a1b88a`), och minneskurateringen blev obligatorisk med doctor #7 som storleksvakt (`5f77294`).

## Härdningsserierna (2026-07-17)

Samma dag landade två serier som gjorde systemet driftsäkert. **P01–P17** var stewardens härdningsförslag: doctor #8 mot modellincidenten där varje spawn gav HTTP 429 (`28bbed7`), TESTKLIENT-ryggraden med den kanoniska flaggan `business.testklient` (`ae79fa3`), pinnad `create-next-app@15` (`555e808`), Base UI-anpassningen (`3581d24`), JSON-LD-escapen (`f94f858`), TODO-FACT som blockerande kundfråga (`0724cf2`), ring-oss-degradering vid saknad Resend-nyckel (`c1fe35a`) med flera. **D1–D6** var lägesbesluten: fixloopens kategori-routning (`2ca416d`), att ≥90-grinden bor i evalen och review är findings-only (`c0a6f1d`), Optimize mode som on-demand-pass (`7e423da`) och när-triggers på eskaleringslistorna (`22d35dc`).

## v6 — säkerhetsgrinden (2026-07-18)

Gate 7 lade säkerhet till prelaunch: beroenden, faktiskt servade headers, formulärmissbruk och hemligheter, med ett copy-paste-facit i `security-checklist.md` och en sjunde launchlins (`2d82f08`). Grinden kalibrerades med en dry-run där två planterade CRITICAL-fynd (nyckel i klientkomponent, mottagare ur request body) båda hittades. Eval-rubriken bumpades v1.0.0 → v1.1.0. Medvetna avgränsningar: ingen DB-baserad rate limiting (static-first intakt) och juridiken stannar hos människan.

## Rorjour-retron — verkligheten in i systemet (2026-07-18)

Den första skarpa lanseringen (rorjour) gav fem retro-lärdomar som alla blev systemändringar: en-klocks-tidsfällan i stället för tvåklocksbuggen som tyst tappade leads (`669ba62`), RESEND_FROM-fällan där onboarding-avsändaren falskt-passerar ägartester (`fe14435`), CSP-kontrollen av Analytics-loadern (`bab377e`), Gate 0:s TODO-precision (`f62fb8b`) och commit+redeploy före varje omkontroll i fixloopen (`ed3cf95`). Dessutom kartfasaden: en live Maps-iframe visade sig vara ett CRITICAL legal-fynd, så kontaktreceptet kräver numera en samtyckesgrindad fasad (`7df5454`). Mönstret är systemets kärnloop: launchfynd → retro → förslag → applicerad systemändring.

## v7 — designkvalitet (2026-07-18)

v7 attackerade systemets största slop-risk: att alla sajter konvergerar mot samma uttryck. Planern fick steg 5c med branschuppslag och differentiering mot de två senaste briefen, plus Motion-nivån som nedströms kontrakt (`18d3b24`). Premium-checklistan PK-1…PK-8 blev antislops positivyta (`e685f1e`). Humanisera-steget blev obligatoriskt för all copy (`e785212`) och designkanonen — sju namngivna tredjepartsskills — blev obligatorisk i design-reviewer med tömd eskaleringslista (`bfc254c`). Stack-buildern fick en-biblioteksregeln och motion-reglerna (`25d6952`), där Three.js medvetet lämnades utanför MCP-parningen. Eftersom kanonen och humaniseraren nu var obligatoriska vendorades alla åtta bärande tredjepartsskills med facit-kopior och drift-diff (`ae6a7fb`) — kedjan obligatorisk ⇒ bärande ⇒ vendorad. Bibliotekarien och "Största hävstången" gjorde retron systematisk (`20d26ff`). Parallellt kopplades komponent- och animations-MCP:erna in (`782b119`) och gsap-build/threejs-build lades till som guardrailade opt-in-skills (`9bb78dc`).

## v8 — kostnadsdisciplin (2026-07-18)

v8 gjorde kostnaden styrbar utan att sänka ribban. Modellmatrisen kodifierades — Fable där systemet tänker, Opus där det bygger — med doctor #8 som kontraktsvakt (`d1118da`). Verify-kalibreringen fick mekaniska beslutsregler och blev ett aktivt engångssteg (`c23d470`). Mellangranskningar diff-skopades med rapportmeta och launchen fick freshness-grinden (`d4d0c0c`). Sonnet-trappan förbereddes utan att aktiveras, tillsammans med kanon-kostnadsvakten (`5ec3a53`). Usage-loggen blev mätryggraden med doctor #10 som täckningsvakt (`f129cbe`), och cache-hygienen blev doctor #11: systemändringar mellan kunder, efter retro (`baad6ba`). Engångsinventeringen avslutade eran: gsap-build behölls och refereras, threejs-build togs bort tills en brief kräver 3D (`b68252e`).

## v9 — versionerad dokumentation (2026-07-18, denna leverans)

Systemet var versionerat men dokumentationen var det inte: guiden och systemplanen låg oversionerade utanför repot, repot saknade README, och designbeslutens motiv levde bara i commit-meddelanden. v9 flyttar dokumentationen in i repot som källa till sanning (README + `docs/00`–`05` + detta arkiv), seedar beslutsloggen bakåt ur git-historiken, och bygger in underhållet så dokumentationen inte ruttnar: varje fil bär en `Senast verifierad`-rad, steward-förslagen får ett obligatoriskt Docs-påverkan-fält, docs-ändringar committas ihop med systemändringen, och en ny doctor-kontroll vaktar drift mekaniskt. Commit-hashar för v9-leveranserna finns i beslutsloggen.
