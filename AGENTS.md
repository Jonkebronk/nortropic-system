# Codex i nortropic-system

Detta är en **router**, inte ett nytt regelverk.

## Auktoritet

Läs och följ i denna ordning när de är relevanta:

1. `docs/07-konstitution.md`
2. `docs/03-regelverk.md`
3. `docs/loop/regler.md` för kontrollplansbygget
4. aktuell task i `specs/tasks.spec.json`
5. taskens frysta `exit_test`
6. relevanta plan- och driftdokument

Vid konflikt gäller den högre auktoriteten. Återge inte reglerna här; peka på källan.

## Repoidentitet före arbete

Innan en ändring som kan påverka Git- eller trust-state:

```bash
git branch --show-current
git rev-parse HEAD
git status --short
git rev-parse origin/main
```

Om remote inte kan kontrolleras: skriv `ORIGIN_MAIN=OVERIFIERAT`; gissa aldrig.

Ingen force-semantik: varken `--force`, `--force-with-lease`, ledande `+` i refspec eller history overwrite.

## Rollseparation

En Codex-tråd/worktree har **en** roll åt gången:

- `$nortropic-test-author` — owner-begärd spec/acceptance-gate-förberedelse. Ingen produktionsimplementation.
- `$nortropic-builder` — implementerar en redan fryst task inom `allowed_write`. Ändrar aldrig sin egen frysta spec/gate.
- `$nortropic-reviewer` — oberoende, normalt read-only, försöker falsifiera builderkandidaten.

Blanda inte roller i samma tråd bara för att spara tid. Om ett uppdrag kräver byte av trustroll: stoppa och rapportera.

## Vad rollseparationen ÄR

Rollerna ovan är **workflow-separation**, inte en mekanisk säkerhetsgräns.

```text
CODEX_ROLE_SEPARATION=WORKFLOW
CODEX_ROLE_SEPARATION_IS_SECURITY_BOUNDARY=NO
FROZEN_OWNER_GATES_REMAIN_TRUST_AUTHORITY=YES
OWNER_GATE_REQUIRED=YES
```

Skills och separata Codex-trådar/worktrees minskar rollblandning och koordinationskostnad,
men de ersätter inte Nortropics mekaniska `allowed_write`, sandbox, frozen exit-test,
attestation eller owner-gates.

En Codex-roll får därför aldrig använda sin Skill som bevis för att en fil faktiskt var
mekaniskt otillgänglig.

## Evidence

Slutrapporten ska följa `docs/loop/codex-evidence-contract.md`.

Codex egen utsaga är inte owner-bevis. Ett grönt exit-test rapporteras med faktiskt kommando + exitkod. Overifierat märks `OVERIFIERAT`.

## Push / merge

Standard är:

```text
PUSH=NO
MERGE=NO
```

Pusha eller merga endast när användaren uttryckligen har gett den befogenheten för den aktuella fasen och projektets gates tillåter det.

<!-- CODEX-OPERATING-MODEL-V2 -->
## Codex operating model v2 — stående owner-befogenhet för mekanisk exekvering

Owner har 2026-08-10 uttryckligen auktoriserat `scripts/nortropic-codex-autopilot.py` att vara den mekaniska exekveraren för redan owner-auktoriserat kontrollplansarbete.

```text
OWNER_AUTHORITY_REQUIRED=YES
HUMAN_OWNER_PRESENT_PER_TASK=NO
OWNER_GATE_EXECUTOR=MECHANICAL
FROZEN_OWNER_GATES_REMAIN_TRUST_AUTHORITY=YES
```

Detta ändrar inte auktoritetsordningen ovan och gör inte Codex-prosa till trust authority. Rollagenterna committar/pushar/mergar fortfarande inte. Autopiloten får däremot, efter sina mekaniska identity/scope/gate/reviewer-kontroller, skapa immutable candidate commits, publicera, skapa PR och rebase-merga med expected-head-guard utan ny interaktiv owner-prompt per transition.

En verklig ny policy-/arkitekturfråga, odömbart gateutfall, oväntad remote-identity eller no-progress stoppar fortfarande fail-closed.
