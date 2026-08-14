#!/usr/bin/python3
import importlib.machinery
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
INSTALLER = ROOT / "controller/provenance/install"


def load_installer():
    loader = importlib.machinery.SourceFileLoader("h033_installer", str(INSTALLER))
    spec = importlib.util.spec_from_loader("h033_installer", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class InstallerFailureTests(unittest.TestCase):
    def setUp(self):
        self.installer = load_installer()

    def test_unprivileged_install_stops_before_source_process_or_target_write(self):
        if os.geteuid() == 0: self.skipTest("unprivileged control")
        with mock.patch.object(self.installer, "exact_sources") as sources:
            with self.assertRaises(SystemExit) as caught:
                self.installer.install(self.installer.AUTHORITY, False)
        self.assertEqual(caught.exception.code, 2)
        sources.assert_not_called()

    def test_git_process_creation_failure_is_closed_error(self):
        with mock.patch.object(self.installer.subprocess, "run", side_effect=OSError("fork failed")):
            with self.assertRaises(SystemExit) as caught:
                self.installer.git_object("verify/h034/kernel", "0" * 64)
        self.assertEqual(caught.exception.code, 2)

    def test_zero_length_install_write_fails_and_removes_temporary(self):
        with tempfile.TemporaryDirectory(prefix="h033-installer-write-") as directory:
            target = Path(directory) / "leaf"
            with mock.patch.object(self.installer.os, "write", return_value=0):
                with self.assertRaises(SystemExit) as caught:
                    self.installer.install_leaf(target, b"reviewed", os.getuid(), os.getgid(), 0o555)
            self.assertEqual(caught.exception.code, 2)
            self.assertFalse(target.exists())
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
