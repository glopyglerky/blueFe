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

After the Rust component qualifies, a separate job checks out the exact Lustr
commit recorded in the workflow and builds its unchanged native Lust compiler,
Lust client, TinyCC runtime and Lustr's in-process native Cargo compiler.
It combines those with this newly built BlueFe
component, validates the BlueFe manifest against the actual compiler identity
and binary hashes, and runs the Lustr package's relocation, runtime, rejection
and native coverage gates. A combined archive is uploaded only after those
checks pass. The Rust component remains independently downloadable if the later
combined-package job fails.

The combined artifact is named `bluefe-lustr-native-preview-x86_64-<commit>`.
Its archive extracts to `bluefe-lustr-native-preview-x86_64-unknown-linux-gnu`.
Native compilation calls Lust directly; Cargo selects the packaged Rust compiler
through its standard `RUSTC` and `RUSTDOC` inputs. The package contains no Lustr
coordinator executables and records `runtime_coordinator: false`.

```sh
LUSTR_ROOT=/absolute/path/to/bluefe-lustr-native-preview-x86_64-unknown-linux-gnu
"$LUSTR_ROOT/bin/lust" build main.rs -o app

# Run in a Cargo project with a lockfile.
RUSTC="$LUSTR_ROOT/bin/rustc" RUSTDOC="$LUSTR_ROOT/bin/rustdoc" \
  "$LUSTR_ROOT/bin/cargo" test --locked
```

Native Lust does not yet implement rustc's complete command and rlib artifact
contracts, so it cannot be selected as Cargo's general-purpose `RUSTC` replacement.
The combined preview records incomplete native Rust coverage. Its full Rust
compatibility comes from the packaged unchanged Rust compiler.

The additional `bin/lustr-native` executable supplies a bounded native Cargo
interface for dependency-free Rust 2024 binaries. It compiles through the original
Lust modules in the same process, supplies Cargo's crate identity through existing
native interfaces, and emits actual source and external-input dependency records.
Select it directly for a supported project:

```sh
RUSTC="$LUSTR_ROOT/bin/lustr-native" "$LUSTR_ROOT/bin/cargo" build --locked
```

This entry point has no rustc fallback. Native rlibs, Rust metadata, procedural
macro artifacts, test harnesses, release optimization and full language coverage
remain unimplemented and fail explicitly. It reports its own experimental
`0.1.0` version, so a manifest's higher minimum Rust version can also reject it.
Its unit cache and Cargo freshness are qualified separately from the original
Lust daemon; the daemon's warm latency is not claimed for this new path.

The native build receipt binds the actual Rust compiler invocation to the binary
hash, source revision and bootstrap identity. The package gate verifies that
receipt and compiles and runs the native fixture while the original build-time
runtime paths are unavailable. It checks included-file, environment, source and
feature changes against the packaged Rust compiler and retains both compilers'
raw timing results. These bounded checks do not establish complete Rust support
or preservation of every upstream speed ratio.

The pinned Lust baseline also has a confirmed external-input cache invalidation
defect involving whitespace or comments before the macro `!`. Read the
[known native cache limitation and scoped workaround](https://github.com/glopyglerky/lustr/blob/f1c4bf2c6a22baa2ea146bb270804be547c15473/docs/compiler-set/native-package.md#known-native-cache-limitation)
before using affected inputs. This package preserves the upstream source and
cache defaults; the defect remains unfixed.

## Build and source boundaries

The workflow runs on explicit `build/lustr-native-package*` branch pushes or a
manual dispatch. Its Linux job has a 180-minute limit. Compiler downloads are
disabled; the upstream stage0 bootstrap inputs and checksums remain unchanged.
LLVM comes from the upstream CI artifact selected by unchanged bootstrap code.
The necessary Cargo and backtrace submodules are initialized, together with the
book, reference and rustc-perf submodules required by upstream distribution's
copyright/dependency collection. LLVM source is not initialized, so a missing
CI artifact cannot silently become a full LLVM source build.

The separate `Assemble qualified BlueFe and Lustr` workflow can reuse an existing
successful component build. It runs on `package/qualified-native*` branch pushes
that change its workflow file, or a manual dispatch with immutable component and
Lustr revisions. It requires the selected component job to have succeeded, then
checks its run/source binding, complete payload manifest, actual tool hashes and
versions, and relocated sysroot before building and qualifying native Lust.
Its job has a 45-minute limit.

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
The host scope is Ubuntu 24.04 Linux GNU x86_64. Inspection of the
[qualified component](https://github.com/glopyglerky/blueFe/actions/runs/42977397326/artifacts/13837825042)
shows that Cargo and the Rust driver require glibc 2.39, and the driver requires
`libstdc++.so.6` providing `GLIBCXX_3.4.32`. Cargo dynamically links OpenSSL 3
through `libssl.so.3` and `libcrypto.so.3`, libcurl through `libcurl.so.4`, and
zlib through `libz.so.1`. These system libraries and their transitive dependencies are
required alongside the native linker and C development headers. The package
includes its Rust driver and LLVM libraries.

Install the dependencies used by the qualified Ubuntu 24.04 build with:

```sh
sudo apt-get update
sudo apt-get install build-essential libssl-dev libcurl4-openssl-dev zlib1g-dev ca-certificates
```

An older glibc host is outside this artifact's supported scope.

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
