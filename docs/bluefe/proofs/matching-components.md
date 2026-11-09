# Matching component build recipe

Status: the matched producer build completed for
[preview-2026.11.09-1](../releases/preview-2026.11.09-1.md). Its compiler,
both sysroots, Clippy, rustfmt, Cranelift with unwinding and coordinator passed
the recorded gates. This template is contributor guidance, not a requirement
for agents using the prebuilt release. Use one owned build root and preserve
accepted payloads.

Use a clean/reviewed source snapshot after the final Lustr gitlink update. Record
`git rev-parse HEAD`, `git diff --binary` hash, `git submodule status --recursive`,
Cargo.lock hashes and tool subtree tree IDs. Existing pins are inputs, not upgrade
requests. The root Lustr crate has no registry dependencies; compiler/bootstrap
and optional components do. Supply locked registry/vendor dependencies, pinned
standard-library submodules and a compatible stage0. No Cargo source rebuild is
required; the configured Cargo remains a bootstrap tool.

Copy [the template](matching-build.toml.example) outside the checkout and replace
its three absolute path parameters: build root, stage0 rustc and stage0 Cargo.
Use the pinned nightly, verified against `src/stage0`, for the privacy-remapped
producer build. Existing retained private compiler artifacts must not become
inputs to that public candidate. Stage0 ABI is not the
ABI of the resulting compiler; never graft the resulting private tools onto the
old accepted compiler without a full ABI/qualification argument.

Exact build invocations from the source root (CONFIG is the completed template):

```sh
./x --config "$CONFIG" build --stage 1 --target x86_64-unknown-linux-gnu,wasm32-unknown-unknown compiler/rustc library src/tools/rustdoc src/tools/clippy src/tools/rustfmt rustc_codegen_cranelift
```

These commands describe one matched stage1 set, including both Clippy binaries.
The preview used the registered `rustc_codegen_cranelift` build alias and a
combined native/Wasm invocation so both installed sysroots remained present.
It set `rust.deny-warnings=false` after inherited Clippy stable-feature warnings
stopped the first attempt; externally maintained source stayed unchanged. Inspect the
resolved bootstrap plan and component logs before packaging. Preserve source
failures; request owner integration for external-tool defects rather than patching
vendored tool source. LLVM is downloaded through existing bootstrap provenance,
not compiled here; network/cache availability is a required input. Do not silently
substitute system LLVM or a downloaded compiler if that input is unavailable.

Run the producer with neutral source, build, Cargo cache and home paths visible
inside a filesystem namespace. Enable path remapping for all metadata as well
as object/debug output. Order overlapping remaps from broad to specific because
the last matching rule wins. A debug-only remap does not cover embedded metadata
or arbitrary build-time environment strings. Rebuild the compiler, both sysroots,
tools and coordinator; never patch paths in compiled bytes. Record the exact
namespace, flags and resolved commands privately, then scan every byte and all
archive metadata in the new frozen candidate.

Generate the copyright and dependency notices from the exact source and locked
dependency closure. Include LLVM and the separately supplied Cargo component's
notices. The compiler build alone does not establish redistribution readiness.

The compiler-private libraries and backend are built in the same bootstrap
closure. `CraneliftCodegenBackend` explicitly enables `unwinding`; confirm this in
the actual Cargo command. After staging a new candidate, check rustc/rustdoc/Cargo
versions and hashes, run the full integration fixture, invoke candidate rustfmt
and Clippy explicitly on a tiny fixture, and compile/run the panic catch/drop
fixture with `-Zcodegen-backend` naming the new backend. Check the selected backend
in the Lustr plan and preserve the real backend command/result. A version probe,
LLVM-only panic test or linking alone cannot qualify cgclif unwinding.

Resource planning: two Cargo jobs, nonincremental compiler, no LTO, no debug info,
256 codegen units; two jobs do not cap linker/LLVM memory or all native threads.
The retained payload is approximately 915 MiB, but lacks rustc-dev metadata, and
its original compiler cache was removed. This is a fresh compiler build rather
than an incremental optional-component build. Reserve provisionally 30–60 GiB
of generated storage and 16–32 GiB RAM; allow 1–4 hours at two jobs. These are
conservative planning estimates, not measured limits or completion promises:
current logs do not contain a comparable clean two-job optional-tools build.
Check actual host pressure before admission and revise from measured output.
Retain a fresh candidate and rollback; clean intermediates only after packaging,
hashing and qualification, with process/file/mount/lock checks and measured df.
