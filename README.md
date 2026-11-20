# blueFe

blueFe preserves the full upstream Rust fork. [Lustr](https://github.com/glopyglerky/lustr)
is the complete-compiler project: Lust exclusively compiles every operation it
covers, and Lustr imports only the upstream implementation needed for the
remaining Rust work. The complete replacement is unfinished.

Read the [current compiler direction](docs/bluefe/native-lustr-status.md), which
links Lustr's canonical contract and active correction. blueFe supplies source
provenance, selective extraction and an independent reference compiler. A full
rustc fallback, complete-driver library or duplicate checking of Lust-owned
work does not implement that goal. Preserve Lust's retained state and speed.

The protected Rust compiler, standard library and bootstrap match upstream
`4b5350e87e487aed08ab2f9f0160a4b2616438bc`. Earlier compiler compatibility edits
and bootstrap coordinator hooks have been removed. `./x` uses upstream bootstrap.
The [upstream preservation gate](docs/bluefe/upstream-preservation.md) requires
necessity and faster equivalent-workload evidence for divergence from these
protected Rust scopes. Lustr's own source policy separately governs its pristine
Lust reference and explicit integration changes.

## Retained previews

The versioned [compatibility preview](docs/bluefe/releases/preview-2026.11.09-2.md)
contains a produced Rust compiler, Cargo, matching tools and a coordinator. It
contains no native Lust. The later
[native preview](docs/bluefe/releases/native-preview-2026.11.15-1.md) contains a
bounded Lust path and an official full Rust compatibility SDK. Both records
preserve their original download instructions, checksums, source identities,
qualification and platform limits.

These are historical artifacts, not completed Lustr replacements or a current
release recipe. This source checkpoint neither rebuilds nor replaces them.
Continue Lustr through its active correction rather than using an old
`--bluefe-root` coordinator to fill missing native coverage. The
[historical integration contract](docs/bluefe/integration-contract.md) and
[scoped proofs](docs/bluefe/proofs/README.md) remain available for reproduction.

## Historical performance evidence

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

## Build the upstream reference from source

The root `lustr/` gitlink preserves an older compatibility checkpoint. Refresh
Lustr's canonical contract and active implementation before integration work;
initializing that gitlink does not select the current correction. Keep the
protected upstream compiler and bootstrap unchanged. The commands in this
section build the independent Rust reference, not Lustr's missing product
compiler. `./x` no longer builds or inserts the compatibility coordinator.

The upstream stage0 data and generator are restored byte for byte. Their beta
pin is dated 2026-11-10. The previous fork's version-floor heuristic and nightly
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
output. Follow the upstream prerequisite and LLVM setup instructions linked
from `CONTRIBUTING.md`. The produced native sysroot is
`<build-dir>/x86_64-unknown-linux-gnu/stage1`; its `bin/rustc` is distinct from
the downloaded stage0 compiler.

When qualifying Lustr outputs, identify the produced compiler explicitly as
the independent upstream reference. Keep compiler-private components, sysroots,
flags and source identity matched. A declared bootstrap compiler may build
Lustr itself; this does not permit it to supply the semantics or artifacts
requested from Lustr. An independent stock Rust consumer may verify an artifact
that Lustr has already constructed from genuine native checked completion.
Artifact creation, downstream rejection, linking and execution need separate
observations; a direct-object or C-ABI bypass is not Rust crate interoperability.

Optional codegen backends need explicit upstream build options and matching
compiler, sysroot and runtime qualification. Bootstrap has no fork-specific
unwinding or coordinator patch at this checkpoint. Historical qualified backend
recipes and release evidence retain their original scope.

The blueFe integration is LLM-generated fork work and is not intended for
submission to `rust-lang/rust`.

## Source map

| Path | Role |
| --- | --- |
| `lustr/` | Retained older Lustr gitlink. Refresh the active Lustr correction before implementation; upstream bootstrap does not build the coordinator. |
| `compiler/` | Protected, unchanged upstream Rust compiler implementation. |
| `library/` | Standard libraries produced for the selected native and WebAssembly targets. |
| `src/bootstrap/` and `x` | Unchanged upstream bootstrap machinery. |
| `docs/bluefe/` | Project decisions, source-layout exceptions, divergence and qualification records. |
| `upstream/rust.pin` and `tools/bluefe-rust-upstream-check.rs` | Upstream identities and a source-drift guard. |

The full compiler and bootstrap remain here for upstream synchronization,
source preservation, independent reference qualification and selective
extraction. They are not waiting to be copied wholesale into Lustr.

Complete Lustr replacement is the active compiler goal. Correct full coverage
and a measured overall speedup over matched stock Rust are the first-release
condition; near-stock subset speed remains the optimization goal. Portability
work should preserve retained compilation and performance. TinyCC, LLVM, Rust
internals and platform dependencies retain their actual implementation and
safety boundaries during that work.

See [the divergence record](docs/bluefe/divergences.md). The original Rust README
and project information remain available in [upstream Rust](https://github.com/rust-lang/rust).
Rust's MIT/Apache licensing and source history are preserved.
