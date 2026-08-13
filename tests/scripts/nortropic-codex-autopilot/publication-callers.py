#!/usr/bin/env python3.12
"""Hermetic integration checks for all production publication callers."""

from __future__ import annotations

import hashlib
import json
import runpy
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts/nortropic-codex-autopilot.py"


def command(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], check=True,
                            text=True, capture_output=True)
    return result.stdout.strip()


def main() -> int:
    namespace = runpy.run_path(str(SCRIPT), run_name="publication_caller_test")
    original_publish = namespace["publish"]
    subject_globals = namespace["roadmap_contract_flow"].__globals__
    with tempfile.TemporaryDirectory(prefix="h035-publication-callers-") as raw:
        repo = Path(raw) / "repo"
        repo.mkdir()
        command(repo, "init", "-q")
        command(repo, "config", "user.email", "fixture@nortropic.invalid")
        command(repo, "config", "user.name", "fixture")
        (repo / "seed").write_text("base\n", encoding="utf-8")
        command(repo, "add", "seed")
        command(repo, "commit", "-qm", "base")
        base = command(repo, "rev-parse", "HEAD")
        command(repo, "checkout", "-qb", "candidate")
        tasks = {
            "spec_version": "2.0.0",
            "tasks": [
                {"id": "h-003", "exit_test": "verify/bin/h-003-exit"},
                {"id": "h-035", "exit_test": "verify/bin/h-035-exit"},
            ],
        }
        (repo / "specs").mkdir()
        (repo / "specs/tasks.spec.json").write_text(
            json.dumps(tasks, sort_keys=True) + "\n", encoding="utf-8")
        gates = {
            "verify/bin/h-003-exit": "#!/bin/sh\nexit 1\n",
            "verify/bin/h-035-exit": "#!/bin/sh\nexit 0\n",
            namespace["EMPIRICAL_GATE_PATH"]: "#!/bin/sh\nexit 1\n",
        }
        for relative, content in gates.items():
            target = repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        command(repo, "add", "specs", "verify")
        command(repo, "commit", "-qm", "candidate")
        candidate = command(repo, "rev-parse", "HEAD")
        changed = command(repo, "diff", "--name-only", f"{base}..{candidate}").splitlines()
        review = Path(raw) / "review.json"
        review.write_text('{"outcome":"READY","role":"REVIEWER"}\n', encoding="utf-8")
        review_run = namespace["AgentRun"](
            {"outcome": "READY", "owner_decision_required": False,
             "blocking_findings": []}, None, review, review)

        # Keep every tested flow on its real production control path while
        # replacing external agents, worktree management and publication with
        # deterministic local boundaries.
        subject_globals.update({
            "ensure_roadmap_plan": lambda _repo: None,
            "ensure_substitution_authority": lambda _repo: None,
            "origin_main": lambda _repo: base,
            "ensure_worktree": lambda *_args: repo,
            "detached_worktree": lambda *_args: repo,
            "remove_worktree": lambda *_args: None,
            "clean": lambda _repo: True,
            "journal": lambda *_args, **_kwargs: None,
            "run_codex_resolving_architecture": lambda *_args, **_kwargs: review_run,
            "run_invariants": lambda _repo: None,
            "assert_roadmap_test_author_scope": lambda *_args: changed,
            "assert_empirical_gate_author_scope": lambda *_args: changed,
            "assert_test_author_scope": lambda *_args: changed,
            "assert_builder_scope": lambda *_args: changed,
            "capture_green_gates": lambda *_args: {},
            "assert_final_gates": lambda *_args: None,
        })

        expected_gate = [""]
        reached: list[tuple[str, dict[str, str]]] = []

        def boundary(_repo: Path, _wt: Path, _branch: str, _base: str,
                     seen_candidate: str, _title: str, seen_changed: list[str], *,
                     publication_authority: dict[str, str]) -> str:
            assert seen_candidate == candidate
            assert sorted(seen_changed) == sorted(changed)
            assert publication_authority["gate_path"] == expected_gate[0]
            assert publication_authority["review_artifact_path"] == str(review.resolve())
            assert publication_authority["review_artifact_sha256"] == hashlib.sha256(
                review.read_bytes()).hexdigest()
            gate_bytes = subprocess.run(
                ["git", "-C", str(repo), "show", f"{candidate}:{expected_gate[0]}"],
                check=True, capture_output=True).stdout
            assert publication_authority["gate_sha256"] == hashlib.sha256(gate_bytes).hexdigest()
            reached.append((publication_authority["task_id"], publication_authority))
            return candidate

        subject_globals["publish"] = boundary
        subject_globals["run_gate"] = lambda *_args, **_kwargs: namespace["Cmd"](1, "red")
        subject_globals["run_empirical_gate"] = lambda *_args, **_kwargs: namespace["Cmd"](1, "red")

        expected_gate[0] = "verify/bin/h-035-exit"
        sl = namespace["RoadmapSlice"]("fixture", "h-035", "fixture",
                                       expected_gate[0], ())
        assert namespace["roadmap_contract_flow"](repo, Path(raw), sl) == candidate

        expected_gate[0] = namespace["EMPIRICAL_GATE_PATH"]
        assert namespace["empirical_gate_contract_flow"](repo, Path(raw)) == candidate

        expected_gate[0] = "verify/bin/h-003-exit"
        assert namespace["test_author_flow"](repo, Path(raw)) == candidate

        subject_globals["run_gate"] = lambda *_args, **_kwargs: namespace["Cmd"](0, "green")
        expected_gate[0] = "verify/bin/h-035-exit"
        assert namespace["builder_flow"](
            repo, Path(raw), "h-035", "candidate", "candidate", "fixture") == candidate
        assert [task for task, _authority in reached] == ["h-035", "L", "h-003", "h-035"]

        try:
            original_publish(repo, repo, "candidate", base, candidate, "fixture", changed)
        except TypeError:
            pass
        else:
            raise AssertionError("missing publication_authority did not reject")
        try:
            original_publish(repo, repo, "candidate", base, candidate, "fixture", changed,
                             publication_authority={})
        except namespace["Stop"]:
            pass
        else:
            raise AssertionError("wrong publication_authority did not reject")

    print("4 publication callers PASS; missing/wrong authority rejects PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
