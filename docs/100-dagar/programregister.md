# Programregister — 100-dagarsprogrammet (v2.3-verified)

**Skapat:** 2026-07-30 (Dag 1 / D001 · BATCH-001-baseline-freeze) · **base-SHA:** `69559a5`
**Repo:** Jonkebronk/nortropic-system (git i `~/.claude`) · **AUTOPILOT:** `off`
**Ägare:** Jonkebronk (kontakt: se privat kanal — ej i publikt repo)

## Scope
Härda, förenkla och komplettera det befintliga Nortropic-systemet till en hel
webbyrålivscykel enligt 100-dagarsmanualen v2.3-verified (10 faser, dag-exitgrindar,
inte kalenderdagar). Målet är INTE att ersätta systemet eller lägga på agent-swarm.
Underlagspaketet (`~/Workflow/nortropic transformation/`) är DATA, inte bevis på dagens
repotillstånd; körbar kod på verifierad commit vinner (källhierarki 1).

## Nulägesmått (baslinje @ 69559a5)
- 244 spårade filer: vendored-skills 170 · skills 40 · docs 12 · agents 7 · workflows 6 ·
  tests 4 · scripts 1 · 4 rotfiler.
- 7 agenter (user-level, ingen plugin-shippad) · 6 workflows · 9 load-bearing vendored skills
  (drift-diff 0, detektiv — NRT-005 kvarstår PARTIAL) · doctor 1–13 · agent-memory 556 rader.
- Claude Code 2.1.212 · 16 plugins (claude-plugins-official) · inget mcpServers-block i ~/.claude.json.
- Baslinjebevis: annoterad tagg `100d-baseline-20260730` (tagg-objekt 7e08d29, peelar till
  69559a5; pushad till origin per BESLUT-004) + backup-arkivets SHA-256 (i baseline-manifestets
  sektion (ii); arkivets plats: se backupkvittot utanför repot).
- **Taggens annotation anger felaktigt "ej pushad"** — den pushades per BESLUT-004. Annotationen
  är MEDVETET ej omskriven: omskrivning hade ändrat tagg-objektets SHA (7e08d29) och brutit
  oföränderligheten. Felet lämnas stå. Tagg-objekt 7e08d29, peelar till 69559a5.
- **Doctor-utfall (C4, mot baslinjen 69559a5): 0 FAIL / 10 PASS / 3 WARN** — namngivna:
  **#3** (seo-eskaleringarnas payload-klass), **#10** (usage-logg saknar rad för senaste
  perioden), **#12(d)** (docs/07-stämpel 2026-07-28 < baslinjen 2026-07-30). Alla tre kända
  och öppna i befintliga förslag/beslut; ingen införd av denna batch.
- **NRT-001…012: status oförändrad** — inget fynd adresserades i denna batch. Doctor är
  systemets HÄLSOKONTROLL och validerar INTE NRT-fynden (t.ex. #001 gate-rerun, #003
  launch-atomicitet, #004 permissions); de klassas om i sina egna dagar, aldrig av doctor-grön.

## Stoppregler (globala)
- AUTOPILOT hålls `off` under sanering; N2 (nattskiftet) förblir av tills dag 60 och 99
  uttryckligen ger GO. AUTOPILOT-filen ändras ENDAST av människa (§A6) — aldrig av denna batch.
- Commit, push, deploy, vendor-update och baseline-/konstitutionsändring kräver separat
  uttrycklig mänsklig review. Aldrig `git add -A`.
- En röd säkerhets-/integritetsgrind blockerar nästa fas.
- Ingen dag markeras klar utan uppfyllt exitkriterium + evidens. UNKNOWN får aldrig bli PASS;
  odömbart = BLOCKED/INVALID. `NO-OP VERIFIED` när målet redan är uppfyllt likvärdigt/säkrare.
- Varje fas avslutas med GO / CONDITIONAL GO / NO-GO. Numrerad dag överrider aldrig exitgrind.

## Registrerade avvikelser (Dag 1)
- **(i) source_archive/ + SHA256SUMS saknas** i det levererade paketet → V2.1-tilläggets
  källarkivhash kan INTE beräknas. Status: **BLOCKED**. Ersättning: git-blob-hash över de
  faktiskt spårade filerna @ 69559a5 (baseline-manifest sektion (i), 244 filer).
- **(ii) MASTER-00 kördes inte som separat pass (BESLUT-003)** — runtime-inventeringen gjordes
  infälld i denna batchs fas A. Medveten avvikelse från START HERE:s startordning.
- **(iii) Baslinjetaggen är LOKAL** tills BESLUT-004 verkställs → exitkriteriet "reproducerbar
  från tagg" är inte fullt uppfyllt vid batchens slut (taggen finns bara lokalt tills push).

## Residualrisker (Dag 1)
- Båda remotes (nortropic-system, workflow-backup) saknar branch protection (free plan) →
  force-push EJ blockerad → remoten är muterbar; oföränderligt bevis = tagg-SHA + arkiv-SHA-256,
  ALDRIG remoten.
- Krypteringsstatus för backupmedia: se backupkvitto (utanför repot).
- Frysningens "inga auto-commits"-påstående vilar på AUTOPILOT=off + N1-triggermekanismen
  (se batchens C6: ingen cron, ingen Windows-schemalagd task, ingen SessionStart/End-hook —
  stewarden har ingen autonom/schemalagd trigger); ett punktprov bevisar det inte, mekanismen gör.

## Uppskjutet (ägarbeslut Dag 1)
- **Verify-suite uppskjuten:** ingen FUNKTIONELL baslinje finns — Dag 1 fryser STRUKTUR
  (filhashar), inte BETEENDE. Första funktionella ändringen ska köra verify-suite **TVÅ gånger**
  — före OCH efter den ändringen — i stället för att jämföra mot Dag 1. Doctor-grinden (1–13)
  är dess fas 1 och är redan grön mot baslinjen ovan.

## Minnesdelta efter baslinjen (Dag 1)
Efter att backup-arkivet byggdes (B4) och exitkriterierna deklarerats uppfyllda skrevs tre
minnesfiler av BATCH-001:s egen avslutning. Arkivet representerar tillståndet FÖRE dessa
skrivningar; arkivets SHA-256 är committad och refererad — **arkivet byggs INTE om**.
- **I arkivets scope** (`agent-memory/`): `nortropic-steward/system_baselines.md` skrevs om av
  C4-doctorkörningen efter arkivbygget (filsystem-mtime 2026-07-31T05:29Z, 32 rader) → arkivet
  bär pre-C4-versionen, disken är nyare.
- **Utanför arkivets scope** (`projects/.../memory/`, EJ i backupen): `nortropic_100dagar_program.md`
  (13 rader, ny) + en pekarrad i `MEMORY.md` (mtime ~2026-07-31T06:14Z) — batch-avslutningens
  minneshygien.
- **NRT-011:s canary-test (Dag 72/93) ska SUBTRAHERA detta delta** — särskilt
  system_baselines.md-omskrivningen — annars går det inte att skilja "kundidentifierare kom in
  under programmet" från "fanns redan i baslinjen".
- **Scopeobservation (mönster, ingen åtgärd nu):** skrivningarna låg UTANFÖR batchens 3-filers
  allowlist och skedde EFTER att exitkriterierna deklarerats uppfyllda.

## Stående regel (ur Dag 1)
Varje batch som ögonblicksbildar agentminnet tar bilden **EFTER alla tester** (inkl. doctor /
verify-suite), ELLER behandlar doctor som en **muterande** operation på agentminnet. Grund:
C4-doctorkörningen skrev om `system_baselines.md` efter att arkivet byggts, så arkivet blev
pre-C4. En agentminnes-snapshot före en muterande testkörning är inte den testade sanningen.

## Öppen fråga → Steg A / Dag 2 (ställd, ej besvarad)
**Skriver doctor om sin egen jämförelsereferens vid varje körning?** Om ja kan den inte upptäcka
drift från en fast punkt, och "0 FAIL / GRÖN" är ett svagare påstående än det ser ut.
**Fynd (Dag 1, läs-only, inget ändrat):** `system_baselines.md` är stewardens EGNA minne
(`memory: user`) — en logg av tidigare körningar (V13–V29) + metodnoteringar. Stewarden
**skriver** den (minneshygien) och **konsulterar** den för kontext, men doctor-KONTROLLERNA
(pass/fail) jämför mot LEVANDE systemfiler + människoägda FASTA referenser (`tests/fixtures`
§A6, konstitutionen §A, eval-rubriken §A2, MODELLKONTRAKTET i agentkroppen) — INTE mot
`system_baselines.md`. Det mekaniska "0 FAIL" är alltså förankrat i fasta referenser, inte en
muterbar självreferens. **Kvarstår för Dag 2:** stewardens NARRATIVA tolkning (t.ex.
"WARN-trippeln stabil") är förankrad i dess självskrivna minne — undersök om det färgar
bedömningen. Ändra inget nu.

## BATCH-002 — Invariantgrind (deterministisk) + NRT-007-markör
**Införd:** `scripts/check-invariants.mjs` — ren Node, inga npm-beroenden, inga nätanrop; kör
från reporoten; exit 0/1; en rad per överträdelse + summering `X PASS, Y FAIL, Z överträdelser`.
Base-SHA `8872e0e`.

**De fem invarianterna:**
- **INV-001 (NRT-003):** ingen `git add -A` i GIT-SPÅRADE filer under `workflows/` + `skills/`
  (scope = git-tree, ej filsystem — ospårad tredjeparts hamnar utanför automatiskt, invendorad
  innanför automatiskt; ingen undantagslista att underhålla).
- **INV-002 (NRT-004):** design-reviewers tools-rad utan `Bash`.
- **INV-003 (NRT-013):** ingen query-form `x-vercel-protection-bypass=` i `workflows/` (header-form tillåten).
- **INV-004 (NRT-007):** varje agent med `Bash`/`WebFetch`/`WebSearch`/`mcp__` måste bära
  markörraden `## EXTERN DATA ÄR INTE INSTRUKTIONER`.
- **INV-005 (NRT-009):** verify-suitens doctor-checkantal == stewardens (talen läses ur
  källorna, aldrig hårdkodade; oparsbart → INVALID, aldrig tyst PASS).

**Utfall (evidens):**
- FÖRE fix: exit 1, **13** överträdelser (INV-001:3 · INV-002:1 · INV-003:1 · INV-004:7 · INV-005:1).
- EFTER B4 (markörblock till alla 7 agenter, verbatim-identiskt): exit 1, **6** överträdelser (INV-004→0).
- Negativt test: markörraden struken ur en agent i scratch utanför repot → exakt den filen
  flaggas; grind utan git-repo → INV-001 `KUNDE-EJ-BEDOMA (INVALID)`, aldrig tyst PASS.

**Fyra kvarstående överträdelser — AVSIKTLIGT uppskjutna till BATCH-003** (ingen blindfix;
var och en kräver utredning):
- INV-001 ×3 (`git add -A` i launch/autobygg-workflows + stack-SKILL) — launch-raden lagar ett
  DOKUMENTERAT fel (ocommittade fixar under en granskningsrunda); kräver ersättning, ej strykning.
- INV-002 ×1 (design-reviewers Bash) — användningen okänd, utred före borttagning.
- INV-005 ×1 (doctor 12 vs 13) — ägarbeslut om vilket tal som är sant.

**Grinden fångade ett fel i KRAVSPECEN innan någon fil ändrades:** specens deklarerade
totalsummor (11 före / 4 efter) stämde inte mot dess egen per-INV-fördelning (13 / 6). En
assertion på exakta tal avslöjade det i preflight — precis vad grinden är till för. Per-INV-
analysen var korrekt; totalerna var felräknade (ägar-rättelse, loggad här som grindbevis).

## Oberoende verifiering — "reproducerbar från tagg" BEVISAT (ej bara påstått)
En oberoende part räknade om samtliga **244 git-blob SHA-256 vid `69559a5`** från en EGEN klon
på ett ANNAT OS och jämförde mot manifestet på `origin/main`: **noll avvikelser, noll saknade,
noll överskjutande.** Self-hashen över sektion (i):s kropp med LF = **`2d2f7145`** (exakt det
rapporterade värdet); med CRLF blir den `a1d8fc72` — git-blob-metoden gjorde alltså precis det
den valdes för (OS-oberoende reproduktion, immun mot CRLF-munging). Exitkriteriet "reproducerbar
från tagg" (Dag 1) är därmed BEVISAT av tredje part på ett annat OS, inte bara internt påstått —
programmets starkaste evidens hittills.

## Styrningsfynd (BATCH-004-material — åtgärda inte nu)
Under BATCH-002 blockerade **security-guidance-pluginens PreToolUse-hook** ett `execSync`-anrop i
`check-invariants.mjs` och tvingade fram `execFileSync` (ingen shell). Två slutsatser:
- **NRT-007-nyansering:** bedömningen av de fyra auto-hookarna var för ensidig — de är OSTYRDA,
  men inte enbart risk; här fångade en av dem ett skalanrop.
- **Beroendefynd:** grinden hade skeppats med ett skalanrop om hooken inte funnits. En
  säkerhetskontroll UTANFÖR nortropic-styrningen fångade något den egna processen missade —
  systemets säkerhetsgrind vilade på en plugin som ingen i styrningen äger, versionshanterar
  eller kan garantera finns kvar.

**Klassning: STYRNINGSFYND.** BATCH-004-frågan är inte om hooken ska bort, utan om systemet ska
ha en EGEN motsvarighet det äger. Ingen åtgärd i denna batch.

## Stående regel — minnesskriv-bokföring (från och med BATCH-002)
Varje slutrapport ska innehålla en egen rad **"Minnesskrivningar denna batch"** som listar
**fil, radantal och tidpunkt** för VARJE skrivning till `agent-memory/` eller `MEMORY.md` —
även när de sker EFTER att exitkriterierna deklarerats. Skäl: minnesskrivning har nu skett efter
exit i två batchar i rad. Innehållet är nyttigt och ska inte upphöra — problemet är bokföringen:
varje oskriven skrivning ökar avståndet mellan Dag 1-arkivet och verkligheten, och NRT-011:s
canary (Dag 72/93) kan subtrahera två deltan men inte sjuttio. Deltat ska vara
SJÄLVDOKUMENTERANDE, inte rekonstruerat i efterhand.

**Retroaktiv registrering — BATCH-002:s egen minnesskrivning:**
- `projects/.../memory/nortropic_100dagar_program.md` — uppdaterad (BATCH-002-sektion tillagd
  → 20 rader), mtime 2026-07-31T08:02:46Z. Ligger utanför arkivets `agent-memory`-scope.
- `MEMORY.md` — orörd i BATCH-002 (senaste ändring i BATCH-001, mtime 2026-07-31T06:14Z).

## Reservation — INV-005 är deklarationskonsistens, inte täckning (ägar-granskning)
**Historik (dåtid, daterad).** Före BATCH-003 läste INV-005 endast **FÖRSTA** förekomsten av
mönstret `checks|kontroller 1–N` i `workflows/nortropic-verify-suite.js` och breakade. Första
träffen var en `detail:`-sträng inuti `meta.phases` (loggmetadata, rad 6), INTE den verkliga
instruktionen till stewarden (rad 86). Båda sade då `1–12`, så grinden gav rätt svar men av fel
skäl: hade man rättat enbart loggmetadata-strängen hade INV-005 blivit grön medan stewarden
fortfarande instruerades köra tolv kontroller — grinden hade då intygat att NRT-009 var löst utan
att beteendet ändrats. **BATCH-003** tog bort `break` och flaggar sedan per förekomst
(deklarationskonsistens: risken att ljuga grön strukturellt borttagen). **BATCH-004A** rättade
båda strängarna till `1–13` och stängde driften mot stewardens tretton kontroller.

**Kvarstående begränsning (levande).** Grinden skiljer inte på VILKEN förekomst som gjorde jobbet
— deklarationskonsistens är inte beteendetäckning. Därför krävs beteendeverifiering att stewarden
faktiskt kör tretton kontroller inklusive #13 (BATCH-004A C2 — resultat i NRT-009-avsnittet nedan).

## Ytterligare härdningspunkter → BATCH-003 (registrera, åtgärda inte nu)
- **INV-003 scannar endast `workflows/`.** Flyttas bypass-strängen till en skill eller ett
  agentblock upptäcks den inte — bredda scope i BATCH-003.
- **INV-004 kontrollerar endast att RUBRIKEN finns.** Blockets brödtext kan bytas ut medan
  kontrollen förblir grön — en HASH över hela blocket vore starkare.

## BATCH-003 — Grindhärdning (endast skärpta kontroller, inga fixar)
Tre kontroller härdade; INV-001 + INV-002 orörda. Utfall **6 → 8** överträdelser (steg, aldrig
sjönk — grundprincipen: en härdning som gör grinden grönare är per definition felskriven).
Base-SHA `7984377`.

- **INV-005 — matcha SAMTLIGA förekomster, inte den första.** `break` borttaget; varje träff på
  `checks|kontroller 1–N` i verify-suite samlas och flaggas per förekomst vars tal avviker från
  stewardens. FÖRE: 1 (rad 6). EFTER: 2 (rad 6 = loggmetadata i `meta.phases`, rad 86 = den
  faktiska instruktionen till stewarden) — båda 12 mot stewardens 13. **Negativt test bevisat:**
  ändras BARA rad 6 till 1–13 i scratch flaggas rad 86 fortfarande → ingen enskild sträng kan
  ljuga grinden grön.
- **INV-003 — breddat scope + medveten undantagsprincip.** FÖRE: endast `workflows/`. EFTER:
  git-spårade filer under `workflows/ + skills/ + agents/`, med `scripts/` och `docs/` UNDANTAGNA.
  Breddningen avslöjade en tidigare OSYNLIG förekomst: `skills/nortropic-prelaunch/SKILL.md:11`.
  FÖRE: 1 (launch.js:54). EFTER: 2.
- **INV-004 — hasha blocket, inte bara rubriken.** Blocket (markörrad → nästa `## ` eller
  filslut, LF-normaliserat) hashas och jämförs mot en hårdkodad konstant `7ecd05e0…` — en
  säkerhetsinvariant; avsiktlig ändring KRÄVER medveten uppdatering av konstanten. Alla sju
  block identiska → EFTER: 0. Negativt test: ett ändrat tecken i ett agentblock flaggar exakt
  den filen (blockhash avviker), övriga rena.

**Stående princip (från INV-003-härdningen):** *En mönstermatchande grind scannar ALDRIG sin
egen källkod eller sin egen dokumentation.* Grindens källa bär nödvändigtvis söksträngen den
letar efter, och programregistret beskriver regeln; skulle de scannas flaggar grinden sig själv,
blir permanent röd, och någon "löser" det genom att ta bort kontrollen.

**Känd begränsning — INV-004 förutsätter identiska block (ägar-tillägg, medvetet vald).** Den
gemensamma blockhashen låser alla sju agenter till ETT identiskt block: enklare, verifierbart och
tillräckligt nu. Men det utesluter per-agent-skärpning. Konkret bär `project-planner` ensam både
`WebFetch`, `WebSearch` och `Write` — en bredare injektionsyta än t.ex. `seo-optimizer`. Vill man
någon gång ge den en strängare klausul kräver det att INV-004 görs om (t.ex. hasha ett
obligatoriskt KÄRNSTYCKE och tillåta agentspecifik text efter det). **INV-004 förutsätter
identiska block. Per-agent-skärpning kräver omdesign av kontrollen. Känd begränsning, medvetet vald.**

**Fixarna av de 8 överträdelserna är BATCH-004.** Denna batch skärpte endast kontrollerna.

## Oberoende verifiering — INV-004:s blockhash reproducerbar (ej bara internt konsekvent)
En oberoende part reproducerade konstanten `7ecd05e0` från en EGEN klon UTAN tillgång till
grindkoden: SHA-256 över blocket (markör→EOF), LF-normaliserat och rstrip:at, räknat på
`origin/main:agents/qa-launcher.md`. **Utan rstrip blir värdet `cb884e24`** — skillnaden är
ENBART den avslutande radbrytningen. rstrip (`\n+$` bort) är rätt val: en agentfil som får en
extra eller saknad slutrad ska inte flagga falskt. Konstanten är därmed oberoende reproducerbar,
inte bara internt konsekvent.

## Stående regel — direkt på main utan branch (endast om SAMTLIGA fyra villkor gäller)
"Direkt på main utan branch och granskning" är tillåtet ENDAST när alla fyra villkor är uppfyllda:
1. Ändringen rör ENBART filer under `docs/100-dagar/` (programmets eget protokoll) — ALDRIG
   `scripts/`, `agents/`, `workflows/`, `skills/`, `docs/00-07` eller `docs/05-beslutslogg.md`
   (den senare är ett maskinläst styrningsregister).
2. Ingen körbar kod, inga agent- eller workflowdefinitioner, inga grindkontroller.
3. Ändringen REGISTRERAR något som redan är beslutat och granskat — den får INTE introducera ett
   nytt påstående, en ny slutsats eller en ny rekommendation.
4. Grinden körs FÖRE och EFTER och ger identiskt utfall — main lämnas aldrig i ett okänt
   grindtillstånd, ens efter en dokumentationscommit.

Kriteriet är ändringens KARAKTÄR, inte dess storlek. En rad ny kod går alltid via branch;
fyrtio rader protokoll som registrerar ett fattat beslut gör det inte. (Denna regel infördes
själv enligt villkoren: docs/100-dagar/, ingen kod, registrerar ett fattat ägarbeslut, grind
oförändrad FÖRE/EFTER.)

## BATCH-004A — NRT-009 STÄNGD (doctor 12→13, §A6/HÖGRISK)
**Fix.** `workflows/nortropic-verify-suite.js` rad 6 (loggmetadata i `meta.phases`) och rad 86
(den faktiska stewardinstruktionen) ändrade `1–12` → `1–13`. Inget annat i filen rört.

**Dateringsevidens (drift, inte designval).** verify-suite.js skapades `6f0f6d1` 2026-07-19 och
sade `1–12` från första commit (`git log -S '1–13'` = tom — filen har aldrig sagt annat). Doctor
#13 tillkom i stewarden `15e2d65` 2026-07-28 → **nio dagars drift**. `15e2d65`:s egen commitmening
flaggade redan att verify-suitens `1–12` lämnades till ägarens HÖGRISK-hand.

**§A6/HÖGRISK.** `docs/07-konstitution.md` §A punkt 6 skyddar `workflows/nortropic-verify-suite.js`
vid namn ("regressionssviten … styrningen själv"). Ändringen är därför en §A6-ändring: tillåten
för människa (§A1: "kräver människa + HÖGRISK-märkning"), aldrig för trappan. Commit + beslutslogg
märkta `[HÖGRISK, ägar-diffgranskad]`; rad 6/86-diffen visades ordagrant för ägaren före commit.

**Beteendeverifiering (C2 — batchens egentliga bevis, körd EXAKT en gång).** Grinden (INV-005)
bevisar bara strängöverensstämmelse. C2 körde verify-suitens doctorfas: stewarden utförde
**FAKTISKT 13 kontroller** (numrerade 1–13), **inklusive #13 (Modellfärskhet) → PASS**. Totalt
0 FAIL · 4 WARN (#3/#10/#11/#12) · 1 KUNDE-EJ (#4 MCP, WARN-klass — huvudsessionen bekräftade
10/10 Connected). Kostnad: 144 497 tokens, 33 verktygsanrop, ~27,6 min. **NRT-009 är därmed
stängd både strukturellt (grind) OCH beteendemässigt (C2).**

**Ägar-rättelse registrerad.** BATCH-004A:s ursprungliga spec ramade ändringen som "icke-§A".
Fel: verify-suite.js är §A6-skyddad, och uppgiften stod redan i BATCH-001:s Fas A-rapport men
missades ändå. Rätt ram (§A6/HÖGRISK) etablerades i preflight och bekräftades medvetet av ägaren.

## 004B — förhandsregistrerat beslut (åtgärdas i 004B, ej här)
design-reviewers `Bash` används till exakt ETT anrop: `pnpm start` (rad 39), en fallback för att
rendera lokalt när ingen Vercel-preview går att nå. Primärvägen är chrome-devtools mot
preview-URL; lokal `.next` avråds uttryckligen (rad 37–38). **Beslut inför 004B:** `Bash` tas bort
och fallbacken accepteras försvinna — en reviewer som tyst faller tillbaka på en lokalt renderad
sajt granskar inte samma artefakt den ska granska; vid en launchgrind är det sämre än att
misslyckas högt. **004B exitkriterium:** reviewern svarar **BLOCKED** vid onåbar preview, aldrig
tyst utebli; testas separat. `agents/design-reviewer.md` rörs INTE i BATCH-004A.

## Stående regel — levande påstående vs historisk förklaring
Registret blandar två sorters påståenden som inte tål samma underhåll:
1. **LEVANDE PÅSTÅENDE** om nuläget (nulägesmått, aktuella grindtillstånd, pågående begränsningar)
   — uppdateras när verkligheten ändras. Ett inaktuellt levande påstående är samma docs↔kod-drift
   programmet finns till för att stänga.
2. **HISTORISK FÖRKLARING** av ett fattat beslut (varför en kontroll härdades, vilket problem som
   fanns) — skrivs i DÅTID och DATERAS med batch-ID. Skrivs ALDRIG om till att beskriva nuläget;
   då förloras motivet.
3. **`docs/05-beslutslogg.md`:** befintliga beslutsrader ändras ALDRIG — historik skrivs inte om. Nya rader appendas i tabellen, direkt efter sista raden. Toppmetadatans stämpelrad underhålls som i alla andra `docs/*.md`, eftersom doctor #12(d) kräver den aktuell. Filens avslutande `---`/`RETRO-1-GENOMFÖRD` rörs aldrig. (Ägar-korrigering BATCH-004BE 2026-07-31: den tidigare lydelsen "redigeras aldrig alls" var för absolut och skyddade av misstag även toppmetadatan — en regel som garanterar en permanent #12(d)-WARN kan inte vara rätt; den skyddar RADERNA, inte stämpeln.)
Nya förklaringar skrivs i dåtid direkt — ett stycke som säger "i nuvarande form" åldras alltid
fel. (INV-005-reservationen ovan reframades enligt denna regel i BATCH-004A: den beskrev grindens
FÖRE-härdnings-beteende i presens och var redan inaktuell sedan BATCH-003 tog bort `break`.)

## GRINDINTEGRITETSFYND → BATCH-004D (registrera, åtgärda inte nu · prioritet > 004C)
**Fyndet (C2, BATCH-004A).** verify-suitens doctorfas rapporterade GRÖN (0 FAIL) med en kontroll
(#4 MCP) som aldrig utvärderades. En KUNDE-EJ-BEDÖMA-kontroll fällde inte grinden → sviten
intygade grönt med en outvärderad kontroll — strukturellt SAMMA hål som INV-005 hade (vi byggde
`INVALID → FAIL` i vår egen grind av exakt detta skäl).

**Diagnos (verifierad mot koden — den tidigare "MCP permanent oevaluerbar"-hypotesen var FEL och
ersätts).** Doctor #4 är INTE trasig: dess text föreskriver KUNDE-EJ-KÖRAS vid omöjlig verifiering
och förbjuder uttryckligen tyst PASS — samma princip som vår grinds INVALID→FAIL. Kontrollen är
välskriven. Felet ligger i MOTTAGANDET i `workflows/nortropic-verify-suite.js`:
- **rad 23** `status: { type: 'string', enum: ['PASS', 'FAIL'] }` — BINÄRT schema, ingen tredje status.
- **rad 89** `const doctorFailed = !doctor || doctor.status === 'FAIL'` — endast FAIL fäller.
KUNDE-EJ-KÖRAS har ingen plats i schemat → hamnar i `warns` → warns fäller inte grinden → sviten
rapporterar GRÖN med en outvärderad kontroll.

**Systemet har redan mönstret.** Proberna har `enum ['PASS','FAIL','OGILTIG']` (rad 55, 70) och
verdiktlogiken hanterar OGILTIG korrekt (rad 128–133); rad 126 säger det uttryckligen: "En probe
som dog är odömbar → OGILTIG, aldrig tyst grön." **Doctor är enda fasen utan tredje status — och
den grindar alla andra.**

**004D är därmed en LITEN schemaändring** (ge doctorfasen en tredje status och fäll grinden
fail-closed på den, precis som proberna), med starkt stöd i systemets egen design — INTE en
utredning av MCP-synlighet. **Prioritet: 004D FÖRE 004C.** Schemat/mottagandet bor i
`verify-suite.js` (§A6-yta, "regressionssviten") → 004D blir en §A6-ändring, människohand/HÖGRISK.

## BATCH-004E (föreslaget ID) — docs-drift som DENNA process skapade
BATCH-002 (`b4d77ab`) rörde sju agentkroppar 2026-07-31 (NRT-007-blocket) utan att omstämpla docs
→ doctor #12(d)/(e) WARN (C2-körningen såg den). Det är drift VÅR EGEN process skapade; den får ett
eget batch-ID (004E: `Senast verifierad`-omstämpling efter agent-body-tillägget), inte en anonym
backloggrad. Vi lämnar inte drift efter oss.

## Mätt kostnad — underlag för verify-suite-uppskjutningen
C2, EN doctorfas: **144 497 tokens · 33 verktygsanrop · ~27,6 min.** Mätt, ej gissat. Underlag för
regeln att verify-suiten körs TVÅ gånger (före+efter) endast vid första FUNKTIONELLA ändringen —
kostnaden är verklig, inte antagen.

## Observation — BATCH-004A färdigställde en PÅBÖRJAD ägarhandling (inte en missad drift)
`docs/05-beslutslogg.md:127` (2026-07-28, "§A-sittning · N1-baslinjen 1–12→1–13, §A6, HÖGRISK,
ägarhandling") visar att ägaren DÅ höjde stewardens baslinje till 1–13 men MEDVETET lämnade
verify-suitens motsvarighet till senare. BATCH-004A var därför INTE en upptäckt av okänd drift —
det var färdigställandet av en redan påbörjad ägarhandling. **Detta förändrar hur NRT-009 ska
läsas i efterhand: fyndet var KÄNT, inte missat.** Nyansering av BATCH-004A:s "ägar-rättelse":
det som missades i 004A:s spec var §A6-NATUREN (att verify-suite.js är grundlagsskyddad), inte
driften i sig — driften var känd och medvetet uppskjuten sedan 2026-07-28.

## BATCH-004D — GRINDINTEGRITET: doctorfasen fick tredje status (OGILTIG). §A6/HÖGRISK. STÄNGD.
**Fix (minsta möjliga), verify-suite.js.** DOCTOR-schemat fick `OGILTIG` + `note`-fält;
doctorinstruktionen (rad 86) instruerar KUNDE-EJ-KÖRAS → status OGILTIG med note (aldrig PASS+WARN);
aggregeringen la `doctorInvalid` i den BEFINTLIGA OGILTIG-grenen (RÖD slår OGILTIG slår GRÖN — ingen
ny hierarki); logg/summary/return visar tre-status. Proberna körs MEDVETET även vid doctor OGILTIG
(#4 är ortogonal mot plan-/eval-/template-regression — motivering som kodkommentar vid rad 93). "checks 1–13"
orörd → INV-005 grön. Inget annat rört.

**Diagnos (dåtid, färdigställd).** Doctor #4 var INTE trasig — dess text föreskrev KUNDE-EJ-KÖRAS
och förbjöd tyst PASS. Felet låg i MOTTAGANDET: DOCTOR-schemat var binärt (PASS/FAIL), så en
KUNDE-EJ-KÖRAS hade ingen plats → hamnade i warns → warns fällde inte grinden → sviten rapporterade
GRÖN med en outvärderad kontroll (samma hål INV-005 hade). Proberna hade redan tredje status
(OGILTIG, rad 55/70) + verdiktlogik; doctor var enda fasen utan den, och den grindade alla andra.

**Beteendeverifiering (C2 — batchens bevis, körd EXAKT en gång).** Doctorfasen kördes med det nya
kontraktet: **status blev OGILTIG** (inte PASS), **note namnger #4** (MCP-integritet KUNDE-EJ-KÖRAS,
8 av 10 mcp__-tokens obekräftbara i subagentkontext), 0 FAIL / 4 WARN / 1 KUNDE-EJ / 8 PASS. Under
det GAMLA binära kontraktet hade samma tillstånd rapporterats **GRÖN/PASS** — precis blindheten 004D
stänger. Aggregerat verdikt: **OGILTIG** (ej GRÖN → batchen lyckades). Kostnad: 149 003 tokens, 15
verktygsanrop, ~17 min (jfr 004A:s C2: 144 497).

**Enhetstest (C3).** Verdiktlogiken enhetstestad mot en KOPIA av rad 141–143: doctor PASS + rena
prober → GRÖN (sviten blir INTE permanent OGILTIG), doctor OGILTIG → OGILTIG, **doctor OGILTIG +
probe FAIL → RÖD** (en verklig regression döljs INTE bakom den oevaluerbara kontrollen — motiverar
prob-körningsvalet).

## Blast radius (ägar-verifierad, registrerad)
- **N1 (Vaktmästaren) berörs INTE.** Dess protokoll är "kör doctor 1–13, grön = 0 FAIL" direkt i
  huvudsessionen, utan DOCTOR-schemat (som bor i verify-suite.js och används bara där). N1 kan mycket
  väl evaluera #4 där subagenten inte kan.
- **N2 (Nattskiftet) berörs HELT.** Dess protokoll kräver "verdikt GRÖN i VERIFY-SUITE-RESULT.md".
  Permanent OGILTIG (om #4 förblir oevaluerbar i grinden) = N2 kan aldrig applicera.
- **AUTOPILOT är `off` → praktisk påverkan i dag = noll. KOPPLING (registrerad så den upptäcks före,
  inte av någon som undrar varför nattskiftet vägrar): AUTOPILOT får INTE höjas till `on` förrän
  OGILTIG-frågan (004F) är löst.**

## 004F — bokat (villkorat på C2, villkoret uppfyllt)
C2 visade att doctor blir OGILTIG i subagentkontext (#4 oevaluerbar där, 8/10 tokens obekräftbara).
Därför skapas **004F**: "gör #4 nåbar i grinden (mata in huvudsessionens /mcp-tillstånd i doctorfasen),
ELLER scopa ut #4 ur verify-suitens doctorfas". Åtgärdas INTE i 004D. **004F blockerar AUTOPILOT `on`**
(se blast radius). Ägd fråga med ID — inte en öppen fråga i löptext.

## Stående regel — AKTUATOR vs PROTOKOLL (ägarbeslut 2026-07-31; formellt registrerad här, per regeln själv)
Rätt processteg beror på artefaktens typ:
1. **AKTUATOR** — cross-session-minnet (`projects/.../memory/`). Styr nästa sessions beteende; en
   felaktig post får en framtida session att börja i fel ände → korrigeras OMEDELBART, i den tur felet
   upptäcks, UTAN branch. Redovisas per bokföringsregeln.
2. **PROTOKOLL** — `docs/100-dagar/programregister.md`. Läses av människor i efterhand, styr inget
   automatiskt → diagnostiska korrigeringar och tolkande slutsatser FÖLJER MED nästa substantiella
   batch (som denna post gör), ingen egen branch/granskningsrunda. Undantag: ett registerpåstående som
   aktivt kan vilseleda PÅGÅENDE arbete → egen branch.
3. `docs/05-beslutslogg.md`: befintliga beslutsrader redigeras aldrig; toppmetadatans stämpelrad underhålls per #12(d) (se den korrigerade regeln under "levande påstående vs historisk förklaring").
Motiv: två dokumentationsbranchar i rad kostade två fulla rundor för 32 rader text ingen kod berodde
på — noggrannheten var rätt, takten fel.

## Worktree-rensning (STEG 0, BATCH-004D)
Sex mergade worktrees rensades före batchen (`git worktree remove` utan --force + `git branch -d`
safe-delete; remota brancher orörda). Motiv: reporoten är `~/.claude`, så mergade worktrees är
DUBBLETTER av agents/skills/workflows i hemkatalogen — redigeras fel kopia märks det inte förrän något
beter sig konstigt. Efter: endast `main`.

## 004F-underlag — #4 är INTE helt blind i subagentkontext (2 av 10 bekräftbara)
C2:s doctorkörning kunde bekräfta **2 av 10 agent-deklarerade `mcp__`-servrar** ur subagentens egen
MCP-kontext: **`claude_ai_Trybloom`** och **`plugin_context7_context7`** (figma var också synlig men
är INTE agent-deklarerad → räknas ej). De övriga 8 (`chrome-devtools`, `21st`,
`plugin_playwright_playwright`, `shadcn-ui`, `reactbits`, `magicuidesign`, `motion-dev`, `gsap`) var
obekräftade. Sannolik struktur (VERIFIERAS i 004F, ej fastslaget här): de två bekräftbara är
HTTP/connector-servrar som är anslutna i subagentens kontext, medan de 8 obekräftade är npx-lanserade
stdio-servrar som inte spinns upp där. **Konsekvens för 004F:s lösningsrum:** #4 är inte HELT blind —
den ser en delmängd. Fixen kan bli att doctorfasen rapporterar det den KAN bekräfta och eskalerar bara
resten (partiell verifiering), i stället för att kapitulera helt till KUNDE-EJ/OGILTIG. Alternativt:
mata in huvudsessionens fulla /mcp-tillstånd i doctorfasen, eller scopa ut #4.

## Minnesskrivnings-observation (mönster över tre batchar)
BATCH-001:s C4-doctorkörning skrev om `agent-memory/nortropic-steward/system_baselines.md`. **004A:s
OCH 004D:s doctorkörningar rörde den INTE** (båda strikt read-only, bekräftat). Två körningar i rad
utan skrivning tyder på att BATCH-001:s skrivning var SITUATIONSBUNDEN (specifikt uppdragsläge), inte
systematisk för varje doctorkörning. **Regeln behålls ändå** — den kostar en rad per slutrapport, och
vi vet fortfarande inte exakt vad som utlöste den första, så bevisbördan ligger på att den ALDRIG
händer oregistrerat, inte tvärtom. Observationen registrerad så mönstret går att läsa i efterhand.

## Mätt kostnadsspann — doctorfasverifiering
Två mätpunkter: **144 497 tokens (004A C2)** och **149 003 tokens (004D C2)** för EN verify-suite-
doctorfas (steward kör 13 kontroller). **~145–150k är ett MÄTT spann, inte en gissning.** Underlag för
beslut om NÄR verify-suiten är värd att köra: regeln "två körningar (före+efter) vid första
funktionella ändringen" kostar därmed **~290–300k** för det paret.

## BATCH-004BE — INV-002 STÄNGD (design-reviewer Bash→BLOCKED) + RIKTAD docs-synk (004B + 004E utförda)
Två delar, base-SHA `2135d0e`. DEL 1 verkställer det förhandsregistrerade 004B-beslutet; DEL 2 verkställer 004E (docs-drift denna process själv skapade) men som RIKTAD delta-verifiering, inte full docs-synk — kostnadsgrinden slog till.

**DEL 1 — INV-002 stängd. Icke-§A** (`agents/design-reviewer.md` är EJ §A-uppräknad). `tools:`-raden tappar `Bash` (enda kvarvarande skalberoende var en `pnpm start`-fallback för lokal rendering, f.d. rad 39); steg 9 tri-state (3) omskriven: onåbar deployad preview → reviewern returnerar **BLOCKED** med orsak och NAMNGER vilken lins/kund som inte kunde bedömas, aldrig en lokal approximation (en reviewer som tyst faller tillbaka på en lokalt renderad sajt granskar inte samma artefakt den ska granska — vid launchgrind är BLOCKED bättre än en falsk bedömning). MCP-kolumnen i `docs/02-agenter.md` oförändrad: Bash listas aldrig där (endast MCP-servrar) → borttagningen rör inte tabellen.
- **C1 (positivt):** worktree-grind = **3 PASS / 2 FAIL / 5 överträdelser**; INV-002 borta ur listan (grön). De 5 kvarstående är de kända 004C-uppskjutna (INV-001 ×3 `git add -A` i stack-SKILL/autobygg/launch, INV-003 ×2 prelaunch:11 + launch:54) — ingen införd här. **Grind 6→5.**
- **C2 (negativt):** git-löst scratch utanför repot med Bash ÅTERINSATT på tools-raden → grinden flaggar exakt `INV-002 agents/design-reviewer.md:3 … innehåller Bash`; INV-001/003/005 blev INVALID (KUNDE-EJ-BEDÖMA, aldrig tyst PASS — tomhetsdisciplin). Grinden fångar regressionen.

**DEL 2 — RIKTAD docs-synk (ej full). Kostnadsgrind (ägarbeslut).** En full docs-synk (omverifiera VARJE påstående mot systemfilerna, def. 00-guide:85) mättes till **77 603 tokens för README ensam**; ×8 filer ≈ **350–620k tokens** >> 200k-taket → full synk är inte rutinmässigt försvarbar. Beslut: RIKTAD delta-verifiering av de 8 filerna mot systemändringarna sedan basstämpeln, med ärlig `Verifieringsomfång:`-rad som SÄGER att omfånget var delta, inte fullt.
- **README fullverifierad (undantag):** 27 påståenden mot HEAD `2135d0e` + batchens design-reviewer-ändring. **Exakt 1 avvikelse, inne i deltat:** `scripts/`-raden (rad 36) namngav bara `gsc-setup.mjs` — `check-invariants.mjs` (BATCH-002) saknades. Rättad i denna commit. **0 avvikelser utanför deltat.** Klassning **(A)** (belagt fel mot källa, rättat); inga (B)-osäkra kvar.
- **7 filer delta-verifierade** (00-borja-har, 00-guide, 01-oversikt, 02-agenter, 03-regelverk, 04-justeringskarta, 06-scope): **0 påståenden ogiltigförklarade.** Per-fil-redovisning (vilka delta-delar som prövades mot filen):
  - **00-guide:** doctor-antalet "tretton"/1–13 (rad 69) + docs-synk-def (rad 85) mot verify-suite/steward → oförändrat korrekt; OGILTIG-status omnämns inte i filen.
  - **02-agenter:** design-reviewer-raden (opus·max, MCP chrome-devtools) mot frontmatter → korrekt; Bash-borttagningen rör ej MCP-kolumnen.
  - **01-oversikt:** nod 6/7-raderna (design-reviewer opus·max) → korrekt; ingen tool-nivå-claim att drifta.
  - **03-regelverk:** 21 sökvägar mot disk (#12b) → existerar; inga check-invariants/Bash-påståenden.
  - **04-justeringskarta / 06-scope / 00-borja-har:** inga påståenden om det verkställda deltat (Bash/BLOCKED, OGILTIG, check-invariants, NRT-007-block) → 0 berörda; kontrollerade och rena.
- **Basstämpel-ärlighet (registrerat påstående):** basstämpeln 2026-07-30 sattes av **[AUTO-N1] `64acf9f`** (stämpelsvep) och är **inte oberoende granskad**. Den riktade verifieringen VILAR på den basen → varje ny stämpel bär `Verifieringsomfång:` på egen rad som säger både omfånget OCH att basen är en ogranskad N1-artefakt. Alla 8 + `docs/05` omstämplade **2026-07-31** (= senaste systemcommit → #12(d) parsar och passar). `docs/05`:s stämpel bumpad per retro-appliceringsregeln (SKILL.md:20 — stämpeln uppdateras i varje berörd docs-fil); append-only-regeln skyddar besluts-RADERNA, inte toppmetadatan.

**Doctor #12(a)–(e) körd mekaniskt mot worktree (tomhetsdisciplin bekräftad — ankaret matchade i varje delkontroll):**
- **(a) PASS** — 7/7 agentrader i 02-agenter stämmer mot frontmatter (0 avvikelse, 0 saknat namn).
- **(b) PASS** — 21 unika sökvägar i 03-regelverk existerar (0 saknade).
- **(c) PASS** — 10 unika `/nortropic-<namn>`-kommandon i README/docs löser till skill/workflow (0 olösta; en första grep gav 2 falska "olösta" pga trunkering vid bindestreck — artefakt, ej drift).
- **(d) PASS** för de 9 omstämplade (07-31 ≥ senaste systemcommit 07-31). **1 känd WARN: `docs/07-konstitution.md` = 2026-07-28 < 07-31** — §A6-skyddad (människohand), lämnas → **004G**. WARN-klass, accepterad; doctorn förblir GRÖN (grön = 0 FAIL).
- **(e) PASS** — ingen `0[1-7]`/README committad SENARE än `00-borja-har.md`; alla 8 committas i SAMMA commit 07-31 → delade datum, enkla lagret släpar aldrig.

**Integrationspass (fil-mot-fil över de 8, särskilt 00-borja-har vs 01–04/06): REN.** Enda substantiella `scripts/`-uppräkningen är README:36 (nu korrekt med båda skripten); inget annat dokument bär ett inaktuellt "scripts/ = 1 fil"-påstående. Inget dokument påstår att design-reviewer HAR Bash eller renderar lokalt → tool-ändringen skapar ingen doc-motsägelse. Enkla och tekniska lagret motsäger inte varandra på någon punkt batchen rörde.

**Residual (bärs vidare från 004D) — KOSMETISK STATUSHONESTY (låg prio, efter 004C/004F).** I `verify-suite.js` visar en doctor som DOG (null) `doctor: FAIL` i resultatets metablock + retur med tomt `fails[]`. Verdikt RÖD är korrekt/konservativt (blockerar inget fel), men statustexten påstår att kontroller föll när ingen kördes — samma feldomän 004D stängde, fast den faller alltid åt säkra hållet (RÖD). Möjlig fix: skilj FAIL från DÖD/KUNDE-EJ-STARTAS i visningen; verdikt förblir RÖD. Ej åtgärdad här (kosmetisk, blockerar inget).

## Stående regel — commit-trailers i 100D-serien (ägarbeslut 2026-07-31, registrerat val)
100D-batchcommitsen bär MEDVETET INTE Co-Authored-By/Claude-Session-trailers, trots att trailers är
NORMEN i repot: av 220 commits bär **191 Co-Authored-By (87 %)** och **100 Claude-Session** — vår
programserie är den avvikande stilen, inte tvärtom. **Rättelse av mätfel:** BATCH-004BE:s
commit-granskningsunderlag påstod först att "repo-konventionen" var trailerfri; det var FEL och
rättades genom att räkna hela historiken (191/220). En omätt "konvention" är ett antagande, inte ett
faktum — samma klass som backlog-siffror-är-påståenden. Valet att ändå avstå står, av tre skäl:
- **(a)** Proveniensen fylls redan av beslutsloggraden — läsbar, granskad och maskinellt hittbar; en
  trailer är inget av det.
- **(b)** Claude-Session-URL:er i ett PUBLIKT repo pekar på sessioner som inte är publika.
- **(c)** Byt inte konvention mitt i en batchserie.
Registrerat så att nästa läsare ser en MEDVETEN avvikelse (191/220-normen känd), inte ett slarvfel.

## LINSKONSISTENS — steg 9 (3) ger BLOCKED, bildlinsen (3) ger "EGET tillstånd" (observation → efter 004C)
BATCH-004BE gav steg 9:s (kluster-differentiering) tri-state (3) utfallet **BLOCKED**. Bildlinsens
(steg 10) tri-state (3) ger fortfarande **"EGET tillstånd, rapporteras SEPARAT"** — inte BLOCKED. Den
raden säger dessutom om sig själv att mönstret är "ordagrant ärvt från steg 9", vilket det INTE längre
är efter denna batch. Två linser hanterar alltså "kunde ej bedöma" olika. Det KAN vara rätt — att
sakna bilder att granska är mindre allvarligt än att inte kunna se sajten alls — men det är nu ett
OMEDVETET gap, inte ett medvetet val, och bildlinsens självbeskrivning ("ärvt från steg 9") är
inaktuell. **Klassning: LINSKONSISTENS. Låg prioritet, efter 004C.** Ägar-observation, ingen fix här.

## GRANSKNINGSLÄXA — en minimal ändringsinstruktion kan bevara en bugg (ägar-observation)
Under BATCH-004BE:s DEL 1-granskning kvalificerades steg 9:s tri-state (3) BLOCKED-villkor först ENDAST
för de två klausuler ägaren namngav ("rör inget annat i raden"). Den avgränsningen lämnade kvar en
konflikt av SAMMA klass: villkoret "render-upplösning gav ingen sajt" i (3) betyder — per rad 38
("vald kund → renderbar sajt") — att JÄMFÖRELSEKUNDEN inte kunde lösas upp, och rad 41:s fallback säger
att exakt det ska HOPPAS, aldrig blockera. Två rader instruerade motsatt om samma tillstånd; dessutom
pekade rad 38:s eget fall (3) på tri-state (3) i st.f. fallbacken. En helhetsläsning hade fångat det
direkt — den minimala instruktionen konserverade det. **Läxa: en minimal ändringsinstruktion kan bevara
en bugg som en bredare läsning hade fångat — granska hela den berörda enheten mot principen, inte bara
de namngivna klausulerna.** Rättat i samma commit (andra amend-vändan): "render-upplösning gav ingen
sajt" borttaget ur (3), "render-fel" + rubriken kvalificerade till den nya sajten, rad 38:s fall (3)
pekar nu på fallbacken. (3):s samtliga villkor gäller nu entydigt granskningssubjektet. Klassning:
GRANSKNINGSLÄXA, ingen ytterligare åtgärd.

## METODOBSERVATION — granskningen hittade fler defekter än testerna (BATCH-004BE)
BATCH-004BE är den FÖRSTA batchen där GRANSKNINGEN hittade fler defekter än TESTERNA. Grinden var
oförändrad genom hela batchen (**3 PASS / 2 FAIL / 5**), C1/C2 gröna från första passet, doctor #12
grön. Samtliga fyra defekter — tre tvetydigheter i en punktlista (rad 42:s (3): ospecificerad preview,
ospecificerat "render-fel", ospecificerad rubrik) plus en felriktad hänvisning (rad 38:s (3) pekade på
tri-state (3) i st.f. fallbacken) — hittades genom att läsa PROSA mot PRINCIP. Ingen mekanisk kontroll
kunde ha fångat någon av dem. **Slutsats att bära vidare:** grinden täcker det GREPPBARA (tools-rader,
strängar, hashar, filnamn); systemets faktiska BETEENDE ligger i agentinstruktioner, som är prosa. En
felriktad hänvisning i en punktlista kan blockera ett korrekt kundbygge utan att någon exit-kod någonsin
rapporterar det. Detta betyder INTE att grinden är felbyggd — den gör det den kan deterministiskt. Det
betyder att prosagranskning inte kan ersättas av fler invarianter, och att batcher som ändrar
agentinstruktioner måste läsas i sin HELHET, inte punktvis. **Klassning: METODOBSERVATION. Ingen åtgärd
— men ska vägas in när 004C:s scope sätts (INV-001 och INV-003 rör båda promptsträngar).**

## BATCH-004C — invariantprövning (utredning först, fix bara där den är liten)
Ram: att FIXA KODEN krävde ingen motivering; att LUCKRA UPP en invariant krävde skriftligt bevis att en
funktion försvinner. FAS A prövade de 5 anropsställena read-only; FAS B åtgärdade endast de ägaren
godkände. Base `997385e`.

**FAS A — de fem, med evidens (ej resonemang):**
- **A1 `skills/nortropic-stack/SKILL.md:35`** — `git add -A` i scaffold. Risken (staging av hemlighet)
  EMPIRISKT frånvarande: verifierat i två skarpa `.gitignore` (`nortropic-se`, `rorjour-stockholm`) att
  `.env*` + `.vercel` ignoreras (dubblerat — `vercel link` re-appendar). Men skyddet vilade på en
  tredjeparts-default → gjordes till vårt eget. **ÅTGÄRDAT.**
- **A2 `workflows/nortropic-autobygg.js:203`** + **A3 `workflows/nortropic-launch.js:149`** — `git add -A`
  i fixagent/release-steg. Ren fix = fixagenter returnerar ändrade filer → steget stageer en känd mängd;
  icke-trivialt (agent-returkontrakt). **LÄMNAS ÖPPNA → BATCH-005-fixkontrakt** (se nedan).
- **A4 `workflows/nortropic-launch.js:54`** + **A5 `skills/nortropic-prelaunch/SKILL.md:11`** — query-form
  bypass. SAMMA sträng, samma konstruktion, två filer = ETT beslut (ägaren rättade sin egen prelim: A5
  var inte ett separat fall). **ÅTGÄRDAT ihop.**

**Cookie-verifieringen (A4/A5, prövad mot de FAKTISKA MCP-schemana, som header-verifieringen):** kan
bypass-cookien sättas DIREKT så hemligheten aldrig når en URL? **NEJ.** chrome-devtools-kedjan (bär
Lighthouse + de flesta URL-grindar) har varken cookie- eller header-verktyg; `evaluate_script` kör sid-JS
och når inte HttpOnly-cookien; Playwright exponerar inget `addCookies` — enda teoretiska vägen är
`browser_run_code_unsafe` (schemat: **"Unsafe: RCE-equivalent"**, dessutom bara Playwright-grindar). Rå CDP
`Network.setCookie` exponeras inte. **Den direkta vägen prövades och fanns inte → anti-läck-modellen
kördes.** (Registrerat att den prövades, per ramen — annars ser nästa läsare inte att den övervägdes.)

**FAS B — vad som gjordes (härdat efter ägar-granskning: ett ord får inte räcka, och vakten måste vara kedjad):**
- **A1:** deterministisk **SECRET-VAKT, KEDJAD** med `git add -A` på SAMMA rad:
  `! git status --porcelain | grep -E '\.env|\.vercel|node_modules' | grep -vqE '\.example' && git add -A && … || { echo AVBRYT; exit 1; }`.
  En fälld vakt gör stageningen **OMÖJLIG** (short-circuit på `&&`), inte bara olämplig — även en agent som
  kör raden når aldrig `git add -A` förbi ett secret (punkt 2). Litar inte på create-next-apps `.gitignore`;
  prövar den faktiska stageningsmängden. **INV-001 härdad:** `git add -A` undantas ENDAST om raden BÖRJAR med
  den exakta kedjade vakt-prefixen (`startsWith` — substanskrav + kedjningskrav i ett) och kommentarrader
  hoppas. En kommentar/echo som bara NÄMNER "SECRET-VAKT" eller vaktkommandot bryter prefixet → flaggas ändå.
- **A4/A5:** **LÄCKSKYDD-klausul** på query-form-raden i båda filerna. **INV-003 härdad:** query-form undantas
  ENDAST om raden bär klausulens SUBSTANS — alla fyra `LÄCKSKYDD` + `hemligheten` + `ALDRIG` + `URL` — inte
  bara rubrikordet. Enbart ordet LÄCKSKYDD flaggas. (Samma härdningsklass som INV-004:s rubrik-svaghet och
  INV-005:s första-förekomst-svaghet — vi återinför den inte i samma andetag som vi tar bort ett förbud.)
- **A2/A3:** orörda.

**Punkt 3 (ägar-observation, registrerad — ingen åtgärd): undantagsvägen är strukturellt otillgänglig för
A2/A3.** Deras `git add -A` ligger i agent-instruktionssträngar i `.js`, inte som exekverbara scaffold-rader
som kan börja med den kedjade vakt-prefixen. **BATCH-005 ska INTE leta efter en vakt-undantagsväg för dem** —
rätt fix är känd filmängd (fixagenter returnerar ändrade filer → stagea exakt dem), inte en SECRET-VAKT
bolt-on. Vakten passar scaffolden (en självständig, känd commit-mängd); A2/A3 passar fixkontraktet.

**Konvergensen (ägar-observation, registrerad):** A1 och A4/A5 landade i SAMMA lösningsform — *behåll
förmågan, gör säkerheten explicit, låt invarianten KRÄVA klausulen i stället för att FÖRBJUDA strängen*.
Att två olika anropsställen självständigt landar i samma form är ett tecken på att formen är rätt. Den
gäller när en förmåga är nödvändig men bär en risk som kan göras explicit och deterministiskt vaktad.

**Grindutfall: 5 → 2 överträdelser (4 PASS / 1 FAIL). Förväntat tal redovisat FÖRE körning; utfallet
matchade exakt.** De 2 kvarvarande är INV-001 på `autobygg:203` + `launch:149` (A2/A3) — de SKA stå kvar
röda; hade de blivit gröna vore invarianten för brett uppluckrad. INV-002/004/005 orörda gröna.

**Beteendeverifiering (läxan: validera att en omformad kontroll fångar i BÅDA riktningar — inkl. markör-utan-substans):**
- SECRET-VAKT: fäller på `.env.local`/`.vercel/`/`node_modules` (även jämte en `.example`), passerar ren
  scaffold + enbart `.env*.example`.
- KEDJNING: på ett secret ger `! … && git add -A` **AVBRUTEN** (git add -A körs ALDRIG); på rent/mall STAGE.
- INV-001 (scratch-git, tre riktningar): flaggar (i) `git add -A` utan prefix, (ii) **MARKÖR-utan-substans**
  (`# SECRET-VAKT`-kommentar + oskyddad git add -A på egen rad), (iii) echo som bara nämner vaktkommandot;
  flaggar EJ den kedjade prefix-raden.
- INV-003 (scratch-git, tre riktningar): flaggar query-form utan klausul OCH med **enbart ordet `LÄCKSKYDD`**;
  flaggar EJ raden med full substans (`LÄCKSKYDD`+`hemligheten`+`ALDRIG`+`URL`).
Undantagen är bundna till skyddets SUBSTANS — ett ord räcker inte.

## BATCH-005-fixkontrakt (öppen, ägar-ID) — A2 + A3 samlade
`git add -A` i **autobygg:203** (fixagent) och **launch:149** (release-steg) står kvar flaggade AVSIKTLIGT.
Rätt fix är ETT mönster, inte två backloggrader: **fixagenterna returnerar sin ändrade-fil-lista →
release-/commitsteget stageer exakt den mängden** (Dag 5/16-arbete, ändrar agent-returkontraktet). **`git
add -u` får ALDRIG användas som mellanlösning** — den missar NYA filer och återinför rorjour-buggen
(ocommittade fixar → preview serverar förfix-värden), exakt felet steget finns för att förhindra. Tills dess
håller INV-001 dem röda, vilket är korrekt: grinden ska visa att arbetet återstår.

**Status 2026-08-06: DEL 1 (launch:149) VERKSTÄLLD — se sektionen "BATCH-005-fixkontrakt DEL 1" nedan.
autobygg:203 kvarstår öppen (DEL 2, egen sittning; grinden håller den röd tills dess).**

## Accepterade begränsningar i BATCH-004C:s grindomformning (ägar-granskning, ingen åtgärd)
Två svagheter i den härdade grinden, MEDVETET accepterade så en framtida läsare ser ett VÄGVAL, inte en glömska:
1. **Kommentar-skippens yta.** INV-001 hoppar rader som börjar med `#`/`//` (kommentar/prosa exekverar aldrig →
   ingen riktig staging). I ett bash-block är `#` en kommentar (korrekt hoppad); UTANFÖR ett block är `#` en
   markdownrubrik som inte heller exekveras. Kvarvarande teoretiskt gap: en rubrik/kommentar som en agent LÄSER
   som instruktion snarare än exekverar. Låg risk — agenter kör scaffold-block, de tolkar inte rubriker som
   körbara kommandon — men skrivet så det inte återupptäcks som nytt.
2. **INV-003:s LEAK003 är token-baserad, inte hash.** Fyra tokens på samma rad (`LÄCKSKYDD`+`hemligheten`+
   `ALDRIG`+`URL`) är väsentligt starkare än ett ord, och klausulerna i båda filerna är verklig substans. Men det
   är en svagare kontrollklass än INV-004:s blockhash. **Blockhash går INTE här:** klausulerna lever i olika
   kontexter (JS-sträng i `launch.js`, markdown-blockquote i `prelaunch/SKILL.md`) och kan inte vara byte-
   identiska — en gemensam hash skulle kräva identiska block, vilket kontexterna omöjliggör. Token-substanskravet
   är därför det starkaste mekaniska krav som är tillgängligt här. Accepterad begränsning med det motivet.

## BATCH-005-fixkontrakt DEL 1 — launch.js (2026-08-06, ägar-lett, HÖGRISK §A3-yta)
Base-SHA `1d9ed4f`. FAS A-utredning (read-only, redovisad i sittningen) → tre ägarbeslut: (1) **ORDNING**
launch först, autobygg DEL 2 i egen sittning — samma batch-ID, grind 2→1→0; (2) **DIFFSCOPE-formen
återanvänds** (`files: string[]` + mekanisk rapportdisciplin, `nortropic-review.js:54`) — inget nytt
schema uppfunnet; prosarapporten "fixed / needs-human" **BORTTAGEN** i stället för schemalagd, eftersom
grep visade noll nedströms konsumenter (endast launch-prompterna själva + `agents/stack-builder.md:48`,
som synkats i samma commit); (3) **felmoderna**: 1 (utelämnad fil), 2b (deklarerad-men-redan-smutsig),
3 (sökväg utanför byggkatalogen) och 4 (ingen lista) **BLOCKERAR** rundan utan commit (`contractStop`;
aldrig svepande staging som fallback — INV-005 INVALID→FAIL-klassen, verify-suitens "död probe är
odömbar"); 2a (deklarerad-men-oförändrad) WARN. Mekanisk grund: **delta-snapshot** `git status
--porcelain -uall` FÖRE/EFTER varje runda; alla beslut i REN JS (`normPath`/`badRepoPaths`/`fixDelta`),
aldrig agentprosa. Pure functions isolerat testade **32/32 PASS i BÅDA riktningar** (fånga + släppa-
igenom, guard-honesty-läxan); `-uall` är bärande (utan den listas ny katalog som `dir/` → falskblock).

**Adversariell trippellins FÖRE ägargranskning (prompttext/mekanik/§A3, tre oberoende skeptiker,
2026-08-06) fann 5 verkliga defektklasser i första utkastet — empiriskt belagda av skeptikerna i
scratch-git, alla åtgärdade MEKANISKT (aldrig med mer prosa):**
- **Pathspec ≠ literal (HIGH, alla tre linser):** deklarationer nådde `git add` som GLOB-pathspecs —
  `app/[stad]/page.tsx` (kärnan i stacken) är ett mönster för git; katalog/`.`/`content/*.ts`
  passerade badRepoPaths och WARN:ades under falsk "no-op"-premiss trots att de SVEPER. Fix: stagea
  SNITTET `declared ∩ efter-snapshot` (endast verkliga porcelain-filer kan nå git — katalog/glob/
  fantom kan per definition inte stå i porcelain-utdata) + `--literal-pathspecs` på add och commit.
- **Index-svepning (HIGH):** en pathspec-lös commit committar HELA indexet → för-stagat främmande
  innehåll åkte med. Fix: pathspec:ad commit (`git --literal-pathspecs commit -m … -- <mängden>`).
- **Sista ledet var prosa (MEDIUM, konvergens i alla tre linser):** release-utfallet verifierades
  aldrig — 004BE-klassen återinförd på exakt det steg kontraktet ska skydda. Fix: mekanisk
  EFTERKONTROLL (`git show --name-only` via scout + JS-mängdlikhet mot stageade mängden; avvikelse
  → contractStop FÖRE omkontrollen).
- **åäö-oktalescapning (MEDIUM):** porcelains default `core.quotepath` C-escapar svenska filnamn →
  deterministisk falsk felmod-1 i en svensk pipeline. Fix: `git -c core.quotepath=off` i snapshot-
  och inspektionskommandona.
- **Z1-kollisionen (MEDIUM):** agentdefinitionernas EGEN friktionslogg (AGENT-LOG.md skrivs mitt i
  arbetet; gates-fasen kan redan ha lämnat ett ocommittat block) fällde rundan som falsk felmod
  1/2b. Fix: namngivet mekaniskt undantag (CONTRACT_EXEMPT) ur pre/post/declared; efterkontrollen
  fäller ändå en release som committar loggen. Dessutom: `$`/backtick/CR avvisas i badRepoPaths
  (shell-aktiva ÄVEN inom dubbelcitat; legitima Next.js-sökvägar bär dem aldrig) och
  `seo-optimizer.md` fick fix-mode-raden (asymmetrin mot stack-builder.md var ett skeptikerfynd).

**NRT-001 (`launch.js` `const failing = ...`, endast tidigare RÖDA grindar omkontrolleras) MEDVETET
ORÖRD** — ägardirektiv: två §A3-ingrepp i samma tjugo rader slås inte ihop; utredningsunderlaget för
BATCH-006 redovisat i sittningsrapporten. §A3-ytor verifierade orörda: GATE-schemat, PASS/FAIL-logiken,
3-rundorsgränsen, freshness-grinden, legal-exkluderingen — kontraktet HÖJER ett krav, sänker inget.

**Grindutfall: 2 → 1 överträdelser (autobygg:203 kvar — SKA stå röd tills DEL 2).** Förväntat tal
redovisat före körning; utfallet matchade.

Accepterade begränsningar i DEL 1 (vägval, inte glömska):
1. **Porcelain-deltat kan inte särskilja "var smutsig FÖRE rundan + ändrades IGEN av fixern".**
   Deklareras filen → foreign-BLOCK (säkra sidan, människan reder ut); deklareras den inte → den nya
   ändringen är osynlig i deltat (filen låg redan i före-snapshoten) och förblir ocommittad. Trädet
   förutsätts i praktiken rent vid launchstart; för-existerande smuts commitas aldrig av loopen
   (den pathspec:ade committen håller även för-STAGAT främmande innehåll ute).
2. **Efterkontrollen är detektion, inte prevention:** en release-agent som trots allt sveper upptäcks
   mekaniskt (commit-mängd ≠ stagead mängd → contractStop före omkontrollen) men committen existerar
   då redan — revert är en mänsklig handling. Prevention vore att workflow-koden själv körde git,
   vilket DSL:en inte kan (agenter är enda aktuatorn); detta är samma aktuator-vs-protokoll-gräns
   som registrerades i BATCH-004D.
3. **Förbudsprosan bär inte INV-001-literalen:** release-promptens förbud uttrycks utan strängen
   ("NEVER stage sweepingly (no \"-A\", no \"-u\"...)"), annars hade grinden hållit raden röd av fel
   skäl — semantiken (förbudet) är starkare uttryckt än förr, och den exekverbara vägen stagear en
   explicit uppräknad, delta-verifierad mängd.
4. **CONTRACT_EXEMPT (AGENT-LOG.md) är en skopning, ingen sänkning:** kontraktet vaktar SAJT-fixarna;
   loggen är meta-observabilitet som aldrig commitas av loopen. Utan undantaget fäller systemets egen
   loggdisciplin ärliga rundor falskt. Loggens hemvist-/commitfråga ägs av Z1-spåret, inte launch.

## Ägar-registrering efter BATCH-005 DEL 1 — fyra återanvändbara mönster + metodobservations-stöd (2026-08-06)
Ägaren verifierade DEL 1-diffen oberoende i egen miljö (grind 4/1/1; badRepoPaths adversariellt prövad
mot 12 sökvägar — traversal/shell-injektion blockerade, `app/[stad]/`, `app/(grupp)/`, åäö och
Windows-backslash intakta; §A3-ytorna orörda) och registrerade fyra saker som blev STARKARE än begärt —
**mönster att återanvända**, inte engångslösningar:
1. **Snittet `declared ∩ post`:** begäran var "stagea deklarerad mängd"; lösningen stagear endast filer
   som bevisligen står i porcelain-utdata → kataloger, globs och fantomsökvägar blir OMÖJLIGA, inte
   upptäckta. Mönsterklass: gör felmoden orepresenterbar i stället för att detektera den.
2. **`core.quotepath=off`:** utan den oktalescapas `tjänster.ts` till `tj\303\244nster.ts` och kan
   aldrig matcha agentens UTF-8-deklaration → deterministisk falsk blockering i varje svensk pipeline.
   Fyndklassen kräver att kommandot KÖRTS skarpt — skrivbordsgranskning ser den inte.
3. **`-uall`:** utan den listas en ny katalog som `dir/` → ärligt deklarerade nya filer falskblockeras.
   Samma klass som 2: porcelain-utdatats faktiska form, inte dess antagna.
4. **Efterkontroll av commit-mängden:** sista ledet vilar inte på prosa; kommentarens ärlighet om
   detektion-vs-prevention (committen finns när avvikelsen upptäcks) är rätt hållning — lova aldrig
   prevention som mekaniken inte ger.

**Ytterligare stöd för METODOBSERVATIONEN (BATCH-004BE, "granskning > tester"):** att `seo-optimizer.md`
HELT saknade fix-mode trots att launch anropar agenten i fixläge kunde bara hittas genom att läsa hela
avsnittet mot principen — ingen grind, inget schema och ingen körning hade flaggat en agentdefinition
som saknar det läge dess anropare använder. Samma slutsats som 004BE: batcher som ändrar
agentinstruktioner läses i sin HELHET, aldrig punktvis.

**Ägarbeslut inför DEL 2 (samma sittning, 2026-08-06):**
1. **Content-fasen får F1** (fasgränscommit med samma kontrakt) **och den INGÅR i DEL 2** — en batch
   som levererar ett obrukbart kontrakt är inte klar. **F1 TÄCKER EN OTÄCKT YTA:** i dag förblir
   content-rester ocommittade ända till överlämning vid REN review — en verklig lucka som råkar döljas
   av `git add -A`, inte en ny kostnad som införs. F2 avvisad: DEL 2 flyttar commit-ansvaret UT ur
   agenterna och F2 lägger samtidigt IN det i content-designern — går åt två håll; init-prejudikatet
   håller inte (init committar en SCAFFOLD ingen agent redigerat, content committar AGENTPRODUCERAT
   innehåll — exakt skillnaden kontraktet finns för). F3 avvisad: foreign-blocket blir normalfall i
   stället för undantag, och en kontraktsvakt som fäller vid normal drift blir bortkopplad inom en månad.
2. **Commit-granularitet U (union):** attribution är LOGGDATA, inte commit-data — AUTOBYGG-LOG bär den
   redan; P kostar dubbla scouts för information som redan finns. Formlikhet med launch är ett värde
   när samma mönster underhålls på två ställen.
3. **Blockhash-vakten ingår i DEL 2 som INV-006** (GATE-schemat är redan dubblerat mellan filerna UTAN
   driftvakt — exakt den drift som väntar på att hända): FIXKONTRAKT-KÄRNAN hålls byte-identisk i båda
   workflowfilerna och hashas i samma form som INV-004; avviker de flaggas det.
4. **Rad 197-kommentaren får textuppdateras men ALDRIG semantiskt** — 1-vs-3 står fast.

## BATCH-005-fixkontrakt DEL 2 — autobygg.js + INV-006 (2026-08-06, ägar-lett; autobygg EJ §A-namngiven, grep-verifierat; commit HÖGRISK-märkt p.g.a. EN §A1-rad — stewardens SYSTEM MAP-versionssync v16→v17, ren faktasync, ägar-diffgranskad)
Base-SHA `9a47e88`. Verkställer FAS A-utredningens fyra ägarbeslut (sektionen ovan). A2 stängd.

**Ändringen i `workflows/nortropic-autobygg.js` (v16→v17):**
- **FIXKONTRAKT-KÄRNAN** (FILELIST + normPath/badRepoPaths/fixDelta + CONTRACT_EXEMPT +
  porcelainPrompt) delas nu med launch.js — DSL-filer kan inte importera varandra, så kärnan är
  MEDVETET duplicerad, hålls BYTE-IDENTISK (splitsad maskinellt ur launch, aldrig handavskriven;
  kärnhash `aa674a36…` i båda) och vaktas av INV-006. porcelainPrompt parametriserades
  `(when, where)` så samma kärna tjänar cwd-läget (launch) och buildDir-läget (autobygg).
- **F1 — fasgränscommit i Content:** content-designern deklarerar per FILELIST (rapportessensen
  bevaras i `note`-fältet; "facts still missing" överlever ändå mekaniskt som TODO-FACT-markörer
  som final-touches greppar), ett mekaniskt commit-steg committar snittet declared ∩ post.
  **Täcker en OTÄCKT yta** (ägar-registrering): vid REN review förblev content-arbetet ocommittat
  ända till överlämning — hålet doldes av den gamla svepande fix-stageningen.
- **Fixloopen (U):** de tre sekventiella fixagenterna deklarerar var för sig (schema per anrop),
  EN unionscommit committar snittet; per-agent-attribution är LOGGDATA (`byAgent` →
  contentCommit/fixCommit-fälten i AUTOBYGG-LOG + retur). **EXAKT EN runda oförändrad** —
  kommentaren textuppdaterad, aldrig semantiskt; strukturen är ett if-block, ingen loop.
- **kontraktsCommit-hjälparen** (autobygg-specifik, utanför kärnan): felmod 4→3→snapshot→2b→1→2a i
  samma ordning som launch, därefter commit-steg (generisk mekanisk agent, `--literal-pathspecs`
  add + pathspec:ad commit) + EFTERKONTROLL av commit-utfallet (git show --name-only + JS-mängd-
  likhet). Kontraktsbrott → `overlamnadKontrakt(stage, reason)` = exakt samma maskineri som övriga
  stopp (AUTOBYGG-LOG + return); stage `content` respektive `fixkontrakt`. Content-stoppet följer
  del-c-stoppets form (log + return UTAN final-touches — sajten är halvbyggd, en TODO-punchlista
  mitt i content vore brus); review-stoppet (CRITICAL efter EN runda) är oförändrat och kör
  final-touches som förr.

**INV-006 i `scripts/check-invariants.mjs`:** LF-normaliserad SHA-256 över blocket mellan de exakta
markörraderna i BÅDA filerna, hashade MOT VARANDRA (inte mot konstant — invarianten är ICKE-DIVERGENS;
samordnad ändring av båda blocken är underhållsmodellen). Saknad/dubblerad/omvänd markör → INVALID,
aldrig tyst PASS. **Ärlighetstestad i tre riktningar** (scratch): identiska block → ingen flagga;
en-byte-mutation → flagga med båda hasharna; borttagen END-markör → KUNDE-EJ-BEDOMA.

**launch.js i samma commit:** markörrader + fil-neutraliserade kommentarer i kärnan
("release-kommandot"→"stagingkommandot", "gates-fasen"→"tidigare faser") + porcelainPrompt-signaturen
(anropsplatserna ger identiska slutsträngar) SAMT skeptikerhärdningarna nedan (HEAD-spårning,
diff.renames=false i inspektionen, tom-snapshot-motsägelseblocket) — samtliga ÅTSTRAMNINGAR av
kontraktet, ingen sänkning. §A3-ytorna orörda (GATE-schema, PASS/FAIL, 3-rundor, freshness, legal,
`const failing`-raden byte-identisk).

**Grindutfall: 1 → 0 överträdelser, 6 PASS (INV-006 tillagd) — programmets FÖRSTA helgröna körning.**
Förväntat tal redovisat FÖRE körning; utfallet matchade. Pure functions 32/32 PASS mot BÅDA filernas
kärna. INV-001:s A2/A3-rader är därmed stängda: fixkontraktet ersatte den svepande stageningen i båda
pipelinefilerna.

**Metodincident (registrerad läxa, kostnad ~5 min):** första kärn-splitsen använde `String.replace`
med blocktext som replacement — `` $` `` i badRepoPaths-regexen är en MAGISK replacement-sekvens
("allt före träffen") och expanderade filprefixet mitt i blocket. Åtgärd: radoperationer (aldrig
String.replace med okontrollerad replacement), reparerad + hashverifierad. Klass: samma som
quotepath/-uall — verktygsytans FAKTISKA semantik, inte dess antagna.

**Adversariell trippellins DEL 2 (prompttext/mekanik/semantik, tre oberoende skeptiker, 2026-08-06)
— fynden empiriskt belagda i scratch-git och åtgärdade MEKANISKT före ägargranskningen:**
- **Rename-kollapsen (HIGH, 2 linser):** `git show --name-only` kör rename-detektion per default →
  en KORREKT commit av en omdöpning (porcelain + stageade mängden bär BÅDA sökvägarna) listades som
  EN → falsk mängddivergens → falsk ÖVERLÄMNAD med revert-instruktion mot en riktig commit. Fix:
  `-c diff.renames=false` i inspektionskommandot, i PAR i båda filerna; par-regeln (flödespromptar
  ligger UTANFÖR INV-006-kärnan och ändras alltid samordnat) inskriven i kärnkommentaren.
- **Självcommit-hålet (HIGH):** en fixagent som committar SJÄLV (exakt v16-beteendet för samma
  agenter) gjorde trädet rent → cleanDeclared-WARN → tomt stageSet → tyst ok — kontraktet passerat
  utan granskning. Fix: HEAD-SPÅRNING i kärnan (FILELIST.head + validHead; porcelainPrompt kör
  rev-parse): HEAD-flytt under fasen = brott ("en agent committade själv"); HEAD-stillestånd efter
  commit-steget = "ny commit saknas — commit-steget fallerade" (ärlig stopptext; stänger samtidigt
  falsk-PASS-scenariot där föregående commits filmängd råkar matcha stageade mängden, och
  falsk-revert-anvisningen mot legitima commits).
- **Scriptskrivna filer (HIGH):** bildkedjan skrivs "av ett script, inte av dig direkt"
  (content-designer.md) — en ordagrant lydig agent deklarerade inte public/images/raw|ref,
  BILDRAPPORT.json, SLOTS.json, fotouppdrag-klient.md → falsk felmod 1 på en LYCKAD fas. Fix:
  F1-promptens deklarationsklausul kräver nu scriptens outputs uttryckligen.
- **Tom-snapshot-motsägelsen (MEDIUM):** declared icke-tom ∧ efter-snapshot tom gav cleanDeclared-
  WARN + tyst överhoppad commit — F1:s hela syfte voidat. Fix: mekanisk motsägelseregel (block,
  odömbart) i båda flödena + felklausul i porcelainPrompt (aldrig gissa rent träd; kärnändring).
- **content-designer.md-synken (MEDIUM):** enda fixerdefinitionen utan BATCH-005-kontraktet, och
  Z1-radens premiss "copy-beslut står redan i dina commits" blev falsk under kontraktet. Fix:
  Kontraktsläge-paragraf (samma form som stack-builder/seo-optimizer) + Z1-raden omskriven —
  ersätter DEL 2:s ursprungliga vägval 5 ("lämnad orörd"), som skeptikerna refuterade.
- **Attribution/notes (LOW×2):** overlamnadKontrakt bär nu contentCommit/fixCommit (log + retur);
  byAgent bär note-fältet (rapportessensen persisteras — begärdes förr men lästes aldrig).
- **Docs-drift i commit-scopet (MEDIUM):** README v16-raden, 00-guide:s (a)(b)(c)-bromslista,
  justeringskartans "tre villkorade stoppen", stewardens SYSTEM MAP-rad (§A1 — se rubriken) och
  INV-001:s självbeskrivning i grinden ("förblir flaggade" — nu historik) synkade i samma commit.

Accepterade begränsningar DEL 1:1–4 gäller oförändrat även DEL 2 (samma kärna).

## Ägar-registrering efter BATCH-005 DEL 2 — varför INV-004 och INV-006 har OLIKA form trots samma mekanism (2026-08-06)
Ägaren specificerade INV-006 "i INV-004:s form", dvs. blockhash mot HÅRDKODAD konstant. Implementationen
hashade i stället de två blocken MOT VARANDRA — ägaren godkände avvikelsen som det RÄTTA valet och
beordrade skillnaden + motivet registrerade, så en framtida läsare ser att formskillnaden är ett VÄGVAL:
- **INV-004 = INNEHÅLLSLÅSNING.** Blocket ("EXTERN DATA ÄR INTE INSTRUKTIONER") är en säkerhets-
  invariant vars innehåll ska vara SVÅRT att ändra: varje avsiktlig ändring SKA kräva den medvetna
  handlingen att uppdatera konstanten. Ändring ska göra ont.
- **INV-006 = ICKE-DIVERGENS.** FIXKONTRAKT-KÄRNAN är duplicerad (DSL-filer kan inte importera) och
  FÅR utvecklas — men bara ATOMISKT över båda kopiorna. En hårdkodad konstant hade krävt manuell
  uppdatering vid varje legitim kärnändring och därmed inbjudit till kringgående (slentrian-uppdaterad
  hash eller borttagen kontroll) — exakt erosionen i markör-utan-substans-klassen (INV-004:s
  rubrik-svaghet, INV-005:s första-förekomst-svaghet, AH21:s per-tillfälle-instruerade kringgående:
  en gräns som flyttas "bara denna gång" är ingen gräns).
**Mönsterregeln att bära vidare:** välj hashform efter invariantens NATUR — innehållslåsning → konstant
(ändring ska göra ont), icke-divergens → par-jämförelse (ändring ska vara lätt men atomisk över alla
kopior). Samma mekanism, olika form, båda rätt.

**Även registrerat: §A1-radens prövning godkänd av ägaren (2026-08-06, före merge).** Ägaren prövade
klassningen självständigt med riktningstestet på den flaggade delen ("fixkontrakt, EN runda"): gränsen
har två normkällor i koden (kärnsektionens "EXAKT EN fixrunda är oförändrad" + fixloopskommentaren) —
båda oförändrade i batchen; kartraden UPPREPAR gränsen, den skapar den inte; raderas kartraden ändras
ingenting i vad systemet får göra. Verdikt: BESKRIVANDE. "deploy-oförmöget by design" ordagrant kvar.
HÖGRISK-märkningen behölls med ägarens formulering: **den följer YTAN, inte bedömningen.** Ägaren
verifierade även oberoende (Linux, node v22.22.2): grind 6/0/0 och INV-006-hashen `2aaac302…a5ff2994`
reproducerad byte-identiskt i båda filerna (75 rader var).

## BATCH-006-full-sweep — launch.js (2026-08-06, ägar-lett, HÖGRISK: §A3-fil + §A1-rad i SYSTEM MAP)
Base-SHA `9d10d40`. Stänger NRT-001 ("Launch kan godkänna regression efter fix" — Appendix A:
"Alla gates om mot final SHA/URL; PASS-invariant"). FAS A-utredning read-only → fyra ägarbeslut:
1. **contractStop → SKIP:** en helmätning mot ett träd i kontraktsbrott ankrar ingenting; verdiktet
   är BLOCKED ändå. Redundant med beslut 2 — dubbelt skäl, registrerat båda.
2. **SVEP ENDAST VID PRE-SVEP-PASS** (inte "kör + aldrig-uppåt-spärr"): svepet är en PASS-INVARIANT —
   det finns för att verifiera att ett READY är SANT, inte för att ge en fjärde chans åt något som
   redan är BLOCKED. Villkorsformen gör uppåt-flipp (röd→grön via svep = de facto-erosion av
   3-rundorsgränsen) STRUKTURELLT ONÅBAR i stället för regelspärrad — struktur före regel, samma
   princip som INV-001:s kedjade vakt och INV-006:s par-hash. **Accepterad kostnad (ägar-
   registrering):** en människa som läser en BLOCKED-rapport får ingen färskhetsgaranti för "gröna"
   rader — rapporten är redan BLOCKED och läses av en människa.
3. **none-vägen → READY blockeras mekaniskt, deploy måste BEVISAS:** en boolean räcker inte (kan
   säga true medan URL:en serverar för-fix-bygget). Bevis i tre led: (1) JS-spårat att sista
   COMMITTADE rundans release repointade freshUrl (`lastFreshRound === fixLog[sista].round`),
   (2) mekanisk scout hämtar deployens skapelsetid (vercel inspect) + slutcommitens tid
   (git show -s --format=%cI) som RÅDATA, (3) ren JS-prövning `deployBevis` kräver deploy EFTER
   commit. Faller något led → svepet ODÖMBART → FAIL-fallback på alla sex grindarna med ärlig orsak
   ("fixar committade men aldrig deployade — deploya och kör om") — samma form som contractStop och
   doctors OGILTIG: odömbart blir aldrig tyst grönt.
4. **Eval-URL-fyndet → EGEN BATCH (BATCH-007-eval-url, registrerad nedan):** två ändringar i samma
   villkorskedja i samma batch är svårare att ägargranska, inte lättare.

**Mekaniken:** villkor `!contractStop && fixLog.length >= 1 && preSweepPass` — fixLog (inte round)
eftersom round även räknar no-op-rundor där inget ändrades; preSweepPass beräknas med samma
filteruttryck som failing/nonLegalPass/remaining (`GATES.filter(g => g.key !== 'legal')` — legal dras
ALDRIG in, §A3-exkluderingen bevaras genom ORDAGRANN återanvändning, aldrig ny logik). ERSÄTTNINGS-
semantik: svepets sex resultat ersätter kartinnehållet FÖRE nonLegalPass-raden — verdiktraderna
byte-identiska (sweepNote appendas per evalNote-prejudikatet v5, grenlogiken orörd). Död svepagent →
FAIL-fallback per rad-200-precedentet — en odömbar svepgrind får ALDRIG tyst behålla sitt gamla gröna
värde. `sweep.regressions` (statussnapshot före/efter) + explicit log- och verdiktsats gör NRT-001-
fallet (grön i rond 0 → röd i svepet) omöjligt att missa; fixkontraktets per-runda-filmängder
(`fixLog[].files`, BATCH-005-utdelningen) visar VAD som ändrats sedan de gröna mätningarna. Två
loggdatalyft i loopen utan logik: `lastHead` (efter godkänd efterkontroll) + `lastFreshRound`.

**§A3-genomgång:** GATE-schemat orört (svepet återanvänder det); `nonLegalPass`-raden, verdiktgrenarna,
`while (round < 3)`, `const failing`, freshness-blocket, legal-filtren — byte-identiska (sånär som på
`+ sweepNote`-appenden i verdiktsträngen, evalNote-klassen, och `sweep: null` i freshness-returen).
Kravet HÖJS: ett READY kräver nu färsk, bevisat deployad helmätning. Ingen väg gör en körning grönare
än före batchen (villkorsformen + FAIL-fallbacks). INV-006-kärnan ORÖRD (hash `2aaac302…` oförändrad).

**Adversariell trippellins BATCH-006 (prompttext/mekanik/§A3, tre oberoende skeptiker, 2026-08-06) —
7 defektklasser i första utkastet, empiriskt belagda (Node 22 + Vercel CLI 55), alla mekaniskt åtgärdade:**
- **Två konkurrerande URL:er i sveppromten (HIGH, 2 linser):** baspromptens inbäddade `${site}` (rond-
  0-URL) mot appendens freshUrl — den verdiktankrande mätningen kunde tyst köras mot för-fix-deployen
  och beviskedjan bevisar URL:ens färskhet, aldrig att agenterna MÄTTE den. Fix: SUPERSEDE-mening i
  svep- OCH recheck-prompterna ("varje URL tidigare i prompten är ersatt — kontakta den aldrig, starta
  aldrig dev-server; VARJE URL-baserad kontroll körs mot exakt denna preview").
- **Tid utan identitet i deploy-beviset (MEDIUM):** vercel inspect följer ALIAS, och en samtidig
  auto-deploy (t.ex. git-integrationens, som saknar de lokalt committade fixarna — release pushar
  aldrig) kan repointa aliaset → färsk-men-fel deployment passerade tidsbeviset. Fix: IDENTITET SLÅR
  TID — scouten rapporterar deployens commit-SHA när vercel inspect visar den (deployCommit i
  schemat); JS kräver = lastHead, annars ODÖMBART; tidsbeviset är fallback när metadata saknas.
  Release-prompten kräver dessutom den UNIKA deploy-URL:en, aldrig alias.
- **Offset-hålet (MEDIUM, 2 linser):** offsetlös ISO tolkas som VÄRDDATORNS lokaltid av Date.parse —
  beviset kunde förskjutas ±offset åt BÅDA hållen, inklusive att en stale deploy passerade som färsk.
  Fix: deployBevis kräver fullständig datetime MED explicit Z/offset (regex), annars ODÖMBART.
- **Trim-hålet (HIGH mekanik/LOW prosa):** `%cI` slutar med newline; "verbatim" → Date.parse NaN →
  deterministiskt falskt ODÖMBART på grön körning. Fix: trim i deployBevis (samma disciplin som
  HEAD-hanteringen).
- **Ovaliderad freshUrl i "Run exactly"-prompter (MEDIUM, 2 linser):** `(\S+)` släpper `;`/`$`/
  backtick — samma hotmodell som kärnans badRepoPaths, med direktare exekveringskanal. Fix:
  `validPreviewUrl` (ren JS: https + vercel.app-värd + rot-path + ingen query/hash/auth; isolerat
  testad 10/10 båda riktningar) — ogiltig form behandlas som PREVIEW_URL=none, aldrig interpolering.
  Dessutom förankrad SISTA-raden-match (`^PREVIEW_URL=(\S+)\s*$` multiline, .pop()) — release-
  prompten citerar själv strängen och first-match kunde fånga instruktionsekot.
- **fixLog betydde "nådde staging", inte "committad" (LOW, 2 linser):** pushen låg före release-
  steget; invarianten bars implicit av contractStop. Fix: fixLog.push flyttad till EFTER godkänd
  release-efterkontroll — en rad BETYDER nu committad runda per konstruktion, och rapportens
  fixRounds kan aldrig innehålla ocommittade rundor.
- **ODÖMBAR-grenen rapporterade sex "regressioner" som aldrig mätts (LOW, 2 linser)** (backlog-
  numbers-are-claims-klassen) **+ recheck-textens falska "REDEPLOYED" på none-vägen (LOW):** Fix:
  regressions beräknas endast för GENOMFÖRT; recheck-augmentationen villkorad på deployedThisRound
  med ärlig stale-varning när rundan inte kunde deployas.

Accepterade begränsningar BATCH-006 (vägval, inte glömska):
1. **Identitetsbeviset gäller när vercel inspect visar deployens commit-SHA** — CLI-deploys utan
   git-metadata faller tillbaka på tidsbeviset + unik-URL-kravet i release-prompten + validPreviewUrl.
   Alias kan inte robust regex-detekteras (alias- och unika URL:er delar form) — därför SHA-företräde
   när det finns, prosakrav + tid annars. Omprövas om ett falskt ankare någonsin observeras skarpt.
2. **BLOCKED-rapporter får ingen färskhetsgaranti för gröna rader** (ägarbeslut 2 — svepet är en
   PASS-invariant; rapporten är redan BLOCKED och läses av en människa).
3. **Klockskev mellan git-klockan och Vercels klocka saknar tolerans** — tidsbeviset kräver
   deploy ≥ commit exakt; en deploy som skapas inom skevet kan falskt fällas (säkra riktningen,
   aldrig falskt grönt). Identitetsbeviset är immunt mot klassen.

## BATCH-007-eval-url (öppen, ägar-ID) — eval-fasen mäter fel URL efter fixrundor
**Fyndet (verifierat i FAS A-utredningen för BATCH-006):** eval-fasen kör mot `site` — strängen byggd
av det URSPRUNGLIGA `args.url` (launch.js, `const site`-raden) — medan fixrundorna deployats till
`freshUrl`. Varje launch med fixrundor scorar alltså det för-fixade bygget; poängen skrivs till
EVAL-RESULT.md och matar retrons kundjämförelse. NRT-002-klassen inne i launch. Blir MER synlig efter
BATCH-006: svepet ankrar verdiktet färskt medan evalen förblir gammal (eval körs vid nonLegalPass —
exakt när svepet körts). **Inte en en-radsfix:** rör även site-strängens fallback-formulering ("find
the preview/dev URL…"), och två ändringar i samma villkorskedja som svepet ägargranskas sämre i samma
batch (ägarbeslut 4, 2026-08-06). Eval-RUBRIKEN är §A2 och rörs inte — endast URL-pekaren i prompten.
Körs direkt efter BATCH-006:s merge.
