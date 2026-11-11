# Package the unchanged Rust implementation

The `Pristine BlueFe package` workflow builds the current fork's unchanged Rust
implementation and produces a relocatable Linux GNU x86_64 compiler component.
It is separate from the historical stage2 previews. A successful artifact
contains a newly built stage1 rustc, matching native standard library, rustdoc
and Cargo built from the pinned Cargo submodule.

This is the full-Rust compatibility component for the combined toolchain. It
does not contain Lust or implement Lustr's missing native Rust coverage. The
manifest records `complete_native_lustr: false`. No compilation speedup is
claimed by this packaging workflow.

## Build and source boundaries

The workflow runs on explicit `build/lustr-native-package*` branch pushes or a
manual dispatch. Its Linux job has a 180-minute limit. Compiler downloads are
disabled; the upstream stage0 bootstrap inputs and checksums remain unchanged.
LLVM comes from the upstream CI artifact selected by unchanged bootstrap code.
Only the necessary Cargo and backtrace submodules are initialized. LLVM source
is not initialized, so a missing CI artifact cannot silently become a full LLVM
source build.

The build uses supported options in `bootstrap.example.toml`, with all output
and generated configuration outside source. It uses two build jobs, optimized
compiler code, no debug information and no cross-crate LTO. These are bounded
build settings, not a performance qualification.

Upstream bootstrap's GitHub Actions detection assumes that the current commit's
first parent is an upstream Rust CI commit. That is false for a fork branch.
The helper removes `GITHUB_ACTIONS` and `CI` from the bootstrap process's
environment so the existing ordinary Git-history lookup selects an upstream
commit. This setting is recorded in the package provenance. It does not change
bootstrap source or supply a replacement stage0 compiler.

Before and after building, the existing source guard runs. The package helper
also compares complete `compiler`, `library`, `src`, `tests`, entry-point,
Cargo manifest/lock and example-configuration identities with the pinned
upstream revision. Tracked edits and untracked additions in those scopes fail
qualification. No patches or generated overlays are applied.

## Qualification and artifacts

Upstream distribution installers assemble the package. The helper then moves
the toolchain into a path containing spaces and renames the old build directory
so its original location is unavailable. With inherited compiler wrappers,
compiler flags and dynamic-library path overrides removed, it checks:

- The produced compiler's commit hash, host and relocated sysroot.
- A Cargo workspace with a library, binary, procedural macro and build script.
- Generic and dynamic dispatch, program output, unit tests and doctests.
- Panic recovery with exactly one destructor invocation and thread execution.
- Structured rejection of invalid Rust with no executable produced.

Only a successful job uploads the package artifact. Build and qualification
logs are uploaded separately on success or failure. An uploaded log alone is
not a qualified package.

The package artifact contains a `.tar.gz` archive, `SHA256SUMS`, the exact
bootstrap configuration, a payload manifest and source/qualification metadata.
The compiler's upstream distribution licenses and notices remain included.
The host scope is the Ubuntu 24.04 Linux GNU x86_64 runner; a working native
linker, headers and system development libraries are still required.

Download the artifact belonging to the desired successful workflow commit into
a new directory, then run:

```sh
sha256sum -c SHA256SUMS
tar -xf bluefe-pristine-<commit>-x86_64-unknown-linux-gnu.tar.gz
BLUEFE_ROOT="$(pwd)/bluefe-rust"
"$BLUEFE_ROOT/bin/rustc" --version --verbose
"$BLUEFE_ROOT/bin/cargo" --version --verbose
```

Use the extracted compiler and documentation tool explicitly for a project:

```sh
RUSTC="$BLUEFE_ROOT/bin/rustc" \
RUSTDOC="$BLUEFE_ROOT/bin/rustdoc" \
"$BLUEFE_ROOT/bin/cargo" test --locked
```

These are bounded package integration tests. They do not certify every Rust
program, target, platform, dependency or runtime behavior. They do not admit any
upstream-source divergence or supersede the native compiler contract.
