#!/usr/bin/env python3
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tarfile
import time


TARGET = "x86_64-unknown-linux-gnu"
SCOPES = ("compiler", "library", "src", "tests", "x", "x.py", "x.ps1",
          "Cargo.toml", "Cargo.lock", "bootstrap.example.toml")
REMOVED_ENV = (
    "GITHUB_ACTIONS", "CI", "RUSTC", "RUSTDOC", "RUSTC_WRAPPER",
    "RUSTC_WORKSPACE_WRAPPER", "RUSTFLAGS", "RUSTDOCFLAGS",
    "CARGO_ENCODED_RUSTFLAGS", "CARGO_ENCODED_RUSTDOCFLAGS",
    "CARGO_BUILD_TARGET", "RUSTUP_TOOLCHAIN", "LD_LIBRARY_PATH",
    "LD_PRELOAD", "DYLD_LIBRARY_PATH", "DYLD_INSERT_LIBRARIES",
)


def clean_environment(environ):
    return {
        key: value for key, value in environ.items()
        if key not in REMOVED_ENV and not key.startswith("CARGO_PROFILE_")
    }


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def run(argv, cwd, env, log, check=True, live=False):
    command = [str(value) for value in argv]
    started = time.monotonic()
    if live:
        lines = []
        with subprocess.Popen(command, cwd=cwd, env=env, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True) as process:
            with log.open("a") as stream:
                for line in process.stdout:
                    print(line, end="", flush=True)
                    stream.write(line)
                    stream.flush()
                    lines.append(line)
            result = subprocess.CompletedProcess(command, process.wait(), "".join(lines))
    else:
        result = subprocess.run(command, cwd=cwd, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True)
    record = {"argv": command, "returncode": result.returncode,
              "elapsed_seconds": time.monotonic() - started, "output": result.stdout}
    with log.open("a") as stream:
        stream.write(json.dumps(record) + "\n")
    if not live:
        print(result.stdout, end="", flush=True)
    if check and result.returncode:
        raise subprocess.CalledProcessError(result.returncode, command, result.stdout)
    return result


def build_configuration(build_dir):
    return "\n".join([
        "[build]", "build = " + json.dumps(TARGET),
        "host = [" + json.dumps(TARGET) + "]",
        "target = [" + json.dumps(TARGET) + "]",
        "build-dir = " + json.dumps(str(build_dir)),
        "jobs = 2", "docs = false", "submodules = false", "extended = true", "locked-deps = true",
        'tools = ["cargo", "rustdoc"]', "full-bootstrap = false", "",
        "[llvm]", "download-ci-llvm = true", "assertions = false", "",
        "[rust]", "download-rustc = false", "optimize = true", "debug = false",
        "debuginfo-level = 0", "codegen-units = 16", "codegen-units-std = 16",
        'lto = "off"', 'channel = "dev"', "omit-git-hash = false",
        "rpath = true", "remap-debuginfo = true", "",
        "[dist]", 'compression-formats = ["gz"]',
        'compression-profile = "fast"', "src-tarball = false", "",
    ])


def read_pin(path):
    result = {}
    for line in path.read_text().splitlines():
        key, value = line.split("=", 1)
        result[key.strip()] = json.loads(value.strip())
    return result


def verify_source(source, guard, env, log):
    run([guard], source, env, log)
    pin = read_pin(source / "upstream/rust.pin")
    revision = pin["revision"]
    identities = {}
    for scope in SCOPES:
        expected = run(["git", "rev-parse", revision + ":" + scope], source, env, log).stdout.strip()
        actual = run(["git", "rev-parse", "HEAD:" + scope], source, env, log).stdout.strip()
        if actual != expected:
            raise RuntimeError("upstream identity mismatch: " + scope)
        identities[scope] = actual
    run(["git", "diff", "--no-ext-diff", "--exit-code", revision, "--", *SCOPES], source, env, log)
    untracked = run(["git", "ls-files", "--others", "--exclude-standard", "--", *SCOPES], source, env, log)
    if untracked.stdout:
        raise RuntimeError("untracked upstream source additions")
    return {"upstream": pin, "protected_objects": identities}


def select_component(directory, component):
    matches = list(directory.glob(component + "-*-" + TARGET + ".tar.gz"))
    if len(matches) != 1:
        raise RuntimeError("expected exactly one " + component + " archive")
    return matches[0]


def install_components(build, work, prefix, source, env, log):
    records = []
    for component in ("rustc", "rust-std", "cargo"):
        archive = select_component(build / "dist", component)
        destination = work / ("installer-" + component)
        destination.mkdir()
        with tarfile.open(archive) as bundle:
            bundle.extractall(destination, filter="data")
        installers = list(destination.glob("*/install.sh"))
        if len(installers) != 1:
            raise RuntimeError("component installer missing or ambiguous: " + component)
        run(["sh", installers[0], "--prefix=" + str(prefix), "--disable-ldconfig"], source, env, log)
        records.append({"component": component, "archive": archive.name,
                        "sha256": digest(archive), "bytes": archive.stat().st_size})
    return records


def qualify(prefix, fixture_source, work, env, log, expected_revision):
    env = clean_environment(env)
    env.update({"PATH": str(prefix / "bin") + os.pathsep + env["PATH"],
                "RUSTC": str(prefix / "bin/rustc"), "RUSTDOC": str(prefix / "bin/rustdoc"),
                "CARGO_HOME": str(work / "qualification-cargo-home"),
                "CARGO_TARGET_DIR": str(work / "qualification-target"),
                "CARGO_BUILD_JOBS": "2", "CARGO_NET_OFFLINE": "true"})
    fixture = work / "qualification workspace"
    shutil.copytree(fixture_source, fixture)
    rustc = prefix / "bin/rustc"
    cargo = prefix / "bin/cargo"
    versions = {name: run([prefix / "bin" / name, "--version", "--verbose"], fixture, env, log).stdout
                for name in ("rustc", "rustdoc", "cargo")}
    compiler_identity = dict(line.split(": ", 1) for line in versions["rustc"].splitlines() if ": " in line)
    if compiler_identity.get("commit-hash") != expected_revision or compiler_identity.get("host") != TARGET:
        raise RuntimeError("produced compiler identity does not match the requested source and host")
    sysroot = run([rustc, "--print", "sysroot"], fixture, env, log).stdout.strip()
    if Path(sysroot).resolve() != prefix.resolve():
        raise RuntimeError("relocated compiler selected another sysroot")
    run([cargo, "generate-lockfile", "--offline"], fixture, env, log)
    result = run([cargo, "build", "--workspace", "--locked", "--offline", "--message-format=json"], fixture, env, log)
    messages = [json.loads(line) for line in result.stdout.splitlines() if line.startswith("{")]
    if not any(message.get("reason") == "build-finished" and message.get("success") for message in messages):
        raise RuntimeError("missing Cargo build-finished success record")
    run([cargo, "test", "--workspace", "--locked", "--offline"], fixture, env, log)
    result = run([cargo, "run", "-p", "bluefe-app", "--locked", "--offline", "--quiet"], fixture, env, log)
    if result.stdout.strip() != "bluefe-package-ok:42":
        raise RuntimeError("unexpected runtime result")
    invalid = fixture / "invalid.rs"
    invalid.write_text('fn main() { let x: u32 = "wrong"; println!("{x}"); }\n')
    rejected_output = fixture / "invalid-program"
    rejection = run([rustc, "--edition=2024", "--error-format=json", invalid, "-o", rejected_output], fixture, env, log, check=False)
    diagnostics = [json.loads(line) for line in rejection.stdout.splitlines() if line.startswith("{")]
    if rejection.returncode == 0 or rejected_output.exists() or not any(
        item.get("level") == "error" and (item.get("code") or {}).get("code") == "E0308"
        for item in diagnostics
    ):
        raise RuntimeError("invalid Rust rejection contract failed")
    return {"versions": versions, "relocated_sysroot": True, "cargo_workspace_build": True,
            "cargo_workspace_tests_and_doctests": True, "proc_macro": True, "build_script": True,
            "runtime": True, "panic_recovery_and_drop": True, "type_error_rejection": True}


def payload_manifest(prefix):
    records = []
    for path in sorted(prefix.rglob("*")):
        relative = path.relative_to(prefix).as_posix()
        if path.is_symlink():
            target = os.readlink(path)
            if Path(target).is_absolute() or not path.resolve().is_relative_to(prefix.resolve()):
                raise RuntimeError("package link escapes its root: " + relative)
            records.append({"path": relative, "type": "symlink", "target": target})
        elif path.is_file():
            records.append({"path": relative, "type": "file", "bytes": path.stat().st_size,
                            "mode": path.stat().st_mode & 0o777, "sha256": digest(path)})
        elif not path.is_dir():
            raise RuntimeError("unsupported package member: " + relative)
    return records


def archive_package(prefix, destination, epoch):
    with destination.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=epoch, compresslevel=6) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.GNU_FORMAT) as archive:
                for path in [prefix, *sorted(prefix.rglob("*"))]:
                    name = "bluefe-rust" if path == prefix else "bluefe-rust/" + path.relative_to(prefix).as_posix()
                    info = archive.gettarinfo(str(path), arcname=name)
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    info.mtime = epoch
                    if info.isfile():
                        with path.open("rb") as stream:
                            archive.addfile(info, stream)
                    else:
                        archive.addfile(info)


def validate_roots(source, work, output):
    for first, second in ((source, work), (source, output), (work, output)):
        if first.is_relative_to(second) or second.is_relative_to(first):
            raise RuntimeError("source, work and output must be separate non-overlapping directories")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--work", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--guard", required=True, type=Path)
    args = parser.parse_args()
    source, work, output = args.source.resolve(), args.work.resolve(), args.output.resolve()
    validate_roots(source, work, output)
    work.mkdir(parents=True)
    output.mkdir(parents=True)
    env = clean_environment(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    log = work / "build.log"
    source_record = verify_source(source, args.guard.resolve(), env, log)
    revision = run(["git", "rev-parse", "HEAD"], source, env, log).stdout.strip()
    epoch = int(run(["git", "show", "-s", "--format=%ct", "HEAD"], source, env, log).stdout.strip())
    build = work / "build"
    config = work / "bootstrap.toml"
    config.write_text(build_configuration(build))
    run(["python3", source / "x.py", "--config", config, "dist", "--stage", "1", "rustc", "rust-std", "cargo"], source, env, log, live=True)
    llvm = build / TARGET / "ci-llvm/bin/llvm-config"
    if not llvm.is_file():
        raise RuntimeError("required upstream CI LLVM was not used")
    llvm_version = run([llvm, "--version"], source, env, log).stdout.strip()
    stage0_versions = {name: run([build / TARGET / "stage0/bin" / name, "--version", "--verbose"], source, env, log).stdout
                       for name in ("rustc", "cargo")}
    prefix = work / "installed-toolchain"
    components = install_components(build, work, prefix, source, env, log)
    verify_source(source, args.guard.resolve(), env, log)
    build.rename(work / "unavailable-build-directory")
    relocated = work / "relocated toolchain" / "bluefe-rust"
    relocated.parent.mkdir()
    prefix.rename(relocated)
    qualification = qualify(relocated, source / "tools/bluefe-package/fixture", work, env, work / "qualification.log", revision)
    source_record.update({"repository": "glopyglerky/blueFe", "commit": revision,
                          "config_sha256": digest(config), "stage": 1,
                          "stage0": stage0_versions, "llvm": {"source": "upstream-ci", "version": llvm_version},
                          "components": components, "bootstrap_github_actions_detection": False})
    manifest = {"schema": "bluefe.pristine-rust-package.v1", "target": TARGET,
                "role": "rustc-compatibility-component", "native_lust_included": False,
                "complete_native_lustr": False, "source": source_record,
                "tool_sha256": {name: digest(relocated / "bin" / name)
                                for name in ("rustc", "rustdoc", "cargo")},
                "qualification": qualification,
                "qualified_host": {"system": platform.system(), "machine": platform.machine(),
                                   "libc": list(platform.libc_ver())}}
    write_json(relocated / "bluefe-package.json", manifest)
    shutil.copy2(config, output / "bootstrap.toml")
    write_json(output / "source-and-qualification.json", manifest)
    write_json(output / "payload-manifest.json", payload_manifest(relocated))
    archive = output / ("bluefe-pristine-" + revision[:12] + "-" + TARGET + ".tar.gz")
    archive_package(relocated, archive, epoch)
    with (output / "SHA256SUMS").open("w") as sums:
        for path in sorted(output.iterdir()):
            if path.name != "SHA256SUMS":
                sums.write(digest(path) + "  " + path.name + "\n")
    print("Qualified package: " + str(archive), flush=True)


if __name__ == "__main__":
    main()
