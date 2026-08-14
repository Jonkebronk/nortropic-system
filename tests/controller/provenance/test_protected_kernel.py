#!/usr/bin/python3
import importlib.machinery
import importlib.util
import stat
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
CLI = ROOT / "controller/provenance/cli"


def load_cli():
    loader = importlib.machinery.SourceFileLoader("h033_cli", str(CLI))
    spec = importlib.util.spec_from_loader("h033_cli", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def fs(mode, uid, inode, *, device=7):
    return types.SimpleNamespace(st_mode=mode, st_uid=uid, st_gid=0,
                                 st_dev=device, st_ino=inode, st_nlink=2,
                                 st_size=52_208, st_mtime_ns=1, st_ctime_ns=2)


class ProtectedKernelTests(unittest.TestCase):
    def setUp(self):
        self.cli = load_cli()
        self.directories = [fs(stat.S_IFDIR | 0o755, 0, number) for number in range(10, 16)]
        self.repository = fs(stat.S_IFREG | 0o755, 0, 99)
        self.protected = fs(stat.S_IFREG | 0o755, 0, 99)

    def exercise(self, directories=None, protected=None):
        directories = directories or self.directories
        protected = protected or self.protected
        opened = iter(range(10, 17))
        stats = {9: self.repository, **dict(zip(range(10, 16), directories)), 16: protected}
        with mock.patch.object(self.cli.os, "open", side_effect=lambda *a, **k: next(opened)), \
             mock.patch.object(self.cli.os, "fstat", side_effect=lambda fd: stats[fd]), \
             mock.patch.object(self.cli.os, "close") as close:
            result = self.cli.open_protected_kernel()
        return result, close

    def test_exact_root_protected_installed_leaf_positive(self):
        (opened, kernel_fd), close = self.exercise()
        self.assertEqual(opened, list(range(10, 17)))
        self.assertEqual(kernel_fd, 16)
        close.assert_not_called()

    def test_requester_owned_parent_rejects(self):
        directories = list(self.directories)
        directories[4] = fs(stat.S_IFDIR | 0o755, 501, 14)
        with self.assertRaises(SystemExit) as caught:
            self.exercise(directories=directories)
        self.assertEqual(caught.exception.code, 2)

    def test_requester_writable_parent_rejects(self):
        directories = list(self.directories)
        directories[3] = fs(stat.S_IFDIR | 0o775, 0, 13)
        with self.assertRaises(SystemExit) as caught:
            self.exercise(directories=directories)
        self.assertEqual(caught.exception.code, 2)

    def test_requester_owned_kernel_rejects(self):
        alternate = fs(stat.S_IFREG | 0o755, 501, 99)
        with self.assertRaises(SystemExit) as caught:
            self.exercise(protected=alternate)
        self.assertEqual(caught.exception.code, 2)

    def test_same_euid_stage_removed(self):
        source = CLI.read_text()
        self.assertNotIn("TemporaryDirectory", source)
        self.assertNotIn("os.link(", source)
        self.assertNotIn("/private/tmp", source)
        self.assertEqual(str(self.cli.PROTECTED_KERNEL),
                         "/Library/Application Support/Nortropic/provenance/bin/h034-kernel")

    def test_missing_protected_authority_stops_before_kernel_spawn(self):
        values = {"candidate": "1" * 40, "task-spec-sha256": "2" * 64,
                  "gate-sha256": "3" * 64, "probe": "probe",
                  "request-id": "4" * 64, "require-result": "PASS"}
        calls = []
        real_popen = self.cli.subprocess.Popen

        def observed(argv, *args, **kwargs):
            calls.append(argv)
            return real_popen(argv, *args, **kwargs)

        with mock.patch.object(self.cli, "open_protected_kernel", side_effect=SystemExit(2)), \
             mock.patch.object(self.cli.subprocess, "Popen", side_effect=observed):
            with self.assertRaises(SystemExit) as caught:
                self.cli.kernel_handoff((0, 1, 2), values, False)
        self.assertEqual(caught.exception.code, 2)
        self.assertEqual([argv[0] for argv in calls], ["/usr/bin/git", "/usr/bin/git"])


if __name__ == "__main__":
    unittest.main()
