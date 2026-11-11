# Native Lustr integration

Lustr must be a complete rustc replacement building on the upstream Lust implementation.
Lust must compile everything it supports; Lustr-owned native code must supply
the missing language, standard-library and crate support. blueFe packages that
compiler. A Cargo coordinator or a tuned rustc build does not complete it.

## Source baseline

The root `lustr` gitlink selects the recovery revision
[`40a2488d90018ed8fb89cb5b9b5a1bd43315295e`](https://github.com/glopyglerky/lustr/commit/40a2488d90018ed8fb89cb5b9b5a1bd43315295e).
The immutable upstream Lust baseline remains recorded separately from the
working fork. The recovery restores the native macOS startup, FFI, Cargo
build-script, cache handling and test work that the prior upstream reset removed.
Its source guard records both the upstream baseline and reviewed fork tree.
See Lustr's
[preservation policy](https://github.com/glopyglerky/lustr/blob/40a2488d90018ed8fb89cb5b9b5a1bd43315295e/docs/compiler-set/upstream-lust.md).

## Rust source baseline

The original Rust baseline remains
`5b7b37aefcb5b2fba3c2392bc9065b9e4602d494`.
[`upstream/rust.pin`](../../upstream/rust.pin) retains its object identities.
[`upstream/bluefe-fork.pin`](../../upstream/bluefe-fork.pin) records fourteen
restored files for compiler compatibility, bootstrap coordination, stage0 and
optional Cranelift unwinding. Other upstream changes from the intervening merge
remain. The [source guard](upstream-preservation.md) protects the combined
upstream and fork state from unrecorded changes or another reset.

This repairs source integration. It does not qualify a new full compiler build
or change existing release assets.

## Actual implementation

The compatibility coordinator's `auto` mode selects Cargo/rustc. Native Lust
remains an explicit separate engine. The required native expansion interface,
automatic integrated routing, full Rust coverage and Rust rlib/metadata emission
are not implemented. Linking a Rust compiler library alone does not implement
those missing interfaces or prove that native Lust handles supported code.

The earlier pristine-source checkpoint passed 391 upstream unit tests with Cargo
1.99.1 and isolated relocated check/build/run and invalid-type rejection probes.
That checkpoint failed to read Cargo 1.101 nightly's newer build-script artifact
layout. Those are historical results, not qualification of the recovered native
fork or a full compiler. The recovery retains the original failure evidence and
the restored compatibility work; source checks and focused routing tests do not
establish complete Rust coverage or a speedup.

## Release distinction

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
