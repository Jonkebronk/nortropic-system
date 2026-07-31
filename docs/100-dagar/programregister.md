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
  — före OCH efter den ändringen — i stället för att jämföra mot Dag 1. Doctor-grinden (1–12)
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
