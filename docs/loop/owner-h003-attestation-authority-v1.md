# Owner decision — h-003 attestation authority v1

**Beslutad:** 2026-08-10
**Gäller:** reparationskedjan före ny S3/h-004-builder
**Historiskt avvisad kandidat:** `1e21a7fe150f25626301f3656893d1798ae46c3d`

Detta är owner-authority för nästa test-author-pass. Den avvisade S3-kandidaten är endast historiskt reviewer-evidence och får inte amend/reset/rebase/adopteras eller publiceras.

## 1. Generisk authority-generation i h-003

`h-003` ska exponera ett generiskt authority-generation-protokoll. Authority-id är opaque. `h-003` känner inte till leases; framtida `h-004` använder sitt opaque `lease_id` som authority-id.

### BEGIN AUTHORITY

- etablerar ett opaque authority-id som aktuell publiceringsauktoritet för en task;
- fencar äldre authority-bound publiceringsrätt;
- äldre authority-id får aldrig senare skapa eller återställa giltigt state.

### PROVISIONAL WRITE

- en attestation under aktuell authority-id skrivs först som `PROVISIONAL`;
- `PROVISIONAL` får aldrig passera `read --require-valid`;
- write lyckas endast för aktuell authority-id.

### FINALIZE

- endast aktuell authority-id får finalisera sin egen provisional attestation;
- finalize gör exakt den publicationen `VALID`;
- stale/äldre authority-finalize ska falla utan att ändra nuvarande giltiga state.

### INVALIDATE

- befintlig h-003 SHA-global stale-semantik kvarstår;
- invalidate måste ordnas tillsammans med BEGIN, provisional WRITE och FINALIZE;
- en äldre snapshot/write får aldrig resurrecta state som senare invalidate eller authority-transition supersedat.

### READ

- legacy h-003-semantik kvarstår för äldre unbound attestations;
- authority-bound `--require-valid` lyckas endast för FINALIZED aktuell-authority-publication som inte är stale;
- corrupt, contradictory, partial eller unorderable authority-state failar stängt.

Alla auktoritativa mutationsvägar ska ha **en authoritative ordering**. Kontraktet binder effekt, inte implementation; det föreskriver inte flock, databas, CAS, rename-strategi eller lagringsformat.

## 2. Framtida h-004 lease → attestation protocol

Den framtida loopen ska använda h-003 API i denna ordning:

1. acquire unik `lease_id`;
2. etablera `lease_id` som taskens attestation authority **före** task/event/session-arbete som kan leda till publicering;
3. kör arbete med heartbeat;
4. skriv candidate attestation som `PROVISIONAL` under samma `lease_id`;
5. gör sista lease-loss guard;
6. stop/join heartbeat;
7. token-bound clean release av samma `lease_id`;
8. **endast efter lyckad clean release** får loopen requesta `FINALIZE(lease_id)`.

Konsekvenser:

- lease loss ⇒ ingen FINALIZE;
- release failure ⇒ ingen FINALIZE;
- stale generation ⇒ ingen FINALIZE;
- crash efter release men före FINALIZE ⇒ ingen giltig attestation;
- FINALIZE failure ⇒ run är inte clean och får inte ge giltig attestation;
- ny authority-generation fencar gammal publiceringsauthority;
- post-hoc best-effort invalidation är **inte** root mechanism för lease-loss safety.

Konstruktionen är alltså `publish provisional → gör validity till sista authority-transition`, aldrig `publish valid → försök rollback efter katastrof`.

## 3. Concurrent attestation mutations

h-003 ska hindra äldre authoritative snapshot/mutation från att skriva över nyare validity-beslut. Minst:

- write vs invalidate;
- provisional write vs begin-authority;
- finalize vs nyare begin-authority;
- äldre write/finalize vs nyare authority-state.

Ett command success måste motsvara durably observable authoritative state som commandot påstår sig ha etablerat. Mutation failure får inte lämna state som `--require-valid` tolkar som giltigt i strid med completed ordering.

## 4. Holder process incarnation för h-004

Numerisk PID ensam får inte vara liveness authority.

Konceptuell holder identity:

```text
host + pid + opaque process-incarnation identity
```

Incarnation identifierar den faktiska OS-processlivstiden.

- långlivad holder medan den lever skyddas även efter TTL;
- samma numeriska PID för en **annan** processlivstid är inte original holder;
- efter TTL får PID reuse ensam inte hindra reclaim;
- PID får finnas kvar för owner/display, men räcker inte som liveness authority.

Kontraktet föreskriver inte boot-id, process-start timestamp, procfs-fält, kernel-API eller serialiseringsrepresentation.

För deterministisk gate tillåts prepared incarnation-state analogt med befintliga clock-skew controls: ankra först genom verklig public acquire, bevara opaque incarnation-id, konstruera sedan motsvarande state där samma numeriska PID avser annan live process incarnation och kräv reclaim som för död original holder efter TTL. Inga source-string checks.

Kan detta inte mätas mekaniskt utan implementationsoracle ska test-author stoppa med exakt blocker.

## 5. Stale release / successor safety

Befintlig effekt kvarstår: stale generation får aldrig delete/mutate successor.

Gate ska också täcka overlap där stale operation pågår samtidigt som successor installeras:

- stale operation ska faila eller bli harmless;
- successor bytes/identity ska överleva.

Owner-controlled barrier i disposable test harness är tillåten om den behövs för deterministisk scheduling, men barriären blir aldrig production authority och får inte föreskriva production mechanism.

## 6. Component ownership

`h-004` builder-scope ska **inte** vidgas till `controller/attest/**`.

Ordningen är:

```text
h-003 owner gate hardening
→ h-003 builder inom controller/attest/**
→ independent review + mechanical owner gate + merge
→ färsk S3/h-004 builder från dåvarande authoritative main
```

h-004 konsumerar därefter det frysta generiska h-003 API:t.

## 7. Rejected S3 candidate

`1e21a7fe150f25626301f3656893d1798ae46c3d` förblir immutable historiskt evidence. Ingen framtida remediation staplas på den. Ny S3 startar från dåvarande authoritative main på ny builderbranch. Ingen amend/reset/rebase/history overwrite.

## 8. Budgets

h-004 `max_changed_files` och `max_added_lines` vidgas inte i denna owner-pass. Den gamla kandidatens additionsbudget ärvs inte från den; framtida fresh S3 mäts från sin nya authoritative base.

## 9. Owner-authorized test-author edit surface

Endast:

- `specs/tasks.spec.json` — endast befintliga h-003/h-004 task objects när nödvändigt;
- `verify/bin/h-003-exit`;
- `verify/bin/h-004-exit`;
- `docs/05-beslutslogg.md`;
- `docs/loop/drift.md` endast vid behov.

Ingen `controller/**` eller `tests/controller/**`. Ingen production implementation.

Preferred ownership split:

- **H003:** existing sequential semantics; serialized authoritative mutations; generic opaque authority generation; provisional/final validity; stale/invalidate ordering; no resurrection.
- **H004:** existing lease/heartbeat/fencing; process-incarnation holder identity; stale-operation/successor overlap; lease_id as h-003 authority-id; begin before publishable work; provisional write; clean release before finalize; no finalize after lease loss/release failure.

Efter controls ska authoritative-main h-003 vara RED för nya authority-controls av rätt orsak; h-004 ska fortsatt vara RED för saknade S3-funktioner och nya ärligt körbara controls. Environment/platform refusal är inte product RED.

Adversarial gate review ska bland annat försöka fälla vacuous implementations där authority-bound read alltid failar, begin invalidater allt globalt, finalize godtar valfritt id, provisional redan är valid, äldre writes resurrectar nyare state, failure returneras efter unsafe valid persistence, alla concurrent mutations bara failar, process-incarnation är ett meningslöst randomfält utan OS-lifetime-bindning eller stale release redan hunnit radera successor innan failure rapporteras.

Om effekterna kan frysas ärligt:

```text
FROZEN_GATE_READY=YES
BASELINE_RED_FOR_RIGHT_REASON=YES
OWNER_ARCHITECTURE_DECISION_REQUIRED=NO
```

Annars:

```text
FROZEN_GATE_READY=NO
OWNER_ARCHITECTURE_DECISION_REQUIRED=YES
MISSING_CONTRACT_BOUNDARY=<exact remaining boundary>
```
