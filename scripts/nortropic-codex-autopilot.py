#!/usr/bin/env python3
"""Nortropic Codex Build Autopilot v2.

Unattended workflow executor for already owner-authorized control-plane work.
It never treats an agent's prose as trust authority: Git identity, scope checks,
frozen exit tests and independent reviewer identity drive transitions.

No force/amend/reset/rebase remediation semantics are implemented.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

EXPECTED_REPO = "Nortropic/nortropic-system"
OWNER_DECISION_PATH = "docs/loop/owner-h003-attestation-authority-v1.md"
REPORT_SCHEMA_PATH = "docs/loop/codex-autopilot-report.schema.json"
REJECTED_S3 = "1e21a7fe150f25626301f3656893d1798ae46c3d"

H003_GATE_SUBJECT = "[LOOP] ÄGARHAND: freeze h-003 attestation authority v1"
H003_BUILD_SUBJECT = "[LOOP] h-003: attestation authority protocol v1"
H004_BUILD_SUBJECT = "[LOOP] h-004: heartbeat generation integration v2"

TEST_AUTHOR_ALLOWED = {
    "specs/tasks.spec.json",
    "verify/bin/h-003-exit",
    "verify/bin/h-004-exit",
    "docs/05-beslutslogg.md",
    "docs/loop/drift.md",
}

FORBIDDEN_GIT_TOKENS = (
    "--force",
    "--force-with-lease",
    "--amend",
)


class Stop(RuntimeError):
    pass


@dataclass
class Cmd:
    rc: int
    out: str


@dataclass
class AgentRun:
    report: dict[str, Any]
    thread_id: str | None
    event_log: Path
    result_file: Path


def now_id() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def run(argv: list[str], cwd: Path | None = None, *, check: bool = True,
        timeout: int | None = None, env: dict[str, str] | None = None) -> Cmd:
    if not argv or not all(isinstance(x, str) and x for x in argv):
        raise Stop(f"invalid argv: {argv!r}")
    if argv[0] == "git":
        joined = " ".join(argv)
        if any(tok in joined for tok in FORBIDDEN_GIT_TOKENS):
            raise Stop(f"forbidden git semantics requested: {joined}")
        if len(argv) > 1 and argv[1] in {"reset", "rebase"}:
            raise Stop(f"history rewrite command forbidden: {joined}")
        if any(arg.startswith("+") for arg in argv[1:]):
            raise Stop(f"leading + refspec forbidden: {joined}")
    p = subprocess.run(
        argv,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=timeout,
        env=env,
    )
    if check and p.returncode != 0:
        raise Stop(f"command failed rc={p.returncode}: {' '.join(argv)}\n{p.stdout}")
    return Cmd(p.returncode, p.stdout)


def git(repo: Path, *args: str, check: bool = True, timeout: int | None = None) -> Cmd:
    return run(["git", *args], cwd=repo, check=check, timeout=timeout)


def clean(repo: Path) -> bool:
    return git(repo, "status", "--porcelain=v1", "--untracked-files=all").out.strip() == ""


def sha(repo: Path, ref: str = "HEAD") -> str:
    return git(repo, "rev-parse", ref).out.strip()


def branch(repo: Path) -> str:
    return git(repo, "branch", "--show-current").out.strip()


def changed_files(repo: Path, base_ref: str = "HEAD") -> list[str]:
    names: set[str] = set()
    # `git diff <commit>` compares the complete working tree/index view against that
    # commit, so it also gives cumulative PR scope when base_ref is the task base.
    for line in git(repo, "diff", "--name-only", base_ref).out.splitlines():
        if line.strip():
            names.add(line.strip())
    for line in git(repo, "diff", "--cached", "--name-only", base_ref).out.splitlines():
        if line.strip():
            names.add(line.strip())
    for line in git(repo, "ls-files", "--others", "--exclude-standard").out.splitlines():
        if line.strip():
            names.add(line.strip())
    return sorted(names)


def path_allowed(rel: str, patterns: Iterable[str]) -> bool:
    rel = rel.replace(os.sep, "/")
    for pat in patterns:
        pat = pat.replace(os.sep, "/")
        if pat.endswith("/**"):
            prefix = pat[:-3].rstrip("/")
            if rel == prefix or rel.startswith(prefix + "/"):
                return True
        if fnmatch.fnmatchcase(rel, pat):
            return True
    return False


def common_git_dir(repo: Path) -> Path:
    raw = git(repo, "rev-parse", "--git-common-dir").out.strip()
    p = Path(raw)
    return (repo / p).resolve() if not p.is_absolute() else p.resolve()


def journal_root(repo: Path) -> Path:
    p = common_git_dir(repo) / "nortropic-codex-autopilot"
    p.mkdir(parents=True, exist_ok=True)
    return p


def journal(repo: Path, event: str, **fields: Any) -> None:
    rec = {"ts": dt.datetime.now(dt.timezone.utc).isoformat(), "event": event, **fields}
    path = journal_root(repo) / "events.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"AUTOPILOT {event}: " + " ".join(f"{k}={v}" for k, v in fields.items()))


def load_spec(repo: Path) -> dict[str, Any]:
    try:
        data = json.loads((repo / "specs/tasks.spec.json").read_text(encoding="utf-8"))
    except Exception as e:
        raise Stop(f"cannot load tasks spec: {e}") from e
    if not isinstance(data, dict) or not isinstance(data.get("tasks"), list):
        raise Stop("tasks spec malformed")
    return data


def task_obj(repo: Path, task_id: str) -> dict[str, Any]:
    spec = load_spec(repo)
    hits = [t for t in spec["tasks"] if isinstance(t, dict) and t.get("id") == task_id]
    if len(hits) != 1:
        raise Stop(f"task {task_id} count={len(hits)}")
    return hits[0]


def task_limits(repo: Path, task: dict[str, Any]) -> tuple[int, int]:
    defaults = load_spec(repo).get("defaults", {})
    return (
        int(task.get("max_changed_files", defaults.get("max_changed_files", 8))),
        int(task.get("max_added_lines", defaults.get("max_added_lines", 600))),
    )


def added_lines(repo: Path, files: Iterable[str], base_ref: str = "HEAD") -> int:
    tracked = set(git(repo, "ls-files").out.splitlines())
    total = 0
    diff = git(repo, "diff", "--numstat", base_ref).out
    for line in diff.splitlines():
        parts = line.split("\t", 2)
        if len(parts) == 3 and parts[0].isdigit():
            total += int(parts[0])
    for rel in files:
        if rel not in tracked:
            p = repo / rel
            if p.is_file():
                try:
                    total += len(p.read_text(encoding="utf-8").splitlines())
                except UnicodeDecodeError:
                    raise Stop(f"untracked binary/undecodable file in candidate: {rel}")
    return total


def assert_builder_scope(repo: Path, task_id: str, task_base: str) -> list[str]:
    task = task_obj(repo, task_id)
    delta_files = changed_files(repo, "HEAD")
    files = changed_files(repo, task_base)
    allowed = task.get("allowed_write") or load_spec(repo).get("defaults", {}).get("allowed_write", [])
    bad = [f for f in files if not path_allowed(f, allowed)]
    if bad:
        raise Stop(f"ALLOWED_WRITE_VIOLATION task={task_id}: {bad}")
    max_files, max_lines = task_limits(repo, task)
    adds = added_lines(repo, files, task_base)
    if len(files) > max_files:
        raise Stop(f"file budget exceeded: {len(files)} > {max_files}")
    if adds > max_lines:
        raise Stop(f"added-line budget exceeded: {adds} > {max_lines}")
    git(repo, "diff", "--check")
    git(repo, "diff", "--cached", "--check")
    return delta_files


def assert_test_author_scope(repo: Path, base_sha: str) -> list[str]:
    files = changed_files(repo)
    bad = [f for f in files if f not in TEST_AUTHOR_ALLOWED]
    if bad:
        raise Stop(f"test-author write outside owner surface: {bad}")
    if any(f.startswith("controller/") or f.startswith("tests/controller/") for f in files):
        raise Stop("test-author modified production/test implementation")
    if "specs/tasks.spec.json" in files:
        base_raw = git(repo, "show", f"{base_sha}:specs/tasks.spec.json").out
        base = json.loads(base_raw)
        cur = json.loads((repo / "specs/tasks.spec.json").read_text(encoding="utf-8"))
        for key in set(base) | set(cur):
            if key == "tasks":
                continue
            if base.get(key) != cur.get(key):
                raise Stop(f"test-author modified top-level spec key {key}")
        bmap = {t["id"]: t for t in base["tasks"]}
        cmap = {t["id"]: t for t in cur["tasks"]}
        if set(bmap) != set(cmap):
            raise Stop("test-author changed task id set")
        for tid in bmap:
            if tid not in {"h-003", "h-004"} and bmap[tid] != cmap[tid]:
                raise Stop(f"test-author modified non-authorized task object {tid}")
    git(repo, "diff", "--check")
    return files


def run_gate(repo: Path, task_id: str, timeout: int = 1200) -> Cmd:
    task = task_obj(repo, task_id)
    rel = task.get("exit_test")
    if not isinstance(rel, str) or not rel:
        raise Stop(f"task {task_id} has no exit_test")
    p = repo / rel
    if not p.exists():
        raise Stop(f"exit_test missing for {task_id}: {rel}")
    cmd = [str(p)] if os.access(p, os.X_OK) else ["bash", str(p)]
    res = run(cmd, cwd=repo, check=False, timeout=timeout)
    journal(repo, "GATE", task=task_id, exit=res.rc, command=" ".join(cmd))
    return res


def run_invariants(repo: Path) -> Cmd | None:
    p = repo / "scripts/check-invariants.mjs"
    if not p.exists():
        return None
    res = run(["node", str(p)], cwd=repo, check=False, timeout=1200)
    journal(repo, "INVARIANTS", exit=res.rc)
    return res


def capture_green_gates(repo: Path) -> list[str]:
    spec = load_spec(repo)
    green: list[str] = []
    for t in spec["tasks"]:
        tid = t.get("id")
        if not isinstance(tid, str) or not isinstance(t.get("exit_test"), str):
            continue
        try:
            res = run_gate(repo, tid)
        except Stop as e:
            journal(repo, "BASELINE_GATE_UNJUDGEABLE", task=tid, reason=str(e))
            continue
        if res.rc == 0:
            green.append(tid)
    journal(repo, "BASELINE_GREEN_SET", tasks=green)
    return green


def assert_final_gates(repo: Path, task_id: str, baseline_green: Iterable[str]) -> None:
    current = run_gate(repo, task_id)
    if current.rc != 0:
        raise Stop(f"frozen task gate failed at final gate: {task_id} rc={current.rc}\n{current.out}")
    for tid in baseline_green:
        if tid == task_id:
            continue
        res = run_gate(repo, tid)
        if res.rc != 0:
            raise Stop(f"historically green gate regressed: {tid} rc={res.rc}\n{res.out}")
    inv = run_invariants(repo)
    if inv is not None and inv.rc != 0:
        raise Stop(f"invariants failed rc={inv.rc}\n{inv.out}")


def ensure_dependencies() -> None:
    for name in ("git", "gh", "codex", "node"):
        if shutil.which(name) is None:
            raise Stop(f"required executable missing: {name}")
    if sys.version_info < (3, 11):
        raise Stop(f"Python 3.11+ required, got {sys.version.split()[0]}")
    help_text = run(["codex", "exec", "--help"], check=False).out
    for flag in ("--json", "--output-schema"):
        if flag not in help_text:
            raise Stop(f"Codex CLI lacks required flag {flag}")
    global_help = run(["codex", "--help"], check=False).out
    for flag in ("--ask-for-approval", "--sandbox"):
        if flag not in global_help:
            raise Stop(f"Codex CLI lacks required global flag {flag}")
    run(["gh", "auth", "status"])


def repo_identity(repo: Path) -> str:
    out = run(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"], cwd=repo).out.strip()
    return out


def origin_main(repo: Path) -> str:
    git(repo, "fetch", "origin", "main")
    return sha(repo, "refs/remotes/origin/main")


def worktrees(repo: Path) -> list[dict[str, str]]:
    raw = git(repo, "worktree", "list", "--porcelain").out
    rows: list[dict[str, str]] = []
    cur: dict[str, str] = {}
    for line in raw.splitlines() + [""]:
        if not line:
            if cur:
                rows.append(cur)
            cur = {}
            continue
        key, _, val = line.partition(" ")
        cur[key] = val
    return rows


def local_branch_exists(repo: Path, name: str) -> bool:
    return git(repo, "show-ref", "--verify", "--quiet", f"refs/heads/{name}", check=False).rc == 0


def ensure_worktree(repo: Path, wt_root: Path, branch_name: str, base_sha: str,
                    dirname: str) -> Path:
    wt_root.mkdir(parents=True, exist_ok=True)
    wanted = (wt_root / dirname).resolve()
    for row in worktrees(repo):
        if row.get("branch") == f"refs/heads/{branch_name}":
            p = Path(row["worktree"]).resolve()
            if not clean(p):
                raise Stop(f"existing worktree for {branch_name} is dirty: {p}")
            head = sha(p)
            if head != base_sha:
                head_before_base = git(repo, "merge-base", "--is-ancestor", head, base_sha, check=False).rc == 0
                base_before_head = git(repo, "merge-base", "--is-ancestor", base_sha, head, check=False).rc == 0
                if head_before_base:
                    git(p, "merge", "--ff-only", base_sha)
                elif base_before_head:
                    # Clean descendant = an immutable candidate left by an interrupted
                    # orchestrator run. Keep it and re-run reviewer/final gates.
                    journal(repo, "RECOVER_CANDIDATE", branch=branch_name, base=base_sha, candidate=head)
                else:
                    raise Stop(f"existing branch {branch_name} diverges from required base: head={head} base={base_sha}")
            return p
    if wanted.exists() and any(wanted.iterdir()):
        raise Stop(f"wanted worktree path already non-empty: {wanted}")
    if local_branch_exists(repo, branch_name):
        git(repo, "worktree", "add", str(wanted), branch_name)
        if sha(wanted) != base_sha:
            head = sha(wanted)
            head_before_base = git(repo, "merge-base", "--is-ancestor", head, base_sha, check=False).rc == 0
            base_before_head = git(repo, "merge-base", "--is-ancestor", base_sha, head, check=False).rc == 0
            if head_before_base:
                git(wanted, "merge", "--ff-only", base_sha)
            elif base_before_head:
                journal(repo, "RECOVER_CANDIDATE", branch=branch_name, base=base_sha, candidate=head)
            else:
                raise Stop(f"local branch {branch_name} diverges from required base {base_sha}")
    else:
        git(repo, "worktree", "add", "-b", branch_name, str(wanted), base_sha)
    if not clean(wanted):
        raise Stop(f"new worktree is dirty: {wanted}")
    head = sha(wanted)
    if head != base_sha and git(repo, "merge-base", "--is-ancestor", base_sha, head, check=False).rc != 0:
        raise Stop(f"new worktree identity is neither base nor descendant candidate: {wanted} head={head} base={base_sha}")
    return wanted


def detached_worktree(repo: Path, wt_root: Path, name: str, commit_sha: str) -> Path:
    p = (wt_root / name).resolve()
    if p.exists():
        if any(p.iterdir()):
            raise Stop(f"review worktree path not empty: {p}")
    git(repo, "worktree", "add", "--detach", str(p), commit_sha)
    if sha(p) != commit_sha or not clean(p):
        raise Stop(f"detached reviewer identity mismatch: {p}")
    return p


def remove_worktree(repo: Path, p: Path) -> None:
    if p.exists() and not clean(p):
        raise Stop(f"refusing to remove dirty reviewer worktree: {p}")
    git(repo, "worktree", "remove", str(p))


def agent_prompt_common() -> str:
    return """
You are running under Nortropic Codex Operating Model v2.
Do not commit, push, open a PR, merge, reset, rebase, amend, force-push, or rewrite Git history.
The orchestrator owns Git trust transitions.
Use actual commands/evidence. PASS/FAIL only for tests actually run. Mark unknowns OVERIFIERAT.
Your final response MUST conform exactly to docs/loop/codex-autopilot-report.schema.json.
""".strip()


def run_codex(repo: Path, wt: Path, role: str, prompt: str) -> AgentRun:
    jr = journal_root(repo) / "runs" / f"{now_id()}-{role.lower()}"
    jr.mkdir(parents=True, exist_ok=False)
    events = jr / "events.jsonl"
    result = jr / "result.json"
    schema = wt / REPORT_SCHEMA_PATH
    if not schema.exists():
        raise Stop(f"report schema missing in worktree: {schema}")
    full_prompt = prompt.rstrip() + "\n\n" + agent_prompt_common()
    argv = [
        "codex",
        "-C", str(wt),
        "-a", "never",
        "--sandbox", "danger-full-access",
        "exec",
        "--json",
        "--output-schema", str(schema),
        "-o", str(result),
        full_prompt,
    ]
    journal(repo, "AGENT_START", role=role, worktree=str(wt), head=sha(wt))
    thread_id: str | None = None
    with events.open("w", encoding="utf-8") as log:
        p = subprocess.Popen(argv, cwd=str(wt), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        assert p.stdout is not None
        for line in p.stdout:
            sys.stdout.write(line)
            log.write(line)
            log.flush()
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if obj.get("type") == "thread.started" and isinstance(obj.get("thread_id"), str):
                thread_id = obj["thread_id"]
        rc = p.wait()
    if rc != 0:
        raise Stop(f"Codex role {role} failed rc={rc}; events={events}")
    try:
        report = json.loads(result.read_text(encoding="utf-8"))
    except Exception as e:
        raise Stop(f"Codex role {role} produced invalid structured result: {e}; file={result}") from e
    if report.get("role") != role:
        raise Stop(f"Codex role mismatch expected={role} got={report.get('role')}")
    journal(repo, "AGENT_END", role=role, outcome=report.get("outcome"), thread_id=thread_id or "OVERIFIERAT")
    return AgentRun(report, thread_id, events, result)


def report_blockers(report: dict[str, Any]) -> list[dict[str, str]]:
    raw = report.get("blocking_findings")
    return raw if isinstance(raw, list) else []


def blocker_digest(report: dict[str, Any]) -> str:
    relevant = [(x.get("id"), x.get("summary")) for x in report_blockers(report)]
    raw = json.dumps(relevant, ensure_ascii=False, sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()


def stage_and_commit(repo: Path, files: list[str], subject: str) -> str:
    if not files:
        raise Stop("candidate has no changed files")
    git(repo, "add", "--", *files)
    git(repo, "diff", "--cached", "--check")
    staged = [x for x in git(repo, "diff", "--cached", "--name-only").out.splitlines() if x]
    if sorted(staged) != sorted(files):
        raise Stop(f"staged file identity mismatch expected={files} actual={staged}")
    git(repo, "commit", "-m", subject)
    if not clean(repo):
        raise Stop("worktree dirty after candidate commit")
    c = sha(repo)
    journal(repo, "CANDIDATE_COMMIT", sha=c, subject=subject, files=files)
    return c


def reviewer_prompt(task_id: str, base_sha: str, candidate_sha: str) -> str:
    return f"""
Use `$nortropic-reviewer`.

Review task {task_id} against the frozen owner contract and frozen exit-test in this exact detached candidate.
BASE_SHA={base_sha}
CANDIDATE_SHA={candidate_sha}

Lock identity first. Inspect the complete base..candidate diff before accepting builder claims.
Try to falsify the implementation by effect, including concurrency/failure/cleanup paths relevant to the frozen criterion.
Run safe decisive tests where possible. Do not modify production files in this worktree.

Set outcome=READY only with no confirmed blocking findings.
Set outcome=NEEDS_REMEDIATION for confirmed blockers that the builder can fix inside current authority.
Set outcome=OWNER_DECISION_REQUIRED only for a genuine missing owner-contract boundary.
"""


def builder_prompt(task_id: str, base_sha: str, extra: str = "") -> str:
    return f"""
Use `$nortropic-builder`.

Implement/remediate frozen task {task_id} from the current branch.
TASK={task_id}
TASK_BASE_SHA={base_sha}

Read AGENTS.md, the current task object in specs/tasks.spec.json, its frozen exit_test, docs/loop/regler.md and relevant owner/drift documents.
Do PLAN-VS-CODE first. Stay strictly inside current allowed_write and budgets. Never modify the frozen spec/gate/register for this builder task.
Run targeted tests, the current frozen exit-test, directly affected historical regressions and adversarial self-review.
First green is not completion.

{extra}

Finish with outcome=READY only when the implementation is ready for the orchestrator's mechanical candidate gate. If authority is insufficient, return OWNER_DECISION_REQUIRED rather than widening it.
"""


def test_author_prompt() -> str:
    return f"""
Use `$nortropic-test-author`.

The owner architecture decision is already supplied in `{OWNER_DECISION_PATH}`. Treat it as the exact owner authorization for this pass.
Rejected historical S3 candidate: {REJECTED_S3}. It is evidence only and must never be adopted, amended, reset, rebased or published.

Prepare/harden the existing h-003 and h-004 frozen owner contracts exactly within the edit surface named in the owner-decision file. Do not modify controller/** or tests/controller/** and do not implement production code.

Requirements include generic opaque h-003 authority generations; provisional → finalize validity; serialized authoritative mutation ordering/no resurrection; future h-004 lease_id binding; process-incarnation liveness; stale-operation/successor overlap; preservation of previous K controls; truthful RED baselines; positive anchors and adversarial mutants.

If the owner decision is mechanically sufficient and the gates can be frozen honestly, set:
frozen_gate_ready=true, baseline_red_for_right_reason=true, owner_decision_required=false, outcome=READY.
If a contract boundary is genuinely missing, set outcome=OWNER_DECISION_REQUIRED and name it exactly in stop_reason.
"""


def gate_reviewer_prompt(base_sha: str, candidate_sha: str) -> str:
    return f"""
Use `$nortropic-gate-reviewer`.

Independently falsify the test-author candidate at exact CANDIDATE_SHA={candidate_sha} against BASE_SHA={base_sha} and `{OWNER_DECISION_PATH}`.
The candidate worktree is detached and must remain read-only.

Check owner edit-surface, preservation of old controls, positive anchors, mechanism-agnostic effect binding, RED reason honesty, concurrency scheduling strength, rig/platform separation and vacuous implementations listed by the owner decision.
Do not repair the gate yourself.
"""


def remediation_prompt(role: str, task_id: str | None, findings: list[dict[str, str]], base_sha: str) -> str:
    rendered = json.dumps(findings, ensure_ascii=False, indent=2)
    if role == "TEST_AUTHOR":
        return f"""
Use `$nortropic-test-author` again on the existing candidate branch. The independent gate reviewer confirmed these blockers:
{rendered}

BASE_SHA={base_sha}
Owner authority remains `{OWNER_DECISION_PATH}`. Make the smallest gate/spec correction inside the same owner-authorized edit surface. Do not implement production code and do not rewrite history. Re-run decisive RED/adversarial evidence and return the structured report.
"""
    assert task_id is not None
    return f"""
Use `$nortropic-builder` again for TASK={task_id}. The independent reviewer confirmed these blockers against the latest immutable candidate:
{rendered}

TASK_BASE_SHA={base_sha}
Make the smallest remediation inside the existing frozen task allowed_write. Do not modify frozen artifacts and do not rewrite history. Re-run decisive tests and adversarial review, then return the structured report.
"""


def publish(repo: Path, wt: Path, branch_name: str, base_sha: str, candidate_sha: str,
            title: str, changed: list[str]) -> str:
    if not clean(wt) or sha(wt) != candidate_sha:
        raise Stop("publication candidate identity/cleanliness mismatch")
    actual_main = origin_main(repo)
    if actual_main != base_sha:
        raise Stop(f"REMOTE_MAIN_CHANGED before push expected={base_sha} actual={actual_main}")
    git(wt, "push", "-u", "origin", branch_name)
    ls = git(repo, "ls-remote", "origin", f"refs/heads/{branch_name}").out.split()
    if not ls or ls[0] != candidate_sha:
        raise Stop(f"remote head mismatch after push expected={candidate_sha} got={ls[:1]}")
    body_dir = journal_root(repo) / "publish"
    body_dir.mkdir(exist_ok=True)
    body = body_dir / f"{now_id()}-{branch_name.replace('/', '-')}.md"
    body.write_text(
        "Nortropic Codex Operating Model v2 unattended publication.\n\n"
        f"- expected base: `{base_sha}`\n"
        f"- reviewed candidate: `{candidate_sha}`\n"
        f"- changed files: {len(changed)}\n"
        "- no force/amend/rebase remediation semantics used\n"
        "- frozen/mechanical gates were rerun by the orchestrator before push\n",
        encoding="utf-8",
    )
    existing = run([
        "gh", "pr", "view", branch_name,
        "--json", "number,headRefOid,headRefName,baseRefName,state,url",
    ], cwd=wt, check=False)
    if existing.rc == 0:
        journal(repo, "PR_REUSE", branch=branch_name)
        view = existing
    else:
        created = run([
            "gh", "pr", "create", "--base", "main", "--head", branch_name,
            "--title", title, "--body-file", str(body)
        ], cwd=wt)
        journal(repo, "PR_CREATE", branch=branch_name, output=created.out.strip())
        view = run([
            "gh", "pr", "view", branch_name,
            "--json", "number,headRefOid,headRefName,baseRefName,state,url",
        ], cwd=wt)
    meta = json.loads(view.out)
    if meta.get("headRefOid") != candidate_sha or meta.get("headRefName") != branch_name or meta.get("baseRefName") != "main":
        raise Stop(f"PR identity mismatch: {meta}")
    num = int(meta["number"])
    remote_files = [x for x in run(["gh", "pr", "diff", str(num), "--name-only"], cwd=wt).out.splitlines() if x]
    if sorted(remote_files) != sorted(changed):
        raise Stop(f"remote PR file set mismatch expected={changed} actual={remote_files}")
    if origin_main(repo) != base_sha:
        raise Stop("main changed during PR creation")
    merge_argv = [
        "gh", "pr", "merge", str(num), "--rebase",
        "--match-head-commit", candidate_sha, "--delete-branch"
    ]
    merge = run(merge_argv, cwd=wt, check=False)
    if merge.rc != 0:
        # Required checks may still be running. Wait for them if the repository has checks,
        # then retry the same expected-head guarded merge exactly once.
        checks = run(["gh", "pr", "checks", str(num), "--watch", "--fail-fast"], cwd=wt, check=False)
        if checks.rc != 0:
            raise Stop(
                f"guarded merge refused and required checks did not become green; "
                f"merge_rc={merge.rc} checks_rc={checks.rc}\nMERGE:\n{merge.out}\nCHECKS:\n{checks.out}"
            )
        if origin_main(repo) != base_sha:
            raise Stop("main changed while waiting for PR checks")
        merge = run(merge_argv, cwd=wt, check=False)
        if merge.rc != 0:
            raise Stop(f"guarded merge still refused after green checks rc={merge.rc}\n{merge.out}")
    deadline = time.time() + 4 * 60 * 60
    merged_sha = ""
    while time.time() < deadline:
        q = run([
            "gh", "pr", "view", str(num),
            "--json", "state,mergedAt,mergeCommit,headRefOid,url"
        ], cwd=wt)
        m = json.loads(q.out)
        if m.get("headRefOid") != candidate_sha:
            raise Stop(f"PR head moved while waiting for merge: {m}")
        if m.get("mergedAt"):
            mc = m.get("mergeCommit") or {}
            merged_sha = mc.get("oid") or ""
            break
        if str(m.get("state")).upper() == "CLOSED":
            raise Stop(f"PR closed without merge: {m}")
        time.sleep(20)
    if not merged_sha:
        raise Stop(f"merge wait timed out for PR #{num}")
    new_main = origin_main(repo)
    if new_main != merged_sha:
        # Rebase merge metadata should point at the resulting main commit. Fail if not exact.
        raise Stop(f"merged main identity mismatch PR mergeCommit={merged_sha} origin/main={new_main}")
    candidate_tree = sha(repo, f"{candidate_sha}^{{tree}}")
    merged_tree = sha(repo, f"{new_main}^{{tree}}")
    if candidate_tree != merged_tree:
        raise Stop(f"merged tree differs from reviewed candidate tree candidate={candidate_tree} main={merged_tree}")
    journal(repo, "MERGED", pr=num, candidate=candidate_sha, main=new_main, tree=merged_tree)
    return new_main


def test_author_flow(repo: Path, wt_root: Path) -> str:
    base = origin_main(repo)
    wt = ensure_worktree(repo, wt_root, "owner/h-003-attestation-validity-v1", base,
                         "owner-h003-attestation-validity")
    if not clean(wt):
        raise Stop("test-author worktree dirty before agent/recovery")
    head = sha(wt)
    if head == base:
        agent = run_codex(repo, wt, "TEST_AUTHOR", test_author_prompt())
        if sha(wt) != base:
            raise Stop("test-author changed Git history; orchestrator requires uncommitted candidate bytes")
        r = agent.report
        if r.get("owner_decision_required") or r.get("outcome") == "OWNER_DECISION_REQUIRED":
            raise Stop(f"OWNER_DECISION_REQUIRED: {r.get('stop_reason')}")
        if r.get("outcome") != "READY" or r.get("frozen_gate_ready") is not True or r.get("baseline_red_for_right_reason") is not True:
            raise Stop(f"test-author did not establish freeze-ready state: {r}")
        files = assert_test_author_scope(wt, base)
        if not files:
            raise Stop("test-author reported READY but changed no owner artifacts")
        # Product should remain RED for the new owner controls at this point.
        h3 = run_gate(wt, "h-003")
        h4 = run_gate(wt, "h-004")
        if h3.rc != 1:
            raise Stop(f"h-003 owner-gate baseline must be product RED exit 1, got {h3.rc}")
        if h4.rc != 1:
            raise Stop(f"h-004 owner-gate baseline must be product RED exit 1, got {h4.rc}")
        candidate = stage_and_commit(wt, files, H003_GATE_SUBJECT)
    else:
        if git(repo, "merge-base", "--is-ancestor", base, head, check=False).rc != 0:
            raise Stop(f"test-author recovery candidate is not based on current main: {head}")
        candidate = head
        cumulative = assert_test_author_scope(wt, base)
        if not cumulative:
            raise Stop("test-author recovery branch is ahead of base with no owner-surface diff")
        h3 = run_gate(wt, "h-003")
        h4 = run_gate(wt, "h-004")
        if h3.rc != 1 or h4.rc != 1:
            raise Stop(f"recovered test-author candidate must preserve product RED h-003/h-004, got {h3.rc}/{h4.rc}")
        journal(repo, "RECOVER_TEST_AUTHOR_CANDIDATE", candidate=candidate)
    seen: list[str] = []
    while True:
        rvwt = detached_worktree(repo, wt_root, f"gate-review-h003-{candidate[:12]}", candidate)
        try:
            review = run_codex(repo, rvwt, "GATE_REVIEWER", gate_reviewer_prompt(base, candidate)).report
            if not clean(rvwt):
                raise Stop("gate reviewer modified reviewed worktree")
        finally:
            if rvwt.exists() and clean(rvwt):
                remove_worktree(repo, rvwt)
        if review.get("owner_decision_required") or review.get("outcome") == "OWNER_DECISION_REQUIRED":
            raise Stop(f"OWNER_DECISION_REQUIRED from gate reviewer: {review.get('stop_reason')}")
        blockers = report_blockers(review)
        if review.get("outcome") == "READY" and not blockers:
            break
        if not blockers:
            raise Stop(f"gate reviewer outcome not READY but no actionable blockers: {review}")
        dg = blocker_digest(review)
        seen.append(dg)
        if len(seen) >= 3 and len(set(seen[-3:])) == 1:
            raise Stop("NO_PROGRESS: identical gate-review blockers repeated three consecutive candidates")
        if sha(wt) != candidate or not clean(wt):
            raise Stop("test-author remediation prestate changed unexpectedly")
        remediation = run_codex(repo, wt, "TEST_AUTHOR", remediation_prompt("TEST_AUTHOR", None, blockers, base)).report
        if sha(wt) != candidate:
            raise Stop("test-author remediation changed Git history")
        if remediation.get("owner_decision_required"):
            raise Stop(f"OWNER_DECISION_REQUIRED during test-author remediation: {remediation.get('stop_reason')}")
        if remediation.get("outcome") != "READY":
            raise Stop(f"test-author remediation not ready: {remediation}")
        files = assert_test_author_scope(wt, candidate)
        if not files:
            raise Stop("NO_PROGRESS: test-author remediation made no changes")
        candidate = stage_and_commit(wt, files, "[LOOP] ÄGARHAND: remediate h-003 authority gate review")
    # Final owner gate: exact candidate, no production changes, RED expected, invariants unchanged.
    if not clean(wt) or sha(wt) != candidate:
        raise Stop("test-author final identity mismatch")
    h3 = run_gate(wt, "h-003")
    h4 = run_gate(wt, "h-004")
    if h3.rc != 1 or h4.rc != 1:
        raise Stop(f"test-author final RED baselines must both be exit 1, got h-003={h3.rc} h-004={h4.rc}")
    inv = run_invariants(wt)
    if inv is not None and inv.rc != 0:
        raise Stop(f"invariants regressed in owner gate candidate: {inv.out}")
    changed = [x for x in git(wt, "diff", "--name-only", f"{base}..{candidate}").out.splitlines() if x]
    new_main = publish(repo, wt, branch(wt), base, candidate,
                       "[LOOP] ÄGARHAND: freeze h-003 attestation authority v1", changed)
    return new_main


def builder_flow(repo: Path, wt_root: Path, task_id: str, branch_name: str, dirname: str,
                 subject: str, extra: str = "") -> str:
    base = origin_main(repo)
    wt = ensure_worktree(repo, wt_root, branch_name, base, dirname)
    if not clean(wt):
        raise Stop(f"builder worktree dirty at prestate task={task_id}")
    head = sha(wt)
    if head == base:
        baseline_green = capture_green_gates(wt)
        if not clean(wt):
            raise Stop(f"baseline gate battery left builder worktree dirty task={task_id}")
        baseline_current = run_gate(wt, task_id)
        if baseline_current.rc == 0:
            journal(repo, "TASK_ALREADY_GREEN", task=task_id, base=base)
            return base
        if baseline_current.rc != 1:
            raise Stop(f"task gate is not judgeable product RED; task={task_id} exit={baseline_current.rc}")
        agent = run_codex(repo, wt, "BUILDER", builder_prompt(task_id, base, extra)).report
        if sha(wt) != base:
            raise Stop(f"builder changed Git history task={task_id}; candidate must remain uncommitted")
        if agent.get("owner_decision_required") or agent.get("outcome") == "OWNER_DECISION_REQUIRED":
            raise Stop(f"OWNER_DECISION_REQUIRED task={task_id}: {agent.get('stop_reason')}")
        if agent.get("outcome") not in {"READY", "NO_CHANGES"}:
            raise Stop(f"builder not ready task={task_id}: {agent}")
        files = assert_builder_scope(wt, task_id, base)
        if not files:
            raise Stop(f"builder returned ready but made no changes while gate is red: {task_id}")
        gate = run_gate(wt, task_id)
        if gate.rc != 0:
            raise Stop(f"builder candidate is not green against frozen gate task={task_id} rc={gate.rc}\n{gate.out}")
        candidate = stage_and_commit(wt, files, subject)
    else:
        if git(repo, "merge-base", "--is-ancestor", base, head, check=False).rc != 0:
            raise Stop(f"recovered builder candidate is not based on current main task={task_id}: {head}")
        # Recompute historical-green baseline at the exact task base, not at the recovered candidate.
        bw = detached_worktree(repo, wt_root, f"baseline-{task_id}-{base[:12]}-{now_id()}", base)
        try:
            baseline_green = capture_green_gates(bw)
        finally:
            if bw.exists() and clean(bw):
                remove_worktree(repo, bw)
        assert_builder_scope(wt, task_id, base)
        gate = run_gate(wt, task_id)
        if gate.rc != 0:
            raise Stop(f"recovered candidate is not green task={task_id} rc={gate.rc}\n{gate.out}")
        candidate = head
        journal(repo, "RECOVER_BUILDER_CANDIDATE", task=task_id, candidate=candidate)
    seen: list[str] = []
    while True:
        rvwt = detached_worktree(repo, wt_root, f"review-{task_id}-{candidate[:12]}", candidate)
        try:
            review = run_codex(repo, rvwt, "REVIEWER", reviewer_prompt(task_id, base, candidate)).report
            if not clean(rvwt):
                raise Stop(f"reviewer modified candidate worktree task={task_id}")
        finally:
            if rvwt.exists() and clean(rvwt):
                remove_worktree(repo, rvwt)
        if review.get("owner_decision_required") or review.get("outcome") == "OWNER_DECISION_REQUIRED":
            raise Stop(f"OWNER_DECISION_REQUIRED from reviewer task={task_id}: {review.get('stop_reason')}")
        blockers = report_blockers(review)
        if review.get("outcome") == "READY" and not blockers:
            break
        if not blockers:
            raise Stop(f"reviewer not READY but no blockers task={task_id}: {review}")
        dg = blocker_digest(review)
        seen.append(dg)
        if len(seen) >= 3 and len(set(seen[-3:])) == 1:
            raise Stop(f"NO_PROGRESS task={task_id}: identical blockers repeated three consecutive candidates")
        if sha(wt) != candidate or not clean(wt):
            raise Stop(f"builder remediation prestate changed unexpectedly task={task_id}")
        rem = run_codex(repo, wt, "BUILDER", remediation_prompt("BUILDER", task_id, blockers, base)).report
        if sha(wt) != candidate:
            raise Stop(f"builder remediation changed Git history task={task_id}")
        if rem.get("owner_decision_required"):
            raise Stop(f"OWNER_DECISION_REQUIRED during remediation task={task_id}: {rem.get('stop_reason')}")
        if rem.get("outcome") != "READY":
            raise Stop(f"builder remediation not READY task={task_id}: {rem}")
        files = assert_builder_scope(wt, task_id, base)
        if not files:
            raise Stop(f"NO_PROGRESS task={task_id}: remediation made no changes")
        gate = run_gate(wt, task_id)
        if gate.rc != 0:
            raise Stop(f"remediation remains red task={task_id} rc={gate.rc}\n{gate.out}")
        candidate = stage_and_commit(wt, files, f"[LOOP] {task_id}: remediate independent review")
    assert_final_gates(wt, task_id, baseline_green)
    if origin_main(repo) != base:
        raise Stop(f"REMOTE_MAIN_CHANGED before publication task={task_id}")
    changed = [x for x in git(wt, "diff", "--name-only", f"{base}..{candidate}").out.splitlines() if x]
    return publish(repo, wt, branch_name, base, candidate, subject, changed)


def main_has_subject(repo: Path, subject: str) -> bool:
    out = git(repo, "log", "refs/remotes/origin/main", "--format=%s", "--fixed-strings", "--grep", subject).out
    return any(line.strip() == subject for line in out.splitlines())


def scan_gate_state(repo: Path, wt_root: Path) -> tuple[dict[str, int], dict[str, Any], Path]:
    base = origin_main(repo)
    scan = detached_worktree(repo, wt_root, f"scan-{base[:12]}-{now_id()}", base)
    spec = load_spec(scan)
    statuses: dict[str, int] = {}
    for t in spec["tasks"]:
        tid = t.get("id")
        if isinstance(tid, str) and isinstance(t.get("exit_test"), str):
            try:
                statuses[tid] = run_gate(scan, tid).rc
            except Stop:
                statuses[tid] = 125
    return statuses, spec, scan


def drain(repo: Path, wt_root: Path) -> None:
    while True:
        statuses, spec, scan = scan_gate_state(repo, wt_root)
        try:
            green = {tid for tid, rc in statuses.items() if rc == 0}
            red = [t for t in spec["tasks"] if isinstance(t.get("id"), str) and statuses.get(t["id"], 125) == 1]
            unjudgeable = {tid: rc for tid, rc in statuses.items() if rc not in {0, 1}}
            if unjudgeable:
                raise Stop(f"DRAIN_UNJUDGEABLE_GATES: {unjudgeable}")
            if not red:
                journal(repo, "DRAIN_COMPLETE", green=sorted(green))
                return
            eligible: list[dict[str, Any]] = []
            for t in red:
                deps = t.get("depends_on") or []
                if all(d in green for d in deps):
                    eligible.append(t)
            if not eligible:
                unresolved = {t["id"]: t.get("depends_on", []) for t in red}
                raise Stop(f"BLOCKED_NO_ELIGIBLE_TASK: {unresolved}")
            task = eligible[0]
            tid = task["id"]
            # h-003/h-004 are handled by the explicit bootstrap chain.
            if tid in {"h-003", "h-004"}:
                raise Stop(f"bootstrap task still red after bootstrap chain: {tid}")
        finally:
            if scan.exists() and clean(scan):
                remove_worktree(repo, scan)
        journal(repo, "DRAIN_PICK", task=tid)
        builder_flow(
            repo, wt_root, tid,
            f"nortropic/auto-{tid}-v2",
            f"auto-{tid}-builder-v2",
            f"[LOOP] {tid}: Codex autopilot remediation",
        )


def bootstrap(repo: Path, wt_root: Path, do_drain: bool) -> None:
    ensure_dependencies()
    if repo_identity(repo) != EXPECTED_REPO:
        raise Stop(f"wrong repository: {repo_identity(repo)}")
    base = origin_main(repo)
    journal(repo, "BOOTSTRAP_RECONCILE", origin_main=base, rejected_s3=REJECTED_S3)
    owner_on_main = git(repo, "cat-file", "-e", f"refs/remotes/origin/main:{OWNER_DECISION_PATH}", check=False)
    if owner_on_main.rc != 0:
        raise Stop(f"owner decision artifact missing from authoritative origin/main: {OWNER_DECISION_PATH}")
    if not main_has_subject(repo, H003_GATE_SUBJECT):
        test_author_flow(repo, wt_root)
    else:
        journal(repo, "BOOTSTRAP_STAGE_SKIP", stage="h003_gate", reason="merge subject present on origin/main")
    if not main_has_subject(repo, H003_BUILD_SUBJECT):
        builder_flow(
            repo, wt_root, "h-003",
            "nortropic/auto-h-003-attestation-authority-v1",
            "h003-attestation-authority-builder-v1",
            H003_BUILD_SUBJECT,
            extra=f"Implement the generic authority protocol frozen from `{OWNER_DECISION_PATH}`. Do not touch h-004 implementation here.",
        )
    else:
        journal(repo, "BOOTSTRAP_STAGE_SKIP", stage="h003_builder", reason="merge subject present on origin/main")
    if not main_has_subject(repo, H004_BUILD_SUBJECT):
        if git(repo, "merge-base", "--is-ancestor", REJECTED_S3, "refs/remotes/origin/main", check=False).rc == 0:
            raise Stop(f"rejected S3 candidate unexpectedly appears in authoritative main ancestry: {REJECTED_S3}")
        builder_flow(
            repo, wt_root, "h-004",
            "nortropic/s3-h-004-heartbeat-v2",
            "s3-h004-heartbeat-builder-v2",
            H004_BUILD_SUBJECT,
            extra=(
                f"This is a FRESH S3 candidate from current origin/main. Never reuse rejected candidate {REJECTED_S3}. "
                f"Consume the frozen generic h-003 authority API from `{OWNER_DECISION_PATH}` and preserve h-004 allowed_write/budgets."
            ),
        )
    else:
        journal(repo, "BOOTSTRAP_STAGE_SKIP", stage="h004_builder", reason="merge subject present on origin/main")
    if do_drain:
        drain(repo, wt_root)
    else:
        journal(repo, "BOOTSTRAP_COMPLETE", drain="disabled")


def doctor(repo: Path) -> None:
    ensure_dependencies()
    ident = repo_identity(repo)
    if ident != EXPECTED_REPO:
        raise Stop(f"wrong repository: {ident}")
    om = origin_main(repo)
    print(f"DOCTOR=PASS\nREPOSITORY={ident}\nORIGIN_MAIN={om}\nCODEX_FULL_ACCESS_MODE=danger-full-access\nAPPROVAL_POLICY=never")


def acquire_lock(repo: Path):
    lock_path = common_git_dir(repo) / "nortropic-codex-autopilot.lock"
    f = lock_path.open("w")
    try:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as e:
        raise Stop(f"another Nortropic Codex autopilot is already running: {lock_path}") from e
    f.write(f"pid={os.getpid()} started={dt.datetime.now().isoformat()}\n")
    f.flush()
    return f


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Nortropic Codex Build Autopilot v2")
    p.add_argument("--repo", default=str(Path.home() / "nortropic/nortropic-system"))
    p.add_argument("--worktrees", default=str(Path.home() / "nortropic/worktrees"))
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor")
    r = sub.add_parser("run")
    r.add_argument("--no-drain", action="store_true", help="stop after explicit h-003→h-004 bootstrap chain")
    return p.parse_args()


def main() -> int:
    a = parse_args()
    repo = Path(a.repo).expanduser().resolve()
    wt_root = Path(a.worktrees).expanduser().resolve()
    if not repo.exists():
        print(f"AUTOPILOT_BLOCKED: repo missing: {repo}", file=sys.stderr)
        return 2
    try:
        if a.cmd == "doctor":
            doctor(repo)
            return 0
        lock = acquire_lock(repo)
        try:
            bootstrap(repo, wt_root, not a.no_drain)
        finally:
            lock.close()
        return 0
    except Stop as e:
        try:
            journal(repo, "BLOCKED", reason=str(e))
        except Exception:
            pass
        print(f"AUTOPILOT_BLOCKED: {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("AUTOPILOT_INTERRUPTED", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
