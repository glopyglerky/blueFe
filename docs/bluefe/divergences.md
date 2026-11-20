# BlueFe decisions and divergences

blueFe retains the complete Rust fork for upstream preservation, reference
qualification and selective extraction into Lustr. The
[current compiler direction](native-lustr-status.md) requires exclusive Lust
ownership and only the necessary imported complement. Earlier compatibility
packaging is retained evidence, not a competing Lustr destination.

The protected compiler, library, bootstrap, stage0 and stage0-generator
sources match upstream Rust `4b5350e87e487aed08ab2f9f0160a4b2616438bc`.
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

Historical compatibility application builds used an explicit produced toolchain
root. That produced rustc cannot supply Lustr's missing product compilation.
Independent reference qualification may use it after Lustr has generated the
output being evaluated. A declared bootstrap compiler may build Lustr itself,
with that construction identity recorded separately.
Native and wasm sysroots are identified separately from the stage0 compiler
used to build them.
A different nightly backend or semantic driver is not an interchangeable
component. Historical LLVM and alternative-backend observations retain their
original qualification scopes.

Historical compiler optimization experiments retain their preview identities.
The [stage2 PGO checkpoint](measurements/2026-11-09-pgo/README.md)
records successful runtime qualification and an unresolved diagnostic gate.
Profile warnings and missing evidence are retained; an untimed candidate does
not establish a speed improvement or justify changing the default backend.

Complete Lustr compilation is the active goal. Preserve usable source and
rollback while integrating genuine native completion and necessary upstream
services. Full-driver fallback, duplicate supported checking and trial-compile
routing cannot count as progress toward that goal. Portability changes must
preserve retained compilation and speed. Record exact source heads, component
hashes, unsupported targets and failures with each delivered toolchain.

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
