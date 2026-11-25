# Native Lustr integration

Lustr must be a complete rustc replacement containing unchanged upstream Lust.
Lust must compile everything it supports; Lustr-owned native code must supply
the missing language, standard-library and crate support. blueFe packages that
compiler. A Cargo coordinator or a tuned rustc build does not complete it.

## Source baseline

The root `lustr` gitlink selects
[`7cea76c9d3adc587b54ccff168fe07efafd40309`](https://github.com/glopyglerky/lustr/commit/7cea76c9d3adc587b54ccff168fe07efafd40309).
Its `compiler/native` tree is exactly upstream Lust revision
`240e08d91d4aed0299639f6f11fd522912b248f9`, tree
`0ab1b09815802894e6078de0af59273cbdf46cb0`. Earlier fork overrides and an
unpublished expansion candidate are excluded. The source guard rejects drift.
Lustr-owned work belongs outside the upstream baseline. Any proposed Lust
exception requires demonstrated necessity and faster equivalent-workload results.
See the [preservation policy](https://github.com/glopyglerky/lustr/blob/82d77539680fec9cf822ca8231d1abb985069c48/docs/compiler-set/upstream-lust.md).

## Rust source baseline

The protected Rust implementation now matches upstream
`42e0b13fb7310a12a827f6a28891c11d2e10923a`. The compiler tree is
`0cc73933ffdd3218ffec6a9d1fe4c412003d55b0`; the library tree is
`2be35fdfe5e4857ef29981291f81618a1288cd27`. Bootstrap and stage0 are also
restored to upstream. The [preservation gate](upstream-preservation.md) binds
all five protected scopes and rejects unqualified source divergence. Existing
releases keep their earlier source and binary identities.

## Actual implementation

The root Lustr compiler entry now routes representable whole-file requests
through unchanged Lust and supplies bounded source-library additions for naming
constants, borrowed paths and OS-string/path capacity reservation. Cold C ABI
and retained native-daemon paths are qualified on the recorded Linux host.
The separate compatibility coordinator's `auto` mode still selects Cargo/rustc.
Full native language coverage, Rust rlib/metadata emission and general native
Cargo interoperability remain incomplete. Unsupported requests use the official
unmodified full Rust compiler; that compatibility does not count as native
coverage. See the [native preview record](releases/native-preview-2026.11.15-1.md).

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

The complete replacement must still demonstrate complete supported-request
routing, mixed-feature programs, real crate artifacts, correct rejection,
ownership/panic/drop behavior and warm/cold edit consistency. Compare the actual
native compiler against stock Rust on equivalent work, preserving every
regression. Upstream subset speed cannot be multiplied into a full-project
speed claim without measuring covered work and integration cost. No universal
non-regression or memory-safety claim is made.
