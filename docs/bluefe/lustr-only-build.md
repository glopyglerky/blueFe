# BlueFe uses Lustr

BlueFe preserves the stock Rust implementation at `upstream/rust.pin`. Lustr is
the required compiler for that source. Lustr must compile Lust's supported
subset through unchanged Lust and implement the remaining Rust semantics,
libraries and artifacts in its own native code. Cargo selects Lustr directly.

The old stock-rustc component and mixed-package workflows are retained as
manual historical experiments. Their successful builds and archives do not
satisfy this contract. New native work is qualified by
[`bluefe-lustr-only.yml`](../../.github/workflows/bluefe-lustr-only.yml).
The inherited upstream compiler-matrix workflow is restricted to
`rust-lang/rust`; it no longer automatically builds BlueFe with stock rustc on
fork pull requests. Source-preservation checks remain active in the fork.

## Actual build selection

[`tools/bluefe-native/build.py`](../../tools/bluefe-native/build.py) creates an
external bootstrap configuration with `build.rustc` pointing to the supplied
native Lustr executable and `build.cargo` pointing to Cargo. It runs unchanged
`x.py build --stage 0 compiler/rustc`. Stage zero is deliberate: later stages
would start using the stock compiler produced from BlueFe's source. The
selected native compiler must perform BlueFe's Rust compilation throughout
this gate.

Compiler downloads are disabled with `rust.download-rustc = false`, and the
configured external stage-zero compiler prevents upstream bootstrap from
downloading a substitute. The original Rust stage-zero data, bootstrap source
and compiler source remain unchanged. LLVM and the C toolchain remain normal
native build inputs. Preparing Lustr itself with the recorded Rust bootstrap
compiler is separate from compiling BlueFe with Lustr.

The runner records the compiler binary hash and verbose identity, source
commit, exact bootstrap configuration, command, exit code and process trace.
It clears inherited Rust compiler selectors and wrappers and puts failing
sentinels on the executable search path for ambient compiler/toolchain names.
The only permitted Rust compiler executable is the supplied Lustr. Upstream's
own bootstrap forwarding shim is permitted at its exact generated path; it
must still call Lustr. Source guards run before and after the attempt. A
successful exit without an actual compiler artifact or native compiler
execution does not qualify.

```sh
python3 tools/bluefe-native/build.py \
  --source /absolute/blueFe \
  --lustr /absolute/native-build/lustr-native \
  --cargo /absolute/cargo \
  --guard /absolute/bluefe-source-guard \
  --work /absolute/new-bluefe-build
```

The work directory must be new and outside the checkout. `strace` is required
for compiler-process evidence. Where process tracing is unavailable,
`--diagnostic-without-trace` permits an actual diagnostic build but always
leaves qualification unsuccessful. It cannot turn an unobserved build into
compiler-exclusivity evidence.

## Current result and remaining work

This is a required build gate, not a claim that Lustr can already compile the
Rust compiler. The first local diagnostic attempt selected the real native
compiler and reached Cargo's target-information request. Lustr rejected the
upstream bootstrap option `-Zallow-features=`. That failure is retained.
The new native query implementation answers the exact bootstrap request while
keeping unimplemented lint/feature options as errors for source compilation.
The next actual diagnostic passes that query and stops at Cargo's minimum Rust
version checks: dependencies require versions above Lustr's advertised `0.1.0`.
The compiler identity is not changed to claim unverified Rust compatibility.
Neither attempt reaches BlueFe Rust source compilation.

The strict local attempt was separately blocked by the environment's unavailable
`ptrace`; it did not execute a compiler and is not native failure evidence.
Local diagnostic runs do not establish compiler-process exclusivity. GitHub
Actions runs the strict gate with process tracing.

Native library compilation and cross-crate import are being implemented in
Lustr outside its preserved upstream source. Those additions must pass real
artifact, source-hidden consumer, type/visibility rejection, ownership, panic,
drop and equivalent-workload speed checks. A passing small library fixture does
not establish BlueFe bootstrap, procedural macros, full Rust language support,
Rust ABI interoperability or preservation of all Lust speed gains.

The completion gate remains an unchanged BlueFe build and representative full
Rust projects compiled by Lustr, with their behavior and compilation times
qualified. A stock-rustc binary, a successful package assembly, or a renamed
compiler does not close these implementation gaps.
