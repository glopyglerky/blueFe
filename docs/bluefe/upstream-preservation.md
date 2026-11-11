# Upstream and fork source preservation

All project work is published in `glopyglerky/blueFe` and
`glopyglerky/lustr`. These changes are not intended for upstream Rust or Lust
submissions. Upstream repositories are read-only comparison sources.

## Baseline and working fork

[`upstream/rust.pin`](../../upstream/rust.pin) retains the immutable upstream
Rust revision `5b7b37aefcb5b2fba3c2392bc9065b9e4602d494` and its original
compiler, library, bootstrap, stage0 and stage0-generator identities.

[`upstream/bluefe-fork.pin`](../../upstream/bluefe-fork.pin) records each
reviewed fork path with two blob identities: the original upstream blob and the
working fork blob. The source guard verifies the upstream revision and scope
identities, then compares the complete current scopes with that baseline plus
the recorded fork changes. It rejects unrecorded changes, missing files,
changed modes, dirty tracked files and untracked additions. It also rejects
resetting a recorded fork file to its upstream version.

Fetch the pinned upstream revision before running the guard. `--index` checks
the staged tree. Initialized submodule contents need their own checks; a gitlink
records a source revision but does not prove checked-out bytes.

Fork development may change inherited source when required for working compiler
or integration behavior. Record the exact changed blobs and run the affected
correctness checks. Update the upstream pin only as an explicit integration,
with review of both upstream changes and every retained fork change. Never reset
the working fork to upstream merely to satisfy the guard.

## Recovered functionality

The recovery restores fourteen source files from
`26f837974ddfaef83d89c9ffaa21bd9b70297a81` that were replaced by
`f0f00135a69fdf718ad73aaaecbddeacf36f2b74`:

- Six compiler compatibility files required by the selected stage0.
- Bootstrap coordinator routing, its Python and Rust tests, and the bounded
  stage0 preflight.
- Stage0 checksums, nightly selection and the matching target capability list.
- Unwinding configuration for an explicitly selected in-tree Cranelift build.

Other upstream changes introduced by the removal merge remain. This includes
the newer library, compiler, debugger and lint-test changes. The recovery is a
source repair, not a new compiler release or a fresh full-bootstrap qualification.
Existing preview assets and their historical evidence retain their identities.

## Correctness and performance

A correctness repair needs evidence that the affected behavior works. It does
not need to demonstrate a speedup before existing functionality may be retained.
Performance claims need matched successful workloads, source and toolchain
identities, target and flag details, raw samples and recorded failures. A failed
baseline is a coverage gap, not a timing result.

The guard establishes recorded source identities under the assumed integrity
of Git objects. It does not prove compiler correctness, dependency contents,
runtime identity, universal hardware support or speed. Native compiler,
Cranelift, relocation and release qualifications remain separate.

Lustr's
[statistical methodology](https://github.com/glopyglerky/lustr/blob/next/docs/compiler-set/benchmark-method.md)
records the measurement assumptions for performance claims.
