# Native preview 2026.11.15-1

This pre-alpha preview supplies unchanged upstream Lust, bounded Lustr-native
source-library additions and the official unmodified Rust nightly compatibility
SDK. Identical assets are available from
[blueFe](https://github.com/glopyglerky/blueFe/releases/tag/native-preview-2026.11.15-1)
and [Lustr](https://github.com/glopyglerky/lustr/releases/tag/native-preview-2026.11.15-1).
The [complete release record](https://github.com/glopyglerky/lustr/blob/7cea76c9d3adc587b54ccff168fe07efafd40309/docs/compiler-set/native-preview-2026.11.15-1.md)
describes invocation, source closure, qualification and limits.

The compiler implementation source is Lustr
`60f9d8b2375d2980a46aa15879c737a8f55a43f6`; its subsequent documentation commit
`7cea76c9d3adc587b54ccff168fe07efafd40309` is this integration's Lustr pointer.
Lust's complete protected tree remains upstream `240e08d91d4aed0299639f6f11fd522912b248f9`
with tree `0ab1b09815802894e6078de0af59273cbdf46cb0`. blueFe's protected Rust
compiler/library/bootstrap/stage0 scopes remain upstream
`5b7b37aefcb5b2fba3c2392bc9065b9e4602d494`; no compiler divergence is admitted.

The delivered full Rust compiler is official **unmodified** nightly-2026-11-09,
rustc 1.102.0-nightly / LLVM 23.1.5, not a newly fork-produced compiler. The archive
includes complete corresponding native source, locked offline dependencies,
TinyCC source, original notices and the recipient relink helper under
`share/bluefe-source`. The complete upstream Lust tree retains upstream-tracked
fixture caches; newly generated local build outputs and private recipient proof
artifacts are excluded.

Download every asset and verify `SHA256SUMS` before extracting into a new versioned
directory with hardlinks preserved. Archive SHA256 is
`5ac8009bc616662650a54abd632dd28cb585f4fad1449f18fb9aa7f9d5a2cd4b`,
382,850,313 bytes. Sidecars bind all 19,229 payload entries, actual component
identities, all 32 ELF paths, raw archive-header checks and acceptance evidence.
No global install or default toolchain is changed.

The final extracted runtime passed 17 unit entries and 13 runtime integrations,
including native cold/retained execution, rejection and ownership, unwind/Drop,
non-Unicode values, capacity-overflow recovery, source sealing, Cargo selection,
foreground cancellation, real metadata, build scripts, proc macros, doctests,
Wasm linking, rustfmt/Cargo fmt and direct/Cargo Clippy checks. Frozen-byte review
found no P0–P2 defect; its P3 wording clarification was applied before the final
archive and extraction checks. These bounded results do not prove universal
compiler/tool correctness or arbitrary recipient modifications.

Qualified host is Linux GNU x86_64 on AerynOS 2026.08, with observed GLIBC 2.39,
GCC_4.2.0, libgcc/zlib and both `/usr/lib/ld-linux-x86-64.so.2` and
`/lib64/ld-linux-x86-64.so.2` interpreter paths. System native build/link inputs
remain dependencies. Other hosts and Wasm execution are unqualified; all seven
broader public platform gates remain separately held.

Native source-library expansion and repeated-request gains are bounded. Full
native Rust, raw Rust metadata/rlib, general native Cargo routing and required
full-project speed remain open. The included 1,428-event campaign retains
cold/edit/rejection regressions, original/matched-producer baselines and raw
samples/source/output. This is not a never-slower or whole-stack memory-safety
claim. Original SDK notices and exact missing-text provenance are preserved;
the documented declaration-based supplements are not universal legal clearance.

Historical previews remain immutable with their original components,
qualification, measurements and rollback role.
