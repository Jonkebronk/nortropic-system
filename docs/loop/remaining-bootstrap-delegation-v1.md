# Remaining bootstrap delegation v1

**Owner decision:** 2026-08-13
**Scope:** H-035 → H-034 → H-033 → H-032 → H-031 → supervisor resume → first real autonomous launch.

This is workflow authority, not a second backlog, verdict store, or security boundary. The
canonical tasks remain solely in `specs/tasks.spec.json`; frozen gates and mechanically observed
effects remain trust authority. Source mandate SHA-256:
`f0092e8c394c7bd4b23ad2e9375462813fd1533ac2ba5cf50833019165994178`.

```text
OWNER_MANUAL_FINAL_APPROVAL_REQUIRED=NO
OWNER_FINAL_FREEZE_MAY_BE_EXECUTED_AUTONOMOUSLY=YES
OWNER_PUBLICATION_APPROVAL_REQUIRED=NO
OWNER_PR_APPROVAL_REQUIRED=NO
OWNER_MERGE_APPROVAL_REQUIRED=NO
OWNER_NEXT_TASK_APPROVAL_REQUIRED=NO
OWNER_SUPERVISOR_RESUME_APPROVAL_REQUIRED=NO
NO_FORCE_SEMANTICS=YES
SELF_CERTIFICATION_AS_PROOF=NO
```

The delegation applies only while every applicable mechanical prerequisite is proven: exact
task/spec/gate/base/candidate identity; current-authority lineage; exact file scope and denied-write
compliance; actual required gate/test/empirical results; independent review bound to the immutable
candidate with no unresolved actionable finding; clean worktree; and exact remote/PR identity.
Missing evidence rejects. Ordinary reviewer findings route to a new remediation candidate and fresh
review without a human scheduling stop.

## Guarded publication

Publication uses ordinary non-force push and GitHub's normal merge-commit method only. `--rebase`,
`--squash`, force, amend, reset, cherry-pick and every history rewrite are forbidden. Immediately
before merge the publisher fetches and atomically relocks all of:

- repository `Nortropic/nortropic-system` and base ref `main`;
- `origin/main` equal to the frozen base;
- clean worktree HEAD and candidate tree equal to the reviewed candidate;
- remote candidate branch equal to that candidate;
- open PR base/head refs and exact base/head SHAs;
- PR changed-file set equal to the mechanically approved set;
- current frozen gate/spec and review identities.

The single authorized merge command has method `gh pr merge --merge` and an exact head-commit guard.
Repository configuration permitting squash or rebase is not authority to use them. After GitHub
reports `state=MERGED` with non-null `mergedAt` and `mergeCommit`, the publisher fetches main and proves: returned merge SHA is a commit;
`origin/main` equals it; it has exactly two parents; parent 1 equals the frozen base; parent 2 equals
the reviewed candidate; and its tree equals the reviewed candidate tree. Any mismatch fails closed.

The frozen acceptance gate measures this as one effect-bound operation by invoking the production
publisher against real disposable Git repositories and a hermetic GitHub command boundary. A
returned SHA or the presence of publication-related source tokens is not evidence. The observed
chain must include the exact non-force candidate push; repository, base, head, PR and file relock
after that push and immediately before merge; `gh pr merge --merge --match-head-commit`; GitHub's
merged state; the fetched `origin/main`; two ordered parents; and the candidate-identical tree.
The publication request also binds task id, candidate Git-object task-spec and gate paths plus their
SHA-256 identities, and the immutable independent-review artifact path plus SHA-256. The publisher
must re-read all three identities in the immediate premerge relock. It uses only supported GitHub
fields (`state`, `mergedAt`, `mergeCommit`, `headRefOid`) and, after that response, itself executes
the fetch/main-equality, ordered-parent and candidate-tree proof. A caller, judge, or return value
performing those checks on its behalf is insufficient.
Every returned value must affect the publisher's decision: hostile main, parent-list and tree
responses reject even while the underlying disposable merge graph remains valid. Merely issuing
the full command sequence and discarding its outputs is not proof.
Acceptance installs the executable boundary before importing the publisher. Module-load aliases of
`subprocess.run`, `Popen`, `check_output`, `check_call` and `os.system` therefore cannot bypass the
trace. Git and GitHub remain available through those audited forms, including absolute Git paths;
an unexpected absolute executable is denied and rejects publication.
The audited Git/GitHub identities are fixed before module load by canonical path plus SHA-256.
Names are resolved only through the captured authoritative PATH; basename equality is insufficient.
Harness symlinks may resolve to those identities, but absolute fakes, PATH shadows, changed files
and byte-identical copies at a different canonical path are denied before execution.

The current observed GitHub protection is contextual evidence, not a replacement for the relock:
`enforce_admins=true`, force pushes/deletions disabled, no required linear history, and normal merge
commits supported. The publisher must re-read relevant external state at the transition.

## Stop boundary

No human click is required between the bounded bootstrap phases. A stop remains valid only for a
real higher-authority contradiction, unavailable external credential/capability, uncovered
destructive effect, proven architectural impossibility, or a novel material authority expansion.
Chat context and model/session/role claims never substitute for persisted Git/effect evidence.
