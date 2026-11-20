# Native Lustr integration

Lustr must be a complete rustc replacement containing unchanged upstream Lust.
Lust must compile everything it supports; Lustr-owned native code must supply
the missing language, standard-library and crate support. BlueFe keeps stock
Rust source and uses Lustr as its only Rust compiler. Cargo selects Lustr
directly. A Cargo coordinator or a tuned rustc build does not complete it.

## Source baseline

The root `lustr` gitlink selects
[`0bda81337a528a8ab910208357b65693b2f06fbb`](https://github.com/glopyglerky/lustr/commit/0bda81337a528a8ab910208357b65693b2f06fbb).
Its `compiler/native` tree is exactly upstream Lust revision
`240e08d91d4aed0299639f6f11fd522912b248f9`, tree
`0ab1b09815802894e6078de0af59273cbdf46cb0`. Earlier fork overrides and an
unpublished expansion candidate are excluded. The source guard rejects drift.
Lustr-owned work belongs outside the upstream baseline. Any proposed Lust
exception requires demonstrated necessity and faster equivalent-workload results.
See the [preservation policy](https://github.com/glopyglerky/lustr/blob/0bda81337a528a8ab910208357b65693b2f06fbb/docs/compiler-set/upstream-lust.md).

## Rust source baseline

The protected Rust implementation now matches upstream
`5b7b37aefcb5b2fba3c2392bc9065b9e4602d494`. The compiler tree is
`9bb98adca40010656ac057f2c4103cf72f5cdc6f`; the library tree is
`f48d6700750a1dc11b2f8f1df91a26dee3ef13fb`. Bootstrap and stage0 are also
restored to upstream. The [preservation gate](upstream-preservation.md) binds
all five protected scopes and rejects unqualified source divergence. Existing
releases keep their earlier source and binary identities.

## Actual implementation

The native `lustr-native` executable imports the unchanged Lust compiler
modules in process. Its dependency-free binary path retains the original Lust
driver. Lustr-owned native code now emits real ELF library objects with typed
metadata and imports safe/unsafe scalar function signatures into binary consumers.
Consumers link the compiled objects without the producer's source. This is
Lustr's native format; full Rust metadata and ABI interoperability are not
implemented.

Owned native syntax and semantic checks now implement scalar unsafe function
contracts, unsafe blocks and function pointers. The independent-library fixture
keeps its original unsafe requirements and adds rejection checks for aliases,
scope, pointer conversions, lint precedence and closure returns. Raw-pointer
operations, unsafe FFI, public types/traits/generics, procedural macros,
transitive native libraries, full standard-library support and many
Cargo/compiler requests remain unfinished. The separate safe-library diagnostic
does not replace the required gate.

The [Lustr-only build](lustr-only-build.md) selects the actual native executable
through unchanged upstream bootstrap's `build.rustc` setting and records its
execution. The first local diagnostic reached Cargo's compiler probe and
failed on `-Zallow-features=`. The corrected native query passes that request;
the next actual diagnostic stops at Cargo's minimum Rust version checks because
dependencies require versions above Lustr's advertised `0.1.0`. This still
happens before BlueFe source compilation. BlueFe has not been compiled
successfully by Lustr. The workflow retains failures and source-preservation
results.

An earlier pristine Lust build passed 391 upstream unit tests with Cargo 1.99.1,
plus isolated relocated check/build/run and invalid-type rejection probes.
The build-script reader failed with Cargo 1.101 nightly's newer artifact layout;
the first failure is retained. This is a compatibility constraint, not a reason
to patch Lust without the required admission evidence. These checks establish
the exercised native subset, not a full compiler or a speedup.

## Release distinction

The native Lustr product excludes stock rustc, rustdoc, the stock Rust sysroot
and the historical coordinator. A separate Rust compiler is used to bootstrap
Lustr itself and as a test oracle. The old stock-Rust and mixed-package workflows
are manual historical experiments, separate from BlueFe's Lustr-only gate.
The inherited upstream compiler-matrix workflow runs only for `rust-lang/rust`;
fork pull requests use the native build gate and source-preservation checks.

`preview-2026.11.09-2` remains a rustc-based compatibility package. It contains
no native Lust. Its source and binary bindings remain those in its versioned
release record; updating this gitlink does not rebuild or replace those assets.

The required replacement must first demonstrate complete supported-request
routing, mixed-feature programs, real crate artifacts, correct rejection,
ownership/panic/drop behavior and warm/cold edit consistency. Compare the actual
native compiler against stock Rust on equivalent work, preserving every
regression. Upstream subset speed cannot be multiplied into a full-project
speed claim without measuring covered work and integration cost. No universal
non-regression or memory-safety claim is made.
