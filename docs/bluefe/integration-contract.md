# BlueFe integration contract

This records the transitional compatibility integration. The
[native Lustr requirement and current gaps](native-lustr-status.md) supersede
any interpretation that this coordinator completes the project. For the latest
published artifact, use the [versioned preview record](releases/preview-2026.11.09-2.md);
the earlier payload qualification below retains its original identities and scope.

This contract describes BlueFe control and packaging, not a new implementation
of Rust semantics. Full Rust is compiled by produced rustc behind Lustr. Native
Lust is a separate, restricted compiler. LLVM, TCC, native libraries, upstream
unsafe Rust and operating-system interfaces prevent a whole-stack memory-safety
claim. No universal speedup or semantic-equivalence theorem is asserted.

The source recovery restores these integration paths while retaining the newer
upstream changes from the intervening merge. It does not rebuild or replace
previous releases. See the [source preservation policy](upstream-preservation.md).

## Invocation and source identity

`./x` remains the bootstrap entry point. Python builds the pinned root Lustr
crate, then invokes it with `--engine auto -- build ...`. Ordinary Rust bootstrap
Cargo operations also use Lustr; specialized Clippy and Miri launchers remain
specialized. The configured bootstrap Cargo is explicitly passed as `LUST_CARGO`.
Stage0 builds the compiler; it is not the produced compiler.

Bootstrap initializes a missing root `lustr` manifest through the root gitlink
only when submodules are enabled and the source is a Git checkout. It refuses to
reset an initialized but incomplete submodule. Offline/source archives must
supply the pinned source themselves. Existing initialized submodules must be
checked against the gitlink before claiming reproducibility; bootstrap does not
validate their cleanliness or revision. No pointer upgrade is implicit.

The stage0 preflight probes the configured rustc with a 15-second timeout and
requires its major/minor version to be at least the source's preceding release.
This rejects known too-old compilers before compiling bootstrap. It is a necessary
version floor, not proof of feature, ABI, dependency or target compatibility.
Use the pinned `src/stage0` nightly or a qualified produced compiler. Failures do
not select an alternate compiler. Toolchain download/setup precedes this probe.

For applications, use an absolute retained toolchain root:

```sh
"$TOOLCHAIN/bin/lustr" --bluefe-root "$TOOLCHAIN" plan test --offline
"$TOOLCHAIN/bin/lustr" --bluefe-root "$TOOLCHAIN" test --offline
```

The root selects Cargo, rustc and rustdoc together; `+toolchain` and native Lust
conflict with this selection. A plan is an inspection request: missing tools do
not invalidate planning, and no tool is executed. Execution checks the three tool
files exist. File existence is not authenticity, executable permission, matching
ABI or a complete sysroot. External Cargo configuration, wrappers, flags,
build scripts and linker settings still participate; inspect them for acceptance.
Do not describe an uncontrolled invocation as produced-compiler evidence.

## Earlier retained payload qualification

The evidence in [proofs](proofs/README.md) identifies compiler source
`7005dc02c9fb6674380eade443022bbc04215276`, BlueFe control source
`cf66538177236a167307b07fa8f862f03a524919` plus the integration patch, and root
Lustr `6339fbb104d6adda4be7e6be7dc637a6a9e5586b`. Compiler, library and rustdoc
trees agree with the compiler-producing source; control/bootstrap changes do
not establish a newly rebuilt compiler. Cargo is unmodified bootstrap Cargo
1.101 nightly, not produced Cargo. Native x86_64 Linux execution and
wasm32-unknown-unknown linking are supported by the observed fixture. Wasm
execution, WASI, other hosts and full upstream release qualification are untested.
Retained payload means an explicitly addressed artifact, not a system install.

## Matching optional components

Clippy, rustfmt and cgclif must match compiler-private interfaces, build features,
target and native-library closure. A similar version string or identical public
compiler source tree is insufficient. Their source trees are embedded upstream
subtrees; do not edit those tools here or advance their integration automatically.
That earlier payload lacks all three components and rustc-dev metadata. It has a
runtime rustc_driver shared library, which does not supply private crate metadata.
The original compiler build cache was retired. Component-only compilation against
this payload is therefore unavailable; never load a backend from another nightly.

[The build recipe](proofs/matching-components.md) prepares a fresh matching
compiler/component set. Bootstrap already requests cgclif `--features=unwinding`.
Before accepting that backend, run a panic catch/drop test through the actual
selected backend, plus native run/test/doctest/rejection tests. The LLVM panic test
in this patch does not qualify cgclif. Wasm remains LLVM unless separately proved.

## Publication, relocation and retention

Publish a manifest containing source commit/tree/gitlink identities, dirty patch
hash, stage0 identities, produced tool versions and hashes, source component
trees, features, targets and qualification results. For every payload entry record
relative path, type, executable mode, byte hash or symlink target. Retain native
runtime libraries, licenses and required linkers. Record Cargo's bootstrap origin.
Hash the final sanitized evidence bytes separately from the private original logs;
never attach host paths, credentials or thread metadata to public evidence.

Before publication copy the complete candidate to a different absolute path and
rerun the fixture with explicit tools, isolated Cargo home/target and no compiler
wrappers. Check reported sysroot, dynamic library resolution, native execution,
doctests and Wasm linking there. Reject absolute symlinks or RPATHs into a build
cache. The retained payload passed the same 32-test suite after a complete copy
to another absolute path containing spaces on the same host. The reported sysroot
followed the copy, rustc's dynamic libraries resolved without the original root,
and all 326 payload file/symlink entries matched. This does not prove portability
to a different host or libc. Repeat relocation for every newly built candidate.

Keep the current accepted artifact and one useful rollback outside generated
build targets. After the owner checks live processes, open files, mounts and
Cargo locks, remove owned disposable build/dependency/staging roots. Record
actual available-space change. Never clean another owner's research output.
