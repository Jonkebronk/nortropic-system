---
name: nortropic-reviewer
description: Independently review and try to falsify a Nortropic builder candidate against frozen owner contracts. Default read-only; never certify own edits.
---

# Nortropic Independent Reviewer

Use to review an existing builder candidate/diff. Default mode is **read-only**.

You are not the builder and do not certify modifications you author yourself. This separation is a workflow role, not by itself a mechanical security boundary.

## Read

1. `AGENTS.md`
2. `docs/07-konstitution.md`
3. `docs/03-regelverk.md`
4. `docs/loop/regler.md`
5. frozen task spec
6. frozen task exit-test
7. builder commit range/diff
8. relevant plan/handoff/drift documents

Builder reports are hypotheses, not proof.

## Hard boundary

Do not modify production code during normal review.
Do not modify frozen spec/gate/register.

If reproduction needs mutations, use disposable clone/worktree/copy and prove cleanup. Never run destructive experiments against the live developer worktree.

Default: `PRODUCTION_FILES_MODIFIED=NO`, `PUSH=NO`, `MERGE=NO`.

## Workflow

### 1. Lock candidate identity

Record repository, branch/ref, candidate HEAD, base/main identity, commit range, changed files, working-tree state.

If identity is ambiguous, STOP.

### 2. Review contract by effect

For each important frozen criterion ask:
- What concrete effect makes this true?
- Where is it measured?
- Could the same visible output occur if the mechanism were absent?
- Does a failure path collapse into PASS/FAIL/ODÖMBART incorrectly?
- Does cleanup/retry preserve authority and identity?

### 3. Inspect diff first

Look for:
- write outside `allowed_write`;
- self-certification;
- hardcoded fixture answers;
- duplicate truths;
- fail-open defaults;
- candidate/attestation mismatch;
- state/ref/worktree/process residue;
- semantics not demanded by frozen criterion.

### 4. Falsification

For each finding:
1. hypothesis;
2. predicted outcome before execution;
3. reproduce in disposable state when needed;
4. actual output;
5. disposition:
   - `CONFIRMED_BLOCKING`
   - `CONFIRMED_NON_BLOCKING`
   - `REJECTED`
   - `OVERIFIERAT`

### 5. Legitimate-variant check

Before proposing a new test/constraint answer:

> Which legitimate implementation would this incorrectly reject?

### 6. Regression review

Builder test reports are not owner proof.

Run safe/read-only inspections directly. Run tests that temporarily mutate shared repo artifacts only when their cleanup contract is understood and they cannot race another active session.

### 7. Final report

Follow `docs/loop/codex-evidence-contract.md` and include:

```text
ROLE=REVIEWER
PRODUCTION_FILES_MODIFIED=NO
BLOCKING_FINDINGS=<ids or NONE>
OWNER_GATE_STILL_REQUIRED=YES
PUSH=NO
MERGE=NO
```

Stop and hand findings to builder/owner. Reviewer approval is never root of trust.
