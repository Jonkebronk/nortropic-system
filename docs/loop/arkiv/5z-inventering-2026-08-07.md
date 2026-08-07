# 5Z-inventeringen — bevisstyrd lägesinventering

**Datum:** 2026-08-07 · **Producent:** GPT-5.6 (ChatGPT/Codex) på bevisstyrd inventeringsprompt · **Status:** ARKIVLEGEND — detta är den auktoritativa mappningen av 5Z-kodnamnen och beviset bakom omstarten (byggplan v2). Innehållet är producentens rapport oförändrad; endast rubrikformatering är tillagd.

---

Jag skiljer här strikt mellan lokal checkpoint-/trust-chain och referensplanens P0-kontrollplan. Referensplanen definierar uttryckligen de sju skivorna som SQLite/eventlogg, verifier-runner, attestation/stale, lease, workspace/worktree, worker-launch och diffpolicy.

GitHub-inspektionen av Jonkebronk/nortropic-system gav senast observerade repo-commit 8900b00424df6a2e3d77d46189b3dae0d9b732df. Jag hittade ingen repo-träff för nortropic-checkpoint-5z-hd2b2, sqlite, acquire_repo_lease eller candidate_sha. Därför binder jag inte den SHA:n till de lokala checkpointartefakterna. För dem anges commit-SHA som OVERIFIERAT/SAKNAS.

Det finns dessutom inget verifierat mastermanifest som räknar upp samtliga historiska 5Z-kodnamn. Inventeringen nedan innehåller de komponenter jag kan belägga från nu tillgängliga källor och terminalbevis. Historiska namn som inte kan bindas till en konkret fil eller output får inte fyllas i från minnet.

## DEL 1 — INVENTERING AV BYGGDA KOMPONENTER

**5Z-BW**
- VAD: Tidig checkpoint i kedjan som kontrollerade och etablerade underlag för workspace-activation-implementation innan senare identitetslåsning.
- VAR: Lokala candidate-/checkpointartefakter under /private/tmp och $HOME/Downloads; exakt checkpointfil: OVERIFIERAT; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ enligt tillgänglig kedjeevidens; arbetet gällde lokal maskin och lokala trust-paths.
- EXIT-TEST: SAKNAS som återkörbart funktionstest; historisk PASS uppges i handoff, men rå terminaloutput för BW är inte tillgänglig i denna inventering.
- STATUS: ARKIVERBAR.

**5Z-BX**
- VAD: Read-only preflight som kontrollerade identitet, livegränser och att workspace/authorization ännu inte fanns innan kandidatkedjan fortsatte.
- VAR: Kandidatdesign /private/tmp/nortropic-staging-broker-workspace-activation-implementation-candidate-design-v1.candidate.json; checkpointfilens exakta namn OVERIFIERAT; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ; preflighten läste lokal state.
- EXIT-TEST: SAKNAS som återkörbart exit-test; senare BX1 binder BX:s tillstånd.
- STATUS: ARKIVERBAR.

**5Z-BX1**
- VAD: Klassificerare som analyserade ett tidigare BX-fel och verifierade att live authorization och exakt job-workspace fortfarande var frånvarande.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-bx1-classify.py; livekontroll /usr/local/libexec/nortropic/bin/check-system-state; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ; källan visar lokal read-only klassificering.
- EXIT-TEST: SAKNAS som återkörbart funktionstest; källan innehåller fail-closed preconditions, men aktuell rå PASS-output är OVERIFIERAT.
- STATUS: ARKIVERBAR.

**5Z-EA**
- VAD: Builder för ett privat exactly-once-checkpoint som senare skulle kunna aktivera ett workspace under explicit authorization/claim-semantik.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-ea-build-private-exactly-once-workspace-activation-execution-checkpoint.py; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ enligt källkoden för buildsteget; den beskriver lokala private artifacts och uttryckliga NO-gates för live execution.
- EXIT-TEST: SAKNAS; jag har källkod med en PASS-kodväg men ingen rå terminaloutput som bevisar att just EA faktiskt kördes till exit 0.
- STATUS: BYGGD-OTESTAD.

**5Z-FY / FY-v2**
- VAD: Exactly-once authorization-creation-checkpoint som kapslar skapandet av en single-use execution authorization med fail-closed villkor.
- VAR: Lokala FY-builder/checkpointartefakter under $HOME/Downloads och /private/tmp; exakt aktiv FY-v2-sökväg i denna rapport: OVERIFIERAT; commit-SHA: SAKNAS/OVERIFIERAT. FZ1A-källan binder en byggd FY-checkpoint.
- EXTERN SIDOEFFEKT: NEJ för de testade privata körningarna; ingen nätverks-/GitHub-/mejl-effekt är belagd.
- EXIT-TEST: Historiskt testbevis finns genom efterföljande kedja; exakt fristående återkörbart kommando och senaste tid: OVERIFIERAT.
- STATUS: ARKIVERBAR.

**5Z-FZ1A**
- VAD: Klassificerare som verifierade att ett FY-kontraktsfel berodde på fel antaget invocation-schema, inte på en live mutation.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-fz1a-classify-fy-contract-invocation-schema-assumption.py; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ; lokal fil-/AST-inspektion.
- EXIT-TEST: SAKNAS som återkörbart funktionstest; senare kedja binder klassificeringen, men exakt sista råa kördatum är OVERIFIERAT.
- STATUS: ARKIVERBAR.

**5Z-GB**
- VAD: Privat testmatris för FY-v2:s authorization-creation-semantik innan senare creator-/freeze-led byggdes.
- VAR: Lokala $HOME/Downloads/nortropic-checkpoint-5z-gb-...py och tillhörande /private/tmp testbevis; exakta paths här OVERIFIERAT; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ enligt kedjebindningarna; isolerade simuleringar användes.
- EXIT-TEST: Historisk teststatus binds av senare GD/GF-kedja; återkörbart kommando och exakt senaste tid: OVERIFIERAT.
- STATUS: ARKIVERBAR.

**5Z-GF3**
- VAD: Korrigerad privat kvalificering av en single-use authorization-creator med statiska, runtime-negativa och create-simuleringar utan live create.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-gf3-...py samt lokala testresultat; exakt filnamn i nu öppnade källor OVERIFIERAT; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ; kända bevis anger inga live create-anrop.
- EXIT-TEST: Historiskt terminalbevis anger två validate-only-körningar, statiska kontroller, runtime-negativtester och create-simuleringar; rå fil här: OVERIFIERAT.
- STATUS: ARKIVERBAR.

**5Z-GG**
- VAD: Freeze-led som band och frös den testade GE/GD2-bundna single-use authorization-creatern.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-gg-freeze-tested-ge-gd2-bound-single-use-execution-authorization-creator.py; root-sealed freeze under /private/tmp; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ; lokal freeze/publication.
- EXIT-TEST: SAKNAS som återkörbart test; historiskt PASS binds av senare chain-artifacts.
- STATUS: ARKIVERBAR.

**5Z-GH**
- VAD: Authorization-creation-checkpoint i föregångarkedjan som testades och bands innan GI/GJ/GK/GL-ledet.
- VAR: Lokala GH-checkpoint/resultat under /private/tmp; exakt aktuell path i denna rapport: OVERIFIERAT; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ enligt senare root-sealed bindings.
- EXIT-TEST: Historisk körning finns indirekt bunden i GI/GL-kedjan; exakt rå output och senaste klockslag: OVERIFIERAT.
- STATUS: ARKIVERBAR.

**5Z-GI2**
- VAD: Testad korrigerad version av GH-ledet som blev input till den efterföljande single-use authorization-designen.
- VAR: Lokala /private/tmp GI2 test-/freezeartefakter; exakt filpath OVERIFIERAT; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ.
- EXIT-TEST: Senare artifacts refererar "gj-frozen-tested-gi2-gh"; fristående rå exit-output: OVERIFIERAT.
- STATUS: ARKIVERBAR.

**5Z-GL**
- VAD: Single-use execution-authorization-creator som byggdes ovanpå GJ/GI2/GH-kedjan och sedan testades/fryses.
- VAR: Creator/resultat under /private/tmp; senare GU-/GS-källor binder GL-föregångaren; exakt komplett bundlepath här OVERIFIERAT; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ för kvalificeringskedjan.
- EXIT-TEST: Historiskt kvalificerad; aktuellt återkörbart fristående kommando: OVERIFIERAT.
- STATUS: ARKIVERBAR.

**5Z-GM2**
- VAD: Test-/freeze-evidence-container runt GL-ledet som senare GO/GP-kedjan litade på.
- VAR: /private/tmp/nortropic-tested-gm2-gl-gk-bound-single-use-execution-authorization-creator-freeze-v1.json med independent validation; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ.
- EXIT-TEST: Senare GP-classifiers binder GM2-material; exakt originalkommando och senaste tid: OVERIFIERAT.
- STATUS: ARKIVERBAR.

**5Z-GN**
- VAD: Freeze-led för GL/GK-kedjan innan GO exactly-once authorization-creation-checkpointet testades.
- VAR: Lokala /private/tmp GN freeze-artifacts; exakta paths kan utläsas ur senare GO/GP-skript men är här OVERIFIERAT; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ.
- EXIT-TEST: Senare GO/GP-kedja binder GN; original rå exit-körning: OVERIFIERAT.
- STATUS: ARKIVERBAR.

**5Z-GO**
- VAD: Exactly-once authorization-creation-checkpoint med separat validate-only och execute-semantik ovanpå GN/GL-kedjan.
- VAR: Root-sealed GO checkpoint/contract/validation under /private/tmp; GP4 är dess privata testharness; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ i de körningar som är belagda här; GP-testningen använde lokal subprocess med argv och shell=False.
- EXIT-TEST: Read-only bevis: grep -F 'CHECKPOINT_RESULT=PASS' "$HOME/Downloads/nortropic-checkpoint-5z-gp9-output.txt" om filen finns; senaste GO-kvalificering: 2026-08-06, exakt klockslag OVERIFIERAT.
- STATUS: ARKIVERBAR.

**5Z-GP9**
- VAD: Korrigerad slutlig privata kvalificering av GO efter en längre serie test-/classifier-orakel.
- VAR: /private/tmp/nortropic-go-gn-frozen-gl-authorization-creation-checkpoint-private-test-result-v9.json och independent validation; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ; privata simuleringar och validate-only.
- EXIT-TEST: grep -F 'CHECKPOINT_RESULT=PASS' "$HOME/Downloads/nortropic-checkpoint-5z-gp9-output.txt"; förväntat CHECKPOINT_RESULT=PASS; senaste kördatum 2026-08-06, klockslag OVERIFIERAT.
- STATUS: ARKIVERBAR.

**5Z-GQ**
- VAD: Freeze av det testade GP9/GO/GN/GL/K-bound exactly-once authorization-creation-checkpointet.
- VAR: /private/tmp/nortropic-tested-gp9-go-gn-frozen-gl-gk-bound-exactly-once-execution-authorization-creation-checkpoint-freeze-v1.json och validation; builderpath binds i GU-källan; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ.
- EXIT-TEST: grep -F 'CHECKPOINT_RESULT=PASS' "$HOME/Downloads/nortropic-checkpoint-5z-gq-output.txt"; historiskt PASS binds i GU; senaste datum 2026-08-06.
- STATUS: ARKIVERBAR.

**5Z-GR**
- VAD: Single-use execution-authorization-design ovanpå den frysta GQ/GP9/GO-kedjan.
- VAR: /private/tmp/nortropic-single-use-execution-authorization-design-for-gq-frozen-tested-gp9-go-gn-frozen-gl-gk-bound-exactly-once-execution-authorization-creation-checkpoint-v1.candidate.json; SHA 8a7882e27fffb7e83e886fc7e931a9365711d25989257f2e6542f16b7a9b898a; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ.
- EXIT-TEST: grep -F 'CHECKPOINT_RESULT=PASS' "$HOME/Downloads/nortropic-checkpoint-5z-gr-output.txt"; senare GU binder SHA/output; senaste datum 2026-08-06.
- STATUS: ARKIVERBAR.

**5Z-GS**
- VAD: Creator som kan skapa en single-use execution authorization från GR-designen.
- VAR: /private/tmp/nortropic-create-single-use-execution-authorization-for-gr-gq-frozen-tested-gp9-go-authorization-creation-checkpoint-v1.candidate; SHA 193ce11b2346cd6b4604dfcfaabce54304135a9ce30be86ce38f516d719835c9; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ; lokalt authorization-artifact när create används, inget nätverk är belagt.
- EXIT-TEST: Historiskt validate-only/test bevisas av GT/GU-kedjan; direkt återkörbart kommando i nuvarande state: OVERIFIERAT.
- STATUS: ARKIVERBAR.

**5Z-GT**
- VAD: Privat testharness som kvalificerade GS-creatern med negativa tester och create-simuleringar.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-gt-test-private-gs-gr-gq-frozen-tested-gp9-go-single-use-execution-authorization-creator.py; testresultat /private/tmp/nortropic-gr-gq-frozen-tested-gp9-go-single-use-execution-authorization-creator-private-test-result-v1.json; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ.
- EXIT-TEST: grep -F 'CHECKPOINT_RESULT=PASS' "$HOME/Downloads/nortropic-checkpoint-5z-gt-output.txt"; senare GU binder output SHA; senast 2026-08-06.
- STATUS: ARKIVERBAR.

**5Z-GU**
- VAD: Freeze som band den testade GS/GR/GQ/GP9/GO creator-kedjan till root-sealed evidence.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-gu-freeze-tested-gt-gs-gr-gq-frozen-tested-gp9-go-single-use-execution-authorization-creator.py; freeze /private/tmp/nortropic-tested-gt-gs-gr-gq-frozen-tested-gp9-go-single-use-execution-authorization-creator-freeze-v1.json; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ.
- EXIT-TEST: grep -F 'CHECKPOINT_RESULT=PASS' "$HOME/Downloads/nortropic-checkpoint-5z-gu-output.txt"; kördes 2026-08-06; PASS enligt rå terminalevidens.
- STATUS: ARKIVERBAR.

**5Z-GV3**
- VAD: Exactly-once checkpoint som kapslar authorization creation ovanpå den frysta GU-kedjan och som har validate-only/execute-semantik.
- VAR: /private/tmp/nortropic-execute-exactly-once-gu-frozen-tested-gt-gs-gr-gq-gp9-go-single-use-execution-authorization-creation-v3.candidate plus contract/validation; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ för validate-only; execute skulle skapa lokala authorization-artifacts men inget nätverk är belagt.
- EXIT-TEST: Historiskt kvalificerad av GX2; inte återkörbar nu som current gate eftersom senare evidence uttryckligen behåller gv3_version_transition_requirement=REMAINS_IN_FORCE.
- STATUS: PÅGÅENDE.

**5Z-GVA**
- VAD: Read-only classifier som skilde 47 verifierade transitive records från 55 records i full recursive identity för GU.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-gva-classify-gu-verified-transitive-file-record-count-confused-with-full-identity-recursive-file-record-count.py; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ enligt källans deklarerade scope.
- EXIT-TEST: Denna version nådde ett senare schemafel och ersattes av GVA1/GVA2; därför inget grönt återkörbart exit-test.
- STATUS: ARKIVERBAR.

**5Z-GVA1**
- VAD: Read-only classifier som visade att en live-boundary-snapshot använde positional lists där GU-ankaret använde JSON-objekt.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-gva1-classify-current-live-boundary-creator-bundle-and-future-path-snapshot-schema-uses-positional-lists-instead-of-gu-anchor-objects.py; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ.
- EXIT-TEST: Historisk klassificering binds av GVA2; rå kördatum OVERIFIERAT.
- STATUS: ARKIVERBAR.

**5Z-GVA2**
- VAD: Korrigerad read-only classifier som slutförde 47-vs-55-recordklassificeringen med rätt GU-objektschema.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-gva2-classify-gu-verified-transitive-file-record-count-confused-with-full-identity-recursive-file-record-count.py; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ; källan säger uttryckligen classification-only och ingen authorization/claim/workspace.
- EXIT-TEST: Historisk PASS binds i senare GV2/GV3-kedja; exakt rå terminaloutput i denna rapport: OVERIFIERAT.
- STATUS: ARKIVERBAR.

**5Z-GX2**
- VAD: Privat fulltest av GV3-checkpointet med live validate-only, statiska kontroller, runtime-negativtester och isolerade execution-simuleringar.
- VAR: Lokalt GX2-script/output samt root-sealed result/validation under /private/tmp; exakta scriptpaths här OVERIFIERAT; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ utanför maskinen; live execute skapades inte.
- EXIT-TEST: Historiskt två live validate-only och testmatriser binds av GY/GZ; återkörning nu är spärrad av GV3 version-transition-kravet.
- STATUS: ARKIVERBAR.

**5Z-GY**
- VAD: Freeze som band den testade GV3-checkpointversionen och dess GX2-testbevis.
- VAR: /private/tmp/nortropic-tested-gv3-gu-frozen-tested-gt-gs-gr-gq-gp9-go-exactly-once-authorization-creation-checkpoint-freeze-v1.json och validation; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ.
- EXIT-TEST: Historiskt PASS och root-sealed freeze finns; fristående återkörning av one-shot-builden är inte tillåten.
- STATUS: ARKIVERBAR.

**5Z-GZ4**
- VAD: Root-sealed design/contract/validation för den single-use execution authorization som ska skapas från den testade/frysa GV3/GY-kedjan.
- VAR: /private/tmp/nortropic-single-use-execution-authorization-design-for-gy-frozen-tested-gx2-gv3-exactly-once-authorization-creation-checkpoint-v1.candidate.json plus contract/validation; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ; design-/validation-artifacts lokalt.
- EXIT-TEST: Historisk GZ4-körning med publicering 3/3; rå output finns i tidigare kedja men exakt read-only grep-path här är OVERIFIERAT.
- STATUS: PÅGÅENDE.

**HA2**
- VAD: Första root-sealade creator-versionen som kan skapa GZ4:s single-use execution authorization.
- VAR: /private/tmp/nortropic-create-single-use-execution-authorization-for-gz4-gy-frozen-tested-gx2-gv3-authorization-creation-checkpoint-v1.candidate; SHA 763cad33b26f7b7075f068c24edbcd6e8bef644f9dd88b7f86cab66ee280d5e0; contract/validation bredvid; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ utanför maskinen; create skulle bara skriva lokal authorization/evidence.
- EXIT-TEST: Två live validate-only kördes senare i HB2; versionen är därefter superseded av HA3.
- STATUS: ARKIVERBAR.

**HB2**
- VAD: Korrigerad privat kvalificering av HA2-creatern med validate-only, statiska kontroller, runtime-negativtester och create/fail-stop-simuleringar.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-hb2-test-corrected-private-ha2-gz4-bound-single-use-execution-authorization-creator.py; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ; create-simuleringarna var privata/sandboxade.
- EXIT-TEST: Read-only bevis: grep -F 'CHECKPOINT_RESULT=PASS' "$HOME/Downloads/nortropic-checkpoint-5z-hb2-output.txt"; PASS binds av HC; kördes 2026-08-07, exakt klockslag OVERIFIERAT.
- STATUS: ARKIVERBAR.

**HC**
- VAD: Freeze som band HB2:s testade HA2-creator och dess independent validation.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-hc-freeze-tested-ha2-gz4-bound-single-use-execution-authorization-creator.py; root-sealed freeze under /private/tmp; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ; lokal freeze-publication.
- EXIT-TEST: grep -F 'CHECKPOINT_RESULT=PASS' "$HOME/Downloads/nortropic-checkpoint-5z-hc-output.txt"; kördes 2026-08-07 omkring 00:40 lokal tid och outputen visar PASS-markörer.
- STATUS: ARKIVERBAR.

**HD0**
- VAD: Read-only gate som visade att direkt byggande av nästa HD-checkpoint skulle göra HA2:s policy stale och därför krävde en versionerad creator-policyövergång.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-hd0-...py; exakt filnamn OVERIFIERAT; output binds av HD2; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ.
- EXIT-TEST: HD2 binder en HD0-output med CHECKPOINT_RESULT=PASS och marker hd1_version_transition_required_next=YES; exakt rå kommando-path OVERIFIERAT.
- STATUS: ARKIVERBAR.

**HD2**
- VAD: Korrigerad policytransition som skapade HA3, en versionerad creator med utökad stable policy så framtida test/freeze/HD-paths var fördeklarerade.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-hd2-build-corrected-versioned-ha3-creator-policy-transition-from-ha2.py; SHA 7b07c35dd6c1a1703f3468519a94de3b228e2baed3700df552233fcbc181dd09; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ; lokal root-sealed publication.
- EXIT-TEST: grep -F 'CHECKPOINT_RESULT=PASS' "$HOME/Downloads/nortropic-checkpoint-5z-hd2-output.txt"; kördes 2026-08-07 före 09:20 och output SHA binds senare som 1fdc06a6....
- STATUS: ARKIVERBAR.

**HA3**
- VAD: Versionerad single-use authorization-creator som behåller HA2:s transaction-semantik men har en stable policy som fördeklarerar test-, freeze- och HD/HE/HF-paths.
- VAR: /private/tmp/nortropic-create-single-use-execution-authorization-for-gz4-gy-frozen-tested-gx2-gv3-authorization-creation-checkpoint-v2.candidate; SHA b282d305daeb292f4d1348651209ecd72a183c6f1ee85c7e3cf766d5402f971 [transkriptionsosäkerhet: se rå rapport]; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ för validate-only; create skriver enbart lokal authorization/evidence enligt testad design.
- EXIT-TEST: sudo /private/tmp/nortropic-create-single-use-execution-authorization-for-gz4-gy-frozen-tested-gx2-gv3-authorization-creation-checkpoint-v2.candidate --validate-only; förväntad exit 0; kördes två gånger i HD2A5 och gav identisk stdout SHA 495112c1ccd659fd825d25c909df092d377829384369dad79ba2bf65c1700ec1.
- STATUS: TESTAD.

**HD2A1**
- VAD: Read-only classifier som korrekt identifierade HD2:s dubbla correction-chain-marker men själv föll senare på fel stable-policy-helper.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-hd2a1-classify-hd2-correction-chain-marker-cardinality-oracle.py; SHA 3cde646ec5bbded04b7e3725050f2a84e806a366283f460a986e867eabd97a7a; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ; process-/mutation count var noll.
- EXIT-TEST: Historisk output $HOME/Downloads/nortropic-checkpoint-5z-hd2a1-output.txt slutade CHECKPOINT_RESULT=FAIL; ingen grön exit-test.
- STATUS: ARKIVERBAR.

**HD2A1A / namespace oracle / classify-hd2a1-stable-policy-helper-schema**
- VAD: Read-only classifier som bevisade att HD2A1 använde fel policy-key, saknade Nortropic-namespacefilter och använde fel record-schema.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-hd2a1a-classify-hd2a1-stable-policy-helper-schema-and-namespace-oracle.py; SHA 9d9183fd52a357e4982ba5048a7dbbc85b237808df55670b3b1aba51f207e10c; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ; AST-auditen kräver inga process- eller mutationsanrop.
- EXIT-TEST: grep -F 'CHECKPOINT_RESULT=PASS' "$HOME/Downloads/nortropic-checkpoint-5z-hd2a1a-output.txt"; kördes 2026-08-07 omkring 09:26 och PASS finns i rå output.
- STATUS: ARKIVERBAR.

**HD2A2A**
- VAD: Read-only classifier som bevisade att HD2A2 läste två gamla HD2A-statusmarkörer med fel current-checkpoint-prefix.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-hd2a2a-classify-hd2a2-predecessor-status-marker-prefix-oracle.py; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ.
- EXIT-TEST: grep -F 'CHECKPOINT_RESULT=PASS' "$HOME/Downloads/nortropic-checkpoint-5z-hd2a2a-output.txt"; kördes 2026-08-07 omkring 09:45; PASS enligt rå terminalevidens i konversationen.
- STATUS: ARKIVERBAR.

**HD2A3A**
- VAD: Read-only classifier som bevisade att HA2:s hela sensitive-set felaktigt jämfördes mot endast de tre nytillkomna HA3-recordsen.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-hd2a3a-classify-ha2-stale-delta-whole-policy-vs-added-records-oracle.py; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ.
- EXIT-TEST: grep -F 'CHECKPOINT_RESULT=PASS' "$HOME/Downloads/nortropic-checkpoint-5z-hd2a3a-output.txt"; kördes 2026-08-07 omkring 09:56; PASS enligt rå terminalevidens.
- STATUS: ARKIVERBAR.

**HD2A4A**
- VAD: Read-only classifier som bevisade ytterligare två predecessor-prefixfel när HD2A4 läste HD2A3:s fail-output.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-hd2a4a-classify-hd2a4-failed-hd2a3-predecessor-status-marker-prefix-oracle.py; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ.
- EXIT-TEST: grep -F 'CHECKPOINT_RESULT=PASS' "$HOME/Downloads/nortropic-checkpoint-5z-hd2a4a-output.txt"; kördes 2026-08-07 omkring 10:10; PASS enligt rå terminalevidens.
- STATUS: ARKIVERBAR.

**HD2A5**
- VAD: Den privata kvalificering som faktiskt körde HA3 två gånger i validate-only, statiska kontroller, runtime-negativtester och isolerade create/fail-stop-simuleringar och publicerade testresultat.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-hd2a5-test-private-ha3-version-transition-creator-after-hd2a4-prefix-classification.py; testresultat /private/tmp/nortropic-ha3-gz4-bound-single-use-execution-authorization-creator-version-transition-private-test-result-v1.json; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ; två live-anrop var validate-only och create-simuleringarna låg i sandbox.
- EXIT-TEST: grep -E '^(PASS live_ha3_creator_validate_only=2/2_IDEMPOTENT_PASS|PASS runtime_negatives=32/32_PASS|PASS isolated_create_transactions=14/14_PASS|CHECKPOINT_RESULT=PASS)$' "$HOME/Downloads/nortropic-checkpoint-5z-hd2a5-output.txt"; kördes 2026-08-07 efter 10:15 och alla fyra rader finns i terminalbeviset.
- STATUS: ARKIVERBAR.

**HD2B**
- VAD: Första freeze-försöket för den testade HA3-versionen, som stoppade därför att HA2-staleness fortfarande förväntades vara tre records i stället för fem efter HD2A5-publiceringen.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-hd2b-freeze-tested-ha3-version-transition-creator.py; SHA 40b2e7f68a92fc409c03467d969a8a40909f1ad7b2291b167150530cc7131121; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ utanför maskinen; freeze-publicering startade inte.
- EXIT-TEST: Historisk output $HOME/Downloads/nortropic-checkpoint-5z-hd2b-output.txt slutade CHECKPOINT_RESULT=FAIL; ingen grön exit-test.
- STATUS: ARKIVERBAR.

**HD2B1**
- VAD: Read-only classifier som fastställde fasmodellen HA2 stale med tre records vid HD2, fem efter HD2A5 och sju efter en lyckad freeze.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-hd2b1-classify-ha2-stale-boundary-after-hd2a5-test-evidence.py; SHA c670da941937b84761327ac2b8a554cfbc92c37be9694f9f31a4b8357ce645a4; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ; process-/mutation calls var noll.
- EXIT-TEST: grep -F 'CHECKPOINT_RESULT=PASS' "$HOME/Downloads/nortropic-checkpoint-5z-hd2b1-output.txt"; kördes 2026-08-07 omkring 10:53 och gav PASS.
- STATUS: ARKIVERBAR.

**HD2B2**
- VAD: Korrigerad freeze av den testade HA3-versionen med fasriktig HA2-staleness före och efter freeze-publiceringen.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-hd2b2-freeze-tested-ha3-version-transition-creator-phase-correct-stale-boundary.py; freeze /private/tmp/nortropic-tested-ha3-gz4-bound-single-use-execution-authorization-creator-version-transition-freeze-v1.json; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ; endast lokal freeze/resultatpublication.
- EXIT-TEST: grep -E '^(PASS publication=2/2_COMPLETE|PASS ha2_post_freeze_status=STALE_BY_EXACTLY_7_RECORDS_3_BUNDLE_PLUS_2_TEST_PLUS_2_FREEZE|CHECKPOINT_RESULT=PASS)$' "$HOME/Downloads/nortropic-checkpoint-5z-hd2b2-output.txt"; kördes 2026-08-07 omkring 11:01 och samtliga finns i rå output.
- STATUS: PÅGÅENDE.

**5Z-HD**
- VAD: Det framtida runtime-checkpoint som ska göra exactly-once authorization creation via HA3 med validate-only/execute-gränssnitt.
- VAR: Avsedd path /private/tmp/nortropic-execute-exactly-once-hc-frozen-tested-ha2-gz4-bound-single-use-execution-authorization-creation-v1.candidate; som fysisk publicerad fil var den fortfarande ABSENT efter HD2B2; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ i validate-only; execute är designad att skriva lokala authorization/resultat men inget nätverk är belagt.
- EXIT-TEST: SAKNAS; komponentfilen var ännu inte publicerad vid senaste körbeviset.
- STATUS: BYGGD-OTESTAD.

**5Z-HD3**
- VAD: Buildern som ska skapa och publicera 5Z-HD-checkpointet, dess contract och independent validation ovanpå HD2B2-freezen.
- VAR: $HOME/Downloads/nortropic-checkpoint-5z-hd3-build-private-exactly-once-hd2b2-frozen-tested-ha3-authorization-creation-checkpoint.py; SHA från levererad fil ea516467de43dd1a792fab073092723150774438e4c7b57bb04b712094048b80; commit-SHA: SAKNAS/OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ enligt källkoden för buildern; den skriver lokala /private/tmp-artifacts och anger noll live execute/create i buildsteget.
- EXIT-TEST: SAKNAS; ingen nortropic-checkpoint-5z-hd3-output.txt eller terminalkörning har presenterats efter att filen skapades.
- STATUS: BYGGD-OTESTAD.

**Post-Workspace Preparation Package**
- VAD: Dokument-/arkitekturpaket som beskriver programming-agent, diff validation, deterministic verification, review, commit och PR-steg efter ett framtida workspace terminal-PASS.
- VAR: README.md, POST_WORKSPACE_ARCHITECTURE.md och paketfiler; status i dokumenten PREPARED_NOT_BOUND_NOT_INSTALLED; commit-SHA: OVERIFIERAT.
- EXTERN SIDOEFFEKT: NEJ enligt paketets egna regler; stage, commit, push, PR, merge och deploy är uttryckligen förbjudna.
- EXIT-TEST: SAKNAS som installerat runtime-test; paketet deklarerar självt att det inte är bound eller installed.
- STATUS: BYGGD-OTESTAD.

**Övriga historiska 5Z-classifiers och failed one-shot-varianter**
- VAD: Flera separata diagnostik-/korrigeringscheckpoints skapades för marker-cardinality, schemafält, source-literal-counts, output-order, call-site-counts och liknande harnessfel.
- VAR: Exempel som kan beläggas är GP5A, GP7A, GP8A2, HB1/HB1A/HB1A1, GX1 och flera GP2A-varianter under $HOME/Downloads; komplett masterlista och commit-SHA: OVERIFIERAT.
- EXTERN SIDOEFFEKT: För de öppnade classifierkällorna NEJ; de är lokala classification-only-checkpoints.
- EXIT-TEST: Per enskilt historiskt kodnamn: OVERIFIERAT i denna inventering eftersom inget auktoritativt mastermanifest kopplar alla script till alla outputs.
- STATUS: ARKIVERBAR.

## DEL 2 — MAPPNING MOT REFERENSPLANEN

Referensplanen kräver bland annat controller-state i SQLite, append-only eventlogg, verifier registry/runner, SHA-attestationer, lease, per-attempt worktree, worker-envelope/outputparser och diffpolicy.

| Komponent ur Del 1 | Planmappning | Bevisad relation |
|---|---|---|
| 5Z-BW | UTANFÖR PLAN | Workspace-activation trust/preflight, inte SQLite-controller-state. |
| 5Z-BX | UTANFÖR PLAN | Live-boundary-preflight; ingen repo-attempt/worktree-funktion. |
| 5Z-BX1 | UTANFÖR PLAN | Klassificerar workspace-activation-state. |
| 5Z-EA | UTANFÖR PLAN, tematisk överlapp Skiva 5 | Hanterar ett specifikt workspace-activation-checkpoint, inte per-attempt clean checkout/GC. |
| FY/FY-v2 | UTANFÖR PLAN | Authorization-creation trust-chain. |
| FZ1A | UTANFÖR PLAN | Schema-/harnessklassificering. |
| GB | UTANFÖR PLAN | Privat authorization-testmatris. |
| GF3 | UTANFÖR PLAN | Creator-kvalificering, inte generell controller-verifier-runner. |
| GG | UTANFÖR PLAN | Freeze/trust-anchor. |
| GH | UTANFÖR PLAN | Exactly-once authorization-led. |
| GI2 | UTANFÖR PLAN | Korrigerat test/freeze-led. |
| GL | UTANFÖR PLAN | Single-use authorization creator. |
| GM2 | UTANFÖR PLAN | Freeze/test-evidence-container. |
| GN | UTANFÖR PLAN | Freeze av authorization-kedja. |
| GO | UTANFÖR PLAN, mekanisk överlapp Skiva 2 | Dess testharness använder argv och shell=False, men det är inte planens generella verifier registry/runner. |
| GP9 | UTANFÖR PLAN | Privat GO-kvalificering. |
| GQ | UTANFÖR PLAN | Freeze. |
| GR | UTANFÖR PLAN | Authorization design. |
| GS | UTANFÖR PLAN | Authorization creator. |
| GT | UTANFÖR PLAN | Creator-testharness. |
| GU | UTANFÖR PLAN | Freeze/trust-chain. |
| GV3 | UTANFÖR PLAN | Exactly-once authorization checkpoint. |
| GVA/GVA1/GVA2 | UTANFÖR PLAN | Identity-/schema-classifiers för trust-chain. |
| GX2 | UTANFÖR PLAN | GV3-kvalificering. |
| GY | UTANFÖR PLAN | GV3 freeze. |
| GZ4 | UTANFÖR PLAN | Authorization design/contract. |
| HA2 | UTANFÖR PLAN | Single-use authorization creator. |
| HB2 | UTANFÖR PLAN | Creator testharness. |
| HC | UTANFÖR PLAN | Creator freeze. |
| HD0 | UTANFÖR PLAN | Policy-staleness gate för trust-chain. |
| HD2 | UTANFÖR PLAN, tematisk överlapp Skiva 3 | Har stale-policy-semantik, men inte task-attestation candidate_sha/valid_through_sha/invalidates_on. |
| HA3 | UTANFÖR PLAN | Versionerad authorization creator. |
| HD2A1/A1A/A2A/A3A/A4A | UTANFÖR PLAN | Harness-/policy-oracle classifiers. |
| HD2A5 | UTANFÖR PLAN | Kvalificering av HA3. |
| HD2B/B1/B2 | UTANFÖR PLAN, tematisk överlapp Skiva 3 | Freeze/stale-evidence för HA2/HA3, inte kontrollplanets task-attestation. |
| 5Z-HD | UTANFÖR PLAN | Authorization-creation runtime checkpoint. |
| 5Z-HD3 | UTANFÖR PLAN | Builder för ovanstående checkpoint. |
| Post-Workspace Preparation Package | Dokumentär överlapp Skiva 2, 5, 6, 7 | Dokumentet beskriver framtida worker/diff/verification-flöde men säger PREPARED_NOT_BOUND_NOT_INSTALLED. |
| Övriga classifiers | UTANFÖR PLAN | De skapades för att klassificera checkpoint-/harnessfel under trust-chain-arbetet. |

## DEL 3 — GAP MOT SKIVA 1–7

| Skiva | Referensplanens konkreta krav | INTE byggt eller INTE verifierat |
|---|---|---|
| 1 — SQLite-state + append-only eventlogg + spec-inläsning | Controllerägd SQLite-state; task state/attempt/claim; append-only eventlogg; immutable spec-loader; schema/dependency validation; done ska kunna räknas om från evidence. | SQLite-databas: INGEN REPO-TRÄFF I INSPEKTIONEN. State-schema/migration/init: OVERIFIERAT. Append-only eventwriter: OVERIFIERAT. Replay/recompute av done: OVERIFIERAT. Spec-loader: OVERIFIERAT. Dependency graph/cycle-check i implementerad controller: OVERIFIERAT. Skivans exit-test: SAKNAS. |
| 2 — verifier-runner | Registrerad verifierare; argv-baserad processstart; shell=False; verifierhash; candidate-SHA-binding; stdout/stderr/exit evidence. | Generell verifier registry: OVERIFIERAT. Generell controller-runner: OVERIFIERAT. Candidate-SHA-binding: ingen repo-träff på candidate_sha. Persistens av verifier-evidence: OVERIFIERAT. Manipulerad-task-får-inte-fri-kod-exit-test: SAKNAS. Det finns lokala checkpointtesters subprocess.run(argv, shell=False), men de implementerar inte skivan. |
| 3 — attestation + stale-invalidering | Attestation bunden till base/candidate SHA, spec hash, verifier hash, registry hash, sandbox hash, diff hash, exit code; valid_through_sha; invalidates_on; stale-markering och reverify. | Task-attestation-schema i controllern: OVERIFIERAT. Candidate-commit-binding: OVERIFIERAT. valid_through_sha: OVERIFIERAT. invalidates_on: OVERIFIERAT. Automatisk impactanalys och stale-reverification: OVERIFIERAT. Exit-test "senare regressionsdiff gör task stale": SAKNAS. Trust-chainens freeze/stale records är en annan mekanism. |
| 4 — lease + heartbeat + säker reclaim | Atomisk repo-lease; repo/lease/host/pid/boot/run identity; heartbeat; TTL; processkontroll + TTL för reclaim; split-brain-evidence; exakt en owner vid samtidiga starter. | acquire_repo_lease gav ingen repo-träff. Lease-store: OVERIFIERAT. Heartbeat-loop: OVERIFIERAT. Safe reclaim: OVERIFIERAT. Split-brain-hantering: OVERIFIERAT. Test med 100 samtidiga starter: SAKNAS. |
| 5 — workspace per attempt | Ren checkout/worktree från base_sha; ett workspace per attempt; lifecycle/ownership; cleanup/GC; crash recovery före/efter attestation; idempotent resume. | Per-attempt Git-worktree-controller: OVERIFIERAT. Clean checkout från taskens base SHA: OVERIFIERAT. Attempt→worktree-register: OVERIFIERAT. GC: OVERIFIERAT. Controller-crash resume: OVERIFIERAT. Exit-test för crash före/efter attestation: SAKNAS. Den långa workspace-activation-kedjan skapar inte detta per-attempt-system. |
| 6 — worker-launch | Immutable taskkuvert med run/task/base/spec/write-scope; headless worker; minimal env/sandbox; timeout; strikt parser; candidate SHA; oparsbar rapport → failure class. | Implementerad envelope-generator: OVERIFIERAT. Headless controller→worker-launch: OVERIFIERAT. Minimal worker-env wiring: OVERIFIERAT. Strict structured-output-parser: OVERIFIERAT. Candidate-SHA-parser: OVERIFIERAT. Oparsbar-output failure-class test: SAKNAS. Post-workspace-paketet beskriver sådant men är uttryckligen inte installerat. |
| 7 — diffpolicy | Diff base→candidate; allowed_write; denied_write; binär/stor fil; test/verifier deletion; dependency/lockfile; fil- och LOC-budget; submodule/hooks/CI/security; symlinkskydd; evidence vid policyfailure. | Controllerfunktion för base→candidate diff: OVERIFIERAT. allowed_write/denied_write enforcement: OVERIFIERAT. LOC-budget: OVERIFIERAT. Binary/large-file rule: OVERIFIERAT. Lockfile/dependency rule: OVERIFIERAT. Symlink/submodule/hook/CI-security rules: OVERIFIERAT. Scope-brott-exit-test: SAKNAS. |

## DEL 4 — ÄRLIGHETSFRÅGORNA

### a) Vilka komponenter har vi byggt mer än en version av, och varför?

FY/FY-v2: flera versioner förekommer; tillgängliga classifiers visar schema-/invocation- och authorization-consumption-fältmismatchar. FZ1A analyserar uttryckligen ett felaktigt antagande om creator_invocation_boundary.

GO/GP-testkedjan: GP gick genom många versioner och classifiers, bland annat GM2-container-schema, call-site-count, markerordning och global marker-cardinality. Exempel: GP5A klassificerar felaktig markerordning, GP7A en dubbelt legitim anchor-marker och GP8A2 ett globalt count-orakel.

GV/GV2/GV3 + GVA/GVA1/GVA2: versionerna uppstod när olika identitetsdomäner blandades: först 47 verifierade transitive records kontra 55 recursive identity-records, därefter positional-list kontra object-schema i live-boundary-snapshot.

HA/HA2/HA3: första HA-builden föll på fel future-path-alias (execution_authorization); HA2 blev den korrigerade creator-versionen; senare visade HD0 att HA2:s stable policy inte fördeklarerade den fortsatta kedjan, vilket ledde till HA3 med utökad policy. Den första HA-failen är rått belagd.

HB/HB1/HB1A/HB1A1/HB2: flera varianter behövdes för separata harness-orakel: correction-chain-marker cardinality, stderr/stdout-ordning och contract/validation fingerprint-field-schema innan HB2 kunde genomföra testprofilen.

HD1→HD2: HD1-versionstransitionen föll genom flera classifierled innan HD2 blev den korrigerade HA2→HA3-transitionen. Exakt komplett lista över varje HD1A-variant finns inte i ett mastermanifest här; därför är antal och full paths OVERIFIERAT.

HD2A→HD2A5: minst fyra separata felklasser är rått belagda: HD2 marker-cardinality, HD2A1 stable-policy-helper schema/namespace, predecessor-prefixar och HA2 stale-delta extraction. Slutliga HD2A5 var första versionen som nådde hela testprofilen.

HD2B→HD2B2: första freeze-försöket förväntade historisk HA2-staleness på tre records trots att HD2A5 redan lagt till två testbevis. HD2B1 klassificerade fasmodellen och HD2B2 verifierade fem records före freeze och sju efter.

Workspace-activation kandidater v1/v2 och post-installation/follow-up-varianter: filnamn i /private/tmp visar flera generationer, men exakt orsak per generation är inte rekonstruerad från ett auktoritativt manifest här. OVERIFIERAT.

### b) Vad i det byggda har aldrig exekverats en enda gång?

5Z-HD3-buildern: inget rått terminalbevis finns efter att filen skapades. Det finns källkod men ingen hd3-output.txt i tillgängligt material. Bevisstatus: BYGGD-OTESTAD.

Den 5Z-HD-runtimefil som HD3 ska publicera: var fortfarande absent efter HD2B2. Den har alltså inte kunnat exekveras som publicerad runtimekomponent.

HA3 --create live: HA3-processen har körts i --validate-only, men live --create har enligt HD2A5/HD2B2 aldrig körts. HD2B2 rapporterar live_ha3_creator_create_invocation_count=0.

GV3 --execute live: tillgängliga senare bevis håller dess live execute-räknare på noll och gv3_version_transition_requirement=REMAINS_IN_FORCE.

Live execution authorization creation i den nuvarande HD/HA3-kedjan: noll enligt HD2B2.

Live execution claim creation i den nuvarande kedjan: noll enligt HD2B2.

Aktuellt exact job workspace för denna kedja: inget har skapats; HD2B2 rapporterar workspace creation noll och workspace-root oförändrad.

Post-Workspace Preparation Package: dokumentationen säger uttryckligen PREPARED_NOT_BOUND_NOT_INSTALLED; dess runtimekomponenter är alltså inte installerade/exekverade som kontrollplan.

5Z-EA: huruvida buildern faktiskt exekverades en gång kan jag inte belägga från rå output här. OVERIFIERAT, inte "aldrig körd".

### c) Om en utomstående granskare fick koden idag utan våra konversationer — vad skulle den inte förstå?

De skulle inte ha ett auktoritativt dokument som mappar alla codenames → predecessor → fail → classifier → corrected successor → current trust anchor. Jag hittar många sådana relationer inbäddade i enskilda Pythonfiler, men inget komplett mastermanifest. Exempelvis binder HD2A5 sin långa correction chain inne i själva testharnessen.

De skulle inte automatiskt förstå att vissa historiska filnamn med ha2 fortfarande används avsiktligt efter HA3-transitionen därför att paths hade fördeklarerats tidigare. Den semantiken ligger i checkpointkedjans evidence, inte i ett normalt repo-API.

De skulle inte förstå one-shot-regeln enbart från vanlig programsemantik: ett script som gav PASS eller FAIL får enligt projektets arbetssätt inte köras om; nästa steg är ett nytt classifier-/corrective checkpoint. Regeln finns i handoffmaterialet, inte som en generell runtimefunktion i kontrollplanet.

De skulle inte veta vilken källa som har företräde när narrativ, script och raw output skiljer sig. Handoffen säger att raw terminal evidence och root-sealed artifact identities ska väga tyngre än minne/narrativ.

De skulle inte förstå varför "stale" betyder olika numeriska deltas vid olika tidpunkter: HA2 var historiskt +3, efter HD2A5 +5 och efter HD2B2 +7; det är fasberoende och bevaras i classifier-/freeze-evidence, inte i en extern state-maskin.

De skulle inte kunna härleda från checkpointkoden att detta är implementeringen av referensplanens sju kontrollplansskivor — eftersom jag inte kan belägga att det är det. Planen beskriver SQLite, verifier registry, task-attestation, lease, per-attempt worktree, worker launch och diffpolicy, medan huvuddelen av det byggda materialet här handlar om workspace activation, trust-chain och authorization creation.

De skulle inte ha någon verifierad artefakt→Git-commit-koppling för de lokala checkpointfilerna. Repo-head jag kunde se är 8900b00424df6a2e3d77d46189b3dae0d9b732df, men checkpointfilerna hittades inte i repo-code-search. Commit provenance för checkpointkedjan är därför OVERIFIERAT.

De skulle inte veta om vissa äldre checkpoints före BX finns kvar exakt i samma bytes som när de kördes, om inte de följer varje senare inbäddad SHA-binding. Ett fristående komplett inventory-manifest är OVERIFIERAT.

### d) Vad har jag godkänt baserat på din rapportering utan att själv ha kört något?

För HD2A1A, HD2A2A, HD2A3A, HD2A4A, HD2A5, HD2B1 och HD2B2 finns rå terminaloutput från din egen körning i konversationen. Jag kan därför inte klassificera dessa som godkända enbart på min rapportering.

För HC finns också rå terminalkörning från din maskin.

För HD3 har du inte kört något efter att jag levererade filen. Där finns alltså inget användarkört godkännandebevis alls; komponenten står som BYGGD-OTESTAD.

För Post-Workspace Preparation Package finns dokument och status, men jag har inget bevis på att du genom ett separat körbart test själv har verifierat dess innehåll. Om "godkänt" betyder att du accepterat paketet som tekniskt korrekt är det OVERIFIERAT.

För äldre delar av kedjan där jag bara har senare SHA-bindningar eller handofftext men inte den ursprungliga terminaloutputen i den här inventeringen kan jag inte avgöra om du själv körde originalcheckpointen eller accepterade min rapportering. Det gäller bland annat delar av BW/BX, FY/GB och vissa tidiga G-led. Svar: OVERIFIERAT.

Jag kan alltså inte belägga någon specifik slutlig komponent som "du godkände endast på min rapport" utan att samtidigt ha ett användarkört bevis som motsäger det. För de historiska luckorna är svaret vet ej.
