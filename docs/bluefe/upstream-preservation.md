# Upstream source and performance admission

All project work is published in `glopyglerky/blueFe` and
`glopyglerky/lustr`. These changes are not intended for upstream Rust or Lust
submissions. Upstream repositories are read-only comparison sources.

The Rust compiler, library, bootstrap, stage0 data and stage0 generator are
pinned in [`upstream/rust.pin`](../../upstream/rust.pin). The source guard
[`bluefe-rust-upstream-check.rs`](../../tools/bluefe-rust-upstream-check.rs)
checks their Git object identities, working-tree differences and untracked
additions. `--index` validates a staged restoration before committing it.
Initialized submodule contents need their own checks; a gitlink identifies the
required source commit but does not prove the checked-out bytes.

The protected sources match upstream Rust
`5b7b37aefcb5b2fba3c2392bc9065b9e4602d494`. Six earlier compiler-file
compatibility edits and the bootstrap coordinator hooks have been removed.
The upstream stage0 inputs are restored too. This is source preservation,
not a fresh bootstrap or platform qualification. Historical releases retain
their original source and artifact records.

Lustr keeps its complete embedded Lust tree identical to its separate upstream
pin. Product entry points, packaging and experiments belong outside these
protected implementations. An include of upstream source must identify that
source explicitly; generated overlays and hidden build-time patches are not
exceptions to the policy.

## Required evidence for a source divergence

A proposed divergence needs both:

1. A minimal reproducible necessity case against the exact upstream baseline.
   Preserve the original failure, requested semantics and artifact contract.
2. Faster equivalent-workload results against that baseline, with exact source,
   compiler, flags, targets, dependency and cache identities. Retain raw paired
   samples, regressions, validation failures, uncertainty assumptions and
   independent replay. Correctness alone does not demonstrate speed.

If the baseline cannot compile a case, that establishes a coverage gap. Its
failure is not a finite timing sample proving a speedup. A new implementation
also needs comparisons with a compiler that successfully performs the requested
work, plus non-regression measurements on upstream-supported work.

No new upstream-source exception is admitted at this checkpoint. A necessity
argument without speed evidence, or a speed result without equivalent behavior,
does not pass. Public-repository workloads are permitted; private host state,
credentials and coordination records stay outside public artifacts.

## What can be proved

Under the assumed integrity of Git objects and the pinned upstream identity,
matching protected tree/blob IDs with empty tracked differences and no untracked
additions establishes tracked-source preservation. It does not prove compiler
correctness, dependency contents, runtime identity or performance.

Let `T` be the baseline time, `S` the work eliminated by an integration and `H`
its added cost, all for the same successful request and execution conditions.
Then `T_new = T - S + H`, so non-regression is equivalent to `S >= H`.
Keeping the compiler source unchanged does not establish this inequality.
Trying Lust and then running the same full Rust compilation adds positive work
unless another saving offsets it. End-to-end measurements must include that
work. A finite benchmark suite cannot prove a wall-clock bound for every future
Rust program, machine or operating-system schedule.

Lustr's [statistical methodology](https://github.com/glopyglerky/lustr/blob/next/docs/compiler-set/benchmark-method.md)
records the conditional estimators and assumptions used for measured claims.
Published claims must remain within their actual qualification scope.
