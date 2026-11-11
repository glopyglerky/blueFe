import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile
import tomllib
import urllib.request


INVALIDATION_PATHS = [
    "src/llvm-project",
    "src/bootstrap/download-ci-llvm-stamp",
    "src/version",
]
GCC_INVALIDATION_PATHS = ["src/gcc", "src/bootstrap/download-ci-gcc-stamp"]
REPOSITORY = "https://github.com/rust-lang/rust"
TARGET = "x86_64-unknown-linux-gnu"
SOURCE_PATHS = {
    *INVALIDATION_PATHS,
    *GCC_INVALIDATION_PATHS,
    "src/ci",
    "src/bootstrap",
    "src/build_helper",
    "src/stage0",
    "src/ci/channel",
    "src/ci/run.sh",
    "src/ci/shared.sh",
    "src/ci/docker/run.sh",
    "src/ci/scripts/run-build-from-ci.sh",
    "src/ci/scripts/setup-environment.sh",
    "src/ci/github-actions/jobs.yml",
    "src/ci/citool",
    "src/ci/docker/host-x86_64/test-tidy/Dockerfile",
    "src/ci/docker/host-x86_64/test-x86_64-gnu-gcc/Dockerfile",
    "bootstrap.example.toml",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def read_pin(root):
    result = {}
    for line in (root / "upstream/rust.pin").read_text().splitlines():
        key, value = line.split("=", 1)
        key = key.strip()
        require(key not in result, "duplicate upstream pin field")
        result[key] = json.loads(value.strip())
    return result


def ensure_upstream(root, revision):
    require(re.fullmatch(r"[0-9a-f]{40}", revision), "invalid upstream revision")
    exists = subprocess.run(
        ["git", "-C", str(root), "cat-file", "-e", f"{revision}^{{commit}}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if exists.returncode:
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
        subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "-c",
                "credential.helper=",
                "-c",
                "http.extraheader=",
                "-c",
                "http.https://github.com/.extraheader=",
                "fetch",
                "--no-tags",
                "--filter=blob:none",
                "--depth=1",
                REPOSITORY + ".git",
                revision,
            ],
            env=env,
            check=True,
        )


def verify_sources(root, manifest):
    pin = read_pin(root)
    require(manifest["schema"] == 1, "unsupported artifact manifest")
    require(pin["repository"] == REPOSITORY, "unexpected upstream repository")
    require(
        manifest["upstream_repository"] == REPOSITORY, "unexpected artifact repository"
    )
    revision = manifest["upstream_revision"]
    require(re.fullmatch(r"[0-9a-f]{40}", revision), "invalid upstream revision")
    require(pin["revision"] == revision, "artifact does not match upstream pin")
    require(
        pin["root_tree"] == manifest["upstream_root_tree"], "upstream tree mismatch"
    )
    require(
        git(root, "rev-parse", revision + "^{tree}") == pin["root_tree"],
        "fetched upstream tree mismatch",
    )
    require(
        manifest["llvm_invalidation_paths"] == INVALIDATION_PATHS,
        "LLVM invalidation contract changed",
    )
    require(
        manifest["gcc_invalidation_paths"] == GCC_INVALIDATION_PATHS,
        "GCC invalidation contract changed",
    )
    parents = git(root, "rev-list", "--parents", "-n", "1", "HEAD").split()
    require(len(parents) == 3, "cache preparation requires the actual PR merge commit")
    objects = manifest["source_objects"]
    require(set(objects) == SOURCE_PATHS, "source/configuration input contract changed")
    for path, expected in objects.items():
        require(
            git(root, "rev-parse", f"{revision}:{path}") == expected,
            f"upstream input mismatch: {path}",
        )
        upstream_entry = git(root, "ls-tree", revision, "--", path)
        for ref in ("HEAD", parents[1]):
            require(
                git(root, "ls-tree", ref, "--", path) == upstream_entry,
                f"fork input mismatch: {ref}:{path}",
            )
    paths = list(objects)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "core.filemode=true",
            "diff",
            "--no-ext-diff",
            "--ignore-submodules=none",
            "--quiet",
            "HEAD",
            "--",
            *paths,
        ],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "diff",
            "--no-ext-diff",
            "--quiet",
            "--cached",
            "HEAD",
            "--",
            *paths,
        ],
        check=True,
    )
    require(
        not git(root, "ls-files", "--others", "--exclude-standard", "--", *paths),
        "untracked source/configuration input",
    )
    require(
        git(root, "show", f"{parents[1]}:src/ci/channel") == "nightly",
        "cache key does not use the pinned nightly artifact channel",
    )
    return parents[0], parents[1]


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def artifact_spec(manifest, component):
    require(component in {"llvm", "gcc"}, "unsupported artifact component")
    return manifest if component == "llvm" else manifest["gcc_artifact"]


def archive_name(component):
    require(component in {"llvm", "gcc"}, "unsupported artifact component")
    package = "rust-dev" if component == "llvm" else "gcc-dev"
    return f"{package}-nightly-{TARGET}"


def verify_archive(path, manifest, component="llvm"):
    spec = artifact_spec(manifest, component)
    require(path.stat().st_size == spec["archive_bytes"], "archive size mismatch")
    require(digest(path) == spec["archive_sha256"], "archive SHA-256 mismatch")
    require(manifest["target"] == TARGET, "unsupported artifact target")
    prefix = archive_name(component) + "/"
    names = ["git-commit-hash", "git-commit-info", "version", "builder-config"]
    if component == "llvm":
        require(manifest["llvm_assertions"] is True, "unsupported LLVM assertion mode")
        names.append("rust-dev/link-type.txt")
    metadata = {}
    with tarfile.open(path, "r:xz") as archive:
        members = archive.getmembers()
        for name in names:
            matches = [member for member in members if member.name == prefix + name]
            require(len(matches) == 1, f"missing or duplicate archive metadata: {name}")
            member = matches[0]
            require(
                member.isfile() and member.size <= 131072,
                f"invalid archive metadata: {name}",
            )
            metadata[name] = archive.extractfile(member).read()
        if component == "gcc":
            libraries = [
                member
                for member in members
                if member.name == prefix + "gcc-dev/lib/libgccjit.so"
            ]
            require(
                len(libraries) == 1 and libraries[0].isfile() and libraries[0].size > 0,
                "missing GCC JIT library",
            )
    revision = manifest["upstream_revision"]
    require(spec["artifact_git_commit"] == revision, "artifact commit differs from pin")
    require(
        metadata["git-commit-hash"].decode().strip() == revision,
        "archive publication commit mismatch",
    )
    require(
        metadata["git-commit-info"].decode().splitlines()[0] == revision,
        "archive commit info mismatch",
    )
    require(
        metadata["version"].decode().strip() == spec["artifact_version"],
        "archive version mismatch",
    )
    require(
        hashlib.sha256(metadata["builder-config"]).hexdigest()
        == spec["builder_config_sha256"],
        "archive builder configuration mismatch",
    )
    configuration = tomllib.loads(metadata["builder-config"].decode())
    result = {
        "git_commit": revision,
        "version": metadata["version"].decode().strip(),
        "builder_config_sha256": spec["builder_config_sha256"],
    }
    if component == "llvm":
        require(
            metadata["rust-dev/link-type.txt"].decode().strip()
            == spec["artifact_link_type"],
            "archive link type mismatch",
        )
        require(
            configuration["llvm"]["assertions"] is True, "archive assertions disabled"
        )
        result["link_type"] = spec["artifact_link_type"]
        result["llvm_configuration"] = configuration["llvm"]
    else:
        result["gcc_configuration"] = configuration["gcc"]
        result["library"] = "gcc-dev/lib/libgccjit.so"
    return result


def archive_url(manifest, component="llvm"):
    revision = manifest["upstream_revision"]
    require(re.fullmatch(r"[0-9a-f]{40}", revision), "invalid upstream revision")
    server = "rustc-builds-alt" if component == "llvm" else "rustc-builds"
    return (
        f"https://ci-artifacts.rust-lang.org/{server}/{revision}/"
        + archive_name(component)
        + ".tar.xz"
    )


def download(manifest, destination, component):
    url = archive_url(manifest, component)
    spec = artifact_spec(manifest, component)
    with (
        urllib.request.urlopen(url, timeout=60) as response,
        destination.open("wb") as output,
    ):
        require(response.geturl() == url, "unexpected artifact redirect")
        size = 0
        while chunk := response.read(1024 * 1024):
            size += len(chunk)
            require(size <= spec["archive_bytes"], "artifact exceeds pinned size")
            output.write(chunk)


def confined_output(root, path):
    require(path.is_relative_to(root), "output path leaves checkout")
    current = root
    for part in path.relative_to(root).parts:
        current /= part
        require(not current.is_symlink(), "output path contains a symlink")
    require(path.resolve().is_relative_to(root), "output path leaves checkout")
    return path


def prepare(root, manifest, job, archive=None, gcc_archive=None):
    root = root.resolve()
    require(job in manifest["jobs"], "job is not qualified for this artifact cache")
    components = manifest["jobs"][job]
    require(
        components
        and len(components) == len(set(components))
        and set(components) <= {"llvm", "gcc"},
        "invalid job artifact profile",
    )
    require(
        os.uname().sysname == "Linux" and os.uname().machine == "x86_64",
        "artifact cache requires Linux x86-64",
    )
    commit, cache_commit = verify_sources(root, manifest)
    output = confined_output(root, root / "obj/ci-artifact-provenance.json")
    artifacts = {}
    for component in components:
        spec = artifact_spec(manifest, component)
        filename = archive_name(component) + ".tar.xz"
        cache_key = (
            f"llvm-{TARGET}-{cache_commit}-true"
            if component == "llvm"
            else f"gcc-{cache_commit}"
        )
        cache_dir = confined_output(root, root / "obj/build/cache" / cache_key)
        cache_dir.mkdir(parents=True, exist_ok=True)
        confined_output(root, cache_dir)
        destination = confined_output(root, cache_dir / filename)
        local_archive = archive if component == "llvm" else gcc_archive
        with tempfile.TemporaryDirectory(
            prefix=".ci-artifact-", dir=cache_dir
        ) as temporary:
            pending = Path(temporary) / filename
            if local_archive is None:
                download(manifest, pending, component)
            else:
                shutil.copyfile(local_archive, pending)
            metadata = verify_archive(pending, manifest, component)
            confined_output(root, destination)
            os.replace(pending, destination)
        artifacts[component] = {
            "official_artifact_url": archive_url(manifest, component),
            "archive_bytes": spec["archive_bytes"],
            "archive_sha256": spec["archive_sha256"],
            "digest_source": spec["digest_source"],
            "cache_path": str(destination.relative_to(root)),
            "artifact_metadata": metadata,
        }
    receipt = {
        "schema": 1,
        "job": job,
        "checkout_commit": commit,
        "upstream_publication_commit": manifest["upstream_revision"],
        "upstream_root_tree": manifest["upstream_root_tree"],
        "bootstrap_cache_key_commit": cache_commit,
        "cache_alias_basis": "All recorded backend source and CI configuration objects match the pinned upstream commit.",
        "artifact_published_for_fork_commit": False,
        "source_objects": manifest["source_objects"],
        "llvm_invalidation_paths": INVALIDATION_PATHS,
        "gcc_invalidation_paths": GCC_INVALIDATION_PATHS,
        "artifacts": artifacts,
        "bootstrap_source_modified": False,
        "existing_bootstrap_validation": {
            "llvm": "configuration compatibility check unchanged; runs during the build",
            "gcc": "source freshness and host/target checks unchanged",
        },
    }
    confined_output(root, output)
    with tempfile.NamedTemporaryFile(
        mode="w", prefix=".ci-artifact-receipt-", dir=output.parent, delete=False
    ) as pending:
        pending.write(json.dumps(receipt, indent=2) + "\n")
        pending_path = Path(pending.name)
    try:
        confined_output(root, output)
        os.replace(pending_path, output)
    finally:
        pending_path.unlink(missing_ok=True)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True)
    parser.add_argument("--llvm-archive", type=Path)
    parser.add_argument("--gcc-archive", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    manifest = json.loads((root / ".github/ci-artifacts.json").read_text())
    require(
        read_pin(root)["revision"] == manifest["upstream_revision"],
        "artifact does not match upstream pin",
    )
    ensure_upstream(root, manifest["upstream_revision"])
    receipt = prepare(root, manifest, args.job, args.llvm_archive, args.gcc_archive)
    print(receipt.read_text())


if __name__ == "__main__":
    main()
