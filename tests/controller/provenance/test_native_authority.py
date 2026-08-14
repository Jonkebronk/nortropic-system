#!/usr/bin/python3
import hashlib
import json
import os
import shutil
import stat
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROBE_SHA = "d17aecd9c4c2df98b945f6c53c5573e71a30e7b242657aeaffa56762d86902ef"
PROBES = (("h033-auth-pass-v1", "PASS", "h033-effect-pass-v1"),
          ("h033-auth-fail-v1", "FAIL", "h033-effect-fail-v1"),
          ("h033-auth-odombart-v1", "ODÖMBART", "h033-effect-odombart-v1"))


def run(argv, timeout=8):
    return subprocess.run([str(v) for v in argv], stdin=subprocess.DEVNULL,
                          capture_output=True, text=True, timeout=timeout,
                          env={"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C",
                               "HOME": "/var/empty", "TMPDIR": "/tmp"})


class NativeAuthorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="h033-native-test-")
        cls.authority = Path(cls.temp.name) / "authority"
        installed = run([ROOT / "controller/provenance/install", "fixture-install", cls.authority])
        if installed.returncode:
            raise RuntimeError((installed.returncode, installed.stdout, installed.stderr))
        allowlist = {"schema_version": 1, "probes": []}
        for probe, result, marker in PROBES:
            allowlist["probes"].append({"probe_identity": probe,
                "probe_path": str(cls.authority / "probes" / probe),
                "probe_sha256": PROBE_SHA, "effect_marker": marker, "result": result})
        cls.allowlist_raw = (json.dumps(allowlist, ensure_ascii=False,
                                        separators=(",", ":")) + "\n").encode()
        os.chmod(cls.authority / "probes.json", 0o644)
        (cls.authority / "probes.json").write_bytes(cls.allowlist_raw)
        os.chmod(cls.authority / "probes.json", 0o444)
        source = ROOT / "controller/provenance/native/service.c"
        cls.fixture_service = Path(cls.temp.name) / "h033-fixture-service"
        allowlist_sha = hashlib.sha256(cls.allowlist_raw).hexdigest()
        compiled = run(["/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                        "-arch", "arm64", "-DNORTROPIC_FIXTURE",
                        '-DPROBE_SHA256="' + PROBE_SHA + '"',
                        '-DALLOWLIST_SHA256="' + allowlist_sha + '"',
                        '-DAUTHORITY_ROOT="' + str(cls.authority) + '"',
                        source, "-o", cls.fixture_service], timeout=30)
        if compiled.returncode:
            raise RuntimeError((compiled.returncode, compiled.stdout, compiled.stderr))
        for name in ("request-producer", "request-observer", "request-consumer"):
            shutil.copyfile(cls.fixture_service, cls.authority / "bin" / name)
            os.chmod(cls.authority / "bin" / name, 0o755)
        cls.candidate = "1" * 40
        cls.spec = "2" * 64
        cls.gate = "3" * 64

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def producer_args(self, probe):
        return [self.authority / "bin/request-producer", "--task", "h-033",
                "--candidate", self.candidate, "--task-spec-sha256", self.spec,
                "--gate-sha256", self.gate, "--probe", probe]

    def observer_args(self, request_id, probe):
        return [self.authority / "bin/request-observer", "--request-id", request_id,
                "--task", "h-033", "--candidate", self.candidate,
                "--task-spec-sha256", self.spec, "--gate-sha256", self.gate,
                "--probe", probe]

    def consumer_args(self, request_id, probe, result, candidate=None):
        return [self.authority / "bin/request-consumer", "consume", "--request-id", request_id,
                "--task", "h-033", "--candidate", candidate or self.candidate,
                "--task-spec-sha256", self.spec, "--gate-sha256", self.gate,
                "--probe", probe, "--require-result", result]

    def create(self, probe):
        p = run(self.producer_args(probe))
        self.assertEqual((p.returncode, p.stderr), (0, ""), p)
        self.assertRegex(p.stdout, r"^REQUEST_ID=[0-9a-f]{64}\n$")
        request_id = p.stdout[11:-1]
        o = run(self.observer_args(request_id, probe))
        self.assertEqual((o.returncode, o.stdout, o.stderr), (0, "", ""), o)
        return request_id

    def test_all_fixed_probes_create_exact_bound_documents_and_h034_accepts(self):
        for probe, result, marker in PROBES:
            request_id = self.create(probe)
            evidence_path = self.authority / "evidence" / (request_id + ".json")
            receipt_path = self.authority / "probe-receipts" / (request_id + ".json")
            evidence_raw, receipt_raw = evidence_path.read_bytes(), receipt_path.read_bytes()
            evidence, receipt = json.loads(evidence_raw), json.loads(receipt_raw)
            self.assertEqual(tuple(evidence), ("schema_version", "producer_authority", "task",
                "candidate_sha", "task_spec_sha256", "gate_sha256", "probe_identity",
                "request_id", "result", "effect_sha256"))
            self.assertEqual(tuple(receipt), ("schema_version", "observer_authority", "request_id",
                "candidate_sha", "probe_identity", "probe_path", "probe_sha256", "effect_marker"))
            self.assertEqual((evidence["result"], receipt["effect_marker"], receipt["probe_sha256"]),
                             (result, marker, PROBE_SHA))
            self.assertEqual(evidence["effect_sha256"], hashlib.sha256(receipt_raw).hexdigest())
            self.assertEqual(run(self.consumer_args(request_id, probe, result)).returncode, 0)
            q = run([ROOT / "controller/provenance/cli", "gate-verify", "--fixture-root", self.authority,
                     "--task", "h-033", "--candidate", self.candidate,
                     "--task-spec-sha256", self.spec, "--gate-sha256", self.gate,
                     "--probe", probe, "--request-id", request_id, "--require-result", result])
            self.assertEqual(q.returncode, 0, q)
            self.assertIn("VERIFIED_RESULT=" + result + "\n", q.stdout)

    def test_producer_generates_fresh_id_and_rejects_caller_selected_id(self):
        first = run(self.producer_args(PROBES[0][0]))
        second = run(self.producer_args(PROBES[0][0]))
        self.assertEqual((first.returncode, second.returncode), (0, 0))
        self.assertNotEqual(first.stdout, second.stdout)
        selected = self.producer_args(PROBES[0][0]) + ["--request-id", "a" * 64]
        self.assertEqual(run(selected).returncode, 1)

    def test_first_consumer_wins_concurrent_race_and_replay_rejects(self):
        probe, result, _ = PROBES[0]
        request_id = self.create(probe)
        barrier = threading.Barrier(3)
        results = []
        def consume():
            barrier.wait()
            results.append(run(self.consumer_args(request_id, probe, result)).returncode)
        threads = [threading.Thread(target=consume) for _ in range(2)]
        for thread in threads: thread.start()
        barrier.wait()
        for thread in threads: thread.join()
        self.assertEqual(sorted(results), [0, 1])
        self.assertEqual(run(self.consumer_args(request_id, probe, result)).returncode, 1)

    def test_wrong_binding_does_not_consume_valid_token(self):
        probe, result, _ = PROBES[0]
        request_id = self.create(probe)
        self.assertEqual(run(self.consumer_args(request_id, probe, result, "9" * 40)).returncode, 1)
        self.assertEqual(run(self.consumer_args(request_id, probe, result)).returncode, 0)

    def test_observer_rejects_missing_or_substituted_producer_evidence(self):
        request_id = "a" * 64
        self.assertEqual(run(self.observer_args(request_id, PROBES[0][0])).returncode, 2)
        p = run(self.producer_args(PROBES[0][0])); request_id = p.stdout[11:-1]
        evidence = self.authority / "evidence" / (request_id + ".json")
        os.chmod(evidence, 0o644); raw = bytearray(evidence.read_bytes()); raw[-3] ^= 1
        evidence.write_bytes(raw); os.chmod(evidence, 0o444)
        self.assertEqual(run(self.observer_args(request_id, PROBES[0][0])).returncode, 2)

    def test_probe_substitution_and_arbitrary_command_reject(self):
        probe_path = self.authority / "probes" / PROBES[0][0]
        original = probe_path.read_bytes()
        try:
            os.chmod(probe_path, 0o755)
            probe_path.write_text("#!/bin/sh\necho hostile\n")
            os.chmod(probe_path, 0o555)
            self.assertEqual(run(self.producer_args(PROBES[0][0])).returncode, 2)
        finally:
            os.chmod(probe_path, 0o755); probe_path.write_bytes(original); os.chmod(probe_path, 0o555)
        marker = Path(self.temp.name) / "arbitrary-ran"
        q = run(self.producer_args(PROBES[0][0]) + ["--command", "/usr/bin/touch " + str(marker)])
        self.assertEqual(q.returncode, 1)
        self.assertFalse(marker.exists())

    def test_observer_rejects_allowlist_substitution(self):
        produced = run(self.producer_args(PROBES[0][0]))
        request_id = produced.stdout[11:-1]
        allowlist = self.authority / "probes.json"
        try:
            os.chmod(allowlist, 0o644)
            hostile = bytearray(self.allowlist_raw); hostile[-3] ^= 1
            allowlist.write_bytes(hostile); os.chmod(allowlist, 0o444)
            self.assertEqual(run(self.observer_args(request_id, PROBES[0][0])).returncode, 2)
        finally:
            os.chmod(allowlist, 0o644); allowlist.write_bytes(self.allowlist_raw); os.chmod(allowlist, 0o444)

    def test_production_installer_refuses_unprivileged_authority_mutation(self):
        if os.geteuid() == 0: self.skipTest("test is specifically unprivileged")
        q = run([ROOT / "controller/provenance/install", "install"])
        self.assertEqual(q.returncode, 2)
        self.assertIn("root-required", q.stderr)

    def test_committed_artifact_identity_and_no_fixture_override(self):
        service = ROOT / "controller/provenance/dist/h033-service"
        probe = ROOT / "controller/provenance/dist/h033-probe"
        self.assertEqual(hashlib.sha256(service.read_bytes()).hexdigest(),
                         json.loads((ROOT / "controller/provenance/artifact-manifest.json").read_text())["service"]["sha256"])
        self.assertEqual(hashlib.sha256(probe.read_bytes()).hexdigest(), PROBE_SHA)
        q = run(["/usr/bin/file", service, probe])
        self.assertEqual(q.returncode, 0)
        self.assertEqual(q.stdout.count("Mach-O 64-bit executable arm64"), 2)
        raw = service.read_bytes()
        self.assertNotIn(b"NORTROPIC_FIXTURE", raw)
        self.assertNotIn(str(self.authority).encode(), raw)


if __name__ == "__main__":
    unittest.main()
