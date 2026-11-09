# Integration proofs and executable evidence

These are mathematical arguments about the control program under explicit
assumptions, backed by small regression/conformance tests. They are not
machine-checked compiler correctness proofs or performance results.

Let a request be `(engine, root, toolchain, explain, frontend_jobs, argv)` and a plan be
`(program, argv', env, removals, backend)`. Assume the pinned Lustr parser/planner
executes as written, the OS executes the selected file, and the caller controls
Cargo configuration, wrappers and environment as recorded. Assume source and
payload identity hashes are authenticated outside this model.

1. **Plan non-execution.** For every successfully parsed request with
   `explain=true`, Lustr returns its JSON plan without executing a child tool.
   Proof: the tool validation/doctor branch is guarded by `!explain`; after
   planning, the explain branch prints and returns before `execute`. Planning
   constructs paths and environment values only. This does not assert that an
   arbitrary future planner, external wrapper or bootstrap invocation is pure.
2. **Root routing.** For absolute root `R`, no `+toolchain`, and auto/rustc engine,
   the plan's Cargo is `R/bin/cargo`, and its explicit CARGO/LUST_CARGO/RUSTC/
   RUSTDOC values are the corresponding files in `R/bin`. Proof: parsing rejects
   the conflicting selectors; `toolchain::environment` maps all four names;
   planning selects Cargo from R. Inherited wrappers or explicit compiler/sysroot
   overrides can affect compilation; this proves selection, not end-to-end
   compiler authenticity in an uncontrolled environment.
3. **Failure has no fallback transition.** Given a selected plan P, failure to
   execute P or a nonzero child result never triggers a different backend.
   Proof: Unix replaces the process with P or returns the spawn error; other
   hosts wait once and return the status/error. No retry edge exists. On Unix a
   signal remains a signal; cross-platform numeric signal-code equivalence is
   not asserted. This excludes a successful stock-compiler retry hidden by this
   coordinator, not retries implemented inside Cargo or a user wrapper.
4. **Version-floor refusal.** Let source version be `(M,m,p)` with `m>0` and
   detected compiler release `(A,a,q)`. Bootstrap proceeds past its preflight
   only if `(A,a) >= (M,m-1)` and the probe completes in the allowed interval.
   Proof: malformed, missing, timed-out or failed probes raise; the lexicographic
   comparison rejects the complement. The OS timeout bounds the probe wait,
   not all download/build work. Passing is not sufficient for compatibility.
5. **Tree identity.** Under collision resistance of Git object hashes, equal
   tree IDs identify equal tracked subtree contents and modes. This supports
   the recorded compiler/library/rustdoc source equality across control commits.
   It proves neither byte-identical builds nor ABI interchangeability: stage0,
   flags, dependencies, native tools and environment remain inputs.

The optional `frontend_jobs` transformation has its own
[argument-preservation proof](../../../lustr/docs/compiler-set/proofs/frontend-scheduling.md).
It applies only to explicit Cargo `rustc` requests. A scheduling parameter does
not establish compiler correctness or a speedup on an unmeasured workload.

Executable coverage is in `src/bootstrap/bootstrap_test.py`: coordinator command
selection; preservation of explicit Cargo; missing/initialized submodule refusal;
stage0 version and timeout checks; real bootstrap build and compiler rejection;
and a retained full-Rust fixture. The latter checks pure planning, native run,
unit panic recovery with exactly one destructor call, doctest execution, type-error
rejection, and Wasm header/link output. Wasm runtime behavior is not observed.

Run from the repository root, with absolute toolchain/build paths on a build
filesystem (no heavy compiler build is started):

```sh
PYTHONDONTWRITEBYTECODE=1 CARGO_BUILD_JOBS=2 \
BOOTSTRAP_TEST_CARGO_BIN="$TOOLCHAIN/bin/cargo" \
BOOTSTRAP_TEST_RUSTC_BIN="$TOOLCHAIN/bin/rustc" \
BLUEFE_TEST_TOOLCHAIN_ROOT="$TOOLCHAIN" \
BLUEFE_TEST_BUILD_ROOT="$EVIDENCE_BUILD_ROOT" \
python3 -m unittest src.bootstrap.bootstrap_test
```

The fixtures remove their temporary outputs. The retained-toolchain test uses
isolated Cargo home/target directories and clears inherited compiler wrappers,
Rust flags and build-target overrides. Review any additional Cargo environment
configuration before treating a run as an acceptance result.

The historical [evidence record](integration-evidence.json) records the observed
32-test passing run and a second 32-test pass after full payload relocation on
the same host. The [payload manifest](payload-manifest.json) hashes all 326
file/symlink entries and records executable modes and relative link targets.
These identify the earlier private retained toolchain, not a public release or
the replacement privacy-remapped producer build. They do not establish privacy
or complete third-party notice coverage.
Test runtime is not benchmark speed evidence. Public workload
comparisons belong to separately controlled measurements; no historical timing
is generalized to current BlueFe performance.

The [stage2 PGO checkpoint](../measurements/2026-11-09-pgo/README.md)
contains separate, conditional arguments about profile aggregation and the
limits of missing-counter evidence. They establish neither compiler correctness
nor a PGO speedup. Its diagnostic gate remains pending.
