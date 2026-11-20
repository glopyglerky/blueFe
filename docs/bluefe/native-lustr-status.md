# Lustr direction and retained integration state

Lustr's sole goal is a complete Rust compiler that preserves Lust's speed for
every operation Lust covers and imports only the upstream implementation needed
for the remaining operations. Lust remains the exclusive owner of its covered
work, including supported work inside mixed programs. A gap in Lustr's bridge
does not transfer that work to the complement.

The [exclusive coverage contract](https://github.com/glopyglerky/lustr/blob/next/docs/compiler-set/exclusive-coverage-contract.md)
controls implementation. Read Lustr's current
[agent instructions](https://github.com/glopyglerky/lustr/blob/next/AGENTS.md),
[active correction](https://github.com/glopyglerky/lustr/blob/next/docs/compiler-set/active-correction.md),
[completion checklist](https://github.com/glopyglerky/lustr/blob/next/docs/compiler-set/completion-checklist.md)
and [performance policy](https://github.com/glopyglerky/lustr/blob/next/docs/compiler-set/practical-performance.md).
Refresh default and active PR heads, actual checks, source pins and the import
inventory before work. A retained gitlink or successful compatibility preview
does not supersede those instructions.

## Current continuation

At the 19 November 2026 review, Lustr's implementation correction is open
[PR #33](https://github.com/glopyglerky/lustr/pull/33), targeting `next`.
Its observed head is `e2709cb3e671ef4a99acb5ec446b506af4c5668e`; this observation
does not freeze the active head or establish that all checks passed. Governing
documentation and corrective product code have different publication states.
The complete replacement remains unfinished. Continue the existing correction
and its actual native completion, metadata and selective-complement work rather
than reviving an earlier full-driver coordinator.

The complete Rust source stays in blueFe for upstream preservation, independent
reference qualification and selective extraction. It must not become Lustr's
fallback, an optional complete compiler feature or a second frontend for
Lust-owned operations. Do not import the full compiler and call it a minimal
complement because selected LLVM emission is disabled.

A declared bootstrap compiler may build Lustr itself. Record its source and
artifact identity separately from the compiler producing Lustr's requested
outputs. That construction use does not authorize a stock compiler to supply
missing semantics, metadata or emitted objects for a Lustr compilation request.

Each imported source slice needs exact provenance and licenses, a missing
operation or necessary dependency witness, active feature/target closure, a
real caller and one semantic owner. Maintain upstream capability rules outside
the compilation request and apply them during the one necessary frontend and
retained-state update. Preliminary source scans, trial compilation and
diagnostic-based compiler retries are not supported routing methods. An
implementation failure remains a failure.

Preserve Lust's retained checked state, stable identities, precise semantic
reads and emission reuse. Prefer `core` and `alloc` with explicit host adapters
and retained compilation without required Unix sockets, while preserving speed.
A fresh process per request is not a substitute for a retained compiler. A
`no_std` encoder does not establish a `no_std` compiler, and implementation
portability must not exclude programs using `std` or target-specific APIs.

The first complete-replacement release requires correct full coverage, exclusive
ownership, justified complementary imports and a measured overall speedup over
matched stock Rust for the declared workload. Near-stock Lust speed for its
subset and near-stock Rust speed for the complement remain separate comparisons
and ongoing optimization goals. Include dispatch, conversions, initialization,
transport, invalidation, linking, publication and retained-state maintenance.
Keep failed, skipped and unqualified cases distinct from passes. Upstream speed
smoke jobs and expected-negative controls do not establish these claims.

## Retained Lustr gitlink and preview behavior

The root `lustr` gitlink still selects the November 15 documentation checkpoint
[`7cea76c9d3adc587b54ccff168fe07efafd40309`](https://github.com/glopyglerky/lustr/commit/7cea76c9d3adc587b54ccff168fe07efafd40309).
Its `compiler/native` tree is exactly upstream Lust revision
`240e08d91d4aed0299639f6f11fd522912b248f9`, tree
`0ab1b09815802894e6078de0af59273cbdf46cb0`. This pointer is preserved history,
not the current implementation correction. It has not been advanced to the
unmerged PR, and a documentation change does not rebuild any release asset.

That checkpoint routed representable whole-file requests through Lust and
provided bounded source-library additions for naming constants, borrowed paths
and OS-string/path capacity reservation. Its cold C ABI and retained-daemon
paths had recorded Linux qualification. Its separate compatibility
coordinator's `auto` mode selected Cargo/rustc, and unsupported requests could
use the official full Rust compiler. This describes the old implementation;
that full-compiler route conflicts with the current contract and must not be
reintroduced. See the [versioned native preview](releases/native-preview-2026.11.15-1.md)
for original source, artifacts and limits.

The recorded pristine Lust build passed 391 upstream unit tests with Cargo
1.99.1, plus isolated relocated check/build/run and invalid-type rejection
probes. The build-script reader failed with Cargo 1.101 nightly's artifact
layout; the first failure is retained. These are historical results for that
source, not qualification of the current correction or full Rust coverage.

Lustr now preserves its pristine reference and explicit integration changes
under its [own source policy](https://github.com/glopyglerky/lustr/blob/next/docs/compiler-set/upstream-lust.md).
A necessary integration or correctness repair needs source identity, a
necessity case, applicable correctness evidence and performance
characterization. It need not independently deliver a speedup. Do not restore
the older absolute-pristine or mandatory-speedup interpretation as Lustr's
current policy. blueFe's separate protected Rust policy is unchanged.

## Protected Rust baseline

At blueFe main `9267fd0d348dc591af85efe96597c6ea774be5c0`, the protected Rust
implementation matches upstream `4b5350e87e487aed08ab2f9f0160a4b2616438bc`.
The compiler tree is `a74c6bc85bb7e3c6891eff1856b7f705bb823768`; the library
tree is `6cbb44578d379884a6bc059aaddca062ddfeace8`. Bootstrap, stage0 and its
generator also match the [source pin](../../upstream/rust.pin).
The [preservation gate](upstream-preservation.md) covers all five scopes.
These source identities do not establish a fresh bootstrap or platform result.
This direction correction changes no protected source, source pin or gitlink.

## Historical releases and other work

`preview-2026.11.09-2` is a rustc-based compatibility package with no native
Lust. The later `native-preview-2026.11.15-1` adds a bounded native path and an
official full Rust compatibility SDK. Both retain their exact versioned source,
binary and qualification records. Neither is a completed exclusive Lustr
replacement or the architecture for its next release.

blueFe [PR #1](https://github.com/glopyglerky/blueFe/pull/1) and
[PR #2](https://github.com/glopyglerky/blueFe/pull/2) retain distinct packaging
and runner/bootstrap work. Refresh their live heads and evidence before using
their changes. Their existence neither changes Lustr's current contract nor
qualifies a full compiler; this documentation correction does not merge,
close or discard them.
