# Stage2 PGO checkpoint — 2026-11-09

**Diagnostic gate pending; no performance result.** A profile-guided optimization
(PGO) candidate was built and passed independent runtime and bounded privacy
checks. It has not been timed, released or selected as the default download.
Use the [packaged preview](../../releases/preview-2026.11.09-1.md) for application
work. Earlier [public workload measurements](https://github.com/glopyglerky/lustr/tree/next/docs/compiler-set/measurements/2026-11-09-shared-v2)
describe a different experiment.

## Inputs and observed checks

[checkpoint.json](checkpoint.json) binds source commits, payload manifests,
profile and review hashes. Both compiler arms used stage2, compiler and standard
library CGU=256, LTO off, optimization level 3, incremental compilation off and
two build jobs. Cargo was the identified upstream bootstrap binary. BlueFe's
produced compiler, sysroot, rustdoc, Clippy and Cranelift backend were kept
together. Stage0 was a build input, not the compiler under evaluation.

Training compiled only the pinned, dependency-free Lustr coordinator's targets
in check, debug and release configurations. Public application holdouts were
excluded from training. The three indexed profiles were merged without weights;
training was not adjusted after inspecting the candidate's warnings.

Independent runtime review passed 42 commands covering native LLVM and
Cranelift execution, panic recovery and destructor behavior, mixed-backend/FFI
fixtures, structured rejection diagnostics, Clippy, formatting and relocation.
Wasm qualification checked linking and the output header; it did not execute
Wasm. Runtime checks were on one compatible x86_64 GNU/Linux host. They do not
prove full compiler equivalence, memory safety or other-host support. Bounded
privacy checks covered both complete frozen runtime roots separately from
runtime execution.

The no-PGO control has a documented provenance limitation: two original metadata
outputs were overwritten. Retrospective reproduction recovered their recorded
hashes, all 19 metadata outputs and 38 terminal output hashes. Independent review
accepted bounded input binding, while the lost command/capture-time records and
historical preservation failure remain unresolved. This is weaker than intact
contemporaneous evidence.

## Why timing remains held

The USE build emitted 678 missing-profile warning occurrences, representing
650 distinct function/hash pairs across 134 modules. Every reported discarded
count was zero. A complete indexed-profile scan found:

| Warned names | Observed profile evidence |
| --- | --- |
| 56 | 1,277 zero-count records in other qualified contexts; no equivalent warning-context occurrence established |
| 594 | No stored key with the exact mangled base, including the checked qualification and dotted-suffix variants |

All 650 causal origins remain unresolved. Matching a suffix, a hash or a final
ELF symbol does not establish that it is the same lookup-stage occurrence.
Counters were not transferred between contexts. The warning count divided by
the number of profile records is not a coverage estimate.

In the pinned LLVM implementation, a missing key returns without observing its
execution count; the warning's accumulator starts at zero. A successfully read
all-zero record follows a different path. See the primary
[profile lookup](https://github.com/rust-lang/llvm-project/blob/0a5579eb649d3634a9c30ac873300cc2944fa070/llvm/lib/ProfileData/InstrProfReader.cpp)
and [warning handling](https://github.com/rust-lang/llvm-project/blob/0a5579eb649d3634a9c30ac873300cc2944fa070/llvm/lib/Transforms/Instrumentation/PGOInstrumentation.cpp).

The missing evidence is an authenticated generation-to-USE correspondence at
the PGO boundary: module/source filename, original function, linkage, lookup
keys, CFG hash and context-sensitive kind, plus the corresponding generation
occurrence or recorded transformation explaining its absence. Final machine
code and indexed profiles do not supply that correspondence. The existing
diagnostic gate has not been waived. No automatic rebuild or timing follows
from this checkpoint.

## Conditional mathematical arguments

These are paper arguments under stated assumptions, not machine-checked proofs.

**Counter aggregation.** Assume compatible counter identities, unweighted
componentwise addition and no overflow or saturation. For finite counter
vectors `c₁, c₂, c₃`, let `mⱼ = c₁ⱼ + c₂ⱼ + c₃ⱼ`. Then
`Σⱼ mⱼ = Σⱼ c₁ⱼ + Σⱼ c₂ⱼ + Σⱼ c₃ⱼ` by distributivity of finite sums.
The observed reported totals satisfy
`224947920 + 467067683 + 548652800 = 1240668403`.
This necessary aggregate consistency check cannot prove individual counter
correspondence: different vectors can have the same sum.

**Zero discarded count does not bound missing execution.** Model a missing-key
lookup as returning the initial diagnostic accumulator `D=0` without reading
the unavailable counter. For every possible unobserved count `H ≥ 0`, the same
lookup can report `D=0`. Hence `D=0` implies no finite upper bound on `H` in this
model. In particular, it does not imply coldness. This argument concerns missing
keys; it does not reinterpret a found, authenticated zero counter.

**Names do not prove occurrence identity.** Let an occurrence be
`(module, name, linkage, CFG hash, context kind)`. Projection onto `name` is
non-injective whenever two occurrences differ in another coordinate. Therefore
name equality alone cannot establish occurrence equality. Supplying additional
coordinates or transformation provenance is necessary to justify this match.
This is a statement about the evidence model, not proof of an actual compiler
defect or the cause of any warning row.

Full profiles, logs and the 650-row review remain retained privately. Their
digests bind this summary; the aggregate JSON is not a public reproduction
bundle. Future speed claims require accepted diagnostics and fresh controlled
measurements, with regressions and resource limits retained.
