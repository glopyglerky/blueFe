# blueFe

blueFe is a fork of Rust integrating [Lustr](https://github.com/glopyglerky/lustr).
The required compiler is a complete rustc replacement: Lustr must contain
the upstream Lust implementation, use it for everything it supports, and supply the
remaining Rust support in Lustr-owned code. That replacement is incomplete.

The current `./x` entry point uses the separate compatibility coordinator for
bootstrap and ordinary compiler, library and tool Cargo builds. rustc still
compiles full Rust, and bootstrap selects the stage compiler. The recovery
restores the fork's stage0 compatibility and bootstrap integration. Upstream
provenance and reviewed fork changes are checked separately by the
[source guard](docs/bluefe/upstream-preservation.md). Existing release binaries
retain their original identities. See the
[native integration status](docs/bluefe/native-lustr-status.md).

## Use a packaged toolchain

Use [preview-2026.11.09-2](https://github.com/glopyglerky/blueFe/releases/tag/preview-2026.11.09-2)
for Linux x86_64 GNU instead of rebuilding the compiler for each project.
Download all six assets into a versioned directory outside source checkouts.
The bundle requires GLIBC 2.39, GLIBCXX_3.4.32 and the libraries recorded in
`platform.json`; native linking also needs a C compiler, linker and development
files. Other hosts are unqualified.

```sh
sha256sum -c SHA256SUMS
tar --zstd -xf bluefe-lustr-preview-2026.11.09-2-x86_64-unknown-linux-gnu.tar.zst
BLUEFE_ROOT="$(pwd)/bluefe-lustr"
"$BLUEFE_ROOT/bin/lustr" --bluefe-root "$BLUEFE_ROOT" doctor
```

From a Rust project, use that absolute root with `build` or `test`. Keep the
compiler, sysroot and compiler-private tools together. Cargo is the identified
upstream bootstrap component. Application builds require no BlueFe source
checkout, compiler bootstrap, installation or global toolchain change.

The preview includes matching Clippy, rustfmt and experimental Cranelift with
unwinding. Select optional tools by their bundled absolute paths with explicit
`CARGO`, `RUSTC` and `RUSTDOC`; an ambient Cargo plugin can select another
installation. Native Lust/TCC/semantic engines and rustc-dev metadata are absent.
Native execution and Wasm linking are qualified; Wasm execution is unqualified.
This package does not implement the required native Lustr replacement. Its
compiler-build measurements do not measure Lust's native acceleration.
See the [release record](docs/bluefe/releases/preview-2026.11.09-2.md) for exact
source bindings, checksums, checks and limits.

See the [integration contract](docs/bluefe/integration-contract.md) and
[scoped proofs and qualification evidence](docs/bluefe/proofs/README.md).

## Measured performance

The [matched CGU16/ThinLTO stage2 pilot](docs/bluefe/measurements/2026-11-09-cgu16-thinlto/README.md)
completed 108 timed metadata-only root checks. The optimized package used 17.9%
less wall time than the matched no-PGO stage2 control, with conditional
candidate/control interval [0.7995, 0.8401]. It remained slower than stock Rust
1.99.1 on all three workloads. The stock comparison has unequal toolchain versions.
Full samples, CPU/scoped RSS, a Rust replay and mathematical arguments are in
the [Lustr data record](https://github.com/glopyglerky/lustr/blob/next/docs/compiler-set/measurements/2026-11-09-cgu16-thinlto-v3/README.md). The joint compiler-build treatment passed its
bounded numerical decision; full-build and general speed claims remain unqualified.

### Earlier frontend experiment

The [2026-11-09 public-repository experiment](https://github.com/glopyglerky/lustr/blob/next/docs/compiler-set/measurements/2026-11-09-shared-v2/README.md)
recorded 72 timed, dependency-primed metadata-only root checks, plus nine excluded
warmups. Ratios above 1 favor the denominator lane. N1/N4 compares explicit one
and four frontend threads on the same preview compiler.

| Project | Stock/N4 | N1/N4 |
| --- | --- | --- |
| t3code-ls | 1.268 | 2.345 |
| gitr | 0.927 | 1.342 |
| bluefin | 0.923 | 1.802 |

One-thread BlueFe regressed against stock in all three cases. Four-thread BlueFe
beat stock only on t3code-ls by point estimate. Different compiler/Cargo versions,
shared-host activity and N1's fixed middle position limit interpretation. Runtime
gates did not use the timed frontend options. These are not default whole-build
or general speedup claims. The report retains every regression, conditional
intervals, exact source/tool hashes, public samples, mathematical assumptions and
a Rust statistics replay command. Frontend parallelism remains explicit.

The separate [stage2 PGO research checkpoint](docs/bluefe/measurements/2026-11-09-pgo/README.md)
records a built candidate, passing runtime checks, exact hashes and narrow
mathematical arguments. Its missing-profile diagnostic gate remains unresolved;
no PGO timing or speedup is reported, and it does not replace the packaged preview.

## Build BlueFe from source

The coordinator is pinned as the root `lustr/` submodule. On a Git checkout,
`./x` initializes that submodule if needed, then builds only its dependency-free
coordinator with stage0 Cargo, offline and locked. It does not build native Lust
or install a Cranelift backend. With automatic submodule updates disabled, or
with a source archive, provide the pinned submodule contents before building.

Use the normal upstream build commands below. Coordinator output goes under
`<build-dir>/bluefe-lustr`; bootstrap uses the same configured build directory.
Cargo arguments, stage compilers, flags, profiles, features, and exit failures
are preserved. Specialized Clippy and Miri launchers and bootstrap's direct
Cargo metadata/version queries retain their upstream paths. Ordinary `cargo`
outside bootstrap and the resulting toolchain's default rustc are unchanged.

Stage0 is pinned to nightly-2026-11-03, Rust 1.101, with component checksums in
`src/stage0`. At the 2026-11-08 qualification, beta was too old for this source. The stage0 updater
therefore selects a nightly for blueFe's nightly channel. To refresh that pin,
use `./x run src/tools/bump-stage0 -- COMPILER_DATE RUSTFMT_DATE` and qualify the
result before publishing it.

To produce a compiler, complete native and wasm sysroots, and rustdoc:

```sh
./x build --stage 1 --target x86_64-unknown-linux-gnu,wasm32-unknown-unknown \
  compiler/rustc library src/tools/rustdoc
```

Use a build directory on a filesystem with enough space, configured through
`build.build-dir` in `bootstrap.toml`. Select the whole `library` tree so the
sysroot includes `proc_macro` and the test harness as well as `std`. Set
`rust.omit-git-hash = false` to include the source commit in compiler version
output. Upstream's prerequisite and LLVM setup
instructions below still apply. The produced native sysroot is
`<build-dir>/x86_64-unknown-linux-gnu/stage1`; its `bin/rustc` is distinct from
the downloaded stage0 compiler.

For an application build, select that produced compiler explicitly:

```sh
/path/to/lustr --bluefe-root /path/to/assembled-toolchain \
  build --target x86_64-unknown-linux-gnu
```

The assembled directory must contain `bin/cargo`, `bin/rustc`, `bin/rustdoc`,
and the produced sysroot libraries. Cargo remains an explicitly identified
upstream component. The selector preserves project arguments, compiler wrappers,
flags and profiles; an inherited explicit sysroot override still takes effect.
Use `lustr --bluefe-root /path/to/assembled-toolchain doctor` to inspect tools.

`rustc --print sysroot` must identify the produced sysroot. Select
`wasm32-unknown-unknown` for wasm builds. Native lustr and its separately pinned
Cranelift/semantic inspection tools are not interchangeable with this compiler;
their use requires separate compatibility qualification.

When explicitly building `compiler/rustc_codegen_cranelift`, bootstrap enables
its `unwinding` feature. This builds against the same in-tree compiler interfaces.
It does not select Cranelift for ordinary builds or establish backend qualification.

The blueFe integration is LLM-generated fork work and is not intended for
submission to `rust-lang/rust`.

## Source map

| Path | Role |
| --- | --- |
| `lustr/` | Pinned Lustr project. Its primary crate is `crates/lustr`; bootstrap builds it without native compiler dependencies. |
| `compiler/` | The current BlueFe compiler implementation, inherited from Rust and maintained as this fork. |
| `library/` | Standard libraries produced for the selected native and WebAssembly targets. |
| `src/bootstrap/` and `x` | Required bootstrap machinery, including BlueFe's coordinator routing and compiler-component integration. |
| `docs/bluefe/` | Project decisions, source-layout exceptions, divergence and qualification records. |

The inherited compiler and bootstrap paths remain because upstream build,
qualification and synchronization contracts use them. This repository has one
working compiler implementation. Required source is retained until its
replacement works and passes qualification.

The current priority is a usable compiler/toolchain and measured improvements.
Full native Lustr replacement and migration toward memory-safe Rust are future
work. TinyCC, LLVM, rustc internals and platform dependencies retain their actual
implementation and safety boundaries during that work.

See [the divergence record](docs/bluefe/divergences.md). The original Rust README
and project information remain available in [upstream Rust](https://github.com/rust-lang/rust).
Rust's MIT/Apache licensing and source history are preserved.
