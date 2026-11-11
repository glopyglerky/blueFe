import os
from pathlib import Path
import tarfile
import tempfile
import tomllib
import unittest

import package


class PackageTests(unittest.TestCase):
    def test_roots_refuse_overlap_in_both_directions(self):
        package.validate_roots(Path("/source"), Path("/work"), Path("/output"))
        for roots in (("/root", "/root/work", "/output"),
                      ("/root/source", "/root", "/output"),
                      ("/source", "/work/output", "/work"),
                      ("/source", "/work", "/work/output"),
                      ("/source", "/work", "/work")):
            with self.assertRaises(RuntimeError):
                package.validate_roots(*(Path(root) for root in roots))

    def test_bootstrap_inputs_require_building_rust_with_ci_llvm(self):
        config = tomllib.loads(package.build_configuration(Path('/tmp/work with "quotes"/build')))
        self.assertFalse(config["rust"]["download-rustc"])
        self.assertTrue(config["llvm"]["download-ci-llvm"])
        self.assertTrue(config["build"]["locked-deps"])
        self.assertEqual(config["build"]["build-dir"], '/tmp/work with "quotes"/build')
        self.assertNotIn("rustc", config["build"])
        self.assertNotIn("cargo", config["build"])

    def test_qualification_cannot_inherit_compiler_overrides(self):
        environment = {"PATH": "/bin", "HOME": "/home/test", "RUSTC_WRAPPER": "incorrect",
                       "LD_LIBRARY_PATH": "/build/lib", "CARGO_PROFILE_DEV_PANIC": "abort",
                       "GITHUB_ACTIONS": "true", "CI": "true"}
        self.assertEqual(package.clean_environment(environment), {"PATH": "/bin", "HOME": "/home/test"})

    def test_component_selection_rejects_ambiguous_and_missing_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(RuntimeError):
                package.select_component(root, "rustc")
            first = root / ("rustc-1-dev-" + package.TARGET + ".tar.gz")
            first.touch()
            self.assertEqual(package.select_component(root, "rustc"), first)
            (root / ("rustc-2-dev-" + package.TARGET + ".tar.gz")).touch()
            with self.assertRaises(RuntimeError):
                package.select_component(root, "rustc")

    def test_archive_preserves_modes_bytes_and_relative_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prefix = root / "original root"
            (prefix / "bin").mkdir(parents=True)
            executable = prefix / "bin/rustc"
            executable.write_bytes(b"compiler fixture\n")
            executable.chmod(0o755)
            (prefix / "bin/alias").symlink_to("rustc")
            expected = package.payload_manifest(prefix)
            archive = root / "package.tar.gz"
            package.archive_package(prefix, archive, 1234567890)
            unpacked = root / "relocated"
            with tarfile.open(archive) as bundle:
                bundle.extractall(unpacked, filter="data")
            self.assertEqual(expected, package.payload_manifest(unpacked / "bluefe-rust"))
            second = root / "second.tar.gz"
            package.archive_package(unpacked / "bluefe-rust", second, 1234567890)
            self.assertEqual(package.digest(archive), package.digest(second))

    def test_manifest_refuses_outside_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prefix = root / "package"
            prefix.mkdir()
            (root / "outside").write_text("outside")
            (prefix / "escape").symlink_to("../outside")
            with self.assertRaises(RuntimeError):
                package.payload_manifest(prefix)


if __name__ == "__main__":
    unittest.main()
