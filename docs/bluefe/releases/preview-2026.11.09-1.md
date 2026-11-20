# Preview 2026.11.09-1

[Download the release](https://github.com/glopyglerky/blueFe/releases/tag/preview-2026.11.09-1).
This is a reusable Linux x86_64 GNU toolchain, with native execution and
wasm32-unknown-unknown link support. The archive includes Cargo, produced rustc
and rustdoc, complete native/Wasm libraries, Lustr, matching Clippy/rustfmt and
experimental Cranelift built with unwinding. Optional native Lust/TCC/semantic
engines and rustc-dev metadata are absent.

| Binding | Value |
| --- | --- |
| BlueFe compiler source | `1b74388e196ee8813f38ba9eeb6d4ab43b6b1071` |
| BlueFe source tree | `929fedcb94afe621cf19ca636037da6474a45982` |
| Lustr coordinator source | `07470b20464bf097c3c88983124aff56c5e44f9a` |
| Upstream bootstrap Cargo | `31d3246e0e8d3a80d4a90b54aa48ff180adb408b` |
| Compiler version | `1.102.0-dev`, LLVM `23.1.5` |
| Archive SHA256 | `1059ad4682ea122fa23c06c0126fd5d41f3a8f3e460c8acda3c5eb2094159e39` |
| Payload manifest SHA256 | `fb87e8dd2306df9665d16d01a08ebae50d21c589b17e6298d97141da58f870a1` |

Download all six assets and run `sha256sum -c SHA256SUMS` before extraction.
The archive has 1,717 entries and 1,143 regular files. Its 1,139 runtime files
match the independently reviewed producer payload; four files add usage and
source/platform/qualification metadata. The manifest binds member paths,
types, modes, sizes and hashes. Tar ownership is numeric zero with empty names,
fixed order/time, no PAX extensions and no links. Independent archive generation
produced identical compressed bytes.

The compiler was rebuilt from the official pinned stage0, using neutral
source/build/cache paths and metadata path remapping. Cargo remains an upstream
bootstrap binary, not a compiler produced by BlueFe. Generated Rust copyright
documents, Rust licenses, the LLVM notice and Cargo notices are included.
Cargo notice coverage is a conservative 526-package locked-source superset,
not a recovered compiled feature graph. The selected LLVM HTTPS archive was
hashed; its unavailable official checksum sidecar was not verified.

The producer passed 32 integration tests and 32 relocation tests. Independent
runtime checks exercised native tests, panic recovery with one destructor call,
frontend scheduling, Wasm linking, compiler rejection, Clippy, formatting and
actual Cranelift loading/unwinding. Another 25 probes passed against a clean
extraction in a path with spaces, with original producer/source paths inaccessible.
Full archive-byte, header and bounded privacy checks passed. Some initial
diagnostic logs were overwritten; surviving command/status records do not
reconstruct them.

Requirements include GLIBC 2.39, GLIBCXX_3.4.32, compatible loader/shared
libraries and native linking prerequisites. `platform.json` records every
bundled ELF object's requirements. No older-host or other-platform acceptance,
Wasm execution, universal compiler correctness, whole-stack memory safety or
current public-workload speedup is established. Performance evidence uses the
[separate measurement protocol](https://github.com/glopyglerky/lustr/blob/next/docs/compiler-set/benchmark-method.md).
