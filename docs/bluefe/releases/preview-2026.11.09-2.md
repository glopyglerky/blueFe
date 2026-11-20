# Packaged stage2 preview 2026.11.09-2

This Linux GNU x86_64 pre-alpha toolchain is available from
[blueFe](https://github.com/glopyglerky/blueFe/releases/tag/preview-2026.11.09-2) and
[Lustr](https://github.com/glopyglerky/lustr/releases/tag/preview-2026.11.09-2). Both repositories
publish the same six immutable assets. Extract once into a new versioned
directory outside source and reuse that absolute root. Project builds do not
bootstrap the compiler.

## Asset identity

| Asset | Bytes | SHA256 |
| --- | ---: | --- |
| `source-components.json` | 2528 | `38bc9ddb19843fb1e79feaa95dbaae8f9a54591b330136bca8f058aee57ccf5b` |
| `qualification.json` | 1697 | `4563ee3887eaa8583c2f3ea59f18c6255c268983a5d936ac705ccd9dd3feb8cc` |
| `bluefe-lustr-preview-2026.11.09-2-x86_64-unknown-linux-gnu.tar.zst` | 247378460 | `c57bfc06b7e2b3a7619d503b7f8d7c7ebc8fe29693fc296d21e27fa2baa836fb` |
| `payload-manifest.json` | 282380 | `5be11a5ded7f604ae9d341aec38644d94a514133f9587250cf257c360957792e` |
| `platform.json` | 28231 | `4c68b2765257d61dcf7a750eca152c2de6e575e46de1a27c69f5f192c9eb9580` |
| `SHA256SUMS` | 475 | `030be119c4c0a1e909607d3135b64f1a21bdf575cea8597b705d77c83dc55455` |

The payload has 1,147 files and 892,861,214 regular-file bytes across 1,721
members. All 1,143 producer files retain their exact hashes and modes. Only the
package root directory is normalized from 0555 to 0755, with four added usage/
metadata files. Independent archive generation reproduced the same compressed
bytes. Complete paths, types, modes, sizes and hashes are in the payload manifest.
Headers use numeric 0/0 ownership, empty user/group names and fixed order/epoch;
links, special files, unsafe paths, PAX and host extended metadata are absent.

## Components and source

The actual produced compiler is Rust 1.102.0-dev from blueFe
`1b74388e196ee8813f38ba9eeb6d4ab43b6b1071`, tree
`929fedcb94afe621cf19ca636037da6474a45982`. The Lustr coordinator uses
`07470b20464bf097c3c88983124aff56c5e44f9a`. LLVM gitlink is
`0a5579eb649d3634a9c30ac873300cc2944fa070`, with the source-selected cached
LLVM 23.1.5 compatibility binary. It was not rebuilt.

This stage2 configuration combines compiler CGU16 and ThinLTO, including stage1
CGU16 preparation and source-selected compiler/private-tool native effects.
Standard-library CGU remains 256; no PGO is used. The
[effective profile](../measurements/2026-11-09-cgu16-thinlto/producer.toml) records
settings separately from the complete input closure.

Cargo is the verified official bootstrap component, SHA256
`16e827eede03ad04b2be898c42ba40ec434fbb6cbbc13fc60354fdf4fd29a36f`, not produced
Cargo. Compiler/private libraries, rustdoc, Clippy, rustfmt, native/Wasm sysroots
and matching experimental unwind-enabled Cranelift stay together. Native
Lust/TCC/semantic engines and rustc-dev metadata are absent. Full Rust still
uses rustc.

The lightweight release tags document this assembled variant at blueFe
`43b9b6229a9024216d32a60df805fd204ae3ec8d` and Lustr
`180e6411648936c1c4bb904a7ab3171a6693a20c`. These later documentation commits and
measurement source `c958a780` are distinct from the actual component build commits.

## Invocation and host contract

Download all six assets to a new empty versioned directory, then:

```sh
sha256sum -c SHA256SUMS
tar --zstd -xf bluefe-lustr-preview-2026.11.09-2-x86_64-unknown-linux-gnu.tar.zst
BLUEFE_ROOT="$(pwd)/bluefe-lustr"
"$BLUEFE_ROOT/bin/lustr" --bluefe-root "$BLUEFE_ROOT" doctor
```

From a project, keep that absolute root and select its tools explicitly:

```sh
export CARGO="$BLUEFE_ROOT/bin/cargo"
export RUSTC="$BLUEFE_ROOT/bin/rustc"
export RUSTDOC="$BLUEFE_ROOT/bin/rustdoc"
"$BLUEFE_ROOT/bin/lustr" --bluefe-root "$BLUEFE_ROOT" build --locked
"$BLUEFE_ROOT/bin/lustr" --bluefe-root "$BLUEFE_ROOT" test --locked
```

The compiler's sysroot is that extracted root. Preserve the complete directory
when moving it. An inherited explicit sysroot or compiler wrapper still has its
documented effect. Matching plugins should use bundled absolute paths with these
tool selectors. No global installation or application deployment is performed.

Qualified host is Linux GNU x86_64. Required symbol floors include GLIBC 2.39,
GLIBCXX_3.4.32 and GCC_4.2.0, with actual interpreter/NEEDED/version observations in
`platform.json`. Native linking also requires host compiler/linker, headers,
startup files and development libraries. Native target is
`x86_64-unknown-linux-gnu`; `wasm32-unknown-unknown` is qualified for linking and
the eight-byte module header only. Other hosts and Wasm execution are unqualified.

## Qualification and interpretation

Fresh extraction with spaces passed with original source/build/home roots
inaccessible. Checks covered exact tool versions/sysroot, Lustr doctor and pure
planning, native build/run/unit unwind/drop/doctest, structured E0308 rejection
without output, Wasm linking, matching Clippy rejection/rustfmt fail-format-pass,
Cranelift dynamic loading/unwinding and native owned-FD/variadic ABI behavior.
The first doctest fixture's flag quoting was repaired using encoded rustdoc
arguments; the failure remains retained. Earlier passes were not relabeled as
reruns. These bounded fixtures are not universal compiler-correctness evidence.

Parent verification independently checked the complete archive/member/hash/header
structure, all regular-file bytes under the configured privacy scanner, five
sidecars and the unchanged legal attribution/Cargo diagnostic dispositions.
Component/source values and all 972 Cargo notice entries match the retained
producer. Cargo notice scope is a conservative locked-source superset, not a
recovered official binary feature graph. CI LLVM source/notice scope and its
unavailable checksum sidecar remain limits. No universal privacy, historical
erasure or license-completeness claim is made.

The immutable sidecars preserve producer-time and packaging-time pending states.
This release record and release notes document the subsequent parent acceptance
and publication. The source/header/privacy checks did not patch any binary.

The [accepted root-check report](https://github.com/glopyglerky/lustr/blob/next/docs/compiler-set/measurements/2026-11-09-cgu16-thinlto-v3/README.md)
records 17.9% less metadata-only root-check wall time versus the matched stage2
control, ratio 0.820912 with conditional 95% interval [0.799523, 0.840145]. Stock
Rust 1.99.1 remained faster in every case; versions differ. This is not a direct
comparison with preview-2026.11.09-1 or evidence of full-build/application speed,
separate knob effects, aggregate memory, whole-stack memory safety or general
compiler equivalence. PGO remains separately held and untimed.

The [previous preview](preview-2026.11.09-1.md) remains available for rollback.
