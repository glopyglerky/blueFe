import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location(
    "ci_llvm_cache",
    Path(__file__).resolve().parents[1] / "prepare-ci-artifact-cache.py",
)
CACHE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CACHE)


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="ci-llvm-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.git("init", "-q", "-b", "fork")
        self.git("config", "user.name", "Cache test")
        self.git("config", "user.email", "cache-test@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        directories = {"src/bootstrap", "src/build_helper", "src/ci", "src/ci/citool"}
        for name in sorted(CACHE.SOURCE_PATHS):
            path = self.root / name
            if name in directories:
                path /= "fixture.txt"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("source\n")
        (self.root / "src/ci/channel").write_text("nightly\n")
        self.commit("upstream")
        upstream = self.git("rev-parse", "HEAD")
        tree = self.git("rev-parse", "HEAD^{tree}")
        objects = {
            path: self.git("rev-parse", f"HEAD:{path}")
            for path in sorted(CACHE.SOURCE_PATHS)
        }
        pin = self.root / "upstream/rust.pin"
        pin.parent.mkdir()
        pin.write_text(
            f'repository = "{CACHE.REPOSITORY}"\n'
            f'revision = "{upstream}"\nroot_tree = "{tree}"\n'
        )
        self.commit("fork")
        self.base = self.git("rev-parse", "HEAD")
        self.git("checkout", "-q", "-b", "topic")
        (self.root / "owned.txt").write_text("reviewed change\n")
        self.commit("topic")
        self.git("checkout", "-q", "fork")
        self.git("merge", "--no-ff", "-qm", "PR merge", "topic")
        self.config = b"[llvm]\nassertions = true\nlibzstd = true\n"
        self.manifest = {
            "schema": 1,
            "upstream_repository": CACHE.REPOSITORY,
            "upstream_revision": upstream,
            "upstream_root_tree": tree,
            "target": CACHE.TARGET,
            "llvm_assertions": True,
            "digest_source": "Test fixture digest",
            "artifact_git_commit": upstream,
            "artifact_version": "1.0.0-nightly",
            "artifact_link_type": "dynamic",
            "builder_config_sha256": hashlib.sha256(self.config).hexdigest(),
            "llvm_invalidation_paths": CACHE.INVALIDATION_PATHS,
            "gcc_invalidation_paths": CACHE.GCC_INVALIDATION_PATHS,
            "source_objects": objects,
            "jobs": {"test-tidy": ["llvm"]},
        }
        self.archive = self.root / "fixture.tar.xz"
        self.write_archive()
        self.gcc_archive = self.root / "gcc-fixture.tar.xz"
        self.gcc_config = b"[gcc]\n"
        self.manifest["gcc_artifact"] = {
            "digest_source": "Test fixture digest",
            "artifact_git_commit": upstream,
            "artifact_version": "1.0.0-nightly",
            "builder_config_sha256": hashlib.sha256(self.gcc_config).hexdigest(),
        }
        self.manifest["jobs"]["test-x86_64-gnu-gcc"] = ["llvm", "gcc"]
        self.manifest["jobs"]["test-x86_64-gnu-llvm-22"] = ["gcc"]
        self.write_gcc_archive()

    def git(self, *args):
        return CACHE.git(self.root, *args)

    def commit(self, message):
        self.git("add", ".")
        self.git("commit", "-qm", message)

    def write_archive(self, overrides=None, duplicate=None):
        metadata = {
            "git-commit-hash": self.manifest["upstream_revision"].encode(),
            "git-commit-info": (
                self.manifest["upstream_revision"] + "\nshort\ndate\n"
            ).encode(),
            "version": b"1.0.0-nightly",
            "builder-config": self.config,
            "rust-dev/link-type.txt": b"dynamic",
        }
        metadata.update(overrides or {})
        with tarfile.open(self.archive, "w:xz") as archive:
            entries = list(metadata.items())
            if duplicate:
                entries.append((duplicate, metadata[duplicate]))
            for name, data in entries:
                info = tarfile.TarInfo(f"rust-dev-nightly-{CACHE.TARGET}/" + name)
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
        self.manifest["archive_bytes"] = self.archive.stat().st_size
        self.manifest["archive_sha256"] = CACHE.digest(self.archive)

    def test_prepares_identical_archive_with_explicit_upstream_receipt(self):
        output = CACHE.prepare(self.root, self.manifest, "test-tidy", self.archive)
        receipt = json.loads(output.read_text())
        self.assertEqual(
            receipt["upstream_publication_commit"], self.manifest["upstream_revision"]
        )
        self.assertEqual(receipt["bootstrap_cache_key_commit"], self.base)
        self.assertNotEqual(receipt["upstream_publication_commit"], self.base)
        self.assertFalse(receipt["artifact_published_for_fork_commit"])
        self.assertEqual(
            CACHE.digest(self.root / receipt["artifacts"]["llvm"]["cache_path"]),
            CACHE.digest(self.archive),
        )

    def write_gcc_archive(self, overrides=None):
        metadata = {
            "git-commit-hash": self.manifest["upstream_revision"].encode(),
            "git-commit-info": (
                self.manifest["upstream_revision"] + "\nshort\ndate\n"
            ).encode(),
            "version": b"1.0.0-nightly",
            "builder-config": self.gcc_config,
            "gcc-dev/lib/libgccjit.so": b"test-only library fixture",
        }
        metadata.update(overrides or {})
        with tarfile.open(self.gcc_archive, "w:xz") as archive:
            for name, data in metadata.items():
                info = tarfile.TarInfo(f"gcc-dev-nightly-{CACHE.TARGET}/" + name)
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
        spec = self.manifest["gcc_artifact"]
        spec["archive_bytes"] = self.gcc_archive.stat().st_size
        spec["archive_sha256"] = CACHE.digest(self.gcc_archive)

    def test_prepares_both_components_with_original_publication_identity(self):
        output = CACHE.prepare(
            self.root,
            self.manifest,
            "test-x86_64-gnu-gcc",
            self.archive,
            self.gcc_archive,
        )
        receipt = json.loads(output.read_text())
        self.assertEqual(set(receipt["artifacts"]), {"llvm", "gcc"})
        self.assertFalse(receipt["artifact_published_for_fork_commit"])
        for component, archive in [("llvm", self.archive), ("gcc", self.gcc_archive)]:
            artifact = receipt["artifacts"][component]
            self.assertEqual(
                CACHE.digest(self.root / artifact["cache_path"]), CACHE.digest(archive)
            )
            self.assertEqual(
                artifact["artifact_metadata"]["git_commit"],
                self.manifest["upstream_revision"],
            )

    def test_external_llvm_job_prepares_only_gcc(self):
        output = CACHE.prepare(
            self.root,
            self.manifest,
            "test-x86_64-gnu-llvm-22",
            gcc_archive=self.gcc_archive,
        )
        receipt = json.loads(output.read_text())
        self.assertEqual(set(receipt["artifacts"]), {"gcc"})
        self.assertFalse(any((self.root / "obj/build/cache").glob("llvm-*")))

    def test_rejects_changed_gcc_source(self):
        (self.root / "src/gcc").write_text("different GCC\n")
        with self.assertRaises(subprocess.CalledProcessError):
            CACHE.prepare(
                self.root,
                self.manifest,
                "test-x86_64-gnu-gcc",
                self.archive,
                self.gcc_archive,
            )

    def test_rejects_wrong_gcc_publication_commit(self):
        self.write_gcc_archive({"git-commit-hash": b"0" * 40})
        with self.assertRaisesRegex(ValueError, "publication commit mismatch"):
            CACHE.verify_archive(self.gcc_archive, self.manifest, "gcc")

    def test_rejects_changed_gcc_builder_configuration(self):
        self.write_gcc_archive({"builder-config": b"[gcc]\ndownload-ci-gcc = true\n"})
        with self.assertRaisesRegex(ValueError, "builder configuration mismatch"):
            CACHE.verify_archive(self.gcc_archive, self.manifest, "gcc")

    def test_rejects_corrupt_gcc_archive(self):
        data = bytearray(self.gcc_archive.read_bytes())
        data[-1] ^= 1
        self.gcc_archive.write_bytes(data)
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            CACHE.verify_archive(self.gcc_archive, self.manifest, "gcc")

    def test_escaping_obj_symlink_creates_no_external_paths(self):
        with tempfile.TemporaryDirectory(prefix="ci-cache-outside-") as temporary:
            outside = Path(temporary)
            (self.root / "obj").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                CACHE.prepare(self.root, self.manifest, "test-tidy", self.archive)
            self.assertEqual(list(outside.iterdir()), [])

    def test_escaping_cache_parent_creates_no_external_paths(self):
        with tempfile.TemporaryDirectory(prefix="ci-cache-outside-") as temporary:
            outside = Path(temporary)
            (self.root / "obj").mkdir()
            (self.root / "obj/build").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                CACHE.prepare(self.root, self.manifest, "test-tidy", self.archive)
            self.assertEqual(list(outside.iterdir()), [])
            self.assertFalse((self.root / "obj/ci-artifact-provenance.json").exists())

    def test_escaping_receipt_symlink_does_not_write_external_file(self):
        with tempfile.TemporaryDirectory(prefix="ci-cache-outside-") as temporary:
            outside = Path(temporary)
            (self.root / "obj").mkdir()
            (self.root / "obj/ci-artifact-provenance.json").symlink_to(
                outside / "receipt.json"
            )
            with self.assertRaisesRegex(ValueError, "symlink"):
                CACHE.prepare(self.root, self.manifest, "test-tidy", self.archive)
            self.assertEqual(list(outside.iterdir()), [])
            self.assertFalse((self.root / "obj/build").exists())

    def test_rejects_worktree_change(self):
        (self.root / "src/version").write_text("changed\n")
        with self.assertRaises(subprocess.CalledProcessError):
            CACHE.verify_sources(self.root, self.manifest)

    def test_rejects_index_change_even_after_worktree_restoration(self):
        path = self.root / "src/version"
        original = path.read_bytes()
        path.write_text("staged change\n")
        self.git("add", "src/version")
        path.write_bytes(original)
        with self.assertRaises(subprocess.CalledProcessError):
            CACHE.verify_sources(self.root, self.manifest)

    def test_rejects_mode_change_in_committed_input(self):
        self.git("update-index", "--chmod=+x", "src/ci/run.sh")
        self.git("commit", "--amend", "--no-edit", "-q")
        with self.assertRaisesRegex(ValueError, "fork input mismatch"):
            CACHE.verify_sources(self.root, self.manifest)

    def test_rejects_untracked_configuration_addition(self):
        (self.root / "src/bootstrap/addition.rs").write_text("changed\n")
        with self.assertRaisesRegex(ValueError, "untracked"):
            CACHE.verify_sources(self.root, self.manifest)

    def test_rejects_missing_source_input(self):
        manifest = copy.deepcopy(self.manifest)
        del manifest["source_objects"]["src/stage0"]
        with self.assertRaisesRegex(ValueError, "input contract changed"):
            CACHE.verify_sources(self.root, manifest)

    def test_rejects_different_upstream_pin(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["upstream_revision"] = "1" * 40
        with self.assertRaisesRegex(ValueError, "upstream pin"):
            CACHE.verify_sources(self.root, manifest)

    def test_rejects_non_merge_checkout(self):
        self.git("checkout", "-q", "--detach", self.base)
        with self.assertRaisesRegex(ValueError, "actual PR merge"):
            CACHE.verify_sources(self.root, self.manifest)

    def test_rejects_different_cache_key_inputs(self):
        self.git("reset", "--hard", "-q", self.base)
        (self.root / "src/version").write_text("different base\n")
        self.commit("different base")
        self.git("checkout", "-q", "-b", "restoration")
        (self.root / "src/version").write_text("source\n")
        self.commit("restore pinned version")
        self.git("checkout", "-q", "fork")
        self.git("merge", "--no-ff", "-qm", "PR merge", "restoration")
        with self.assertRaisesRegex(ValueError, "fork input mismatch"):
            CACHE.verify_sources(self.root, self.manifest)

    def test_rejects_corrupt_archive_without_receipt(self):
        data = bytearray(self.archive.read_bytes())
        data[-1] ^= 1
        self.archive.write_bytes(data)
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            CACHE.prepare(self.root, self.manifest, "test-tidy", self.archive)
        self.assertFalse((self.root / "obj/ci-artifact-provenance.json").exists())

    def test_rejects_wrong_embedded_upstream_commit(self):
        self.write_archive({"git-commit-hash": b"0" * 40})
        with self.assertRaisesRegex(ValueError, "publication commit mismatch"):
            CACHE.verify_archive(self.archive, self.manifest)

    def test_rejects_changed_builder_configuration(self):
        self.write_archive({"builder-config": b"[llvm]\nassertions = false\n"})
        with self.assertRaisesRegex(ValueError, "builder configuration mismatch"):
            CACHE.verify_archive(self.archive, self.manifest)

    def test_rejects_duplicate_metadata(self):
        self.write_archive(duplicate="git-commit-hash")
        with self.assertRaisesRegex(ValueError, "duplicate archive metadata"):
            CACHE.verify_archive(self.archive, self.manifest)

    def test_rejects_unqualified_job(self):
        with self.assertRaisesRegex(ValueError, "job is not qualified"):
            CACHE.prepare(self.root, self.manifest, "unqualified", self.archive)


if __name__ == "__main__":
    unittest.main()
