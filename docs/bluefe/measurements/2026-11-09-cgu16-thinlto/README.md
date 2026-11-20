# CGU16 and ThinLTO stage2 experiment

The optimized stage2 package used 17.9% less root-check wall time than the
matched stage2 control across three fixed cases. Candidate/control geometric
ratio was 0.820912, conditional 95% interval [0.799523, 0.840145]. Stock Rust
1.99.1 remained faster in every case. Its versions differ, so it is a secondary
reference. The [full Lustr report](https://github.com/glopyglerky/lustr/blob/next/docs/compiler-set/measurements/2026-11-09-cgu16-thinlto-v3/README.md) retains all 240 command records,
108 timed observations, nine excluded warmups, regressions, exact identities,
independent review and the Rust replay command.

This is a shared-host, dependency-primed, metadata-only root experiment. It is
not full-build/application speed or a semantic/memory-safety proof. Bootstrap
independence and sign exchangeability remain assumptions. Collector/observer
overhead is retained. All matched scoped RSS checks passed; this is the largest
waited process, not aggregate RAM. PGO remains separately held and untimed.

## Build settings and decisions

Both arms use compiler source `1b74388e196ee8813f38ba9eeb6d4ab43b6b1071` and Lustr
`07470b20464bf097c3c88983124aff56c5e44f9a`, the same Cargo/LLVM/common controls and
default frontend. The joint treatment changes compiler CGU256/off-LTO to
CGU16/ThinLTO. Standard-library CGU stays 256. Compiler CGU16 also affects
stage1 preparation. Stage2 enables source-selected dylib/ThinLTO and compiler/
private-tool native flags. Individual knob and pure Rust-only effects are not
identified. The compiler still implements full Rust through inherited rustc.

[`producer.toml`](producer.toml) records normalized effective settings. It
combines the original base config and actual command-line overrides; the
original base alone would misleadingly show CGU256/off-LTO. It is not a complete
input closure or a byte-for-byte reproduction recipe. Supply initialized exact
submodules, the pinned stage0, matching LLVM/native dependencies, safe source/
cache remaps and a writable `/build` outside source before adapting it.
Cached CI LLVM availability and inherited notice/source-coverage limits remain.

The original matrix selected stage2, native GNU x86_64 and wasm32-unknown-unknown,
and compiler/rustc, the whole library tree, rustdoc, Clippy, rustfmt and
unwind-enabled rustc_codegen_cranelift. Cargo in the assembled payload is the
identified official bootstrap binary, not a newly produced Cargo.

The [experiment record](experiment.json) binds source, profile and payload hashes.
The control's historical prebuild capture preservation failed; retrospective
input binding was independently accepted with limitations. Lost captures remain
lost. Candidate/runtime/privacy review and the fixed pilot passed. Archive,
added-metadata, relocation, notice/source binding and release publication are
separate gates; this experiment itself creates no release.

The [mathematical arguments](https://github.com/glopyglerky/lustr/blob/next/docs/compiler-set/proofs/cgu16-thinlto.md)
cover geometric ratios, reciprocal intervals, position counts, the exact integer
RSS decision, joint-treatment non-identifiability and conditional amortization.
They do not prove compiler semantics or an unmeasured speedup.
