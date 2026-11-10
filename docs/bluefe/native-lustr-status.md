# Native Lustr integration

Lustr must be a complete rustc replacement containing unchanged upstream Lust.
Lust must compile everything it supports; Lustr-owned native code must supply
the missing language, standard-library and crate support. blueFe packages that
compiler. A Cargo coordinator or a tuned rustc build does not complete it.

## Source baseline

The root `lustr` gitlink selects
[`82d77539680fec9cf822ca8231d1abb985069c48`](https://github.com/glopyglerky/lustr/commit/82d77539680fec9cf822ca8231d1abb985069c48).
Its `compiler/native` tree is exactly upstream Lust revision
`240e08d91d4aed0299639f6f11fd522912b248f9`, tree
`0ab1b09815802894e6078de0af59273cbdf46cb0`. Earlier fork overrides and an
unpublished expansion candidate are excluded. The source guard rejects drift.
Lustr-owned work belongs outside the upstream baseline. Any proposed Lust
exception requires demonstrated necessity and faster equivalent-workload results.
See the [preservation policy](https://github.com/glopyglerky/lustr/blob/82d77539680fec9cf822ca8231d1abb985069c48/docs/compiler-set/upstream-lust.md).

## Rust source baseline

The protected Rust implementation now matches upstream
`5b7b37aefcb5b2fba3c2392bc9065b9e4602d494`. The compiler tree is
`9bb98adca40010656ac057f2c4103cf72f5cdc6f`; the library tree is
`f48d6700750a1dc11b2f8f1df91a26dee3ef13fb`. Bootstrap and stage0 are also
restored to upstream. The [preservation gate](upstream-preservation.md) binds
all five protected scopes and rejects unqualified source divergence. Existing
releases keep their earlier source and binary identities.

## Actual implementation

The compatibility coordinator's `auto` mode selects Cargo/rustc. Native Lust
remains an explicit separate engine. The required native expansion interface,
automatic integrated routing, full Rust coverage and Rust rlib/metadata emission
are not implemented. Linking a Rust compiler library alone does not implement
those missing interfaces or prove that native Lust handles supported code.

A fresh pristine Lust build passed 391 upstream unit tests with Cargo 1.99.1,
plus isolated relocated check/build/run and invalid-type rejection probes.
The build-script reader failed with Cargo 1.101 nightly's newer artifact layout;
the first failure is retained. This is a compatibility constraint, not a reason
to patch Lust without the required admission evidence. These checks establish
the exercised native subset, not a full compiler or a speedup.

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
