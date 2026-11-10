# BlueFe decisions and divergences

blueFe owns its product entry points, primary README, Lustr integration and
packaging. The protected compiler, library, bootstrap, stage0 and stage0-generator
sources match upstream Rust `5b7b37aefcb5b2fba3c2392bc9065b9e4602d494`.
The [source and performance admission policy](upstream-preservation.md) records
the exact scopes and requires necessity plus faster equivalent-workload results
before admitting a divergence. No new exception is admitted.

Earlier compiler compatibility edits, the bootstrap coordinator path and custom
stage0 selection have been removed. Lustr-owned entry points stay outside those
upstream implementations. Source restoration does not retroactively rebuild or
qualify a retained release, and a fresh source bootstrap remains unqualified.

The inherited directories preserve upstream build and qualification contracts.
Third-party tools and submodules retain their roles and licenses. Their presence
and unchanged source do not establish whole-toolchain memory safety.

Application builds use an explicit produced toolchain root. Native and wasm
sysroots are identified separately from the stage0 compiler used to build them.
A different nightly backend or semantic driver is not an interchangeable
component. LLVM remains the default backend until a faster requested path has
passed its own qualification.

Compiler optimization experiments retain the working preview as the default
download. The [stage2 PGO checkpoint](measurements/2026-11-09-pgo/README.md)
records successful runtime qualification and an unresolved diagnostic gate.
Profile warnings and missing evidence are retained; an untimed candidate does
not establish a speed improvement or justify changing the default backend.

Working builds take priority. Independent full-Rust compilation and migration
toward memory-safe Rust are future goals pursued through measured iteration,
focused parity tests and preserved rollback. Source movement must keep the
build usable. Record exact source heads, component hashes, unsupported targets
and failures with each delivered toolchain.

This is personal fork work. Generated changes are not intended for
rust-lang/rust pull requests. The inherited source and its licensing remain
preserved; the upstream project does not own BlueFe's product claims.

## Optional optimized stage2 configuration

The [CGU16/ThinLTO record](measurements/2026-11-09-cgu16-thinlto/README.md)
documents the effective compiler-build treatment and retained control. This is
an explicit profile, not a global change to upstream bootstrap defaults or
Lustr's frontend/backend routing. Standard-library CGU remains 256. Native build
and preparation effects prevent separate attribution to either compiler setting.
The fixed metadata-only pilot passed; stock Rust remained faster in its unequal-
version comparison. Full-build evidence, other hosts and release packaging are
separate qualifications. PGO's unresolved diagnostic gate remains independent.
