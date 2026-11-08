# blueFe

blueFe is a personal fork of Rust. Its default `./x` build entry point uses the
[lustr coordinator](https://github.com/glopyglerky/lustr) for bootstrap and ordinary
compiler, library, and tool Cargo builds. rustc still compiles full Rust and
bootstrap still selects the compiler for each stage. Native lustr replacement
of rustc is future work. This integration makes no build-speed claim.

The coordinator is pinned as the `src/bluefe/lustr` submodule. On a Git checkout,
`./x` initializes that submodule if needed, then builds only its dependency-free
coordinator with stage0 Cargo, offline and locked. It does not build native Lust
or install a Cranelift backend. With automatic submodule updates disabled, or
with a source archive, provide the pinned submodule contents before building.

Use the normal upstream build commands below. Coordinator output goes under
`<build-dir>/bluefe-lustr`; bootstrap uses the same configured build directory.
Cargo arguments, stage compilers, flags, profiles, features, and exit failures
are preserved. Specialized Clippy and Miri launchers and bootstrap's direct
Cargo metadata/version queries retain their upstream paths. Ordinary `cargo`
outside bootstrap and the resulting toolchain's default rustc are unchanged.

Stage0 is pinned to nightly-2026-11-03, Rust 1.101, with component checksums in
`src/stage0`. The current beta is too old for this source. The stage0 updater
therefore selects a nightly for blueFe's nightly channel. To refresh that pin,
use `./x run src/tools/bump-stage0 -- COMPILER_DATE RUSTFMT_DATE` and qualify the
result before publishing it.

To produce a compiler, complete native and wasm sysroots, and rustdoc:

```sh
./x build --stage 1 --target x86_64-unknown-linux-gnu,wasm32-unknown-unknown \
  compiler/rustc library src/tools/rustdoc
```

Use a build directory on a filesystem with enough space, configured through
`build.build-dir` in `bootstrap.toml`. Select the whole `library` tree so the
sysroot includes `proc_macro` and the test harness as well as `std`. Set
`rust.omit-git-hash = false` to include the source commit in compiler version
output. Upstream's prerequisite and LLVM setup
instructions below still apply. The produced native sysroot is
`<build-dir>/x86_64-unknown-linux-gnu/stage1`; its `bin/rustc` is distinct from
the downloaded stage0 compiler.

For an application build, select that produced compiler explicitly:

```sh
RUSTC=/path/to/produced-sysroot/bin/rustc \
RUSTDOC=/path/to/produced-sysroot/bin/rustdoc \
LUST_CARGO=/path/to/compatible/cargo \
  /path/to/lustr --engine auto build --target x86_64-unknown-linux-gnu
```

`rustc --print sysroot` must identify the produced sysroot. Select
`wasm32-unknown-unknown` for wasm builds. Native lustr and its separately pinned
Cranelift/semantic inspection tools are not interchangeable with this compiler;
their use requires separate compatibility qualification.

The blueFe integration is LLM-generated fork work and is not intended for
submission to `rust-lang/rust`. Upstream Rust's README follows.

<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/rust-lang/www.rust-lang.org/master/static/images/rust-social-wide-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/rust-lang/www.rust-lang.org/master/static/images/rust-social-wide-light.svg">
    <img alt="The Rust Programming Language: A language empowering everyone to build reliable and efficient software"
         src="https://raw.githubusercontent.com/rust-lang/www.rust-lang.org/master/static/images/rust-social-wide-light.svg"
         width="50%">
  </picture>

[Website][Rust] | [Getting started] | [Learn] | [Documentation] | [Contributing]
</div>

This is the main source code repository for [Rust]. It contains the compiler,
standard library, and documentation.

[Rust]: https://www.rust-lang.org/
[Getting Started]: https://www.rust-lang.org/learn/get-started
[Learn]: https://www.rust-lang.org/learn
[Documentation]: https://www.rust-lang.org/learn#learn-use
[Contributing]: CONTRIBUTING.md

## Why Rust?

- **Performance:** Fast and memory-efficient, suitable for critical services, embedded devices, and easily integrated with other languages.

- **Reliability:** Our rich type system and ownership model ensure memory and thread safety, reducing bugs at compile-time.

- **Productivity:** Comprehensive documentation, a compiler committed to providing great diagnostics, and advanced tooling including package manager and build tool ([Cargo]), auto-formatter ([rustfmt]), linter ([Clippy]) and editor support ([rust-analyzer]).

[Cargo]: https://github.com/rust-lang/cargo
[rustfmt]: https://github.com/rust-lang/rustfmt
[Clippy]: https://github.com/rust-lang/rust-clippy
[rust-analyzer]: https://github.com/rust-lang/rust-analyzer

## Quick Start

Read ["Installation"] from [The Book].

["Installation"]: https://doc.rust-lang.org/book/ch01-01-installation.html
[The Book]: https://doc.rust-lang.org/book/index.html

## Installing from Source

If you really want to install from source (though this is not recommended), see
[INSTALL.md](INSTALL.md).

## Getting Help

See https://www.rust-lang.org/community for a list of chat platforms and forums.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

For a detailed explanation of the compiler's architecture and how to begin contributing, see the [rustc-dev-guide](https://rustc-dev-guide.rust-lang.org/).

## License

Rust is primarily distributed under the terms of both the MIT license and the
Apache License (Version 2.0), with portions covered by various BSD-like
licenses.

See [LICENSE-APACHE](LICENSE-APACHE), [LICENSE-MIT](LICENSE-MIT), and
[COPYRIGHT](COPYRIGHT) for details.

## Trademark

[The Rust Foundation][rust-foundation] owns and protects the Rust and Cargo
trademarks and logos (the "Rust Trademarks").

If you want to use these names or brands, please read the
[Rust language trademark policy][trademark-policy].

Third-party logos may be subject to third-party copyrights and trademarks. See
[Licenses][policies-licenses] for details.

[rust-foundation]: https://rustfoundation.org/
[trademark-policy]: https://rustfoundation.org/policy/rust-trademark-policy/
[policies-licenses]: https://www.rust-lang.org/policies/licenses
