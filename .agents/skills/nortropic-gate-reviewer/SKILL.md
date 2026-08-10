---
name: nortropic-gate-reviewer
description: Independently falsify an owner-authorized test-author candidate before a frozen gate is published. Read-only; never implement production code or repair and certify the same gate candidate.
---

# Nortropic Gate Reviewer

Use after `$nortropic-test-author` has produced an immutable local candidate commit and before publication of a changed spec/frozen gate.

This is workflow separation, never a security boundary. Owner authority and mechanical scope checks remain authoritative.

## Read first

1. `AGENTS.md`
2. `docs/07-konstitution.md`
3. `docs/03-regelverk.md`
4. `docs/loop/regler.md`
5. the exact owner-decision artifact named by the orchestrator
6. the test-author candidate commit/diff
7. relevant current task objects and gates

## Hard boundary

Read-only against the candidate. Do not modify production code, specs, gates or docs in the reviewed worktree.

Disposable mutants/copies are allowed only outside the candidate worktree and must be proven cleaned up.

## Review

1. Lock exact candidate SHA, base SHA, changed files and clean status.
2. Verify the candidate stayed inside the owner-authorized edit surface.
3. Review each new control by **effect**, not source shape.
4. Look for vacuous gates: all-fail implementations, always-valid implementations, hard-coded fixture answers, source-string or implementation-oracle checks, missing positive anchors, ambiguous rig/platform failures, tests that pass without exercising the claimed mechanism.
5. For concurrency/ordering controls, ask whether the test actually exposes the harmful schedule and whether a legitimate implementation can satisfy it without adopting one prescribed mechanism.
6. Preserve previous K controls unless the owner decision explicitly changes them.
7. Every proposed blocker needs hypothesis, predicted effect, reproduction/inspection evidence and disposition.

## Output

Use `docs/loop/codex-autopilot-report.schema.json` when invoked by the autopilot.

Set:

- `role=GATE_REVIEWER`;
- `outcome=READY` only when there are no confirmed blocking findings;
- `outcome=NEEDS_REMEDIATION` when a test-author correction can resolve the finding without a new owner decision;
- `outcome=OWNER_DECISION_REQUIRED` only when the existing owner contract is genuinely insufficient;
- `production_files_modified=false`;
- `changed_files=[]`.

Never push, merge or repair the candidate yourself.
