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
