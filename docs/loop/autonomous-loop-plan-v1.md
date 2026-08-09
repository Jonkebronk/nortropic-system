# Autonoma loopen — implementationsplan v1

**Detta är en PLAN, inte en implementation.** Ingen produktionskod ändrades i sessionen som
skrev den. Planen föreslår spec-rader och exit-kriterier; den bygger dem inte.

Vid konflikt gäller repot: `docs/07-konstitution.md`, `docs/03-regelverk.md` och
`docs/loop/regler.md` står över både denna plan och ägarens målbild.

---

## PLAN_BASE_SHA

```
PLAN_BASE_SHA = 1eaa0724be990e14ae095b3be3910496d47d062e
PLAN_BRANCH   = plan/autonomous-loop-v1
```

Arbetskopian var **ren** vid planering (`git status --short` tomt, ett worktree, gren `main`).

---

## CURRENT_STATE

Mätt mot HEAD, inte mot minnet.

| Capability | SPECIFIED | EXIT_TEST | IMPLEMENTATION | WIRED_INTO_LOOP | REAL_RUN_EVIDENCE | AUTHORITATIVE_FILES |
|---|---|---|---|---|---|---|
| state/eventlog | h-001 | `verify/bin/h-001-exit` | JA | JA (claim) | JA | `controller/state/cli` |
| verify runner/register | h-002 | `verify/bin/h-002-exit` | JA | JA (global) | JA | `controller/verify/cli`, `controller/verify/register.json` |
| attestation/stale | h-003 | `verify/bin/h-003-exit` | JA | JA | JA | `controller/attest/cli` |
| lease | h-004 | `verify/bin/h-004-exit` | JA | JA | JA | `controller/lease/cli` |
| workspace | h-005 | `verify/bin/h-005-exit` | JA | JA | JA | `controller/workspace/cli` |
| worker/parser | h-006 | `verify/bin/h-006-exit` | JA | JA | JA | `controller/worker/cli` |
| policy | h-007 | `verify/bin/h-007-exit` | JA | JA | JA | `controller/policy/cli` |
| envelope | h-008 | `verify/bin/h-008-exit` | JA | JA | JA | `controller/envelope/cli` |
| launch/timeout | h-009 | `verify/bin/h-009-exit` | JA | JA (via utförare) | JA | `controller/launch/cli` |
| task selection/claim | h-010 | `verify/bin/h-010-exit` | JA | JA | JA | `controller/taskval/cli` |
| loop | h-011 | `verify/bin/h-011-exit` | JA | — | JA | `controller/loop/cli` |
| executor | h-012 | `verify/bin/h-012-exit` | JA | JA | JA | `controller/utforare/cli` |
| breaker | h-013 | `verify/bin/h-013-exit` | JA | JA | JA | `controller/brytare/cli` |
| **notification** | **h-014** | **NEJ** | **NEJ** | **NEJ** | **NEJ** | (obyggd) |
| **recovery** | **h-015** | **NEJ** | **NEJ** | **NEJ** | **NEJ** | (obyggd) |
| inkoppling | h-016 | `verify/bin/h-016-exit` | JA | JA | JA | `controller/loop/cli` |
| **per-task verdict** | **h-017** | **NEJ** | **NEJ** | **NEJ** | **NEJ** | (obyggd) |

**h-017 mätt vid HEAD:** noll förekomster av `grind_id` eller `exit_test` i
`controller/loop/cli`, `controller/verify/cli` och `controller/attest/cli`. Spec-raden finns
(slice 15, `depends_on` h-002 + h-016), skrivytan är vidgad med `controller/attest/cli`
(ÄGARHAND-42), men **varken prov eller komponent existerar**.

**REAL_RUN_EVIDENCE** kommer ur premiärkörningen `premiar-1` (LOOP-PREMIÄR-1): två tasks, två
attestationer, noll omförsök, verkliga Claude-sessioner. Sessionerna tog 10–20 min var.

**Fakta med tung planbetydelse, mätt:**

- **Kontrollplanet rör aldrig remote.** Noll träffar på `push`/`remote`/`origin` i samtliga
  tretton `controller/*/cli`. Auto-promotion är en ny förtroendeyta, inte en utvidgning.
- **`RUNNERS = {"node": "node"}`** i `controller/verify/cli` — registret kan inte starta någon
  av husets sexton bash-grindar (`verify/bin/` bär sexton `*-exit` plus `_lib.sh`). Mätt i klon: `"bash": "bash"` + registerpost gav
  `verify run p-001-exit .` → 6 PASS 0 FAIL, `h-002-exit` orört 6 PASS, `hash_mismatch` fäller
  fortfarande.
- **`REGISTER` är en fast sökväg** (`Path(__file__).resolve().parent / "register.json"`) och går
  inte att peka om. Fixturregister kräver mutation med återställning (h-002:s precedent).
- **Eventschemat är `{task, status}`** och inget annat: `giltigt_event` kräver icke-tomma
  strängfälten `task` och `status`. Det rymmer ingen körningshändelse.
- **`LEASE_TTL = "180"`** utan heartbeat, medan ett varv mätts ta 10–20 minuter.
- **Grindarnas kostnad är mätt:** h-002 0,2 s · h-007 2,4 s · h-013 7,7 s · h-011 10,7 s ·
  p-001 17 s · h-016 29 s. Ingen grind når en minut.

---

## CURRENT_FLOW

Rekonstruerad ur `controller/loop/cli` vid HEAD, med rad och ägare.

```
config (las_config, rad 141–200; 14 fält, prövas i sin HELHET före leasen)
→ lease acquire            controller/lease/cli      (TTL 180 s, ingen heartbeat)
→ [drain, per task]
   → taskval claim         controller/taskval/cli    (doneness ur ATTEST, ETT event {task,status})
   → [försök 1..budget, INUTI claimet]
      → workspace create   controller/workspace/cli  (eget ws per försök, OFÖRÄNDRAD base)
      → envelope build     controller/envelope/cli   (nio §12-fält; exit_test följer ALDRIG med)
      → brytare kor        controller/brytare/cli    (budget + fingerprints per task)
         → utforare kor    controller/utforare/cli   (stagar, committar, rapport ur GIT)
            → launch run   controller/launch/cli     (timeout, processgrupp)
      → worker parse       controller/worker/cli     (hela stdout = ett kuvert)
      → policy check       controller/policy/cli     (allowed_write, budgetar, docs-krav)
      → verify run         controller/verify/cli     (CONFIGENS verifier_id, mot kandidatträdet)
      → [TASKGRIND]                                   ← FINNS INTE (h-017 obyggd)
      → attest write       controller/attest/cli     (4 fält: task, candidate_sha,
                                                       invalidates_on, stale)
      → workspace destroy
   → base = kandidat-SHA vid attestation, annars orörd
→ lease release
→ exit 0 drain · 1 fel · 3 rent stopp (brytaren öppen)
```

**Byggt:** allt ovan utom `[TASKGRIND]`.
**Endast design/spec:** h-014 notis, h-015 återtag, h-017 taskgrind.
**Finns inte alls, varken spec eller kod:** failure-feedback, operations-event, promotion,
merge-resolver, trust-transition, Markdown-intake, Task IR, verifier author/challenger,
evaluator, read/command-kontrakt.

**Efter drain:** kandidaterna är commits **utan gren**. Ingen ref når dem; de nås bara via
attestationsbutiken, och `git gc` kan städa bort dem. Människan skapar grenen och mergar.

---

## TARGET_STATE

Enligt `00_NORTROPIC_AUTONOMY_TARGET.md`, förkortat till det planen måste bära:

Markdown-källa → source snapshot → planner → canonical Task IR → verifier author + challenger →
frozen verifier → READY → claim → attempt (fresh workspace, samma task-base) → builder →
kandidat → policy → global verifier → **trusted task-specific acceptance gate** → valfri
independent evaluator → attestation → **auto-promotion till authoritative main** → verifierad
main-identitet → nästa task. Failure ger **strukturerad feedback** till nästa attempt inom
bounded budget. Mergekonflikt löses **agentiskt** med **full omverifiering**. Trust-critical
självmodifiering döms av **pre-task control plane** och kräver **clean termination + bootstrap**,
aldrig hot-reload. Människan är exception-gate, inte merge-gate.

---

## GAP_ANALYSIS

Formen är målfilens. `EXISTING_COMPONENT_CAN_OWN_THIS` besvaras mot faktisk kod.

### G1 · Trusted task gate (h-017)

```
EXISTING_COMPONENT_CAN_OWN_THIS = YES  (controller/verify/cli + controller/loop/cli)
WHY   = verify kör redan den godkända filen UR REPOT, hash-kontrollerad före start, med
        målkatalogen som cwd. Kandidaten kan inte manipulera grinden men grinden dömer den.
        Saknas: bash i RUNNERS, ett uppslagsverb, loopens anrop, bokföring i attestationen.
NEW_COMPONENT_REQUIRED = NO
TRUST_IMPACT = HÖG. Detta ÄR trust-gränsen mellan builder och domare.
STATE_IMPACT = attestationen får två fält (grind_id, grind_sha256). Bakåtkompatibelt.
TEST_IMPACT  = verify/bin/h-017-exit (obyggt). h-003-exit grepar mot värden, inte fältuppsättning
               — extra fält fäller den inte (mätt).
```

Spec-raden finns. **Status: prov och komponent saknas.**

### G2 · Failure-feedback till nästa attempt

```
EXISTING_COMPONENT_CAN_OWN_THIS = NEJ, delvis
WHY   = kuvertet (h-008) är rätt kanal in till buildern, men bär i dag nio fasta fält och
        ingenting om föregående försök. Utföraren kastar redan sessionens stdout vid nonzero
        (h-009), så orsaken finns bara som brytarens text. Ingen artefakt är immutabel eller
        adresserbar.
NEW_COMPONENT_REQUIRED = JA — en feedback-butik. Kuvertet UTVIDGAS, inte ersätts.
TRUST_IMPACT = MEDEL. Feedback får inte läcka verifierarens implementation (målbild §2.2).
STATE_IMPACT = ny artefaktbutik, adresserad per (task, attempt).
TEST_IMPACT  = måste mäta att attempt N+1 FÅR artefakten och att den INTE bär grindens kod.
```

### G3 · Recovery/crash consistency (h-015)

```
EXISTING_COMPONENT_CAN_OWN_THIS = NEJ
WHY   = h-015 har spec-rad men ingen kod. Mätt behov: leasens TTL 180 s utan heartbeat mot varv
        på 10–20 min betyder att en andra controller kan återta resursen mitt i en levande
        körning. Brytaren har inget reset-verb; en öppen brytare stoppar varje ny körning tills
        en människa raderar tillståndsfilen (drift.md §6).
NEW_COMPONENT_REQUIRED = JA (controller/atertag/cli, redan specad)
TRUST_IMPACT = MEDEL-HÖG. Obevakad drift utan återtag betyder att ett avbrott kräver människa.
STATE_IMPACT = läser attest + state + brytartillstånd; skriver lease-återtag.
TEST_IMPACT  = verify/bin/h-015-exit (obyggt).
```

### G4 · Operations/lifecycle-eventström

```
EXISTING_COMPONENT_CAN_OWN_THIS = NEJ
WHY   = skiva 1:s event är {task, status} och `giltigt_event` avvisar allt annat. Loopens
        doktrin säger uttryckligen att kedjan INTE skriver egna event, därför att ett andra
        schema i samma logg vore en ny komponent på ett fel. Att vidga skiva 1:s schema skulle
        blanda authoritative task state med observability.
NEW_COMPONENT_REQUIRED = JA — separat, versionerad eventström i EGEN butik.
TRUST_IMPACT = LÅG för domen, HÖG för observerbarhet. Events är aldrig bevis; attestationen är.
STATE_IMPACT = NY logg. Skiva 1:s semantik rörs INTE.
TEST_IMPACT  = måste mäta att task-state är oförändrat och att eventströmmen är append-only.
```

**Följd som löser ett känt problem:** h-014:s diskriminator (brytare öppnad kontra kvot slut är
båda exit 9, och enda skillnaden är prefixet i en orsakssträng) försvinner när `breaker.opened`
och `budget.exhausted` är skilda eventtyper. **Notisen bör därför byggas som konsument av
eventströmmen, efter G4 — inte före.**

### G5 · Auto-promotion till authoritative main

```
EXISTING_COMPONENT_CAN_OWN_THIS = NEJ
WHY   = MÄTT: noll träffar på push/remote/origin i samtliga tretton controller/*/cli. Kedjan har
        i dag ingen remote-yta alls, ingen credential-hantering och ingen main-identitetskontroll.
NEW_COMPONENT_REQUIRED = JA
TRUST_IMPACT = HÖGST i hela planen. Detta tar bort människan ur merge-gaten.
STATE_IMPACT = promotion måste vara idempotent och crash-safe; se PROMOTION_PLAN.
TEST_IMPACT  = kräver ett prov som kan mäta promotion mot ett LOKALT bare-repo som står för
               origin — aldrig mot den verkliga remoten.
```

### G6 · Main-identitet och compare-and-swap

```
EXISTING_COMPONENT_CAN_OWN_THIS = NEJ
NEW_COMPONENT_REQUIRED = JA (del av G5)
TRUST_IMPACT = HÖG. Utan CAS kan två controllers eller en människa skriva över varandra.
STATE_IMPACT = promotion måste bära förväntad gammal main-SHA.
TEST_IMPACT  = måste mäta att promotion FALLER när main rört sig sedan verifieringen.
```

### G7 · Merge conflict resolver · G8 · Full omverifiering av löst kandidat

```
EXISTING_COMPONENT_CAN_OWN_THIS = NEJ
WHY   = ingen komponent känner till konflikter. Utföraren committar i ett workspace på oförändrad
        base; ingen rebase eller merge sker någonstans i kedjan.
NEW_COMPONENT_REQUIRED = JA
TRUST_IMPACT = HÖG. B:s PASS får aldrig ärvas av D (målbild §2.5).
STATE_IMPACT = D är en ny kandidat med egen attestation.
TEST_IMPACT  = måste mäta att D verifieras från noll och att B:s attestation inte återanvänds.
```

### G9 · Trust-critical självmodifiering

```
EXISTING_COMPONENT_CAN_OWN_THIS = NEJ
WHY   = kedjan kör alltid REPOTS controller/*/cli via ROT = parents[2]. En task som ändrar
        kontrollplanet får sin ändring mergad och NÄSTA körning använder den nya domaren — men
        ingenting hindrar i dag att samma process fortsätter med hot-reload om komponenten
        startas om, och ingenting mäter att den domare ägaren mergar är den han godkände.
NEW_COMPONENT_REQUIRED = JA — supervisor + bootstrap-verifiering.
TRUST_IMPACT = HÖGST tillsammans med G5. Utan detta kan systemet certifiera sin egen födelse.
STATE_IMPACT = controllern måste kunna avslutas rent och startas om av en supervisor.
TEST_IMPACT  = måste mäta att en trust-critical task döms av FÖRE-versionen.
```

### G10 · Markdown intake · G11 · Canonical Task IR

```
EXISTING_COMPONENT_CAN_OWN_THIS = DELVIS
WHY   = `spec` är redan ett SÖKVÄGSFÄLT i configen och loopen läser aldrig tasklistan själv —
        vilken JSON-fil som helst med en tasks-array duger (bevisat: premiären körde mot
        config/premiar-backlog.json, inte mot specs/tasks.spec.json). Runtime-representationen
        finns alltså; det som saknas är kompilatorn från Markdown och provenance-fälten.
NEW_COMPONENT_REQUIRED = JA (intake/planner), men den PRODUCERAR dagens format utvidgat.
TRUST_IMPACT = MEDEL. Intake får aldrig kunna göra en task verifierbar på pappret utan grind.
STATE_IMPACT = nya tillstånd RAW..DONE lever i intake-butiken, inte i skiva 1:s state.
TEST_IMPACT  = NEEDS_SPEC måste vara ett mätbart utfall som INTE startar en builder.
```

### G12 · Verifier author + challenger · G13 · Frusna verifierarartefakter

```
EXISTING_COMPONENT_CAN_OWN_THIS = DELVIS
WHY   = registret ÄR frysmekanismen: id → path + sha256, hash-kontroll före start, och
        `sakra_sokvag` vägrar symlänk och väg ut ur repot. Det som saknas är rollerna som
        FÖRFATTAR och ANGRIPER grinden innan den fryses.
NEW_COMPONENT_REQUIRED = JA för rollerna, NEJ för frysningen.
TRUST_IMPACT = HÖG. Author och builder får inte vara samma behörighetsdomän (målbild §5).
STATE_IMPACT = registerposter skapas per task; registret växer från 2 till ~18+.
TEST_IMPACT  = challengern måste mätas på att den fäller en medvetet svag verifierare.
```

### G14 · Independent evaluator · G15 · Bounded adversarial review

```
EXISTING_COMPONENT_CAN_OWN_THIS = NEJ
NEW_COMPONENT_REQUIRED = JA, provider-neutral
TRUST_IMPACT = LÅG för domen (konsensus är aldrig root of trust), MEDEL för kostnad.
STATE_IMPACT = findings blir feedback (G2) och kräver full omverifiering.
TEST_IMPACT  = måste mäta att evaluatorns JA aldrig ensamt attesterar.
```

### G16 · Read/command-kontrakt för Verkstadsgolvet

```
EXISTING_COMPONENT_CAN_OWN_THIS = NEJ
WHY   = ingen läsyta finns; drift.md §3 föreskriver i dag att människan tittar i katalogerna.
NEW_COMPONENT_REQUIRED = JA, men BYGGER PÅ G4:s eventström.
TRUST_IMPACT = HÖG om fel byggd. Webbappen får aldrig generisk shell-/Git-yta.
STATE_IMPACT = projection, aldrig root of truth. Controller local state är authority.
TEST_IMPACT  = måste mäta att kommandoytan avvisar allt utanför de fem verben.
```

### G17 · Branch protection och GitHub-inställningar

```
EXISTING_COMPONENT_CAN_OWN_THIS = ej tillämpligt
STATUS = OVERIFIERAT. Sessionen når inte nätet (sandboxens allowlist: api.anthropic.com) och
         `gh` kunde inte läsa sin konfiguration. Om main bär branch protection som kräver PR
         eller status checks kommer auto-promotion att FALLA — och det måste mätas FÖRE G5
         byggs, inte upptäckas i drift.
```

### G18 · Credential/permission

```
STATUS = OVERIFIERAT för remote. Mätt lokalt: git add och git commit fungerar från en session;
         push faller på sandboxens nätspärr (SSH-förhandling nekad). Controllern kör utanför
         sandboxen i ägarens terminal och når nätet — men vilken identitet promotion ska använda,
         och var den credentialen bor, är en OBESVARAD ägarfråga.
```

### G20 · Taskgrinden kör kandidatens komponenter *(funnet i planens egen granskning)*

```
EXISTING_COMPONENT_CAN_OWN_THIS = delvis (h-017:s kriterium måste bära det)
WHY   = MÄTT: kmd_run kör grindfilen ur repot men med cwd = kandidatträdet, och husets grindar
        adresserar komponenter relativt (`CLI="controller/verify/cli"`). En taskgrind som körs
        genom registret startar alltså KANDIDATENS controller/*/cli. För en vanlig task är det
        rätt. För en task som ändrar kontrollplanet betyder det att den nya domaren dömer sin
        egen födelse REDAN VID GRINDKÖRNINGEN — långt före den promotion som S8 skulle vakta.
        h-017 är själv en sådan task: dess skrivyta bär controller/verify/cli.
NEW_COMPONENT_REQUIRED = NO. Det är en ORDNINGSREGEL, inte en komponent.
TRUST_IMPACT = HÖG. Målbild §2.7 säger att trust-critical ändringar ska dömas av PRE-task
        control plane. Utan denna regel är §2.7 brutet före promotion ens är byggd.
STATE_IMPACT = ingen ny butik. Configen behöver veta vilken yta som är trust-critical.
TEST_IMPACT  = S1:s prov måste mäta en trust-critical kandidat vars komponent är sabbad så att
        den alltid säger JA — och attestationen ska ändå utebli.
```

**Regeln planen låser:** en task vars diff rör den trust-critical ytan får sin taskgrind körd med
**repots** komponenter, inte kandidatens. Kandidatträdet är då grindens *indata*, inte dess
körmiljö. Vilken yta som är trust-critical står i TRUST_TRANSITION_PLAN och låses av ägarhand.

### G19 · Lease TTL/heartbeat

```
EXISTING_COMPONENT_CAN_OWN_THIS = YES (controller/lease/cli)
WHY   = h-004 bär redan acquire/release/owner med TTL. Heartbeat saknas och har ingen spec-rad;
        loop/cli rad 88–92 skriver ut att det medvetet inte byggts.
NEW_COMPONENT_REQUIRED = NO — h-004 utvidgas.
TRUST_IMPACT = MEDEL. Utan heartbeat är exklusiviteten en utsaga som inte håller över ett varv.
STATE_IMPACT = leasefilen får en förnyelsestämpel.
TEST_IMPACT  = h-004-exit måste vidgas; mätt att ett varv tar 10–20 min mot TTL 180 s.
```

---

## TRUST_MODEL

Fyra domäner, och den bärande regeln är att ingen får döma sin egen produkt.

```
BUILDER            sessionen i workspacet. Ser kuvertet. Ser ALDRIG exit_test.
                   Får redigera filer i workspacet. Får aldrig committa (h-012 fäller det).

DETERMINISTIC      controller/*/cli ur REPOT, aldrig ur kandidaten.
VERIFIER           Grindar körs hash-kontrollerade ur registret med kandidaten som cwd.

INDEPENDENT        valfri LLM-evaluator. Aldrig root of trust. Dess JA attesterar aldrig ensamt.
EVALUATOR

OWNER              spec-rader, register-godkännande, konstitution. Enda som får vidga förtroende.
```

**Mätta egenskaper som bär modellen i dag:** kuvertet utelämnar `exit_test` (h-008) · `specs/**`
är denied_write, så en task kan inte peka om sin egen grind · registret binder path + sha256 och
hash-kontrollen ligger FÖRE start · `sakra_sokvag` vägrar symlänk och väg ut ur repot · utföraren
committar, inte sessionen.

**Grindens laddning är mätt och exakt — och den skär åt två håll:**

```
GRINDFILEN      kommer ur REPOT. sakra_sokvag löser post["path"] mot ROT = parents[2],
                aldrig mot målkatalogen (controller/verify/cli rad 47-56).
_lib.sh         kommer också ur REPOT: grindarna sourcar `. "$(dirname "$0")/_lib.sh"`
                och $0 är den absoluta sökvägen kmd_run startar (str(p)).
                En kandidat kan alltså INTE byta ut biblioteket.
DET GRINDEN     kommer ur KANDIDATEN. kmd_run kör med cwd=mal, och grindarna
RÖR             adresserar komponenter RELATIVT: `CLI="controller/verify/cli"`,
                `krav_komponent "$CLI"` → `[ ! -x "controller/verify/cli" ]`
                löses mot målkatalogen (_lib.sh rad 7-14).
```

För en vanlig task är det andra ledet precis rätt: grinden ska döma kandidatens kod. **För en
trust-critical task är det en inversion som planen måste namnge** — se G20.

**Hål som planen måste stänga:** registret ligger under `controller/`, alltså i en yta en task
kan begära · ingen mäter att den domare ägaren mergar är den han godkände · `_lib.sh` är inte
hash-bunden — mätt exponering: en kandidat når den inte (den laddas ur repot via `$0`), så det är
ett ägarhandslarm, inte en kandidatväg · **taskgrinden kör kandidatens komponenter (G20)**.

---

## PROPOSED_SLICES

Alla nya slices följer beslut 3: **spec-rad och exit-test före kod.** Ingen implementeras i denna
session. `allowed_write` måste ligga inom `.gitignore`-vitlistan (`/*` ignorerar allt i roten).

### S1 · h-017 — per-task-domen *(spec-rad FINNS, slice 15)*

```
DEPENDENCIES  h-002, h-016
ALLOWED_WRITE controller/loop/**, controller/verify/cli, controller/attest/cli,
              tests/controller/loop/**, docs/05-beslutslogg.md, docs/loop/drift.md
EXIT_TEST     verify/bin/h-017-exit                          (OBYGGT)
EXIT CRITERION (utkast, testbart) En kandidat attesteras endast om BÅDA domarna är gröna, och
              attestationen bär grind_id och grind_sha256. Grinden slås upp på spec-radens
              exit_test-SÖKVÄG. En task utan registerpost attesteras som förut men utan grind_id.
NEGATIVA      grind som aldrig körs · grind körd mot reporoten · vänlig post under annat path ·
KONTROLLER    kandidat som lägger alltid-grön kopia av grind, _lib.sh OCH register i eget träd ·
              driven SHA · task utan registerpost (ska attesteras men UTAN grind_id) ·
              **trust-critical kandidat vars komponent alltid säger JA (G20)**
```

**Öppen riggfråga:** `REGISTER` går inte att peka om. Provet måste antingen mutera repots register
med säkerhetskopia och `trap` (h-002:s precedent) eller köra kedjan i en klon som bär
arbetsträdets komponenter. Vald väg enligt ÄGARHAND-42: mutation med återställning.

### S2 · h-015 — återtaget *(spec-rad FINNS, slice 13)*

```
DEPENDENCIES  h-010, h-013   (+ h-016 i praktiken: återtaget måste förstå omförsök)
ALLOWED_WRITE controller/atertag/**, tests/controller/atertag/**, docs/05-beslutslogg.md
EXIT_TEST     verify/bin/h-015-exit                          (OBYGGT)
EXIT CRITERION (utkast, testbart) En körning som dödas mitt i ett försök kan återupptas utan
              människa: leasen återtas först när den verkligen löpt ut, redan attesterade tasks
              körs inte om, och brytaren har ett reset-verb som ersätter dagens manuella radering
              av tillståndsfilen. Med heartbeat överlever exklusiviteten ett helt varv.
NEGATIVA      lease återtagen FÖRE TTL · attesterad task väljs om · öppen brytare överlever inte
KONTROLLER    omstart · två samtidiga återstarter ger två ägare
```

**Vidgning som mätningen kräver:** kriteriet bör bära heartbeat/TTL-frågan (G19). Ett varv tar
10–20 min mot TTL 180 s; utan förnyelse är exklusiviteten inte sann över ett enda varv.

### S3 · NY — strukturerad failure-feedback

```
VARFÖR NY     kuvertet (h-008) bär nio fasta fält och ingen historik; ingen komponent äger en
              immutabel artefakt per försök. Att lägga historiken i kuvertet utan butik hade
              gjort h-008 till både format och lagring.
DEPENDENCIES  h-012, h-013, h-016
ALLOWED_WRITE controller/aterkoppling/**, tests/controller/aterkoppling/**, docs/05-beslutslogg.md
EXIT_TEST     verify/bin/h-018-exit
EXIT CRITERION (utkast, testbart) Efter ett fallet försök finns en immutabel artefakt adresserad
              per task och försöksnummer, och attempt N+1 får den i kuvertet. Artefakten bär
              failureklass, steg och evidence-referens ordagrant ur systern, men INNEHÅLLER
              ALDRIG grindens kod eller dess kontrollnamn — mätt genom att en grind vars text är
              en unik markörsträng aldrig läcker den till kuvertet. Artefakten är oföränderlig:
              ett andra försök skriver en NY artefakt och den första är byte-identisk efteråt.
NEGATIVA      attempt N+1 utan artefakt · artefakt som bär grindens innehåll · artefakt som skrivs
KONTROLLER    över · feedback som når en task den inte gäller
```

**Avgränsning mot S4 (annars två sanningar):** feedbackartefakten är **authority** för vad
buildern får veta. Eventtypen `feedback.created` i S4 bär bara en REFERENS till artefakten,
aldrig dess innehåll. Ingen komponent får läsa feedback ur eventströmmen.

### S4 · NY — operations/lifecycle-eventkontrakt

```
VARFÖR NY     skiva 1:s giltigt_event kräver {task, status} och avvisar allt annat; loopens
              doktrin förbjuder uttryckligen ett andra schema i samma logg. Authoritative task
              state och observability måste vara skilda butiker.
DEPENDENCIES  h-001 (form), h-016
ALLOWED_WRITE controller/handelse/**, tests/controller/handelse/**, docs/05-beslutslogg.md
EXIT_TEST     verify/bin/h-019-exit
EXIT CRITERION (utkast) Varje event bär schema_version, event_id, run_id, task_id, attempt_id,
              ordningsfält, event_type och payload. Strömmen är append-only: en körning som
              avbryts lämnar en läsbar logg där varje rad är exakt ett event. Skiva 1:s state är
              BYTE-IDENTISKT före och efter en körning som skriver hundra event — mätt med sha256
              på events.jsonl och state.db. Ett okänt event_type avvisas, aldrig tolkas.
NEGATIVA      event i skiva 1:s logg · halvskriven rad · event_type utanför schemat · saknad
KONTROLLER    attempt_id på ett attempt-event
```

### S5 · h-014 — notisen *(spec-rad FINNS, slice 12) — OMORDNAD, se MIGRATION_ORDER*

```
VARFÖR EFTER S4   h-014 kräver FYRA skilda händelser, men brytare öppnad och kvot slut är båda
                  exit 9 och skiljs i dag bara av ett prefix i en orsakssträng som inget kriterium
                  binder. Med S4 blir de skilda event_type och klausulen blir byggbar utan att
                  någon parsar prosa.
FÖRUTSÄTTNING     webhooken ÄR uppsatt (ÄGARHAND-37): ~/.nortropic/slack-webhook, rättigheter 600,
                  curl svarade ok. Configen ska bära SÖKVÄGEN, aldrig värdet.
EXIT CRITERION    (utkast, testbart) Fyra skilda händelser ger fyra notiser, och ett felfritt varv
                  ger INGEN notis. Diskrimineringen sker på event_type ur S4, aldrig på prosa.
                  Webhookens värde förekommer inte i något som skrivs till logg, stdout eller
                  felmeddelande — mätt genom att söka efter värdet i allt körningen lämnar efter sig.
NEGATIVA          vanligt varv ger notis · brytare öppnad och kvot slut ger samma notis ·
KONTROLLER        webhookvärdet läcker till logg eller felutskrift
```

### S6 · NY — verifierad auto-promotion

```
VARFÖR NY     kedjan har noll remote-yta (mätt). Ingen befintlig komponent kan äga det.
DEPENDENCIES  h-017 (ingen promotion utan taskgrind-verdikt), h-015, S4
ALLOWED_WRITE controller/befordran/**, tests/controller/befordran/**, docs/05-beslutslogg.md
EXIT_TEST     verify/bin/h-020-exit
EXIT CRITERION (utkast, testbart) Mot ett LOKALT bare-repo som står för origin: en attestation som
              bär grind_id och inte är stale flyttar main till kandidatens SHA med CAS mot den
              förväntade gamla SHA:n, och `ls-remote` svarar kandidatens SHA efteråt. En
              attestation UTAN grind_id flyttar aldrig main. Har main rört sig sedan
              verifieringen avbryts promotion och kandidaten går till S7 — main står orörd.
              Samma promotion körd två gånger ger ett main-läge, inte två.
FÖRUTSÄTTNING Promotion kräver en HÅLLEN och icke-utlöpt lease. Utan G19:s heartbeat kan två
              controllers nå promotion samtidigt; CAS gör utfallet säkert men inte gratis.
NEGATIVA      attestation UTAN grind_id befordras aldrig · main rört sig sedan verifieringen ·
KONTROLLER    force push · promotion utan post-check · dubbelkörning ger inte två promotions ·
              promotion med utlöpt lease
```

### S7 · NY — agentisk merge-resolution med full omverifiering

```
DEPENDENCIES  S6
ALLOWED_WRITE controller/konflikt/**, tests/controller/konflikt/**, docs/05-beslutslogg.md
EXIT_TEST     verify/bin/h-021-exit
EXIT CRITERION (utkast, testbart) En verifierad kandidat B som inte längre går att befordra mot
              main C ger en NY kandidat D med eget SHA, och D:s attestation skapas först efter
              att policy, global verifierare och taskgrind körts om från noll mot D. B:s
              attestation finns kvar oförändrad och är inte indata till D:s dom — mätt genom att
              D:s dom uteblir när D är sabbad, trots att B var grön.
NEGATIVA      D ärver B:s attestation · resolution utan budget · konflikt löst utan evidence ·
KONTROLLER    main som rör sig igen behandlas inte som nytt försök
```

### S8 · NY — trust-transition med supervisor och bootstrap

```
DEPENDENCIES  S6
ALLOWED_WRITE controller/overvakare/**, tests/controller/overvakare/**, docs/05-beslutslogg.md
EXIT_TEST     verify/bin/h-022-exit
EXIT CRITERION (utkast, testbart) En task som ändrar `controller/verify/cli` döms av FÖRE-versionen
              — mätt med en kandidatversion som bär en unik markörsträng, och markören får inte
              förekomma i något som kördes före promotion. Efter promotion avslutas controllern
              rent, supervisorn bootstrap-verifierar nya main, och först därefter startas en ny
              controller. Ingen process överlever promotion och fortsätter döma.
NEGATIVA      ny domare dömer sin egen födelse · hot-reload utan omstart · bootstrap som inte
KONTROLLER    verifierar den nya mainen innan backloggen återupptas · G20-inversionen: taskgrinden
              kör kandidatens komponenter för en trust-critical task
```

### S9 · NY — Markdown-intake och canonical Task IR

```
DEPENDENCIES  S4 (tillstånd som event), h-007 (allowed_write-formen)
ALLOWED_WRITE controller/intag/**, tests/controller/intag/**, docs/05-beslutslogg.md
EXIT_TEST     verify/bin/h-023-exit
EXIT CRITERION (utkast, testbart) En Markdown-fil med två arbetsmål ger två tasks i canonical IR,
              var och en spårbar till källans sha256 och sektion. En task som saknar
              verifieringskontrakt hamnar i NEEDS_SPEC och når aldrig en builder — mätt genom att
              ingen session startar. Den genererade IR-filen kan matas till loopen som `spec` utan
              att någon befintlig komponent ändras.
NEGATIVA      task utan verifieringskontrakt når builder · provenance saknas · NEEDS_SPEC startar
KONTROLLER    ändå en session · genererad JSON som inte går att spåra till källans sha256
```

### S10 · NY — verifier author + challenger

```
DEPENDENCIES  S9, h-017
ALLOWED_WRITE controller/grindsmed/**, tests/controller/grindsmed/**, docs/05-beslutslogg.md
EXIT_TEST     verify/bin/h-024-exit
EXIT CRITERION (utkast, testbart) För en task utan människoskrivet prov produceras en grind som
              fryses i registret med path + sha256, och frysningen sker FÖRE buildern startar.
              Challengern fäller en medvetet svag grind — mätt med en grind som alltid säger JA,
              och challengern måste avvisa den. Author och builder körs i skilda sessioner.
NEGATIVA      author och builder i samma session · challenger som inte fäller en medvetet svag
KONTROLLER    grind · grind som fryses utan att ha prövats åt båda hållen
```

### S11 · NY — independent evaluator, provider-neutral

```
DEPENDENCIES  S3 (findings blir feedback), S4
ALLOWED_WRITE controller/bedomare/**, tests/controller/bedomare/**, docs/05-beslutslogg.md
EXIT_TEST     verify/bin/h-025-exit
EXIT CRITERION (utkast, testbart) Evaluatorn körs först när hårda grindar är gröna. Ett finding
              blir en feedbackartefakt (S3) och tvingar fram en NY kandidat som verifieras från
              noll. En evaluator som säger JA på en kandidat med röd grind ändrar ingenting —
              attestationen uteblir ändå. Rundor och kostnad har tak i configen och en körning som
              når taket stannar med orsak.
NEGATIVA      evaluatorns JA attesterar ensamt · finding som inte ger omverifiering · obundet
KONTROLLER    antal rundor · kostnad utan tak
```

### S12 · NY — smal read/command-yta

```
DEPENDENCIES  S4
ALLOWED_WRITE controller/lucka/**, tests/controller/lucka/**, docs/05-beslutslogg.md
EXIT_TEST     verify/bin/h-026-exit
EXIT CRITERION (utkast, testbart) De fem verben fungerar med typad payload. Ett sjätte verb
              avvisas, och en payload som bär en shell-sträng exekveras aldrig — mätt med en
              payload vars innehåll skulle ha skapat en kanariefil om den tolkats. Läsytan svarar
              ur eventströmmen och kan inte skriva. Controllerns lokala state förblir authority.
NEGATIVA      kommando utanför de fem verben accepteras · shell-sträng exekveras · projection
KONTROLLER    behandlas som authority
```

**Namnen ovan är förslag i planens form `controller/<del>/cli`.** Regel 3 kräver planens namn och
inga nya kodnamn — de slutgiltiga namnen sätts i spec-raden av ägarhand.

---

## DEPENDENCY_GRAPH

```
h-016 (BYGGD)
  └─ S1 h-017 taskgrind ────────┬─ S6 promotion ──┬─ S7 merge-resolver
                                │                 └─ S8 trust-transition
  S2 h-015 återtag ─────────────┤
  S4 eventkontrakt ─────────────┼─ S5 h-014 notis
       │                        └─ S12 read/command-yta
       └─ S9 intake ─ S10 verifier author+challenger
  S3 feedback ─────────────────── S11 evaluator
```

Kritisk väg till obevakad drift: **S1 → S2 → S6**. Utan taskgrinden betyder en attestation inte
att tasken är löst; utan återtaget kräver varje avbrott en människa; utan promotion är människan
kvar i merge-gaten.

---

## EVENT_SCHEMA_PLAN

Egen butik, egen version, aldrig i skiva 1:s logg.

```json
{
  "schema_version": "1.0.0",
  "event_id": "<uuid eller monoton sträng, unik i strömmen>",
  "seq": 1,
  "ts": "2026-08-09T14:47:03.121Z",
  "run_id": "premiar-1",
  "task_id": "p-001",
  "attempt_id": "premiar-1-p-001-1",
  "event_type": "attempt.started",
  "payload": {},
  "evidence": []
}
```

`seq` är ordningsfältet och är auktoritativt; `ts` är för människan och får aldrig användas för
ordning (klockor hoppar). `evidence` bär referenser — sökvägar eller SHA — aldrig innehåll.

Familjer enligt målbilden: `run.*` `task.*` `attempt.*` `workspace.*` `agent.*` `candidate.*`
`policy.*` `verification.*` `feedback.*` `evaluation.*` `attestation.*` `promotion.*` `merge.*`
`main.*` `breaker.*` `budget.*`.

**Två typer som löser h-014:s diskriminator:** `breaker.opened` och `budget.exhausted` är skilda,
och `promotion.failed` skiljs från `verification.failed`.

**Bindande:** UI:t ska aldrig tolka fri terminalprosa. Varje tillstånd en människa behöver se ska
finnas som event_type.

---

## COMMAND_SCHEMA_PLAN

Fem verb, ingenting mer.

```
intake.submit               { source_ref, source_sha256 }
run.start                   { config_ref }
run.pause_at_safe_boundary  { run_id }
run.resume                  { run_id }
inspect                     { task_id | run_id }
```

**Bindande:** ingen generisk shell- eller Git-yta. Ett kommando är ett namn ur listan plus en
typad payload — aldrig en sträng som blir ett kommando. Controllerns lokala state är authority;
transporten är projection. Utgående-först från Macen föredras framför inkommande port.

`run.pause_at_safe_boundary` måste definiera vad en säker gräns är: **mellan tasks, aldrig mitt i
ett försök** — annars lämnas workspace och lease i obestämt läge.

---

## PROMOTION_PLAN

```
AUTHORITATIVE_MAIN          = origin/main hos Jonkebronk/nortropic-system
LOCAL_MAIN_ROLE             = arbetskopia och kandidatbas; aldrig sanning
ORIGIN_MAIN_ROLE            = sanning
PROMOTION_PRECONDITIONS     = attestation finns · attestationen bär grind_id och grind_sha256 ·
                              attestationen är inte stale · kandidatens träd verifierat i denna
                              körning · main-SHA vid verifieringen är känd
PROMOTION_OPERATION         = git push origin <kandidat-sha>:refs/heads/main --force-with-lease=
                              refs/heads/main:<förväntad gammal main-SHA>
EXPECTED_OLD_MAIN_BINDING   = den main-SHA kandidaten verifierades mot; ändras den avbryts
                              promotion och kandidaten går till merge-resolution (S7)
POST_PROMOTION_IDENTITY_CHECK = git ls-remote origin refs/heads/main måste svara kandidatens SHA
REMOTE_UPDATE_SEMANTICS     = compare-and-swap. Om lease-villkoret inte håller är det INTE ett fel
                              utan ett reconciliation-attempt
NO_FORCE_PUSH               = naket --force förbjudet. --force-with-lease med explicit förväntad
                              gammal SHA är CAS, inte force push, och måste stå som sådant
```

**Not:** `--force-with-lease` utan explicit förväntat värde läser reflog och kan lura sig själv.
Planen kräver den EXPLICITA formen.

### Crashpunkter och semantik

| Crashpunkt | Rekonstruktion | Semantik |
|---|---|---|
| kandidat verifierad, före attestation | attestbutiken saknar posten; kandidat-SHA finns i git | gör om verifieringen — attestation utan bevis skrivs aldrig |
| attestation skriven, före promotion | attestation finns, `ls-remote` visar gammal main | promotion är idempotent: kör om med samma CAS |
| promotion påbörjad | okänt utfall | läs `ls-remote`. Är main = kandidat: fortsätt post-check. Annars: gör om CAS |
| main flyttad, state ej uppdaterat | `ls-remote` = kandidat, lokalt state efter | uppdatera state ur remote — remote är sanning |
| main flyttad, post-check ej skriven | samma | kör post-check igen; den är ren läsning |
| post-check klar, nästa claim ej startad | allt konsistent | fortsätt drain |

**Fail-closed:** kan promotion inte avgöras ur `ls-remote` — nätfel, autentiseringsfel — stannar
körningen med orsak. Den gissar aldrig.

---

## MERGE_RESOLUTION_PLAN

```
verifierad kandidat B (attesterad, bär grind_id)
+ current main C (≠ B:s förväntade gamla main)
→ isolerat resolutionsworkspace på C
→ resolver-agent får B:s diff och konflikten, ALDRIG B:s attestation
→ kandidat D
→ FULL verifiering från noll: policy → global verifierare → taskgrind
→ NY attestation för D
→ promotion av D med CAS mot C
```

**Krav, alla mätbara:** D är en ny kandidat med eget SHA · B:s attestation återanvänds aldrig och
B:s PASS är inte indata till D:s dom · resolution har bounded budget (antal försök och väggtid) ·
rör sig main igen under resolutionen är det ett NYTT reconciliation-attempt, inte ett fel · ingen
force push · varje konfliktlösning lämnar evidence.

**Fail-closed:** kan konflikten inte lösas inom budget stannar körningen. Tasken förblir claimed.

---

## TRUST_TRANSITION_PLAN

```
task ändrar trust-critical control-plane-kod
→ döms av FÖRE-versionen av kontrollplanet (den som körde när tasken claimades)
→ promotion
→ clean termination av controllern (inget hot-reload)
→ supervisor kör bootstrap-verifiering av NYA main
→ supervisor startar ny controller ur nya main
→ backloggen återupptas
```

**Trust-critical yta (förslag, låses av ägarhand):** `controller/**`, `verify/**`, `specs/**`,
`scripts/check-invariants.mjs`, `config/managed-settings.json`, konstitution och regelverk.

**Bindande:** den nya domaren får aldrig döma sin egen födelse. Bootstrap-verifieringen körs av
supervisorn, inte av den nya controllern.

**Mätbart:** en task som ändrar `controller/verify/cli` ska dömas av den gamla `verify/cli`, och
provet ska mäta att den NYA aldrig kördes före promotion.

---

## MARKDOWN_INTAKE_PLAN

```
.md / inklistrad text
→ immutable source snapshot + sha256
→ planner
→ canonical Task IR (JSON, GENERERAD artefakt)
→ validering
→ verifieringsförberedelse (S10)
→ READY | NEEDS_SPEC
```

Tillstånd: `RAW PLANNING NEEDS_SPEC READY QUEUED WORKING VERIFYING REVIEWING MERGING DONE STOPPED`.
`NEEDS_SPEC` är ett legitimt slututfall och startar ingen builder.

**Task IR — utgår från dagens nio fält och utvidgar:**

```json
{
  "task_id": "...", "slice": 0, "title": "...", "summary": "...",
  "allowed_write": ["..."], "denied_write": ["..."],
  "exit_test": "verify/bin/...", "exit_criterion": "...",
  "docs_impact": ["..."], "depends_on": ["..."],
  "candidate_requirements": { "omfang": {} },
  "acceptance_criteria": ["..."],
  "risk_class": "low|normal|high",
  "verification_contract": { "grind_id": "...", "grind_sha256": "..." },
  "provenance": { "source_id": "...", "source_sha256": "...", "source_locator": "..." }
}
```

**Återanvändning är mätt möjlig:** `spec` är ett sökvägsfält och loopen läser aldrig tasklistan
själv — premiären körde mot `config/premiar-backlog.json`. En genererad IR-fil kan alltså matas in
utan att någon komponent ändras, så länge de nio befintliga fälten finns.

**Bindande:** Markdown förblir människans primära yta. JSON är genererad artefakt. Originalkällan
ska alltid vara spårbar från en genererad task.

---

## VERIFIER_PREPARATION_PLAN

```
Planner → Task Contract → Verifier Author → Verifier Challenger → freeze → Builder
```

**Frysningen finns redan:** registret binder id → path + sha256, hash-kontrollen ligger före start,
`sakra_sokvag` vägrar symlänk och väg ut ur repot. Grinden läggs i `verify/**`, som ligger i
sandboxens denyWrite — buildern kan inte skriva där ens om den ville.

**Rollseparation:** Author och Builder får inte vara samma agentsession. Challengern ska försöka
FALSIFIERA grinden och måste kunna fälla en medvetet svag verifierare.

**Metodregeln som gäller:** *för varje viktig kontroll — vilken konkret felaktig implementation
ska den fälla?* Positiva ankare krävs; en frånvaromätning utan ankare uppfylls av en kedja som
alltid faller.

**Lärdom som ska in i författandet, mätt i detta repo:** en grind är inte verifierad förrän den
körts i den miljö som ska grinda (`TMPDIR`-snedstrecket, ÄGARHAND-39), och en ärlig referens
räcker inte — en fix ska prövas mot en FAMILJ legitima varianter (ÄGARHAND-38).

Kan kontraktet inte göras tillräckligt starkt: `NEEDS_SPEC`, ingen builder.

---

## EVALUATOR_PLAN

```
LOW      hard gates
NORMAL   hard gates + fresh evaluator
HIGH     hard gates + bounded adversarial cross-model review
```

**När:** efter taskgrinden, aldrig före. En röd grind går aldrig vidare till evaluator.
**Vad den får:** kandidatens diff, task contract och evidence-referenser — aldrig grindens kod.
**Findings:** blir feedback (S3) och kräver en NY kandidat som verifieras från noll.
**Tak:** max antal rundor och en kostnadsbudget, båda i config.
**Bindande:** konsensus är aldrig root of trust. Evaluatorns JA attesterar aldrig ensamt; dess NEJ
kan stoppa en attestation.

---

## TEST_MATRIX

Varje slice följer husets form: baslinje utan komponent (rött av rätt skäl) → ärlig referens som
kastas → lögnstubbar med EN lögn var → hela batteriet → **körning i ägarterminalen före merge**.

| Slice | Positivt ankare | Skarpaste negativa kontroll |
|---|---|---|
| S1 h-017 | kandidat grön på båda domarna attesteras | kandidat lägger alltid-grön kopia av grind, `_lib.sh` OCH register i eget träd — attesteras ändå aldrig |
| S2 h-015 | avbruten körning återupptas, attesterat körs inte om | lease återtagen FÖRE TTL |
| S3 feedback | attempt 2 får artefakten och lyckas | artefakt som bär grindens markörsträng |
| S4 events | hundra event skrivna, skiva 1:s state byte-identiskt | event_type utanför schemat accepteras |
| S5 h-014 | fyra händelser ger fyra notiser | vanligt varv ger notis |
| S6 promotion | attestation med grind_id befordras, `ls-remote` = kandidat | attestation UTAN grind_id befordras |
| S7 resolver | D verifieras från noll och befordras | D ärver B:s attestation |
| S8 transition | task som ändrar verify/cli döms av GAMLA | nya domaren kördes före promotion |
| S9 intake | md → IR → READY, provenance spårbar | task utan verifieringskontrakt når builder |
| S10 author | challenger fäller medvetet svag grind | author och builder i samma session |
| S11 evaluator | finding → ny kandidat → full omverifiering | evaluatorns JA attesterar ensamt |
| S12 yta | de fem verben fungerar | ett sjätte verb accepteras |

---

## MIGRATION_ORDER

Målfilens ordning är A–L. Planen följer den med **en placering som måste motiveras**.

```
1.  S1  h-017 taskgrind              (A)
2.  S2  h-015 återtag                (B)
3.  S3  strukturerad feedback        (C)
4.  S4  eventkontrakt                (D)
5.  S5  h-014 notis                  (— placerad HÄR, se nedan)
6.  S6  verifierad auto-promotion    (E)
7.  S7  merge-resolution             (F)
8.  S8  trust-transition             (G)
9.  S9  Markdown-intake              (H)
10. S10 verifier author + challenger (I)
11. S11 evaluator                    (J)
12. S12 read/command-yta             (K)
13.     empirisk obevakad körning    (L)
```

**Motivering för h-014:s placering (den enda avvikelsen från byggplanens nuvarande ordning):**
byggplan §7 säger i dag *14 → 15 → 12 → 13*, alltså notis (slice 12) före återtag (slice 13).
Planen placerar notisen EFTER eventkontraktet av ett mätt skäl: h-014 kräver fyra skilda
händelser, men *brytare öppnad* och *kvot slut* är båda exit 9 från brytaren och skiljs bara av
ett prefix i en orsakssträng som inget kriterium binder. Byggd före S4 måste notisen parsa prosa;
byggd efter blir de skilda `event_type`. Byggplanens §7 bör rättas i samma ägarhandspass som
S4:s spec-rad, inte här.

**Ingen annan avvikelse från A–L.**

---

## ROLLBACK/RECOVERY

**Per slice:** varje slice är en egen gren och en egen PR. Rullas tillbaka med `git revert` på
main. Ingen slice får lämna systemet i ett läge där en påbörjad körning inte kan avslutas.

**Promotion (S6) är den enda oåterkalleliga operationen** — den flyttar authoritative main. Därför:
CAS med explicit förväntad gammal SHA, post-check mot `ls-remote`, och fail-closed vid varje
oklarhet. En felaktig promotion rullas tillbaka med en NY commit som återställer trädet, aldrig
med force push.

**Öppen brytare:** i dag finns inget reset-verb; en människa raderar tillståndsfilen (drift.md §6).
S2 ska äga det.

**Oreferade kandidater:** kandidater är commits utan gren och `git gc` når dem efter
grace-perioden. S6 löser det för den lyckade vägen (promotion skapar en ref); för fallna kandidater
kvarstår problemet och registreras nedan.

---

## RISKS

1. **Auto-promotion tar bort människan ur merge-gaten.** Det är målbildens uttryckliga beslut, men
   det är också den enda ändring i planen som inte går att ångra tyst. S6 får inte byggas före S1
   — en attestation utan taskgrind-verdikt är inte promotion-eligible, och utan S1 finns inget
   verdikt alls.
2. **Registret växer från 2 till ~18+ poster**, och de nya är just de filer ägarhand skärper
   oftast. Varje skärpning kräver en SHA-uppdatering. Utan en rutin blir det en underhållsbörda
   som ingen äger och som fäller körningar vid fel tillfälle.
3. **Trust-transition är svårast att prova.** Ett prov måste mäta att den NYA domaren aldrig kördes
   före promotion — en frånvaromätning, och husets erfarenhet är att frånvaromätningar utan
   positivt ankare är de som fuskas förbi.
4. **Evaluatorns kostnad är obunden om taket sätts fel.** En session mättes ta 10–20 minuter; en
   adversariell runda kan mångdubbla det.
5. **Verkstadsgolvets kommandoyta är den största nya angreppsytan.** Fem verb och typade payloads
   är planens svar, men en projection som råkar bli authority är ett tyst fel.
6. **Planen är stor.** Tolv slices, varav tio nya komponenter. Regel 9 gäller varje enskild: den
   som bygger ska fråga om en befintlig komponent kan äga ansvaret innan en ny skapas.
7. **Promotionens sprängradie är hela repot, inte bara kontrollplanet.** `origin/main` i
   `nortropic-system` bär också `agents/`, `workflows/` och `skills/` — alltså kundfabriken.
   Auto-promotion flyttar den mainen. Det som håller kundflödet utanför är att `controller/policy/cli`
   avvisar varje diff utanför taskens `allowed_write` INNAN kandidaten ens föreslås, och att §A
   prövas först av alla. **Följd: policyn är en promotionsförutsättning, inte bara en
   kandidatkontroll.** Försvagas policyn försvagas kundflödets skydd i samma andetag, och just den
   filen ligger i den trust-critical ytan (G20/S8).
8. **G20 gäller redan i dag, inte bara efter S6.** Så snart taskgrinden kopplas in (S1) kör en
   trust-critical task sin dom med sina egna komponenter. Ordningsregeln i G20 måste därför byggas
   in i S1:s kriterium — den kan inte skjutas till S8.

---

## OVERIFIERAT

- **Branch protection på `origin/main`.** Sessionen når inte nätet (allowlist `api.anthropic.com`)
  och `gh` kunde inte läsa sin konfiguration. Kräver main PR eller status checks kommer S6 att
  falla. **Måste mätas före S6 byggs.**
- **Credential för promotion.** Vilken identitet som pushar och var dess credential bor är en
  obesvarad ägarfråga. `git push` från en session faller på sandboxens nätspärr; controllern kör
  utanför sandboxen men identitetsfrågan är inte avgjord.
- **Kvotsignalens kanal.** Landar den verkliga kvotsignalen på den stdout h-009 kastar vid nonzero
  är `kvot.monster` strukturellt dött. Öppen post sedan ÄGARHAND-33/35.
- **Lease-TTL i praktiken.** Att en andra controller faktiskt tar över efter 180 s är inte klockat,
  bara härlett ur att varv tar 10–20 min.
- **h-009:s kända gränser** (setsid-flykt, obegränsad stdout) står OVERIFIERAT sedan tidigare.
- **`_lib.sh` är inte hash-bunden.** Bedömt som driftlarm, inte hot — samma hand skriver register
  och bibliotek. Inte mätt som säkerhetsegenskap.
- **Föräldralösa kandidatcommits** från fallna försök: en per fallet försök, ingen ref når dem.
  Bryter ingen invariant, men `git count-objects -v` växer och ingen städar.

---

## PLANGRANSKNING

Granskningen enligt uppdragets §15 kördes mot faktisk kod vid `PLAN_BASE_SHA` innan planen
commit:ades. Den ändrade planen på sex punkter. Kommandona kördes i denna session.

| # | §15-punkt | Fynd | Åtgärd i planen |
|---|---|---|---|
| 1 | falsifiera mot kod | Planen skrev *"sjutton bash-grindar"*. `verify/bin/` bär sexton `*-exit` plus `_lib.sh`. | Rättat i CURRENT_STATE. |
| 2 | self-certification | **`kmd_run` kör grindfilen ur repot men med `cwd=mal`, och husets grindar adresserar komponenter RELATIVT** (`krav_komponent "controller/verify/cli"`, `_lib.sh` rad 7–14). En taskgrind startar alltså kandidatens komponenter. För en trust-critical task dömer den nya domaren sin egen födelse redan vid grindkörningen — före den promotion S8 skulle vakta. | Nytt gap **G20** + ordningsregel; S1:s kriterium och negativa kontroller utvidgade; RISKS 8. |
| 3 | dubbla sanningar | S3:s feedbackartefakt och S4:s `feedback.*`-event kunde båda läsas som källa för vad buildern får veta. | Avgränsning skriven: artefakten är authority, eventet bär bara en referens. |
| 4 | crash gaps | PROMOTION_PLAN krävde inte en hållen lease. Med TTL 180 s utan heartbeat kan två controllers nå promotion samtidigt. | FÖRUTSÄTTNING och negativ kontroll tillagda i S6. |
| 5 | kundflödespåverkan | Promotion flyttar den main som också bär `agents/`, `workflows/`, `skills/`. Planen namngav inte att policyn är det som håller kundflödet utanför. | RISKS 7. |
| 6 | testbart exit criterion | S2 och S5–S12 hade negativa kontroller men **inget uttalat EXIT CRITERION** — uppdragets §5 kräver det per föreslagen slice. | Kriterium skrivet för S2, S5, S6, S7, S8, S9, S10, S11, S12. |

**Motbevisat under granskningen — påståenden som HÖLL:** noll träffar på `push`/`remote`/`origin`
i samtliga tretton `controller/*/cli` · `RUNNERS = {"node": "node"}` · `REGISTER` är en fast sökväg ·
`giltigt_event` kräver icke-tomma `task` och `status` · `LEASE_TTL = "180"` · `exit_test` förekommer
i kedjan endast som en KOMMENTAR i `controller/envelope/cli` som förklarar utelämnandet · noll
förekomster av `grind_id` i loop, verify och attest · `kmd_write` bygger en fast dict med fyra fält ·
`.gitignore` vitlistar `/controller/` så nya underkataloger spåras utan ändring.

**Rättelse av ett tidigare planpåstående:** `_lib.sh` beskrevs som ett hål. Mätningen visar att
grindarna sourcar den via `$(dirname "$0")` där `$0` är den absoluta sökväg `kmd_run` startar — den
laddas alltså ur repot och **en kandidat når den inte**. Kvar står bara att den inte är hash-bunden
mot ägarhand. Formuleringen i TRUST_MODEL är skärpt därefter.
