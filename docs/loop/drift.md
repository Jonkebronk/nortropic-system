# Att köra loopen

**Skriven 2026-08-09, UR den första verkliga körningen** — inte före den. Varje siffra
och varje utfall nedan är mätt på `premiar-1`, som körde `p-001` och `p-002` mot main
`3e781fa` och attesterade båda. En manual skriven i förväg hade varit en gissning.

Detta är driftdokumentet. Byggandet styrs av [byggplan-v3.md](byggplan-v3.md) och
[regler.md](regler.md); de rör inte den här filen.

---

## 1. Vad en körning är

`controller/loop/cli run <config.json>` går igenom backloggen task för task. Per task:
lease → claim → **försök** (workspace på oförändrad base → kuvert → brytare → utförare →
session) → parse → policy → verifierare → attestation. Faller ett försök görs det om
inuti claimet tills brytarens budget tar slut.

**Kedjan dömer tre saker:** att rapporten är välformad, att diffen håller sig inom
`allowed_write` och budgetarna, och att configens verifierare är grön mot kandidatträdet.
Den dömer **inte** om tasken blev löst — taskens eget `exit_test` körs aldrig av kedjan.
En attestation betyder *"diffen var laglig och de globala invarianterna höll"*. Den
per-task-domen fäller du, med taskens grind, innan du mergar.

## 2. Före körningen

Configen ligger utanför repot så att körningen aldrig smutsar arbetskopian. Mall och
fältförklaringar finns i [`config/README.md`](../../config/README.md).

```
mkdir -p ~/.nortropic/kor
cp config/loop-config.exempel.json ~/.nortropic/kor/min-korning.json
```

Fyll i `base_sha` (`git rev-parse HEAD`) och ett unikt `run_id`. Initiera state en gång
per körning — annars faller taskval före första varvet med
`state: … kunde inte rekonstrueras`:

```
./controller/state/cli init ~/.nortropic/kor/state
```

**`budget` måste vara strikt större än `troskel`.** Brytaren prövar budget före öppen, så
ett för snålt tak maskerar en öppen brytare permanent.

## 3. Körningen

Kör **från reporoten** — `spec` och `worker_cmd` pekar repo-relativt:

```
./controller/loop/cli run ~/.nortropic/kor/min-korning.json
```

**Terminalen är tyst medan en session arbetar.** Loopen skriver ingenting förrän ett varv
är avgjort. Mätt på premiären: tio till tjugo minuter per task, och två tasks tog ungefär
en timme. Skillnaden mellan *arbetar* och *hängd* syns inte i terminalen.

Följ den utifrån, från ett annat fönster:

```
ls ~/.nortropic/kor/workspaces/                       # vilket försök som pågår
git -C ~/.nortropic/kor/workspaces/<attempt> status --porcelain   # vad sessionen skrivit
cat ~/.nortropic/kor/state/events.jsonl               # vilka tasks som claimats
```

Attempt-katalogen heter `<run_id>-<task>-<försöksnummer>`, så `premiar-1-p-001-2` är
andra försöket på `p-001`.

## 4. Läs utfallet

```
varv 1 p-001: attesterad c721599bf09342a1d4141869be2ed911688492d3
varv 2 p-002: attesterad 95c33a34bd502575c099610c1cb06a8b04bbf98a
drain klar: 2 varv, 2 attesterade, base 95c33a34bd502575c099610c1cb06a8b04bbf98a
```

| Exitkod | Betyder | Vad du gör |
|---|---|---|
| **0** | Drain slutförd — backloggen är slut eller allt behörigt är gjort | Granska kandidaterna, för dem till main |
| **1** | Fel: trasig config, upptagen lease, brytarens anropsfel, städning som inte gick | Läs orsaken på stderr och åtgärda; ingen körning har skett |
| **3** | Rent stopp: brytaren öppnade och drainet avslutades före nästa claim | Se §6 |

Ett avbrutet varv skriver `varv N <task>: avbrutet i <steg> — <systerns klass ordagrant>`.
Steget namnger vilket led som brast: `workspace`, `kuvert`, `forsok`, `parse`, `policy`,
`verifierare`, `attest`.

## 5. Granska och föra till main

**Kandidaterna är commits utan gren.** Ingen ref pekar på dem; de nås bara via attesta-
tionsbutiken. Läs SHA:t där:

```
./controller/attest/cli ~/.nortropic/kor/attest read p-001
```

Kör **taskens egen grind** mot kandidatträdet — det är den dom kedjan inte kan fälla:

```
git worktree add --detach /tmp/kand <candidate_sha>
( cd /tmp/kand && ./verify/bin/<taskens exit_test> )
git worktree remove /tmp/kand
```

Parenteserna är avsiktliga: står du kvar i `/tmp/kand` när du river den faller `remove`
med *"Unable to read current working directory"* och lämnar en registrering efter sig
(mätt 2026-08-09). Blev det ändå fel: `git worktree prune` från reporoten.

Kedjande base gör att den SISTA attesterade kandidaten innehåller alla föregående. Är den
en ättling till main räcker en gren och en PR:

```
git branch kandidat-<run_id> <sista candidate_sha>
git push -u origin kandidat-<run_id>
gh pr create --base main --head kandidat-<run_id> --title "..." --body "..."
```

**Auto-merge är avstängt beslut.** Systemet producerar attesterade kandidater; människan
för dem till main.

> **Oreferade commits försvinner.** Ingen gren pekar på kandidaterna, så `git gc` kan
> städa bort dem när grace-perioden gått ut. Skapa grenen samma dag som körningen, eller
> acceptera att arbetet måste göras om.

## 6. När brytaren öppnat (exit 3)

Brytaren har ett tillstånd per task i `<brytare_rot>/<task-id>/tillstand.json`:

```json
{"oppen": false, "orsak": null, "forbrukat": 1, "fingerprints": {}}
```

`oppen: true` betyder att den tasken stoppar varje ny körning som når den. **Det finns
inget reset-verb** — h-015 äger återtaget och är inte byggd. Tills dess: läs orsaken,
åtgärda det som brast, och ta bort tillståndsfilen för just den tasken.

`forbrukat` är attempt-budgeten. Har den nått taket startas inget kommando för tasken,
och den förblir claimed resten av körningen.

## 7. Efter körningen — kontrollera att inget lämnades

```
git status --porcelain          # ska vara tom
git worktree list               # ska bara visa huvudträdet
ls ~/.nortropic/kor/workspaces/ # ska vara tom
ls ~/.nortropic/kor/lease/      # ska vara tom
```

Premiären lämnade allt fyra rent. Ligger ett workspace kvar rivs det med
`./controller/workspace/cli ~/.nortropic/kor/workspaces destroy <attempt>` — **destroy före
`rm -rf`**, annars blir föräldralösa poster kvar i `.git/worktrees` som fäller nästa
körnings `create`.

## 8. Kända gränser, mätta

**Leasens TTL är 180 s utan heartbeat.** Ett varv tog tio till tjugo minuter i premiären,
alltså långt över TTL:n. En andra controller kan i teorin ta över resursen mitt i en
levande körning. Kör aldrig två körningar mot samma `lease_dir` samtidigt.

**Kvoten.** En session per försök, tio till tjugo minuter var. Smoke-momentet mätte 8–20
sekunder — det var en trivial enfilsskrivning och säger ingenting om verkligt arbete.
Räkna om din kvotbudget efter den här siffran, inte den gamla.

**Timeouten.** Mallen sätter 900 s. Premiärens sessioner låg på tio till tjugo minuter, så
marginalen är tunnare än den ser ut. Höj den hellre än att låta ett halvfärdigt försök dö.

**Ingen notis.** `controller/notis/cli` (h-014) är obyggd. Tystnad efter en körning betyder
inte att allt gick bra — den är exakt lika tyst när något faller.

**Ingen livssignal.** Kedjan skriver ingenting medan en session arbetar. Använd §3:s
utifrånkommandon.

**Föräldralösa kandidatcommits.** Varje fallet försök lämnar en commit i objektdatabasen
som ingen ref når. De bryter ingenting, men `git count-objects -v` växer.


## G20 runtimegräns för buildern

Från ägarbeslut 2026-08-10 är builderns runtimegräns en del av h-017:s trustmodell. Controllern ska installera gränsen före builderstart.

- kandidatworkspacet får vara skrivbart,
- neutral scratch som controllern uttryckligen tilldelar får vara skrivbar,
- reporotens live control plane får inte vara skrivbar för buildern,
- controllerns pre-task trust-root får inte vara skrivbar för buildern,
- samma skrivgräns ska gälla barn även efter ny process-session.

Claude Codes managed sandbox ligger kvar som defense-in-depth men är inte Nortropics root-of-trust. controller/launch/cli är kommandoagnostisk, därför måste den controller-ägda gränsen gälla oberoende av worker-kommando.

Ägarterminalens fristående Seatbelt-probe gav PARENT_INSIDE=PASS, CHILD_INSIDE=PASS, CHILD_OUTSIDE_DENIED=PASS, OUTSIDE_SENTINEL_ABSENT=YES och PROBE_EXIT=0.

K18R i verify/bin/h-017-exit binder samma runtimeegenskap genom Nortropics launchväg. Baslinjen mot den återställda h-017-WIP:n före implementation var avsiktligt röd: 23 PASS, 1 FAIL med `trust=WROTE/1 repo=WROTE/1`; K19 och K20 förblev gröna.

Gränsen är nu implementerad i `controller/launch/cli` med absoluta `/usr/bin/sandbox-exec` och en parameteriserad Seatbelt-profil. Launch provar att profilen går att installera **innan** buildern startas. Saknat binär, ogiltig profil, tom/relativ trust-root eller en värd som vägrar Seatbelt ger `launch_failed` och ingen rå fallback. Profilen använder `allow default` så workerkommandot förblir kommandoagnostiskt och workspace/neutral scratch förblir skrivbara; den nekar samtidigt filskrivning under controllerns run-root och live-repot. Workspacekatalogens egen entry och `.git`-pekare är skrivskyddade, medan produktfilerna under workspacet är skrivbara.

Git har en uppmätt, smal exception därför att h-016:s motfall måste kunna göra en verklig detached självcommit innan kedjan fäller den: common object store och det **aktuella** worktreets adminyta (bland annat HEAD/index/COMMIT_EDITMSG/logg) är skrivbara. Common config, hooks, refs, info/alternates, andra worktrees samt workspacets `.git`-pekare är fortsatt nekade. Det här ska inte beskrivas som att hela `.git` är skrivskyddad; exceptionen är den minsta yta h-016:s legitima provform mekaniskt behöver.

Loopen märker hela sin privata temp-root — snapshot, kuvert, rapporter och verifierarens senare kandidatvyer — som `NORTROPIC_TRUST_ROOT`; verifierarprocessernas `TMPDIR` pekas till samma rot. Därmed kan ett kvarlevande builderbarn läsa sitt kuvert men inte förskapa eller byta controllerfiler eller domvyer. Seatbelt ärvs genom fork/exec och efter ny process-session; `start_new_session`, timeout och processgruppsdödning ligger kvar i launch.

Slutmätning i Seatbelt-tillåten hostmiljö utanför Codex nästlade sandbox: h-009 **11/0**, h-002 **6/0**, h-003 **8/0**, h-011 **16/0**, h-016 **25/0**, h-017 **24/0** inklusive K18R/K19/K20 och invarianterna **8/0**. Launchs fallsamling gav **53 rätt, 0 fel**. Separata prober visade: om Seatbelt inte kan installeras blir utfallet exit 3 och workermarkören saknas · explicit tom trust-root vägras före worker · kandidatprodukt är skrivbar samtidigt som workspace-`.git` och live hook nekas. Körs launch inuti en redan installerad värdsandbox som förbjuder nästlad Seatbelt ska den alltså falla stängt; ownergrindarna måste köras i den ägarterminalmiljö där macOS-gränsen får installeras.

<!-- CODEX-AUTOPILOT-V2-DRIFT -->
## Codex Build Autopilot v2

Start/diagnostik:

```bash
nortropic-codex-autopilot doctor
nortropic-codex-autopilot run
```

Normal obemannad körning använder Codex `--ask-for-approval never --sandbox danger-full-access`. Behörighetsläget är inte trust authority; frozen gates, immutable candidate SHA, independent review och mechanical final gate är transitionsvillkoren.

Evidence/checkpoint finns under Git common-dir `.git/nortropic-codex-autopilot/`. Den katalogen är inte backlog eller verdict store. Efter avbrott re-deriveras state från Git/worktrees/PR/gates. Ingen force/amend/reset/rebase-remediation används.

<!-- CODEX-AUTOPILOT-V3-DRIFT -->
## Codex build-autopilot v3 — hela kontrollplansroadmapen

V3 använder exakt ägarlåst roadmap på `0b3212c991d4227c8df2656465ae2c0252dda39e` och fortsätter efter h-003/h-004 genom S2, S4–S13 och den empiriska slutkörningen. `OWNER_DECISION_REQUIRED` från en roll är en intern signal till `$nortropic-architect`; den stannar inte supervisor-processen i sig.

Observera utan att styra:

```bash
tail -F "$HOME/Library/Logs/Nortropic/codex-autopilot-v2.log"
"$HOME/.local/bin/nortropic-codex-autopilot" status
"$HOME/.local/bin/nortropic-codex-autopilot" roadmap
```

`status` visar senaste journalhändelsen. `roadmap` mäter aktuell `origin/main` och visar S2/S4–S13 som `UNFROZEN`, `RED`, `GREEN` eller `UNJUDGEABLE`; empirisk closeout L syns som journalhändelserna `EMPIRICAL_UNATTENDED_RUN_PASS` / `FULL_ROADMAP_COMPLETE`. Utsagan är observationsyta och aldrig scheduler-authority.

Supervisorens lokala label och logg behåller namnet `v2` vid cutover för att återanvända den redan bevisade LaunchAgent-gränsen. Versionen avgörs av `origin/main:scripts/nortropic-codex-autopilot.py` och `doctor` ska efter v3 svara `FULL_ROADMAP=YES`.

Om v3 når en verklig `HUMAN_AUTHORITY_HARD_STOP` tas supervisor-enable-markören bort och macOS-notisen skickas. Efter att den externa/human-only förutsättningen är uppfylld återupptas samma mekaniska state utan ny installer med:

```bash
"$HOME/.local/bin/nortropic-codex-autopilot" resume
```

S7 har en uttrycklig extern prerequisite från den frozen planen: GitHub App **Nortropic Promoter**, installerad endast för `Nortropic/nortropic-system`, Metadata:Read + Contents:Read&Write, och endast PR-requirement-bypass. V3 får bygga fram till den gränsen men får inte fabricera eller ersätta appen med användarens bredare `gh`-credential.


### Liveöversikt

```bash
~/.local/bin/nortropic-codex-autopilot watch
```

Kommandot läser endast journal, supervisor-markörer och worktree-lista. Det startar inga gates och
muterar inget repo. För full roadmap/gate-status:

```bash
~/.local/bin/nortropic-codex-autopilot roadmap
```

Stage L ägs av den frysta programnivå-gaten `verify/bin/autonomous-loop-exit`; independent
empirical-runner är en falsifierande andra blick, aldrig ersättning för gate PASS.

## 2026-08-11 — Harness Substitution Amendment v1

- Product goal remains: autonomous Nortropic website factory.
- Kernel target: provider-neutral Trust Kernel; agent-provider workflow is not trust authority.
- Original frozen roadmap SHA remains effect/negative-control authority: `0b3212c991d4227c8df2656465ae2c0252dda39e`.
- New owner implementation-shape authority: `docs/loop/harness-substitution-contract-v1.md`.
- Migration floor after S3: SUB-1/h-027 → SUB-2/h-028 → SUB-3/h-029 → SUB-4/h-030.
- S2/S4/S5 must not freeze without h-030 dependency after this amendment.
- Pre-amendment quota-aborted h-003/h-004 worktree is preserved local evidence, not authority, not a resume candidate.
- No frozen gate, constitution/rulebook boundary, G20, candidate identity, attestation/fencing, promotion identity or no-force rule is weakened by this amendment.

## 2026-08-13 — Python interpreter-authority prerequisite r3

This is owner-authorized prerequisite-gate remediation before H-034, not H-034/H-033/H-032/H-031
production or runtime work and not a task in `specs/tasks.spec.json`. R2
`10844933033015fc56493bebeae24a29fa657f0e` was independently reviewed and rejected before
freeze: R-004 proved its candidate audit followed an active repository-local `refs/replace`
mapping and bound substituted authority/gate bytes to the original SHA; R-005 proved its
review-relative documentation became false when review occurred. R2 was never frozen or
published. R2 and all earlier rejected candidates remain forensic evidence only and are not
authority.

R3 retains the owner-audited authority JSON byte-for-byte and keeps the sound R2 controls:
absolute `/usr/bin/python3 -I -S` judging; one duplicate-aware exact-type authority object;
wrong-type, duplicate, missing and extra rejection; semantic reorder/whitespace/escape
acceptance; absolute non-symlink regular executable identity; exact Python 3.12.13 and digest;
fixed target invocation; stale-path and invalid-object controls; direct-child topology; exact
four-path scope; and equality between executing gate bytes and candidate gate bytes. Candidate
Git commands use absolute `/usr/bin/git` with an isolated caller environment and the explicit
no-replacement object view. The candidate's direct parent is read from its raw actual commit
object rather than replacement-/graft-aware ancestry traversal. Thus repository replacement
state may change default Git presentation but cannot supply the bytes or parent used by a
successful R3 audit of the original 40-hex SHA.

The gate remains a judge, not runtime authority. Future H-034 must implement verified source →
private protected snapshot → final rehash → protected-path execution. R3 makes no claim of
arbitrary same-UID race-free source-path execution. The legitimate owner prerequisite is expected
GREEN, so a generic RED baseline is not manufactured. Independent review is a mandatory
precondition for R3 publication; this candidate records that rule and contains no assertion that
R3 received a passing review verdict.

On 2026-08-13 the owner removed interactive approval only for the bounded remaining-bootstrap chain
while retaining every mechanical gate, identity, reviewer, empirical, scope and fail-closed
precondition. H-035 is freshly re-materialized from authoritative main `15693f9…`; old H-035
candidates are design evidence only. The migration preserves current Python-interpreter authority,
all sound R12 owner/task/gate/Git-object controls and H-034 absence. It additionally freezes guarded
normal merge-commit publication: immediate base/candidate/remote/PR/file relock, `--merge` only, and
post-merge proof of exact two-parent order plus candidate-identical tree. Production remains RED.

The independent gate review of the first fresh candidate found that publication was still inferred
from source tokens and disconnected Git-shape fixtures. The frozen gate now calls the real
production `publish()` against disposable repositories and a hermetic GitHub command boundary.
It observes the non-force branch push, complete repository/PR/base/head/file relock, guarded
`gh pr merge --merge`, GitHub merged state, returned merge identity, fetched `origin/main`, ordered
parents and candidate-identical tree as one operational chain. Hostile repository/PR metadata,
main drift, wrong remote head or files, unmerged state, returned-SHA mismatch, malformed parent
topology and tree mismatch all reject. A gate-local conforming witness proves the rig satisfiable;
the dead-token/no-op publisher rejected by the same effect checks proves source text is insufficient.

R2 independent review then showed that its judge performed the decisive postmerge Git inspection,
its fake accepted a nonexistent GitHub JSON field, and its publication request omitted frozen
spec/gate/review identities. R3 moves acceptance to the publisher's observed process effects: the
actual module subprocess boundary records both helper-mediated and direct invocations; only real
supported GitHub fields are modeled; the request carries candidate-bound task/spec/gate plus
independent-review identities; and immediate premerge reads must verify them. After GitHub reports
the merge, the publisher itself must fetch main, compare the mergeCommit SHA, inspect exact ordered
parents, and compare candidate/merge trees. Dedicated omission and direct-subprocess mutants reject.

R3 independent review found that command presence still did not prove response-dependent behavior:
a publisher could invoke all postmerge probes, ignore every output and let judge corroboration mask
the omission. R4 records `publisher_rejected` separately from actual graph correctness. It injects
hostile main/parent/candidate-tree/merge-tree responses while leaving the real merge valid, and also
runs malformed returned-SHA/parent/tree graphs through the real publisher. Each requires the
publisher itself to raise. A complete-trace ignore-output mutant therefore fails the frozen
production negatives rather than being rescued by judge-side Git inspection.

R4 independent review then demonstrated that replacing the module's `subprocess` name after import
missed callable aliases captured during module execution. R5 installs wrappers before `runpy`
executes the subject and restores host functions afterward; captured `run`, `Popen`, `check_output`,
`check_call` and `os.system` aliases retain the audited boundary. Each form is tested with an
absolute unexpected executable that is denied without execution, and separately with legitimate
absolute Git that passes. The prior identity, response-validation and graph controls remain intact.

R5 independent review found that executable classification still trusted the requested basename.
R6 captures real Git/GitHub canonical paths and SHA-256 identities before subject execution. Bare
names use only the captured host PATH identity; harness symlinks pass only by resolving to an exact
audited target. Absolute same-name fakes and PATH shadows are denied before marker execution, as is
a byte-identical Git copy at another canonical path. Both exact system Git identities available on
the owner host and the hermetic Git/GitHub reference symlinks remain positive.
