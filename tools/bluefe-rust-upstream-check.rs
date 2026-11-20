use std::collections::BTreeMap;
use std::path::{Component, Path};
use std::process::Command;

fn git(root: &Path, args: &[&str]) -> Result<Vec<u8>, String> {
    let output = Command::new("git").arg("-C").arg(root).args(args).output().map_err(|e| e.to_string())?;
    if !output.status.success() { return Err("Rust source guard failed; inspect the protected source diff".into()); }
    Ok(output.stdout)
}

fn check(root: &Path, scopes: &[(&str, &str)], index: bool) -> Result<(), String> {
    for (path, expected) in scopes {
        if !Path::new(path).components().all(|c| matches!(c, Component::Normal(_))) { return Err("invalid protected scope".into()); }
        let object = if index {
            if *path == "src/stage0" {
                git(root, &["rev-parse", &format!(":{path}")])?
            } else { git(root, &["write-tree", &format!("--prefix={path}/")])? }
        } else { git(root, &["rev-parse", &format!("HEAD:{path}")])? };
        if object.strip_suffix(b"\n").unwrap_or(&object) != expected.as_bytes() {
            return Err(format!("{path} differs from pinned upstream Rust; necessity and faster-results evidence are required"));
        }
        git(root, &["-c", "core.filemode=true", "diff", "--no-ext-diff", "--ignore-submodules=none", "--quiet", "--exit-code", "--", path])?;
        if !index { git(root, &["diff", "--cached", "--no-ext-diff", "--quiet", "--exit-code", "HEAD", "--", path])?; }
        if !git(root, &["ls-files", "--others", "--exclude-standard", "-z", "--", path])?.is_empty() {
            return Err(format!("keep blueFe-owned additions outside upstream scope {path}"));
        }
    }
    Ok(())
}

fn main() {
    let args: Vec<_> = std::env::args_os().skip(1).collect();
    let index = match args.as_slice() { [] => false, [a] if a == "--index" => true, _ => { eprintln!("usage: bluefe-rust-upstream-check [--index]"); std::process::exit(2); } };
    let result = (|| {
        let mut pin = BTreeMap::new();
        for line in include_str!("../upstream/rust.pin").lines() {
            let (key, value) = line.split_once('=').ok_or("invalid Rust pin")?;
            let value = value.trim().strip_prefix('"').and_then(|v| v.strip_suffix('"')).ok_or("invalid Rust pin value")?;
            if pin.insert(key.trim(), value).is_some() { return Err("duplicate Rust pin field".into()); }
        }
        if pin.remove("repository") != Some("https://github.com/rust-lang/rust") || pin.len() != 7 { return Err("unexpected Rust pin".into()); }
        for hash in pin.values() { if hash.len() != 40 || !hash.bytes().all(|b| b.is_ascii_hexdigit()) { return Err("invalid Rust object identity".into()); } }
        pin.remove("root_tree");
        let revision = pin.remove("revision").unwrap();
        let scopes: Vec<_> = pin.into_iter().collect();
        check(Path::new("."), &scopes, index)?;
        println!("Protected Rust sources match upstream {revision}; no source divergence admitted");
        Ok::<_, String>(())
    })();
    if let Err(error) = result { eprintln!("{error}"); std::process::exit(1); }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn detects_modified_added_and_staged_source_without_rejecting_owned_code() {
        let root = std::env::temp_dir().join(format!("bluefe-source-guard-{}", std::process::id()));
        std::fs::create_dir(&root).unwrap();
        git(&root, &["init", "-q"]).unwrap();
        std::fs::create_dir(root.join("compiler")).unwrap();
        std::fs::write(root.join("compiler/code.rs"), "fn original() {}\n").unwrap();
        git(&root, &["add", "compiler"]).unwrap();
        git(&root, &["-c", "commit.gpgsign=false", "-c", "user.name=glopyglerky", "-c", "user.email=189872235+glopyglerky@users.noreply.github.com", "commit", "-qm", "guard fixture"]).unwrap();
        let tree = String::from_utf8(git(&root, &["rev-parse", "HEAD:compiler"]).unwrap()).unwrap();
        let scopes = [("compiler", tree.trim())];
        std::fs::write(root.join("owned.rs"), "fn independent() {}\n").unwrap();
        check(&root, &scopes, false).unwrap();
        std::fs::write(root.join("compiler/code.rs"), "fn changed() {}\n").unwrap();
        assert!(check(&root, &scopes, false).is_err());
        git(&root, &["add", "compiler"]).unwrap();
        assert!(check(&root, &scopes, true).is_err());
        std::fs::write(root.join("compiler/code.rs"), "fn original() {}\n").unwrap();
        git(&root, &["add", "compiler"]).unwrap();
        check(&root, &scopes, true).unwrap();
        std::fs::write(root.join("compiler/extra.rs"), "fn extra() {}\n").unwrap();
        assert!(check(&root, &scopes, true).is_err());
        std::fs::remove_dir_all(root).unwrap();
    }
}
