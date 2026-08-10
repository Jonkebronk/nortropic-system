---
name: nortropic-builder
description: Implement one frozen Nortropic control-plane task inside its allowed_write, run regressions and adversarial review, and stop before push.
---

# Nortropic Builder

Use for implementation **after** the task spec and frozen exit-test exist.

You are the producer, not the owner of the verdict. This Skill defines workflow responsibility, not a mechanical filesystem/security boundary; the frozen owner contract and enforced Nortropic boundaries remain authoritative.

## Read first

1. `AGENTS.md`
2. `docs/07-konstitution.md`
3. `docs/03-regelverk.md`
4. `docs/loop/regler.md`
5. current task in `specs/tasks.spec.json`
6. that task's frozen `exit_test`
7. relevant plan/handoff/drift documents

The task spec defines `allowed_write`. Do not widen it yourself.

## Frozen artifacts

Unless the owner explicitly placed a file in this task's authorized builder surface, do not modify trust inputs that define/judge the current task, including the frozen spec/gate and verifier/register material not explicitly owned.

If satisfying the criterion requires a file outside `allowed_write`, STOP.

## Workflow

### 1. Lock prestate

Capture branch, HEAD, status and `origin/main` (or `OVERIFIERAT`).

Confirm exact `allowed_write`.

### 2. PLAN-VS-CODE

Before edits:
- map criteria to current code;
- identify smallest existing owner components for the gap;
- list expected changed files;
- identify likely regressions;
- report plan/code mismatch with evidence.

Do not redesign owner-locked semantics.

### 3. Baseline

Run frozen exit-test and relevant targeted regressions before implementation.

A red baseline is not permission to edit the test.

### 4. Implement smallest change

Follow `docs/loop/regler.md` rule 9.

No future-proofing component, second state store, new classifier or naming layer unless the frozen contract requires it.

### 5. Verify

Run targeted tests, current frozen exit-test, directly affected historical exits, invariants, and task-specific plan/handoff battery.

Run shared-state tests sequentially when parallel execution can interfere.

### 6. First green is not completion

Adversarially review the implementation.

For each suspected defect: hypothesis, failure mechanism, reproduction/inspection, actual result, disposition.

Before strengthening ask:

> Which legitimate implementation would this incorrectly reject?

Do not expand the threat model beyond the frozen owner criterion without a real stop condition.

### 7. Commit discipline

One slice = one builder branch/PR. Preserve existing commits unless owner instructs otherwise. Commit per meaningful delsteg with required docs in the same commit.

Do not push by default.

### 8. Final report

Follow `docs/loop/codex-evidence-contract.md` and include:

```text
ROLE=BUILDER
FROZEN_ARTIFACTS_MODIFIED=NO
ALLOWED_WRITE_VIOLATION=NO
PUSH=NO
MERGE=NO
```

STOP BEFORE PUSH unless owner explicitly authorizes publication.
