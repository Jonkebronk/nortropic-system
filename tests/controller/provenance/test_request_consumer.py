#!/usr/bin/python3
import importlib.machinery
import importlib.util
import json
import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
CLI = ROOT / "controller/provenance/cli"


def load_cli():
    loader = importlib.machinery.SourceFileLoader("h033_consumer_cli", str(CLI))
    spec = importlib.util.spec_from_loader("h033_consumer_cli", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class RequestConsumerTests(unittest.TestCase):
    def setUp(self):
        self.cli = load_cli()
        self.temp = tempfile.TemporaryDirectory(prefix="h033-consumer-")
        self.root = Path(self.temp.name)
        self.bin = self.root / "bin"
        self.state = self.root / "state"
        self.bin.mkdir(); self.state.mkdir()
        self.service = self.bin / "request-consumer"
        self.candidate = "1" * 40
        self.common = {"task": "h-033", "candidate": self.candidate,
                       "task-spec-sha256": "2" * 64, "gate-sha256": "3" * 64,
                       "probe": "h033-auth-pass-v1", "require-result": "PASS"}
        tokens = {character * 64: self.common for character in "acde"}
        source = """#!/usr/bin/python3
import json, os, sys
ROOT = %r
TOKENS = %r
ORDER = ["request-id", "task", "candidate", "task-spec-sha256", "gate-sha256", "probe", "require-result"]
if len(sys.argv) != 16 or sys.argv[1] != "consume": raise SystemExit(1)
raw = sys.argv[2:]
if raw[::2] != ["--" + key for key in ORDER]: raise SystemExit(1)
values = dict(zip(ORDER, raw[1::2]))
expected = TOKENS.get(values["request-id"])
if expected is None or any(values[key] != value for key, value in expected.items()): raise SystemExit(1)
with open(os.path.join(ROOT, "audit-" + values["request-id"] + ".json"), "w") as handle:
 json.dump(sys.argv[1:], handle)
try: os.mkdir(os.path.join(ROOT, "used-" + values["request-id"]))
except FileExistsError: raise SystemExit(1)
""" % (str(self.state), tokens)
        self.service.write_text(source)
        self.service.chmod(0o755)

    def tearDown(self):
        self.temp.cleanup()

    def values(self, token="a", **changes):
        values = {**self.common, "request-id": token * 64}
        values.update(changes)
        return values

    def protected_service(self, name, repository_fd=None):
        self.assertEqual(name, "request-consumer")
        self.assertIsNone(repository_fd)
        parent = os.open(self.bin, os.O_RDONLY | os.O_DIRECTORY)
        leaf = os.open(self.service, os.O_RDONLY)
        return [parent, leaf], leaf

    def invoke(self, values):
        with mock.patch.object(self.cli, "PROTECTED_CONSUMER", self.service), \
             mock.patch.object(self.cli, "open_protected_executable", side_effect=self.protected_service):
            return self.cli.consume_request(values)

    def test_first_consumes_and_second_rejects(self):
        self.invoke(self.values())
        with self.assertRaises(SystemExit) as caught:
            self.invoke(self.values())
        self.assertEqual(caught.exception.code, 1)

    def test_concurrent_consumers_have_one_winner(self):
        results = []

        def consume():
            try:
                self.invoke(self.values("c"))
                results.append(0)
            except SystemExit as exc:
                results.append(exc.code)

        threads = [threading.Thread(target=consume) for _ in range(2)]
        for thread in threads: thread.start()
        for thread in threads: thread.join()
        self.assertEqual(sorted(results), [0, 1])

    def test_wrong_token_and_identity_reject_without_consuming_valid_token(self):
        with self.assertRaises(SystemExit) as wrong_token:
            self.invoke(self.values("b"))
        self.assertEqual(wrong_token.exception.code, 1)
        with self.assertRaises(SystemExit) as wrong_identity:
            self.invoke(self.values("d", candidate="9" * 40))
        self.assertEqual(wrong_identity.exception.code, 1)
        self.invoke(self.values("d"))

    def test_arbitrary_command_is_never_forwarded_or_executed(self):
        marker = self.state / "arbitrary-command-ran"
        values = self.values("e", command=f"/bin/sh -c 'touch {marker}'")
        self.invoke(values)
        argv = json.loads((self.state / ("audit-" + "e" * 64 + ".json")).read_text())
        self.assertNotIn("command", " ".join(argv))
        self.assertFalse(marker.exists())

    def test_service_failure_is_odombart(self):
        failed = self.root / "failed" / "request-consumer"
        failed.parent.mkdir()
        failed.write_text("#!/bin/sh\nexit 2\n")
        failed.chmod(0o755)

        def protected(name, repository_fd=None):
            parent = os.open(failed.parent, os.O_RDONLY | os.O_DIRECTORY)
            leaf = os.open(failed, os.O_RDONLY)
            return [parent, leaf], leaf

        with mock.patch.object(self.cli, "PROTECTED_CONSUMER", failed), \
             mock.patch.object(self.cli, "open_protected_executable", side_effect=protected):
            with self.assertRaises(SystemExit) as caught:
                self.cli.consume_request(self.values())
        self.assertEqual(caught.exception.code, 2)

    def test_kernel_failure_does_not_restore_consumed_token(self):
        opened = ([], (10, 11, 12))
        with mock.patch.object(self.cli, "open_authority", return_value=opened), \
             mock.patch.object(self.cli, "consume_request", side_effect=[None, SystemExit(1)]) as consume, \
             mock.patch.object(self.cli, "kernel_handoff", side_effect=SystemExit(2)) as kernel:
            with self.assertRaises(SystemExit) as first:
                self.cli.verify(self.verify_argv())
            with self.assertRaises(SystemExit) as second:
                self.cli.verify(self.verify_argv())
        self.assertEqual((first.exception.code, second.exception.code), (2, 1))
        self.assertEqual(consume.call_count, 2)
        self.assertEqual(kernel.call_count, 1)

    def verify_argv(self):
        values = self.values()
        return ["--request-id", values["request-id"], "--task", "h-033",
                "--candidate", values["candidate"],
                "--task-spec-sha256", values["task-spec-sha256"],
                "--gate-sha256", values["gate-sha256"], "--probe", values["probe"],
                "--require-result", values["require-result"]]


if __name__ == "__main__":
    unittest.main()
