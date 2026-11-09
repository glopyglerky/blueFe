# BlueFe decisions and divergences

BlueFe owns its entry points, primary README and compiler integration. Lustr is
pinned at the repository root so the coordinating project is visible without
navigating an inherited tools tree. Bootstrap builds its primary Rust crate,
which has no native or registry dependencies.

The Rust compiler, library and bootstrap directories remain in their existing
layout. They implement the working compiler and preserve upstream build and
qualification contracts. Moving or deleting them before a replacement exists
would break full Rust support. Third-party tools and submodules keep identified
roles and licenses; their presence does not establish memory safety.

Current fork changes select Lustr for ordinary bootstrap Cargo operations,
preserve specialized Clippy/Miri launchers, update stage0 through its native
generator, and enable unwinding when explicitly building the matching in-tree
Cranelift backend. Runtime qualification remains separate from source setup.

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
