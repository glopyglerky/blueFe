import importlib.util
import os
from pathlib import Path
import tempfile
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


native = load("bluefe_native_build", Path(__file__).with_name("build.py"))
bootstrap = load("bluefe_upstream_bootstrap", ROOT / "src/bootstrap/bootstrap.py")


class NativeBuildContract(unittest.TestCase):
    def test_upstream_bootstrap_selects_only_configured_native_compiler(self):
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            compiler, cargo = work / "lustr-native", work / "cargo"
            cargo.touch()
            text = native.config_text(compiler, cargo, work)
            parsed = tomllib.loads(text)
            self.assertEqual(parsed["build"]["rustc"], str(compiler))
            self.assertEqual(parsed["build"]["build-stage"], 0)
            self.assertIs(parsed["rust"]["download-rustc"], False)
            args = bootstrap.FakeArgs()
            args.build = "x86_64-unknown-linux-gnu"
            build = bootstrap.RustBuild(text, args)
            self.assertEqual(build.rustc(), str(compiler))
            self.assertEqual(build.cargo(), str(cargo))
            env = native.environment(compiler, work)
            command = build.build_bootstrap_cmd(env)
            self.assertEqual(command[0], str(cargo))
            self.assertEqual(env["RUSTC"], str(compiler))
            self.assertEqual(env["RUSTC_WRAPPER"], "")
            self.assertEqual(env["RUSTC_WORKSPACE_WRAPPER"], "")

    def test_inherited_compiler_selectors_are_removed(self):
        from unittest.mock import patch
        with patch.dict(os.environ, {"RUSTC": "/old/rustc", "RUSTC_WRAPPER": "/old/wrapper",
                                     "RUSTFLAGS": "--sysroot=/old", "CARGO_BUILD_RUSTC": "/old/compiler"}):
            env = native.environment(Path("/native/lustr-native"), Path("/work"))
        self.assertEqual(env["RUSTC"], "/native/lustr-native")
        self.assertEqual(env["RUSTC_WRAPPER"], "")
        self.assertNotIn("CARGO_BUILD_RUSTC", env)
        self.assertNotIn("RUSTFLAGS", env)

    def test_trace_distinguishes_executed_tools_from_failed_path_probes(self):
        trace = '12 execve("/old/rustc", ["rustc"], 0x123) = -1 ENOENT (No such file)\n'
        trace += '12 execve("/native/lustr-native", ["lustr-native", "a.rs"], 0x123) = 0\n'
        trace += '13 execve("/absolute/rustc", ["rustc"], 0x123) = 0\n'
        self.assertEqual(native.successful_execs(trace), ["/native/lustr-native", "/absolute/rustc"])
        concurrent = '12 execve("/native/lustr-native", ["lustr-native"], 0x123 <unfinished ...>\n'
        concurrent += '13 execve("/bin/cc", ["cc"], 0x456) = 0\n'
        concurrent += '12 <... execve resumed>) = 0\n'
        self.assertEqual(native.successful_execs(concurrent), ["/bin/cc", "/native/lustr-native"])
        self.assertEqual(native.successful_execs('14 execveat(AT_FDCWD, "/other/rustc", ["rustc"], 0x123, 0) = 0\n'), ["/other/rustc"])
        with self.assertRaises(ValueError):
            native.successful_execs('14 execveat(5, "", ["rustc"], 0x123, AT_EMPTY_PATH) = 0\n')
        with self.assertRaises(ValueError):
            native.successful_execs('14 execve("rustc", ["rustc"], 0x123) = 0\n')
        with self.assertRaises(ValueError):
            native.successful_execs('14 <... execve resumed>) = 0\n')
        with self.assertRaises(ValueError):
            native.successful_execs('14 execve("/other/rustc", ["rustc"], 0x123 <unfinished ...>\n')


if __name__ == "__main__":
    unittest.main()
