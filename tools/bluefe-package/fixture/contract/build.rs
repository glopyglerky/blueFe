fn main() {
    let path = std::path::PathBuf::from(std::env::var_os("OUT_DIR").unwrap());
    std::fs::write(path.join("generated.rs"), "pub const GENERATED: u64 = 2;\n").unwrap();
    println!("cargo::rerun-if-changed=build.rs");
}
