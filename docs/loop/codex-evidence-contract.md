# Codex evidence contract — report format, never authority

**Purpose:** standardize Codex role reports so the owner can verify facts quickly.

This file is **not** scheduler state, task doneness, a verdict store, an attestation, or a substitute for any frozen exit-test. Git, controller-authoritative stores and frozen gates remain evidence sources.

## Rollseparation

Codex-rollerna i `.agents/skills/` är en arbetsmodell:

```text
CODEX_ROLE_SEPARATION=WORKFLOW
CODEX_ROLE_SEPARATION_IS_SECURITY_BOUNDARY=NO
```

En rapport får aldrig använda `ROLE=...`, en separat Codex-tråd eller ett separat worktree
som mekaniskt bevis för att en viss fil varit otillgänglig. Sådant bevis måste komma från
den faktiska write-/sandbox-/controllergränsen eller från det frysta owner-testet.

## Status vocabulary

- `PROVEN` — supported by command/file/SHA evidence from the same session.
- `OVERIFIERAT` — not established.
- `NOT_RUN` — deliberately not executed.
- `PASS` / `FAIL` — only for an executed gate/test with command and exit code.

No percentages.

## Required identity

```text
ROLE=TEST_AUTHOR|BUILDER|REVIEWER
REPOSITORY=<owner/repo>
BRANCH=<branch/ref>
BASE_SHA=<sha|OVERIFIERAT>
HEAD_SHA=<sha>
ORIGIN_MAIN_SHA=<sha|OVERIFIERAT>
WORKTREE_STATUS=<CLEAN|DIRTY>
PUSH=NO|YES
MERGE=NO|YES
```

If dirty:

```text
UNCOMMITTED_FILES=
  <path>
```

## Commit / diff

```text
COMMITS=
  <sha> <subject>

CHANGED_FILES=
  <path>

ALLOWED_WRITE_VIOLATION=NO|YES|OVERIFIERAT
FROZEN_ARTIFACTS_MODIFIED=NO|YES|NOT_APPLICABLE
```

For a builder, `FROZEN_ARTIFACTS_MODIFIED=YES` is a stop condition unless the current owner-authorized task explicitly owns that artifact.

## Test evidence

```text
TEST=<stable name>
COMMAND=<exact command>
EXIT=<integer>
RESULT=PASS|FAIL
DECISIVE_EVIDENCE=<short exact output/effect or evidence path>
```

If not run:

```text
TEST=<name>
RESULT=NOT_RUN
REASON=<why>
```

Never convert `NOT_RUN` or `OVERIFIERAT` to PASS.

## Adversarial findings

```text
FINDING_ID=<stable local id>
HYPOTHESIS=<what may be wrong>
PREDICTED_EFFECT=<written before reproduction when executed>
EVIDENCE=<command/path/diff and actual result>
DISPOSITION=CONFIRMED_BLOCKING|CONFIRMED_NON_BLOCKING|REJECTED|OVERIFIERAT
```

## Stop conditions

```text
STOP_CONDITION_ACTIVE=YES|NO
STOP_REASON=<reason|NONE>
OWNER_DECISION_REQUIRED=YES|NO
```

## Role closeout

Test author:

```text
FROZEN_GATE_READY=YES|NO
BASELINE_RED_FOR_RIGHT_REASON=YES|NO|OVERIFIERAT
PRODUCTION_IMPLEMENTATION_WRITTEN=NO
PUSH=NO
MERGE=NO
```

Builder:

```text
FROZEN_ARTIFACTS_MODIFIED=NO
ALLOWED_WRITE_VIOLATION=NO
OWNER_GATE_REQUIRED=YES
PUSH=NO
MERGE=NO
```

Reviewer:

```text
PRODUCTION_FILES_MODIFIED=NO
BLOCKING_FINDINGS=<ids or NONE>
OWNER_GATE_STILL_REQUIRED=YES
PUSH=NO
MERGE=NO
```

## Owner interpretation

The report reduces coordination cost. It does **not** remove the owner gate.

Before a trust-relevant push/merge, owner reproduces decisive frozen gates in the intended owner environment and verifies candidate identity/diff scope.
