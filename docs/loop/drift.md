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

Ninth review recovered globals from public frame carriers without calling sys: generators, coroutines,
async generators and tracebacks expose frame objects, whose public namespaces contain subprocess and
builtins. All frame-carrier and frame-namespace attributes are now sensitive reflection and reject in
the whole module. None exists in current production; four independent mutants bind the carrier family.

Tenth review demonstrated that a synchronous before/after oracle can be outrun by a delayed callback:
`subprocess.threading.Timer` scheduled a real provider path after the audit window closed. Public proxies
for threading, signal, exit handlers, schedulers, futures and finalizers now join process/import/FFI
modules in the sensitive set. Timer, signal, atexit and weakref-finalizer mutants bind this asynchronous
effect class; current production uses none of those proxy capabilities.

Eleventh review found two delayed paths without module proxies. An atfork callback combined with
`preexec_fn` fired on a later legitimate Popen, and cyclic `__del__`/yield-finally objects deferred work
to GC. Atfork is now a prohibited process callback; admitted process sites reject pre-exec, shell,
executable substitution and expanded keyword dictionaries. Since production contains no asynchronous
function, yield or await, those language forms and `__del__` are also excluded from the bounded source
envelope. In-place Popen mutants prove the one legitimate site itself remains constrained.

Twelfth review separated a lifecycle method's name from its installation: assigning an ordinary helper
to class key `__del__` creates the same delayed finalizer. Finalizer assignment, setattr/delattr and
dynamic three-argument type construction now reject; only current scalar schema `type(x) is/is not`
checks remain. The review also found direct process signaling outside both inventories. `os.kill` and
`os.killpg` are now prohibited source/effect APIs with independent mutants and audit-event binding.

Thirteenth review recovered dynamic class construction through a public `types.new_class` proxy and
placed executable/preexec substitutions into positional Popen slots. `types` is now sensitive, and the
sole Popen plus generic run site each require exactly one non-starred positional argument in addition to
the existing unsafe-keyword prohibition. In-place positional and starred mutants test the legitimate
site itself rather than adding an obviously extra process call.

Fourteenth review recovered finalizer installation without `types` or a direct finalizer target: a
metaclass `__prepare__` mapping injected the lifecycle key while Python executed an ordinary class-body
assignment. The source envelope therefore admits only the product's existing `__init__` lifecycle
method, rejects class keywords and literal finalizer keys, and binds the exact metaclass construction as
a mutant. The same review changed process-global cwd, environment and umask before invalid-role
rejection; the first three audit events had merely been omitted and umask emitted no event. Direct OS
access is now frozen to the exact current product attributes and its sole read-only environment form,
with process-state APIs prohibited. The runtime oracle independently snapshots cwd/environment/umask,
restores them after measurement, and aborts audited mutation operations after recording their attempt.

Fifteenth review aliased the builtin `type`, hiding dynamic class creation from the direct-call rule,
and moved already-admitted `os.write`/`os.close` capabilities before role validation. The latter mutate
descriptor state without Python audit events, so cwd/environment/umask snapshots alone were incomplete.
`type` may now be loaded only as the direct scalar schema call checked separately. Every current OS
descriptor-effect call is frozen by exact owner and count, preventing reference capture or an added site.
The invalid-role execution additionally replaces all available OS/process mutation functions and Popen
with recording guards that raise before invocation; stdout and stderr are isolated and must stay empty.
Those guards compose with, rather than replace, the audit hook, process-state snapshot and persistent
artifact comparisons.

Sixteenth review moved the effect before every previous observation by creating and removing a file at
module import. It also used the already imported `fcntl.flock` capability and stream objects captured
before stdout/stderr redirection. Subject import is now inside the same fail-before-operation audit and
OS/process guard boundary as invalid-role execution, with independent cwd/environment/umask and output
comparisons. Effectful module-level methods reject structurally. `fcntl.flock` is frozen to its one
existing lock owner/site and is guarded plus audited at runtime. Direct stdout/stderr objects are frozen
to the product's exact existing write and error-print forms, so neither stream can be retained for a
later bypass. Import create-clean, fcntl alias and captured-stream mutants bind each route.

Seventeenth review poisoned `sys.path` from a function default during import. Python import state was
absent from the process snapshot, even though the current product legitimately inserts its authority
library and enables no-bytecode mode at module load. Those two mutations are now exact source forms with
exact counts. Runtime import observation requires precisely one new leading authority path and bytecode
suppression, then restores the prior interpreter state. More fundamentally, a rejected source envelope
previously continued into `exec_module`; an unguarded `fcntl.fcntl/ioctl` could therefore act before the
eventual FAIL. Source or observer rejection now terminates before upstream or subject execution, while
fcntl/ioctl also join the audit and mutation guards as an independent backstop.

Eighteenth review retained the exact admitted `sys.path.insert` syntax while changing what its operands
meant: a reassigned `AUTHORITY_LIB` or shadowed `str` loaded attacker-controlled `core` before the
post-import path comparison. The authority assignment is now frozen as one exact AST object, and its
name, `Path`, builtin `str` and `__file__` cannot be rebound by assignments, parameters, functions or
classes. The same review removed a gap in the early-stop composition: complete required API presence now
joins task identity, upstream identity, source form and observer separation as a mandatory precondition
before either upstream execution or subject import. Authority-shadow and missing-API mutants bind both
transitions.

Nineteenth review used two binding mechanisms outside ordinary Name(Store). An exception handler stores
its `as` target as a string AST field, allowing temporary `AUTHORITY_LIB` replacement, and public
assignment to `Path.resolve` changed the exact expression's semantics before restoring the class. All
exception and global/nonlocal bindings of protected authority names now reject. `Path` itself is a
non-capturable capability: it may appear in annotations or as the direct constructor/class-method root,
but not as an alias, container value or class-attribute mutation target. The gate deliberately targets
the owner Python AST version; newer pattern syntax cannot compile there and therefore cannot reach
subject import. Exact exception-binding and public-monkeypatch mutants bind the closure.

Twentieth review showed that admitting every direct `Path` class-method call still leaked the class
through `Path.mro()`: the returned list exposed `Path` at index zero, where `resolve` could be replaced
and restored around the otherwise exact authority assignment. The product uses only `Path.home()` as a
class method. That exact zero-argument form is now the sole admitted class-method root; constructor calls
remain admitted. A class-container monkeypatch mutant permanently binds the reviewed bypass.

## 2026-08-14 — H-031 builder: explicit provider model routing

The existing H-032 provider boundary now selects its model route from one static role policy before
creating any run state. The six admitted roles all use `gpt-5.6-sol`; BUILDER uses reasoning effort
`high`, while ARCHITECT, TEST_AUTHOR, GATE_REVIEWER, REVIEWER and EMPIRICAL use `max`. Unknown, empty
and case-variant roles stop before journal lookup, snapshot creation or process effects.

The selected route is inserted into the actual provider argv as exactly one `--ignore-user-config`,
one model selector and one `model_reasoning_effort` override. The same in-memory route values populate
AGENT_START's model, effort and `AUTOPILOT_ROLE_POLICY` source, so persisted legacy routing remains
readable but cannot select a new launch. Hostile CODEX_HOME and PATH configuration did not alter the
spawned fake provider's observed argv.

The generic subprocess helper remains available for Git, GitHub, node and controller tools, but now
rejects any executable basename whose Unicode case-fold is `codex` before its sole subprocess.run site.
No alternate provider process component, session store or selector was introduced. The frozen whole-
module source audit and its process/import/reflection mutants remain the bounded enforcement surface.

## 2026-08-14 — H-031 post-publication dependency-preflight remediation

The first real file-backed observer execution after publication exposed a call-site conflict that the
frozen role-routing gate did not exercise. `ensure_dependencies()` retained two historical
`codex --help` probes through generic `run()`, while H-031 intentionally made that boundary reject every
Codex basename. Consequently both `status` and `doctor` stopped before their actual observer work.

The dependency preflight now checks executable presence without executing Codex. The removed help text
was not identity authority and could not certify the later process: provider identity, exact supported
model/effort argv and the actual process effect remain bound at the sole H-032-protected `run_codex`
boundary. Generic `run()` remains closed to Codex, and no subprocess site or alternate launch route was
added. Physical file-backed `status` and `doctor` runs now proceed through dependency preflight.

## 2026-08-14 — H-032 execution-family authority amendment after first launch

The first real autonomous launch falsified the single-executable H-032 model. The verified Codex 0.147
snapshot started and emitted `thread.started`, but stable `code_mode_host` resolves a required native
sibling named `codex-code-mode-host`; the isolated snapshot root contained only `provider`, so no
structured result was produced. This is a provider execution-family dependency, not a second provider
selector or a caller-configured helper.

Owner measurement binds the installed sibling at the exact native vendor path: arm64 Mach-O,
49,991,616 bytes, SHA-256 `a059beb029cdbc989e72e23f8680be9f703cb6cf83d9598d91041f82178d018d`.
The main provider digest remains `19c4f144c5226a9f17c58e6f0fa854843b0f77a6eb420f40e2745a12f10f5d37`.
Authority schema v2 binds both absolute paths and digests. The frozen H-032 amendment measures both
from no-follow opened objects, requires exact private basenames `provider` and
`codex-code-mode-host` in one root, final-rehashes both, directly executes only the provider, denies
namespace mutation of either under G20 and requires whole-family cleanup on every path. H-031's role
routing fixture is upgraded to the same family authority; its route and process-source controls are
unchanged. The owner pre-builder state is RED only for
`CODE_MODE_HOST_IDENTITY_BOUNDARY_ABSENT`; no production implementation is included here.

Independent gate review then found five ways a superficial family implementation could pass. The
amended controls now mutate provider and host independently at their launch-adjacent reads, with a
spawn-boundary fallback that exposes implementations which verified only immediately after copying.
The host's same-opened-object metadata is observed through fstat and raced against stale path
stat/access plus a nonexecutable symlink target. Every identity-negative attempt records any created
provider root and requires no partial member/root residue. Finally, the host fixture is executable and
writes a dedicated marker if directly launched; the legitimate provider run requires that marker to
remain absent. These are gate-only changes. The one intended product RED and all prior upstream
regressions remain unchanged.

R3 gate hardening replaces the second-read heuristic with a causal post-protection mutation point for
each family member. It adds a positive exactly-once provider-to-host ancestry anchor, filesystem-effect
cleanup observation independent of tempfile API/prefix, and separate oversized sparse provider/host
negatives at 256 MiB + 1 byte. This remains owner TEST_AUTHOR work only: no production implementation
is present and H-032 must stay RED solely for the absent execution-family boundary.

R4 replaces R3's first-matching protection mutation with an ordered launch trace spanning chmod,
fchmod, complete member reads and actual Popen; both fresh reads must follow the final mode transition.
Cleanup now retains every audited absent-at-event path anywhere and uses exact pre-seeding for system
noise rather than location or basename exclusions. Both 256 MiB + 1 fixtures are valid executable
programs whose unbounded capture effects are run and proven. No production byte is changed.

R5 adds independent connected physical corruption for provider and host, rejects cached or ignored
digest comparisons through actual capture effects, and requires no writable family descriptor at spawn.
Expected journal paths are classified exactly; every other audit-observed success or failure residue is
forbidden. The alternate-root cleanup fixture is now trap-owned and finally-cleaned. Production remains
untouched and the sole intended RED is unchanged.

R6 binds connected corruption to the first actual post-protection read of the snapshot object, including
pre-opened handles and descriptors. Actual process fd enumeration plus fstat/F_GETFL replaces API-level
writer bookkeeping at Popen. The journal cleanup exemption is now an exact finite shape, and a family
subtree beneath runs is an explicit rejection mutant. Production remains unchanged.

R7 removes original-fd history from connected corruption: every actual read fstats its live descriptor
against current snapshot dev/inode, including a connected duplicated-RO subject control. Cleanup now
binds the exact single run directory created by the invocation and rejects empty sibling roots or valid
leaf names beneath any other child. Production remains unchanged.

R8 seeds snapshot dev/inode identities from the observed exact private family at protection transitions,
not from pathname-open spelling. Connected corruption covers high-level buffered variants plus os.read,
pread, readv and preadv, with actual all-openat and positional-read subject controls. Production remains
unchanged.

R9 always wraps fdopen handles and resolves their live fileno identity on every buffered read, allowing
identity seeding to occur later at protection. A connected pre-protection openat-to-fdopen subject path
proves corruption precedes its actual final complete verification. Production remains unchanged.

R10 preserves that live identity observation transitively when a pre-protection buffered handle yields
its readable opened object through detach() or the public raw chain. Separate connected openat-to-fdopen
detach and raw subject controls require corruption before their complete final verification read and do
not accept the launch fallback. Ownership remains single-close and production remains unchanged.

R11 removes all historical integer-descriptor fallback from connected read classification. Every read
receives snapshot credit only from its current live fstat identity; a delegated pre-seed handle must also
match the same live opened object. A close-and-forced-number-reuse control proves an unrelated read stays
unchanged before the genuine duplicate/fdopen snapshot reader triggers pre-verification corruption.

Post-publication integration exposed three gate-only false negatives hidden by the earlier schema-v1 RED.
Provider race mutation is now reset and digest-anchored before each host control. Cleanup admits the exact
root `events.jsonl` journal leaf but no sibling or subtree. The R11 fd-reuse experiment now surrounds the
actual live snapshot read for both file-handle and descriptor APIs, rather than requiring an os.open shape.

## 2026-08-14 — H-032 code-mode execution family activated

Production now consumes authority schema v2 as one coherent six-key document per launch. The main Codex
Mach-O and its required `codex-code-mode-host` sibling are independently opened with no-follow semantics,
checked as executable regular files on those descriptors, read under the 256 MiB per-member ceiling and
hashed before any private execution root exists. Only bytes from those opened objects are materialized.

The private root contains exact `provider` and `codex-code-mode-host` basenames alongside the already
authority-bound controller Python snapshot. All members and the root are made non-writable first; fresh
complete SHA-256 reads occur afterward and immediately before AGENT_START and the sole Popen boundary.
The controller invokes only `provider`. Codex discovers and executes the verified same-root host as its
descendant inside the existing G20 namespace, so the sidecar is neither a second controller-selected
provider nor ambient PATH authority. Cleanup removes the complete root after success and every exception.

The frozen H-032 gate is green at 130 PASS / 0 FAIL. Its matrix includes coherent schema rejection,
same-opened-object source races for both members, live descriptor reuse and aliases, post-protection
corruption, final-transition ordering, valid oversize effects, exact provider-to-host ancestry, G20
namespace denials and residue-free success/failure cleanup. H-031 continues to bind the exact role route
at this execution boundary; H-033 and the older H-034/H-035/invariant suites remain unchanged.

## 2026-08-14 — H-032 structured result handoff amendment

The first real host-backed TEST_AUTHOR run completed in the provider event stream but could not create
its configured `-o` leaf inside the controller-owned live Git journal, exactly as H017/G20 requires.
The frozen amendment keeps that denial intact and requires one fresh connected result through a
least-authority disposable transport. The controller independently binds it to the exact invocation,
run, role, route and process/thread context, validates one complete strict schema value, atomically
publishes it and cleans transport state on success and every failure interval. Preseed, replay, wrong
binding, partial/multiple/trailing values, mechanism-specific object/channel attacks and live-state
writes reject. Schema-shaped event text alone remains non-authoritative.

Independent review then showed that the first executable oracle used only a standalone
fixture Git directory and checked only selected report fields. R2 uses a temporary linked
worktree whose common Git directory is the candidate repository's physical LIVE_GIT,
restores every journal/worktree-admin effect, and still executes the verified provider
family through G20. Its negative family now exercises strict UTF-8/duplicate/framing and
the complete frozen JSON Schema recursively, plus binding, writer, failure and cleanup
variants; all remain aggregated under the single intentional product RED.

R3 replaces that shared linked-worktree control entirely. The physical composition is
now a no-hardlink disposable Git/control-plane root made from the exact candidate bytes;
its imported controller, launcher ROT, repository and LIVE_GIT are the same isolated
authority domain, so no canonical journal rollback or global worktree pruning occurs.
Causal stale/replay controls predate their invocation, an active reader observes partial
canonical publication, a real one-second launcher timeout and signal interruption run,
and the frozen result ceiling is exactly 4 MiB with a valid 2 MiB positive.

R4 makes the ceiling controls byte-exact: a complete schema-valid encoding of exactly
4 MiB is admitted and 4 MiB + 1 rejects through a no-follow, same-opened, stable bounded
reader. An accepted value is replayed into a fresh invocation by an unrelated writer,
transient cleanup failure and delayed interruption quiescence are observed, and the
gate classifies filesystem versus descriptor/stream transport before applying attacks.
A length-framed bounded stream positive plus EOF/partial/trailing/oversize negatives
keeps the frozen criterion open to a legitimate non-path implementation.

R5 removes that unconnected parser demonstration and freezes the least-authority
primitive actually exposed by the authority-bound Codex CLI: an exclusive private
regular filesystem result object beneath a controller-owned staging root, outside
LIVE_ROOT/LIVE_GIT. Path construction, helper and bounded read APIs remain free to
refactor. Cleanup faults are now injected against the observed result transport itself,
with transient retry and persistent-exhaustion outcomes separated, while delayed signal
quiescence inventories object type/content/dev-inode/mode plus process and descriptor state.

R6 binds the observed private staging root itself: current uid, exact 0700 mode,
nofollow identity, exactly one result leaf during provider output, and complete parent
cleanup. FIFO, Unix socket and parent-swap join symlink/directory/hardlink attacks with
a one-second fail-safe. A fresh admitted invocation has an API-neutral audit count of
exactly one canonical result read before causal external-writer replay, and hostile
provider attempts now cover global events, envelope, sibling run, refs, config, hooks,
source and trust paths, all mechanically confined beneath the gate's disposable root.

The R6 closure also drives mutation through the product's actual result consumption:
Path/io/builtin-handle reads and os.open/os.read descriptors are instrumented by live
result identity. Path replacement after open, same-inode rewrite, growth and valid
shortening occur immediately before the real read. Each must reject; the exact-bound
positive and +1 negative remain connected through the same provider/run_codex route.

R7 counts consumption on the captured private transport `output_path`, not on the
canonical observer file: exactly one transport read is required, while atomic publish
may return without reopening canonical. The connected read harness now also wraps
fdopen, readline/readlines/readall/iteration and positional/vector read capabilities.
Object attacks require removal of every seeded leaf and moved parent before verdict.
Timeout/SIGTERM quiescence derives the actual staging root from the audited provider
argv and inventories surviving provider commands plus each survivor's lsof fd table.

R8 adds semantic exactly-once counters around the actual product route: one complete
schema parse and one atomic promotion to the invocation's canonical destination. A
second run injects a genuine duplicate parse and proves the same oracle rejects it.
Uninstrumented C-backed acquisition routes are mechanically closed by an exact source
capability inventory (mmap/FileIO/dup/raw/buffer/detach absent and the two pre-existing
non-result memoryview sites unchanged). Timeout/SIGTERM monitoring records provider
families by pid, ppid and process-start identity while alive, then requires every such
identity gone after delay; the actual staging tree and survivor fd inventories are zero.

R9 removes parser-function, rename-function and raw source-substring authority. A live
effect observer binds the opened transport's dev/inode and records complete stable
schema-valid value identities; a second-value provider produces two distinct accepted
boundaries and is caught. Canonical publication is observed as an absent-to-present
complete object-identity transition independent of helper API; an injected second inode
transition is caught. Both timeout and SIGTERM are sampled from spawn, staging roots
must be absent (not empty), and a fast provider fork/exec descendant that writes late
residue must be discovered by pid/ppid/start ancestry and rejected after delay.

R10 replaces that asynchronous effect observer with a causal controller-boundary
handshake. The provider pauses after closing each private sink; the gate opens the exact
sink no-follow, binds dev/inode/digest and proves canonical absence before release. A
second accepted close or an injected prior/second canonical promotion must cause the
actual invocation to reject, rather than merely incrementing an observer count. This is
independent of parser, mmap/FileIO/raw/fd helper, or atomic-publication API choice. The
process oracle assigns a session at Popen return and exercises timeout and SIGTERM with
a rapid double-fork+setsid+exec late writer; delayed success requires absent staging root,
no live recorded identity or process group, and no late filesystem effect.

R11 removes fixture authority from the imported subject's environment. Mode, capture
and pause controls live in judge state and are added only by the final provider-child
interceptor after production has constructed its launch environment. Result acceptance
uses opened-object dev/inode/value and promotion effects; mmap, FileIO, raw, dup-fd and
bounded helper reads are positive equivalent routes. The observer does not add or alter
Popen session kwargs. Its hostile double-fork+setsid child receives no cooperative
ledger/marker channel and can derive only the real private output parent for its delayed
external write, which timeout and SIGTERM containment must prevent.

R12 gives all new handoff PASS credit only to fresh-interpreter runs with the real
stdlib Popen type. Per-attempt behavior is embedded in separately hashed provider
authority bytes; no fixture token or monkeypatch enters the subject. The same actual
run_codex route exercises exact-source mmap, FileIO, raw and helper read-call variants,
whose process topology is AST-identical. The timeout variant changes only the unique
86400 constant to one second. Its uncooperative double-fork+setsid survivor loops on
the actual sink indefinitely, forcing bounded causal containment instead of a finite
observation-window success.

R13 reserves one real owner-provider model call for the final owner-host phase only
after the entire deterministic boundary is green. Prebuilder and builder RED iterations
therefore make no live call. The invocation binds candidate/source/spec/gate, exact
provider and host paths/digests, production role/route/argv and the complete schema;
timeout, auth, network or sandbox unavailability is ODÖMBART. The deterministic sink
oracle retains its nofollow descriptor through before/after fstat, read and mutation or
swap injection, then requires exact canonical digest/schema and total staging cleanup.
Literal source-expression variants are removed; timeout acceleration is a semantic
candidate seam whose absence is ordinary RED.

R14 owner-freezes `_consume_private_result(sink_fd, canonical_destination,
invocation_id, run_id, role)` as the sole result-consumer security seam. AST/dataflow
checks require one definition, exact capability/binding arguments, one run_codex call
and no provider/host/authority/fixture identity loads. The sole timeout seam is exactly
86400 with one production load; only the fresh test runner may set it to one. Held-fd
identity now includes mode, size, mtime and ctime as well as dev/inode before and after
the complete bounded read. Success requires one audit-observed atomic publication;
mutation, swap, double-value and promotion paths require zero. The final exact-family
call runs from an isolated no-hardlink clone at exact HEAD/tree with its own `.git`.

R15 closes the recursive project-helper graph rooted at the consumer. Only explicit
pure builtin and stdlib calls are admitted; reflection, dynamic attributes/imports,
aliases, indirect calls and argument/seam rebinding are rejected. The seam name has one
load: the exact direct run_codex call using the five exact provenance locals. The sole
timeout load must be `timeout=CODEX_RUN_TIMEOUT_SECONDS` on wait/communicate of the
sole Popen result. Before canonical rename/replace, the audit hook nofollow-opens and
retains the source object, records fstat/digest, and later binds destination identity and
digest. The mutation control now writes a complete schema-valid equal-length alternate
value, while the swap control replaces the path behind the retained accepted fd.

R16 propagates provider/authority/fixture taint through every reachable helper and
inventories module/local bindings for all seam/helper identities. Exact call arguments
must derive from a nofollow-created sink fd and nonconstant canonical, invocation and
run bindings plus the run_codex role argument. The closed capability graph admits mmap,
FileIO, pread/readv/preadv, fdopen, raw/buffer and helper reads without a narrow method
spelling. There is exactly one assigned Popen object, no reassignment or extra site;
its reachable timeout wait/communicate precedes every successful return. Rename-source
capture is bounded to MAX+1, destination dev/inode must equal the retained source, and
all post-transition canonical open/unlink/rename events reject.

R17 replaces the remaining name and line-order claims with semantic value flow. A
monotone abstract interpreter propagates identity, sink, canonical and invocation/run/
role tags across aliases, containers, helper parameters and returns. Capability reader
families transfer authority only from a tagged descriptor/receiver; an exact
`os.open(..., O_RDONLY|O_NOFOLLOW)` is the only sink-tag source. Popen aliases are
resolved before inventory, and the structured control-flow check rejects branch, loop,
context-manager or exception bypass around the sole timeout-bearing wait/communicate.
Atomic same-object promotion, bounded retained-source verification and live-phase skip
semantics remain unchanged.

R18 makes identity and process origins concrete. Provider-family authority parsing and
derived path/digest/snapshot values seed IDENTITY; actual argument tags flow into helper
formals context-sensitively and returned descriptor capabilities flow back to callers,
with recursion rejected conservatively. subprocess module, Popen constructor and process
object tags propagate through aliases, containers, attributes and helper returns before
the sole-site CFG check. Exact-body admissibility now separately executes preadv, readv,
BufferedReader.read, raw.read and a mandatory nested bounded helper through complete
fresh-process run_codex effects, without crediting the exact production verdict.

R19 preserves the exact tag sets at the run_codex-to-consumer boundary: every argument
must contain its required provenance and no IDENTITY/UNKNOWN or position-forbidden tag,
and those actual sets seed all consumer/helper analysis. Each generated reader body must
also pass the gate's semantic source-admissibility vocabulary before its connected
runtime effect can count. Import/ImportFrom subprocess origins and process constructor/
object values are inventoried through aliases and supported stores; unresolved process-
relevant stores or calls reject before the sole-site timeout CFG can pass.

R20 makes semantic origins non-sanitizing: journal/run/invocation tags union all operand
tags, while the five seam arguments must equal the exact singleton provenance sequence
SINK/CANONICAL/INVOCATION/RUN/ROLE. Call binding implements Python positional-only,
positional, keyword, keyword-only, default, varargs and kwargs rules with duplicate or
missing bindings fail-closed. Attribute/subscript stores join into their owning heap
object, so container and helper laundering cannot erase process or identity tags. The
same complete tree-analysis entry point is invoked for the exact candidate and every
generated exact-body reader variant before connected runtime evidence is considered.

R21 first mechanically extracts the complete inline consumer/interprocedural/identity/
process/CFG analyzer into `analyze_candidate_tree`; the exact candidate and every
generated reader variant now receive that identical full analysis and context. Distinct
zero-argument `_new_run_id()` and `_new_invocation_id()` origins make exact singleton
provenance satisfiable without name-based tag splitting. Formal environments include
positional-only, positional, keyword-only, vararg tuple and kwarg mapping categories;
literal star and double-star expansion follows Python duplicate/missing/default rules,
while unresolved dynamic expansions reject.

R22 grants RUN/INVOCATION tags only after the complete zero-argument origin helper body
passes a provider-independent secrets.token_hex(16)/uuid.uuid4 entropy audit. Multiple
runtime calls must be shaped, nonempty, pairwise fresh and disjoint across the two
classes. `analyze_candidate_tree` no longer mutates AST nodes; its single semantic
vocabulary admits the owner-frozen reader templates. Process constructor sites are
recorded during context-sensitive actual-to-formal interpretation rather than a global
call rescan. Positional-only keywords reject, literal star/double-star expansions bind
faithfully, and unresolved dynamic expansions remain fail-closed.

R23 freezes both identifier origins to the exact undecorated AST body
`return secrets.token_hex(16)` plus one unaliased, unrebound `import secrets`; aliases,
concatenation, other globals, helpers, defaults, annotations, closures and decorators
reject. Runtime freshness/disjointness remains mandatory. The context-sensitive
interpreter now evaluates bare expressions, conditions, iterators, with-contexts,
asserts, raises and comprehension inputs/filters, so bare helper-mediated process
constructor effects cannot disappear. Literal `**` keys targeting positional-only
parameters reject exactly like direct keywords.

R24 protects the entropy primitive itself: direct or aliased attribute stores, token_hex
subscripts/`__dict__` writes, reflection and binding deletion/replacement reject across
the whole module. The analyzer replaces ast.walk reachability with structured Python
runtime traversal. Function/lambda decorators, defaults and annotations execute at
definition time but dormant bodies do not; class bases, keywords and decorators execute,
then the class body executes. A dormant nested Popen body is therefore a legitimate
positive until called, while decorator/default/class-body/helper constructor effects are
recorded with their actual context and count against the sole process site.

R25 treats `secrets` as an exclusive capability rather than a single-attribute
blocklist. Only the two exact `secrets.token_hex(16)` origin calls are admissible;
module aliases carried through containers/helper returns and every attribute,
subscript, computed `__dict__`, update-method or reflective mutation are rejected.
Capability-reader provenance is accumulated monotonically across every reachable
context, so neither safe/unsafe traversal order can erase an unsafe receiver while
all-safe contexts remain admissible.
