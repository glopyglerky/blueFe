"""Bootstrap tests

Run these with `x test bootstrap`, or `python -m unittest src/bootstrap/bootstrap_test.py`."""

from __future__ import absolute_import, division, print_function
import os
import unittest
from unittest.mock import patch
import tempfile
import hashlib
import sys
import json
import shutil
import subprocess

from shutil import rmtree

# Allow running this from the top-level directory.
bootstrap_dir = os.path.dirname(os.path.abspath(__file__))
# For the import below, have Python search in src/bootstrap first.
sys.path.insert(0, bootstrap_dir)
import bootstrap  # noqa: E402
import configure  # noqa: E402


def serialize_and_parse(configure_args, bootstrap_args=None):
    from io import StringIO

    if bootstrap_args is None:
        bootstrap_args = bootstrap.FakeArgs()

    section_order, sections, targets = configure.parse_args(configure_args)
    buffer = StringIO()
    configure.write_config_toml(buffer, section_order, targets, sections)
    build = bootstrap.RustBuild(config_toml=buffer.getvalue(), args=bootstrap_args)

    try:
        import tomllib

        # Verify this is actually valid TOML.
        tomllib.loads(build.config_toml)
    except ImportError:
        print(
            "WARNING: skipping TOML validation, need at least python 3.11",
            file=sys.stderr,
        )
    return build


class VerifyTestCase(unittest.TestCase):
    """Test Case for verify"""

    def setUp(self):
        self.container = tempfile.mkdtemp()
        self.src = os.path.join(self.container, "src.txt")
        self.bad_src = os.path.join(self.container, "bad.txt")
        content = "Hello world"

        self.expected = hashlib.sha256(content.encode("utf-8")).hexdigest()

        with open(self.src, "w") as src:
            src.write(content)
        with open(self.bad_src, "w") as bad:
            bad.write("Hello!")

    def tearDown(self):
        rmtree(self.container)

    def test_valid_file(self):
        """Check if the sha256 sum of the given file is valid"""
        self.assertTrue(bootstrap.verify(self.src, self.expected, False))

    def test_invalid_file(self):
        """Should verify that the file is invalid"""
        self.assertFalse(bootstrap.verify(self.bad_src, self.expected, False))


class ProgramOutOfDate(unittest.TestCase):
    """Test if a program is out of date"""

    def setUp(self):
        self.container = tempfile.mkdtemp()
        os.mkdir(os.path.join(self.container, "stage0"))
        self.build = bootstrap.RustBuild()
        self.build.date = "2017-06-15"
        self.build.build_dir = self.container
        self.rustc_stamp_path = os.path.join(self.container, "stage0", ".rustc-stamp")
        self.key = self.build.date + str(None)

    def tearDown(self):
        rmtree(self.container)

    def test_stamp_path_does_not_exist(self):
        """Return True when the stamp file does not exist"""
        if os.path.exists(self.rustc_stamp_path):
            os.unlink(self.rustc_stamp_path)
        self.assertTrue(self.build.program_out_of_date(self.rustc_stamp_path, self.key))

    def test_dates_are_different(self):
        """Return True when the dates are different"""
        with open(self.rustc_stamp_path, "w") as rustc_stamp:
            rustc_stamp.write("2017-06-14None")
        self.assertTrue(self.build.program_out_of_date(self.rustc_stamp_path, self.key))

    def test_same_dates(self):
        """Return False both dates match"""
        with open(self.rustc_stamp_path, "w") as rustc_stamp:
            rustc_stamp.write("2017-06-15None")
        self.assertFalse(
            self.build.program_out_of_date(self.rustc_stamp_path, self.key)
        )


class ParseArgsInConfigure(unittest.TestCase):
    """Test if `parse_args` function in `configure.py` works properly"""

    @patch("configure.err")
    def test_unknown_args(self, err):
        # It should be print an error message if the argument doesn't start with '--'
        configure.parse_args(["enable-full-tools"])
        err.assert_called_with("Option 'enable-full-tools' is not recognized")
        err.reset_mock()
        # It should be print an error message if the argument is not recognized
        configure.parse_args(["--some-random-flag"])
        err.assert_called_with("Option '--some-random-flag' is not recognized")

    @patch("configure.err")
    def test_need_value_args(self, err):
        """It should print an error message if a required argument value is missing"""
        configure.parse_args(["--target"])
        err.assert_called_with("Option '--target' needs a value (--target=val)")

    @patch("configure.err")
    def test_option_checking(self, err):
        # Options should be checked even if `--enable-option-checking` is not passed
        configure.parse_args(["--target"])
        err.assert_called_with("Option '--target' needs a value (--target=val)")
        err.reset_mock()
        # Options should be checked if `--enable-option-checking` is passed
        configure.parse_args(["--enable-option-checking", "--target"])
        err.assert_called_with("Option '--target' needs a value (--target=val)")
        err.reset_mock()
        # Options should not be checked if `--disable-option-checking` is passed
        configure.parse_args(["--disable-option-checking", "--target"])
        err.assert_not_called()

    @patch("configure.parse_example_config", lambda known_args, _: known_args)
    def test_known_args(self):
        # It should contain known and correct arguments
        known_args = configure.parse_args(["--enable-full-tools"])
        self.assertTrue(known_args["full-tools"][0][1])
        known_args = configure.parse_args(["--disable-full-tools"])
        self.assertFalse(known_args["full-tools"][0][1])
        # It should contain known arguments and their values
        known_args = configure.parse_args(["--target=x86_64-unknown-linux-gnu"])
        self.assertEqual(known_args["target"][0][1], "x86_64-unknown-linux-gnu")
        known_args = configure.parse_args(["--target", "x86_64-unknown-linux-gnu"])
        self.assertEqual(known_args["target"][0][1], "x86_64-unknown-linux-gnu")


class GenerateAndParseConfig(unittest.TestCase):
    """Test that we can serialize and deserialize a bootstrap.toml file"""

    def test_no_args(self):
        build = serialize_and_parse([])
        self.assertEqual(build.get_toml("profile"), "dist")
        self.assertIsNone(build.get_toml("llvm.download-ci-llvm"))

    def test_set_section(self):
        build = serialize_and_parse(["--set", "llvm.download-ci-llvm"])
        self.assertEqual(build.get_toml("download-ci-llvm", section="llvm"), "true")

    def test_set_target(self):
        build = serialize_and_parse(["--set", "target.x86_64-unknown-linux-gnu.cc=gcc"])
        self.assertEqual(
            build.get_toml("cc", section="target.x86_64-unknown-linux-gnu"), "gcc"
        )

    def test_set_top_level(self):
        build = serialize_and_parse(["--set", "profile=compiler"])
        self.assertEqual(build.get_toml("profile"), "compiler")

    def test_set_codegen_backends(self):
        build = serialize_and_parse(["--set", "rust.codegen-backends=cranelift"])
        self.assertNotEqual(
            build.config_toml.find("codegen-backends = ['cranelift']"), -1
        )
        build = serialize_and_parse(["--set", "rust.codegen-backends=cranelift,llvm"])
        self.assertNotEqual(
            build.config_toml.find("codegen-backends = ['cranelift', 'llvm']"), -1
        )
        build = serialize_and_parse(["--enable-full-tools"])
        self.assertNotEqual(build.config_toml.find("codegen-backends = ['llvm']"), -1)


class GetTomlDottedKeys(unittest.TestCase):
    """Test that get_toml understands the dotted-table key syntax that a
    hand-written bootstrap.toml may use (e.g. `build.cargo = "..."`), and that
    it checks the table a key belongs to. See issue #156948."""

    def parse(self, config_toml):
        return bootstrap.RustBuild(config_toml=config_toml, args=bootstrap.FakeArgs())

    def test_dotted_key(self):
        build = self.parse('build.cargo = "/path/to/cargo"')
        self.assertEqual(build.get_toml("cargo", "build"), "/path/to/cargo")

    def test_dotted_key_matches_section_form(self):
        dotted = self.parse('build.cargo = "/path/to/cargo"')
        section = self.parse('[build]\ncargo = "/path/to/cargo"')
        self.assertEqual(
            dotted.get_toml("cargo", "build"), section.get_toml("cargo", "build")
        )

    def test_dotted_key_wrong_section(self):
        # A `cargo` key in some other table must not be picked up for `build`.
        build = self.parse('[foo]\ncargo = "false"')
        self.assertIsNone(build.get_toml("cargo", "build"))

    def test_program_config_requires_build_table(self):
        # A cargo/rustc key outside [build] must be ignored; program_config
        # falls back to the stage0 default path rather than the misplaced value.
        wrong = self.parse('[foo]\ncargo = "/wrong/cargo"')
        cargo_default = os.path.join(
            wrong.bin_root(), "bin", "cargo" + bootstrap.EXE_SUFFIX
        )
        self.assertEqual(wrong.cargo(), cargo_default)

        wrong_rustc = self.parse('[foo]\nrustc = "/wrong/rustc"')
        rustc_default = os.path.join(
            wrong_rustc.bin_root(), "bin", "rustc" + bootstrap.EXE_SUFFIX
        )
        self.assertEqual(wrong_rustc.rustc(), rustc_default)

        # A dotted key in the build table is honored.
        right = self.parse('build.cargo = "/path/to/cargo"')
        self.assertEqual(right.cargo(), "/path/to/cargo")

    def test_dotted_target_key(self):
        build = self.parse('target.x86_64-unknown-linux-gnu.cc = "gcc"')
        self.assertEqual(build.get_toml("cc", "target.x86_64-unknown-linux-gnu"), "gcc")

    def test_dotted_key_inside_section(self):
        # A dotted key nested under a `[section]` header composes with that
        # section's name; it is equivalent to the fully top-level dotted form.
        nested = self.parse('[target]\nx86_64-unknown-linux-gnu.cc = "gcc"')
        self.assertEqual(
            nested.get_toml("cc", "target.x86_64-unknown-linux-gnu"), "gcc"
        )
        top_level = self.parse('target.x86_64-unknown-linux-gnu.cc = "gcc"')
        self.assertEqual(
            nested.get_toml("cc", "target.x86_64-unknown-linux-gnu"),
            top_level.get_toml("cc", "target.x86_64-unknown-linux-gnu"),
        )

    def test_dotted_prefix_does_not_alias_other_section(self):
        # `build.cargo` inside `[foo]` is `foo.build.cargo`, not the top-level
        # `[build]` table, so it must not be returned for section "build".
        build = self.parse('[foo]\nbuild.cargo = "false"')
        self.assertIsNone(build.get_toml("cargo", "build"))


class BuildBootstrap(unittest.TestCase):
    """Test that we generate the appropriate arguments when building bootstrap"""

    def build_args(self, configure_args=None, args=None, env=None):
        if configure_args is None:
            configure_args = []
        if args is None:
            args = []
        if env is None:
            env = {}

        # This test ends up invoking build_bootstrap_cmd, which searches for
        # the Cargo binary and errors out if it cannot be found. This is not a
        # problem in most cases, but there is a scenario where it would cause
        # the test to fail.
        #
        # When a custom local Cargo is configured in bootstrap.toml (with the
        # build.cargo setting), no Cargo is downloaded to any location known by
        # bootstrap, and bootstrap relies on that setting to find it.
        #
        # In this test though we are not using the bootstrap.toml of the caller:
        # we are generating a blank one instead. If we don't set build.cargo in
        # it, the test will have no way to find Cargo, failing the test.
        cargo_bin = os.environ.get("BOOTSTRAP_TEST_CARGO_BIN")
        if cargo_bin is not None:
            configure_args += ["--set", "build.cargo=" + cargo_bin]
        rustc_bin = os.environ.get("BOOTSTRAP_TEST_RUSTC_BIN")
        if rustc_bin is not None:
            configure_args += ["--set", "build.rustc=" + rustc_bin]

        env = env.copy()
        env["PATH"] = os.environ["PATH"]

        parsed = bootstrap.parse_args(args)
        build = serialize_and_parse(configure_args, parsed)
        # Make these optional so that `python -m unittest` works when run manually.
        build_dir = os.environ.get("BUILD_DIR")
        if build_dir is not None:
            build.build_dir = build_dir
        build_platform = os.environ.get("BUILD_PLATFORM")
        if build_platform is not None:
            build.build = build_platform
        return build.build_bootstrap_cmd(env), env

    def test_cargoflags(self):
        args, _ = self.build_args(env={"CARGOFLAGS": "--timings"})
        self.assertTrue("--timings" in args)

    def test_default_coordinator(self):
        args, env = self.build_args(env={"LUST_CARGO": "unrelated-cargo"})
        self.assertEqual(args[1:5], ["--engine", "auto", "--", "build"])
        suffix = ".exe" if bootstrap.platform_is_win32() else ""
        self.assertEqual(os.path.basename(args[0]), "lustr" + suffix)
        self.assertIn("bluefe-lustr", args[0])
        self.assertNotEqual(env["LUST_CARGO"], "unrelated-cargo")

    def test_coordinator_preserves_custom_cargo(self):
        cargo = os.environ.get("BOOTSTRAP_TEST_CARGO_BIN")
        if cargo is None:
            self.skipTest("requires BOOTSTRAP_TEST_CARGO_BIN")
        args, env = self.build_args()
        self.assertEqual(env["LUST_CARGO"], cargo)
        self.assertNotEqual(args[0], cargo)

    def test_missing_lustr_with_submodules_disabled(self):
        build = bootstrap.RustBuild(config_toml="[build]\nsubmodules = false\n")
        with tempfile.TemporaryDirectory() as root:
            build.rust_root = root
            with patch.object(bootstrap, "run") as run:
                with self.assertRaisesRegex(RuntimeError, "pinned root lustr"):
                    build.build_lustr({})
                run.assert_not_called()

    def test_initialized_lustr_is_not_reset(self):
        build = bootstrap.RustBuild()
        with tempfile.TemporaryDirectory() as root:
            build.rust_root = root
            source = os.path.join(root, "lustr")
            os.makedirs(source)
            with open(os.path.join(source, ".git"), "w") as git_file:
                git_file.write("gitdir: preserved-local-source\n")
            with patch.object(bootstrap, "run") as run:
                with self.assertRaisesRegex(RuntimeError, "pinned root lustr"):
                    build.build_lustr({})
                run.assert_not_called()

    def test_stage0_version_floor(self):
        with tempfile.TemporaryDirectory() as root:
            os.mkdir(os.path.join(root, "src"))
            with open(os.path.join(root, "src", "version"), "w") as output:
                output.write("1.102.0\n")
            build = bootstrap.RustBuild()
            build.rust_root = root
            for release in ["1.100.0-beta.2", "1.85.0"]:
                with patch.object(bootstrap.subprocess, "check_output", return_value="release: " + release + "\n"):
                    with self.assertRaisesRegex(RuntimeError, "build.rustc"):
                        build.check_bluefe_stage0()
            for release in ["1.101.0-nightly", "1.102.0-dev"]:
                with patch.object(bootstrap.subprocess, "check_output", return_value="release: " + release + "\n") as probe:
                    build.check_bluefe_stage0()
                    self.assertEqual(probe.call_args.kwargs["timeout"], 15)

    def test_stage0_probe_failure_is_bounded(self):
        build = bootstrap.RustBuild()
        with patch.object(bootstrap.subprocess, "check_output", side_effect=subprocess.TimeoutExpired("rustc", 15)):
            with self.assertRaisesRegex(RuntimeError, "build.rustc"):
                build.check_bluefe_stage0()

    def test_warnings(self):
        for toml_warnings in ["false", "true", None]:
            configure_args = []
            if toml_warnings is not None:
                configure_args = ["--set", "rust.deny-warnings=" + toml_warnings]

            args, env = self.build_args(configure_args, args=["--warnings=warn"])
            self.assertFalse("CARGO_BUILD_WARNINGS" in env)

            args, env = self.build_args(configure_args, args=["--warnings=deny"])
            self.assertEqual("deny", env["CARGO_BUILD_WARNINGS"])


@unittest.skipUnless(
    os.environ.get("BLUEFE_TEST_BUILD_ROOT")
    and os.environ.get("BOOTSTRAP_TEST_CARGO_BIN")
    and os.environ.get("BOOTSTRAP_TEST_RUSTC_BIN"),
    "requires an explicit build filesystem and real Cargo/rustc",
)
class BluefeRealBootstrap(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(
            prefix="bluefe fixture ", dir=os.environ["BLUEFE_TEST_BUILD_ROOT"]
        )
        self.addCleanup(self.directory.cleanup)
        self.root = self.directory.name
        config = "[build]\ncargo = {}\nrustc = {}\n".format(
            json.dumps(os.environ["BOOTSTRAP_TEST_CARGO_BIN"]),
            json.dumps(os.environ["BOOTSTRAP_TEST_RUSTC_BIN"]),
        )
        self.build = bootstrap.RustBuild(config_toml=config)
        self.build.rust_root = self.root
        self.build.build_dir = os.path.join(self.root, "output with spaces")
        coordinator = os.path.abspath(
            os.path.join(bootstrap_dir, "..", "..", "lustr", "crates", "lustr")
        )
        shutil.copytree(
            coordinator,
            os.path.join(self.root, "lustr", "crates", "lustr"),
            ignore=shutil.ignore_patterns("target", ".git"),
        )
        lustr_root = os.path.abspath(os.path.join(coordinator, "..", ".."))
        for name in ["Cargo.toml", "Cargo.lock"]:
            shutil.copyfile(os.path.join(lustr_root, name), os.path.join(self.root, "lustr", name))
        self.package = os.path.join(self.root, "src", "bootstrap")
        os.makedirs(os.path.join(self.package, "src"))
        with open(os.path.join(self.root, "src", "version"), "w") as output:
            output.write("1.102.0\n")
        self.write(
            "Cargo.toml",
            '[package]\nname = "bootstrap"\nversion = "0.0.0"\nedition = "2024"\n[workspace]\n',
        )
        self.write(
            "build.rs",
            'fn main() { println!("cargo:rustc-env=BLUEFE_PROBE=build-script-ok"); }\n',
        )
        self.write(
            "src/main.rs",
            'fn main() { println!("{}", env!("BLUEFE_PROBE")); }\n',
        )

    def write(self, name, source):
        with open(os.path.join(self.package, name), "w", encoding="utf-8") as output:
            output.write(source)

    def test_real_coordinator_builds_bootstrap(self):
        self.build.build_bootstrap()
        output = subprocess.check_output([self.build.bootstrap_binary()])
        self.assertEqual(output, b"build-script-ok\n")
        env = {}
        args = self.build.build_bootstrap_cmd(env)
        plan = subprocess.check_output(
            [args[0], "--engine", "auto", "plan"] + args[4:],
            env=dict(os.environ, **env),
        )
        decision = json.loads(plan)
        self.assertEqual(decision["selected_engine"], "rustc")
        self.assertEqual(decision["program"], os.environ["BOOTSTRAP_TEST_CARGO_BIN"])
        self.assertEqual(decision["args"], args[4:])

    def test_real_coordinator_preserves_compiler_failure(self):
        self.write("src/main.rs", 'fn main() { let value: u8 = "invalid"; }\n')
        with self.assertRaises(SystemExit) as error:
            self.build.build_bootstrap()
        self.assertNotEqual(error.exception.code, 0)
        self.assertFalse(os.path.exists(self.build.bootstrap_binary()))

    def test_retained_full_rust_toolchain(self):
        root = os.environ.get("BLUEFE_TEST_TOOLCHAIN_ROOT")
        if not root:
            self.skipTest("requires BLUEFE_TEST_TOOLCHAIN_ROOT")
        self.write("src/lib.rs", '''/// ```
/// assert_eq!(bootstrap::answer(), 42);
/// ```
pub fn answer() -> u32 { 42 }
#[test]
fn panic_runs_drop() {
    struct Guard<'a>(&'a std::cell::Cell<u32>);
    impl Drop for Guard<'_> { fn drop(&mut self) { self.0.set(self.0.get() + 1); } }
    let drops = std::cell::Cell::new(0);
    let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
        let _guard = Guard(&drops);
        panic!("fixture");
    }));
    assert!(result.is_err());
    assert_eq!(drops.get(), 1);
}
''')
        self.write("src/main.rs", 'fn main() { assert_eq!(bootstrap::answer(), 42); }\n')
        env = os.environ.copy()
        for name in ["RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER", "CARGO_BUILD_TARGET"]:
            env.pop(name, None)
        env.update(CARGO_TARGET_DIR=os.path.join(self.root, "full-rust"), CARGO_BUILD_JOBS="2",
                   CARGO_HOME=os.path.join(self.root, "cargo-home"))
        command = [os.path.join(root, "bin", "lustr"), "--bluefe-root", root]
        plan = json.loads(subprocess.check_output(command + ["plan", "test", "--offline"], env=env))
        self.assertEqual(plan["program"], os.path.join(root, "bin", "cargo"))
        self.assertFalse(os.path.exists(env["CARGO_TARGET_DIR"]))
        for arguments in [["run", "--offline"], ["test", "--offline"],
                          ["build", "--offline", "--target", "wasm32-unknown-unknown"]]:
            subprocess.run(command + arguments, cwd=self.package, env=env, check=True, timeout=120)
        wasm = os.path.join(env["CARGO_TARGET_DIR"], "wasm32-unknown-unknown", "debug", "bootstrap.wasm")
        with open(wasm, "rb") as artifact:
            self.assertEqual(artifact.read(8), b"\0asm\x01\0\0\0")
        self.write("src/main.rs", 'fn main() { let value: u8 = "invalid"; }\n')
        rejected = subprocess.run(command + ["check", "--offline"], cwd=self.package, env=env,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn(b"E0308", rejected.stderr)
