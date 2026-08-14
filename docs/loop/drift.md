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

The fresh H-035 production candidate from authoritative main `b3137f3` closes the published RED
contract at 303 PASS and 0 FAIL with `MATERIAL_PROPERTIES_JUDGE_ONLY=NONE`. It re-materializes the
R12 owner workflow without importing old history, preserves frozen Python interpreter-authority
bytes, and adds the effect-bound guarded publisher. Focused historical taskval, policy and H-007
checks pass. The owner-terminal V6 subgate is `ODÖMBART` in the builder sandbox because `ps` is
denied; no product failure is inferred from that environment limitation. No push or merge occurred.

After H-035 publication at authoritative main `c883720`, H-034 is freshly materialized as the next
owner-authority task. Current owner sources and the exact registry agree on C, arm64 macOS, an exact
final signed Mach-O, zero third-party runtime dependencies, Apple system runtime/dyld only, a fixed
finite verification plan, and no Python runtime authority. The only owner surface is the four
registry-reserved H034 families; H-033 remains intentionally absent and will consume H-034 later, so
H-034 depends only on final H-035. The frozen gate retains the valid historical closed-argv,
codesign `-dvvv` CDHash, LC_UUID/loadability, deterministic unsigned build, stable semantic/Mach-O,
same-descriptor, fresh metamorphic tri-state and bounded process-group requirements without adopting
stale history. It additionally mutates each receipt schema and recomputes the dependent evidence
digest, isolating strict receipt parsing from digest mismatch. Production remains RED on exactly the
four missing owner artifacts.

The independent review of that first fresh H-034 candidate found three gate defects rather than an
authority conflict. The additive remediation makes the exact manifest schema satisfiable and binds
`language=C`, the final artifact/recipe/source digests and every observed Mach-O field consistently.
It executes the closed production recipe in two disposable trees, proves deterministic unsigned
output, signs and compares stable native identities, and tests inherited same-open-description,
nonregular and bounded-input behavior. Fresh black-box evidence/receipt/allowlist families now isolate
every schema and cross-binding defect; a real arm64 C consumer that is receipt-focused, uses substring
evidence and ignores the allowlist is caught. Production remains absent and RED only on its four paths.

R3 closes the remaining semantic input-space gap with isolated black-box rows. An unchanged valid
receipt paired with a different valid-hex evidence digest now rejects as a relation failure. Exact
schema versions and observer authority, empty/invalid allowlists, receipt/allowlist size and trailing
data, and missing/duplicate/malformed forms of every required descriptor/binding argument are sent
through the production kernel. Receipt-dependent evidence is recomputed only where needed to isolate
the intended parser, exact-value or finite-bound defect. The valid positive and real permissive arm64
C mutant controls remain intact; production remains absent and RED only on its four owner paths.

After the first native implementation review exposed C-prefix acceptance of a decoded escaped NUL,
the contract was freshly extended from published main rather than from an unpublished test-author
branch. Black-box rows now inject escaped NUL, embedded control and lone-surrogate sequences into
every material evidence, receipt and allowlist string while preserving dependent receipt digests.
Exact decoded byte length plus bytes is required; a legitimate Unicode probe/path/marker family stays
positive. The vulnerable native artifact is RED and the additive builder fix is GREEN in disposable
composition; neither production lineage is copied into this contract-only candidate.

Final implementation review then showed that the per-document U+0001 rows could reject only through
a cross-document mismatch while a consistently bound decoded control still reached VERIFIED. The
fresh additive gate now runs the complete U+0000..U+001F matrix over probe identity, path and effect
marker, updates every related caller/document binding and recomputes the receipt digest. U+0000 probe
identity stays in parser-only document controls because an operating-system argv cannot carry NUL;
its path and marker rows remain coordinated. The existing legitimate Unicode positive is unchanged.

After final H-034 publication at authoritative main `9436387`, H-033 is freshly materialized from
that main as an ordinary authenticated-runner task depending exactly on H-034. Current H-034 is the
architecture authority: H-033 owns protected origin and safe opening, supplies the exact three
already-opened evidence/observer-receipt/allowlist descriptors, and delegates semantic judgment to
the exact frozen native kernel with candidate/spec/gate/probe/request/result bindings. The new
contract does not import the historical launchd service shape. It freezes effects and identities:
OS-resolved `_nortropic_provenance`, an independent root-owned observer, protected canonical roots,
fresh caller-unselectable request IDs, no-follow same-opened-object traversal, and exact H-034
handoff. The disposable gate surface exists only to exercise path substitutions and a deterministic
rename race; it cannot select authority during the normal verify operation.

H-034's former phase assertion that H-033 was absent is monotonically replaced by exact-one H-033,
dependency `h-034`, and canonical `verify/bin/h-033-exit` lifecycle checks. Absence, duplication,
wrong dependency and wrong gate are explicit adversarial controls. All prior H-034 semantic,
artifact, rebuild and identity controls remain unchanged; the materialized phase runs H-034 green.
H-033 itself is RED only because `controller/provenance/cli` is absent. No provenance production
implementation or external provisioning is created by this contract candidate.

The same phase reconciliation is applied additively to H-035's lifecycle-only assertions. Its stale
H-034-task/byte absence checks become exact published H-034 plus exact materialized H-033 identity,
dependency and canonical-gate checks, with absence/duplicate/wrong-dependency/wrong-gate mutants for
both downstream tasks and an exact four-file H-034 artifact set. H-035's owner routing, publication,
identity, atomicity and provider-observation mechanism controls are otherwise byte-for-byte unchanged.

The H-033 builder candidate adds one closed provenance CLI. Its fixture-only gate operation performs
protected no-follow opens, stable bounded reads and exact descriptor handoff to the repository H-034
kernel; normal verification never accepts a caller-selected authority root or kernel. Production
request creation is delegated only to fixed protected OS helpers and fails closed when the canonical
producer identity or authority installation is unavailable. On an unprovisioned host this boundary is
ODÖMBART by the frozen contract, while all disposable product controls remain judgeable.

Independent review of the first H-033 contract found that live owner acceptance required an evidence
leaf owned by merely any non-requester UID. The additive remediation applies one shared live-`lstat`
predicate to judge controls and canonical owner acceptance: evidence UID must equal the exact
OS-resolved non-root `_nortropic_provenance` UID, receipt UID must equal root, the two inodes and UIDs
must differ, and neither leaf may be group/other writable or a symlink. A live separated-ownership
positive and root-writes-both, requester-owned and symlink negatives run before the component RED.

H-033's normal H-034 execution boundary additionally requires an externally provisioned canonical
`provenance/bin/h034-kernel` hard link. Every fixed parent and the leaf are opened no-follow and must
be root-owned and non-group/other-writable; the leaf must be executable and the same device/inode as
the repository H-034 kernel whose bytes are bound to the frozen Git-object manifest and artifact
digest. Opened parent, repository and protected-link identities remain stable through execution, and
the protected pathname must still name the same inode afterward. The disposable `gate-verify` path
continues to exercise the repository kernel without claiming normal authority. No repository code
provisions this root-owned link; its absence or mismatch is an external-owner ODÖMBART boundary.

Single consumption is delegated to the fixed root-owned protected
`provenance/bin/request-consumer` authority before the normal H-034 handoff. The exact operation is
`consume` with only the request ID and frozen task/candidate/spec/gate/probe/result bindings; no
command, path or authority selector is forwarded. Exit 0 is the one atomic authorization, exit 1 is
denial or replay, and service/identity/timeout/cleanup failure is ODÖMBART. The observer-owned
external authority validates the token against its request state and never exposes its state store to
repository code. Consumption is deliberately not rolled back after any later kernel failure, so a
failed first handoff cannot revive the request. Fixture-only differential verification does not
consume external owner state.

The previously external H-033 authority is now versioned under its frozen production surface without
claiming that repository ownership supplies root authority. A root-run fixed-destination installer
copies only reviewed digest-bound native service/probe bytes and the exact H-034 Git object into
`/Library/Application Support/Nortropic/provenance`; it requires a pre-existing, distinct
`_nortropic_provenance` OS account and creates root/protected bin, probe, receipt and one-time state
directories plus a producer-owned evidence directory. The installed service has only three basename
interfaces. Producer generates the request ID and executes one fixed digest-bound probe after UID/GID
drop; observer independently verifies the protected allowlist and exact effect before writing its
receipt/pending token; consumer performs the irreversible pending-to-used atomic rename. Repository
runtime code cannot select an install root, service, probe, result, destination or command and never
copies an executable at handoff. The installed H-034 kernel and service bytes must stay identical to
their exact candidate Git objects across execution. On this unprovisioned owner host, normal H-033
remains ODÖMBART until the external root ceremony is deliberately executed; no sudo or `/Library`
mutation occurred during this builder slice.

Independent review found a native failure-path hazard that the successful-probe tests could not
exercise: after `fork()` returned `-1`, the old loop could interpret that value as the wildcard
`waitpid`/`kill` target. With another child remaining live, the timeout path could reach
`kill(-1, SIGKILL)`. H-033 now treats every nonpositive fork result as a terminal closed error before
any wait/signal operation. The only signal helper requires a positive PID; waits use monotonic elapsed
time without deadline addition, retry `EINTR`, and never equate an error return with the requested
child. A deterministic linked syscall shim reproduces the exact failed-fork/live-wildcard condition
and proves immediate exit, no `kill(-1)`/`kill(0)`, and no evidence write. The same audit bounds the
producer writer child, verifies the complete post-setuid identity, checks exec-environment setup, and
makes installer subprocess/write failures explicit. Signed native bytes and their candidate bindings
were regenerated; the external root ceremony remains unexecuted.

The first provisioned owner-environment run exposed a Darwin group-list failure before any producer
evidence was created. A compile-time-only diagnostic build of the same service path proved that
setgroups/GID/UID transitions all succeeded. A second numeric diagnostic then proved Darwin returned
the eight Directory Services memberships of the resolved `_nortropic_provenance` account after UID
transition: `309,12,61,701,703,702,100,704`, exactly matching the OS account record. Both the zero-entry
and one-entry candidate postconditions were therefore invalid machine-local assumptions. The drop now
requires successful clearing before GID-before-UID transition and exact real/effective dedicated UID/GID;
it does not reinterpret the OS-resolved account's membership list. A linked Darwin-semantics control
reproduces the eight-entry result, while independent mutants prove setgroups failure and wrong IDs still
reject before evidence. Diagnostic logging is absent from production, and live authority is unchanged.

## 2026-08-14 — Fresh H-032 exact provider identity after H-033

Authoritative main `5baee0e` closes H-033 and is the only base for the new H-032 contract. The old
`1cf2caf..878445b` H-032 line remains forensic evidence only. Its useful physical findings survive:
macOS has no portable descriptor-exec primitive for this Python boundary, so one safely opened source
object is copied to a private snapshot, the snapshot is finally rehashed, and absolute-path execution
is protected by the already frozen controller G20/Seatbelt trust root. The impossible claim that a
pathname alone is race-free against every same-UID process is not revived.

The measured provider authority is the actual OpenAI Codex vendor Mach-O, not `/opt/homebrew/bin/codex`
or its JavaScript/Node delegation layer. Its current absolute path and SHA-256 are frozen in
`config/codex-provider-identity.json`; SHA-256 is the exact-byte authority, while the observed Developer
ID signature remains corroborating context rather than a second acceptance system. Every start must
reread one duplicate-free authority document and revalidate a no-follow opened regular executable,
copy only those bytes, rehash the private executable, and pass that absolute snapshot as argv[0]. PATH,
basename, caller configuration, a prior successful validation and a stale snapshot grant no authority.

H-032 depends exactly on H-033. It does not alter H-033's fixed probe allowlist or reinterpret a generic
PASS probe as provider identity. Instead the frozen H-033 gate and protected owner installation are a
fresh upstream provenance prerequisite, while H-032 owns only the downstream executable identity effect.
The G20 containment probe remains independently candidate/spec/gate/launcher-bound because H-033 does
not replace H-017's runtime namespace authority. Nested sandbox denial is ODÖMBART; the owner runner is
required for the actual H-033 and Seatbelt effects. Before builder implementation the only legitimate
product RED is the absent provider-identity boundary in `scripts/nortropic-codex-autopilot.py`.

Independent review rejected the first fresh gate because its shell bootstrap inherited caller PATH,
its historical `--g20-evidence` input was self-asserted JSON rather than authenticated effect, and it
did not execute the production generic non-provider dispatcher. The remediated gate uses canonical
absolute judge/tool identities and a fixed validated private cleanup root. G20 authorization is now
live-only: JSON may be emitted after a real candidate-bound probe for durable evidence, but no JSON can
be supplied back to obtain PASS. Separate production controls execute system Git, GitHub CLI and an
arbitrary fixed controller-style helper through `run()` and require exact effects with no AGENT_START.

## 2026-08-14 — H-032 builder: provider identity becomes an execution boundary

The provider-only launch path now rereads one strict authority document at every attempt. Both the
authority and executable are opened with no-follow semantics; regular-file identity, executable mode,
bounded complete reads and stable metadata are decided on those opened objects. Only the verified
bytes are copied into a newly private root, and the copied executable is rehashed immediately before
the provider trust transition. The source pathname is never reopened to populate or execute the
snapshot, so a same-byte hard link remains admissible while symlinks, PATH shadows and pathname swaps
gain no authority.

`AGENT_START` occurs only after the final digest check. The absolute snapshot argv[0] is passed through
the existing controller launcher with the private root as its G20 trust root; provider descendants are
therefore denied write/chmod/unlink/rename/create authority over both snapshot and namespace. The root
is removed on success and every failure path. The generic `run()` dispatcher is deliberately untouched,
preserving exact Git, GitHub and fixed helper effects without producing provider lifecycle events.

The frozen gate's deterministic identity negatives, opened-object races, final-rehash mutation and
cleanup controls are judgeable in the builder sandbox. Actual provider success, namespace denials and
fresh protected H-033 provenance require the ordinary owner runner because nested Seatbelt is rejected
inside the builder sandbox; those effects remain explicitly ODÖMBART here rather than being simulated.

Independent review then found a boundary ordering defect: the absolute G20 launcher still had an
`/usr/bin/env python3.12` shebang, so caller PATH could execute attacker code before the launcher
installed Seatbelt. The provider path now reads the already frozen Python interpreter authority,
verifies its canonical no-follow regular executable and exact digest, and invokes that absolute
interpreter with isolated `-I -S` flags. It does not sanitize or replace the provider environment;
PATH reaches the provider only after the trusted controller process has established G20. A disposable
fake `python3.12` placed first in caller PATH was not invoked, while the provider remained a descendant
of the real launcher and all six namespace attacks stayed denied.

The next review correctly rejected that candidate's partial consumption of the separate Python
interpreter authority: hashing one opened descriptor and later executing its pathname did not satisfy
that authority's full same-opened-object private-snapshot model. H-032 now makes no Python-authority
claim. It relies on the already frozen H-017 launcher trust boundary and closes only the environment
that reaches the launcher's pre-Seatbelt `/usr/bin/env` step: fixed non-caller PATH and removal of every
caller `PYTHON*` variable. Other provider environment is retained. Dedicated fake PATH and
launcher-specific `sitecustomize` controls remained silent; the actual provider still ran below the
real launcher with G20 namespace attacks denied.

Review also demonstrated that a preserved caller `HOME` enabled Python 3.12's user-site
`usercustomize.py` before the script and therefore before G20. Removing HOME would break the
provider's credential environment, so the launcher environment instead forces no-user-site and safe
path startup, disables bytecode emission, strips all caller `PYTHON*`, and explicitly strips Darwin's
non-PYTHON-prefixed `__PYVENV_LAUNCHER__` framework redirect. HOME and unrelated provider variables
remain intact. A combined hostile HOME, usercustomize, PATH, PYTHONPATH and pyvenv-launcher run left
all intercept markers absent and retained the live provider/G20 effects.

Environment controls alone still left interpreter selection at an owner-writable Homebrew symlink and
allowed global site/`.pth` processing before G20. The final correction consumes the existing Python
authority completely rather than partially: exact 14-key semantics, canonical no-follow opened object,
regular/executable mode, stable bounded bytes and exact digest. Those opened bytes are copied next to
the provider snapshot in the same private root. Immediately before `AGENT_START`, both executables are
rehashed and protected; the absolute Python snapshot runs the exact `-I -S` flags and absolute launcher.
The provider environment is otherwise retained, but `DYLD_*`, `LD_PRELOAD`, `LD_LIBRARY_PATH` and
`__PYVENV_LAUNCHER__` are removed because they can execute or redirect code before isolation/G20. A
constructor dylib plus hostile global/user site, PATH, HOME and Python-family inputs produced no marker.

## 2026-08-14 — Fresh H-031 role routing after published H-032

H-031 is rematerialized from authoritative main `32b6e07`; every historical H-031 gate and candidate
remains forensic evidence only. The task is ordinary, depends exactly on H-032 and owns no new provider,
session or verdict component. Its effect is the route received by the actually spawned provider process
through H-032's exact opened-object, co-snapshot, final-rehash and G20 boundary. Provider prose, a would-be
argv variable and a paid live response are not routing authority.

The owner-frozen matrix remains `gpt-5.6-sol` for all six runtime roles, with `high` for BUILDER and
`max` for ARCHITECT, TEST_AUTHOR, GATE_REVIEWER, REVIEWER and EMPIRICAL. This matches the machine's
current owner configuration and active Codex model surface. Codex CLI 0.147.0 exposes `-m/--model`,
`-c/--config`, `model_reasoning_effort` and `--ignore-user-config`; H-031 therefore binds exact actual
argv and requires user configuration to be ignored. Backend availability and model self-report are
deliberately outside the deterministic verdict.

The frozen pre-builder baseline is exactly four product failures: absent actual role route, absent
AGENT_START route binding, unknown-role effects before rejection, and a generic `run()` boundary that
does not yet reject a Codex basename. H-032 itself is freshly green at 71/0. The new source-form control
retains Design B's explicit composition boundary—one Popen site, one generic subprocess.run site and the
literal watch clear—while auditing the whole module for methods, lambdas, defaults, containers, aliases,
dynamic attribute access and dynamic code. It admits ordinary non-provider helpers and harmless role
call consolidation, so it does not revive the abandoned general Python dataflow evaluator.

Independent review found three gate omissions before publication. Codex accepts attached short model
and config forms, which can carry competing routing authority; the route oracle now parses and mutates
those forms. Dynamic `importlib` and computed `__import__` could create an uncounted process boundary,
so the source-form audit rejects those dispatch mechanisms explicitly. Finally, persistent-state
comparison alone could miss a provider snapshot created and cleaned before an invalid-role rejection.
The invalid-role oracle now replaces the production snapshot function with a recording tripwire and
requires that it is never reached, while retaining the journal, run-directory and provider-effect checks.

A second review demonstrated why security oracles cannot privilege today's helper names. Attached
profile and dangling known selectors are now part of the closed route grammar. Builtins and reflected
module registries join importlib as prohibited alternate dispatch sources, with only production's exact
read-only `__file__` selftest lookup admitted. Most importantly, invalid-role ordering is now observed at
the effect boundary with a scoped audit hook: file creation/writes/removal/rename/link/chmod and process
start are recorded even when implementation inlines, renames or cleans its snapshot helper. The existing
persistent journal, run-directory and provider capture comparisons remain independent corroboration.

Third review found that Python audit events alone are not a native-syscall sandbox: a newly imported
`ctypes` module could call libc below the observed event set, and reflected or aliased `sys.modules`
could recover subprocess. H-031 needs no new dependency to add a constant role policy, so the bounded
Design B envelope now freezes the product's exact existing import inventory. Bare or reflected `sys`
is rejected; only direct non-registry attributes already used by production remain admissible. This
composition makes the effect hook meaningful without claiming it observes arbitrary native code.

Fourth review then recovered dynamic import through private state on modules already in the frozen
inventory. The final reflection envelope is structural: all private attributes are rejected except the
single exact `super().__init__()` call already present, and `getattr` is admitted only for the two exact
read-only `os.O_*` fallback constants production uses. Module dictionaries, reflected builtins, Python
frames and function globals are explicit mutants. This closes the path that dynamically recovered FFI
and keeps the scoped audit hook within the source domain it can actually observe.

Fifth review found a remaining composition error: a safe-form check on a builtin call is ineffective if
the builtin can first be stored under another name. Sensitive builtin names are now capabilities at
every load site. `getattr` and `globals` must be the direct callee of their separately checked exact safe
forms; all references or aliases reject. `vars`, `locals`, dynamic-code and import builtins reject on load.
Mutants cover assignment aliases that previously recovered ctypes without adding an import node.

Sixth review found two native process constructors omitted from both layers: `os.fork` and
`os.forkpty`. A forked child inherits the Python audit hook but mutates a copied observation list, so
the parent cannot rely on the child's recorded events. Both APIs are now prohibited process sites in
the whole-module source envelope, and their audit events are also forbidden before role validation.
Direct fork/forkpty mutants prevent the omission from recurring.

Seventh review confirmed the parent-side fork observation, but found that modules already loaded can
publicly re-export other module objects. A Name-rooted matcher therefore missed `subprocess.os.fork()`
and equivalent chains. Attribute access to sensitive process, import and FFI module proxies is now
forbidden independently of the root object, while direct approved modules remain governed by the exact
import inventory and their enumerated process APIs. Proxy fork/spawn/registry mutants bind the closure.

Eighth review recovered a frame without private syntax by installing public sys trace/profile callbacks;
the frame's public globals then exposed subprocess and dynamic import. Direct sys access is now frozen to
the six attributes the current product already uses. Trace, profile, hooks, frames and registries are not
available to H-031 implementation. Ambient module-loader globals plus builtins that can invoke dynamic
debug/help machinery also reject on load. Dedicated mutants bind each newly closed capability.
