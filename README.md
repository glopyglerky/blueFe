# blueFe

BlueFe holds the stock Rust source and must use
[Lustr](https://github.com/glopyglerky/lustr) as its only Rust compiler.
Lustr uses unchanged upstream Lust for its supported Rust subset and supplies
the remaining compiler behavior in Lustr-owned native code. Cargo selects
Lustr directly. The complete replacement remains unfinished.

The protected Rust compiler, standard library and bootstrap now match upstream
`5b7b37aefcb5b2fba3c2392bc9065b9e4602d494`. Earlier compiler compatibility edits
and bootstrap coordinator hooks have been removed. `./x` uses upstream bootstrap;
Lustr integration belongs outside that implementation. The
[upstream preservation gate](docs/bluefe/upstream-preservation.md) requires both
necessity and faster equivalent-workload evidence for any future divergence.
This source checkpoint does not replace existing release assets. See the
[native integration status](docs/bluefe/native-lustr-status.md).

## Build with Lustr

The [Lustr-only build contract](docs/bluefe/lustr-only-build.md) selects the
actual native compiler using upstream bootstrap's `build.rustc` option, with
Cargo supplied directly. The `BlueFe with Lustr only` workflow attempts the
unchanged compiler sources at stage zero and retains the native failure when
Lustr cannot compile them. It cannot qualify a build using a downloaded or
produced stock rustc. There is no fallback compiler or additional coordinator.

The older stock-Rust and mixed-package workflows are manual historical
experiments. They are not the BlueFe/Lustr product build and do not establish
native Lustr coverage.

## Historical packaged toolchain

The retained [preview-2026.11.09-2](https://github.com/glopyglerky/blueFe/releases/tag/preview-2026.11.09-2)
is a stock-rustc compatibility experiment for Linux x86_64 GNU. The following
commands reproduce that historical package, which does not meet the current
requirement. Its six assets belong in a versioned directory outside source checkouts.
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

## Historical rustc performance measurements

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

## Historical stock-rustc bootstrap recipe

This retained recipe builds and uses stock rustc. Current product work uses the
[Lustr-only gate](docs/bluefe/lustr-only-build.md) above.

Lustr is pinned as the root `lustr/` submodule. Its source and integration remain
separate from the protected upstream compiler and bootstrap. Initialize required
submodules explicitly and use upstream's normal build configuration. `./x` no
longer builds or inserts the compatibility coordinator into each Cargo call.

The upstream stage0 data and generator are restored byte for byte. Their beta
pin is dated 2026-09-29. The previous fork's version-floor heuristic and nightly
substitution are removed. A date or major/minor comparison alone does not prove
bootstrap compatibility. A fresh complete bootstrap with these restored inputs
has not been qualified here; retained binaries keep their versioned provenance.
Any necessary replacement build input needs an actual failing-first check and
qualification, without concealing changes to the compiler implementation.

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

Optional codegen backends need explicit upstream build options and matching
compiler, sysroot and runtime qualification. Bootstrap has no fork-specific
unwinding or coordinator patch at this checkpoint. Historical qualified backend
recipes and release evidence retain their original scope.

The blueFe integration is LLM-generated fork work and is not intended for
submission to `rust-lang/rust`.

## Source map

| Path | Role |
| --- | --- |
| `lustr/` | Pinned Lustr project. Compiler integration is owned here; upstream bootstrap does not build the coordinator. |
| `compiler/` | Protected, unchanged upstream Rust compiler implementation. |
| `library/` | Standard libraries produced for the selected native and WebAssembly targets. |
| `src/bootstrap/` and `x` | Unchanged upstream bootstrap machinery. |
| `docs/bluefe/` | Project decisions, source-layout exceptions, divergence and qualification records. |
| `upstream/rust.pin` and `tools/bluefe-rust-upstream-check.rs` | Upstream identities and a source-drift guard. |

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
