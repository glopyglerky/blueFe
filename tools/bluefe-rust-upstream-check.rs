use std::collections::BTreeMap;
use std::path::{Component, Path};
use std::process::Command;

fn git(root: &Path, args: &[&str]) -> Result<Vec<u8>, String> {
    let output = Command::new("git").arg("-C").arg(root).args(args).output().map_err(|e| e.to_string())?;
    if !output.status.success() { return Err("Rust source guard failed; inspect the protected source diff and fetch the pinned upstream revision".into()); }
    Ok(output.stdout)
}

fn object(root: &Path, expression: &str) -> Result<String, String> {
    String::from_utf8(git(root, &["rev-parse", expression])?).map(|s| s.trim().to_owned()).map_err(|e| e.to_string())
}

fn entries(root: &Path, revision: &str, scopes: &[(&str, &str)]) -> Result<BTreeMap<String, String>, String> {
    let mut args = vec!["ls-tree", "-r", "-z", revision, "--"];
    args.extend(scopes.iter().map(|(path, _)| *path));
    let output = git(root, &args)?;
    let mut result = BTreeMap::new();
    for entry in output.split(|b| *b == 0).filter(|e| !e.is_empty()) {
        let entry = std::str::from_utf8(entry).map_err(|e| e.to_string())?;
        let (identity, path) = entry.split_once('\t').ok_or("invalid Git tree entry")?;
        if result.insert(path.to_owned(), identity.to_owned()).is_some() { return Err("duplicate Git tree entry".into()); }
    }
    Ok(result)
}

fn check(root: &Path, revision: &str, scopes: &[(&str, &str)], overrides: &[(&str, &str, &str)], index: bool) -> Result<(), String> {
    for (path, expected) in scopes {
        if !Path::new(path).components().all(|c| matches!(c, Component::Normal(_))) { return Err("invalid protected scope".into()); }
        if object(root, &format!("{revision}:{path}"))? != *expected {
            return Err(format!("{path} no longer identifies the pinned upstream source"));
        }
    }
    let mut expected = entries(root, revision, scopes)?;
    let mut admitted = BTreeMap::new();
    for (path, upstream, fork) in overrides {
        if admitted.insert(*path, ()).is_some() { return Err(format!("duplicate fork path {path}")); }
        let original = expected.get_mut(*path).ok_or_else(|| format!("fork path outside upstream scopes: {path}"))?;
        let (kind, hash) = original.rsplit_once(' ').ok_or("invalid Git object identity")?;
        if !kind.ends_with(" blob") || hash != *upstream || upstream == fork {
            return Err(format!("fork provenance mismatch for {path}"));
        }
        *original = format!("{kind} {fork}");
    }
    let current = if index { String::from_utf8(git(root, &["write-tree"])?).map_err(|e| e.to_string())?.trim().to_owned() } else { "HEAD".into() };
    let actual = entries(root, &current, scopes)?;
    for path in expected.keys().chain(actual.keys()) {
        if expected.get(path) != actual.get(path) {
            return Err(format!("{path} differs from the recorded upstream-plus-fork source; preserve fork work and review the exact change"));
        }
    }
    for (path, _) in scopes {
        git(root, &["-c", "core.filemode=true", "diff", "--no-ext-diff", "--ignore-submodules=none", "--quiet", "--exit-code", "--", path])?;
        if !index { git(root, &["diff", "--cached", "--no-ext-diff", "--quiet", "--exit-code", "HEAD", "--", path])?; }
        if !git(root, &["ls-files", "--others", "--exclude-standard", "-z", "--", path])?.is_empty() {
            return Err(format!("unrecorded source additions in {path}"));
        }
    }
    Ok(())
}

fn fields(source: &str) -> Result<BTreeMap<&str, &str>, String> {
    let mut result = BTreeMap::new();
    for line in source.lines() {
        let (key, value) = line.split_once('=').ok_or("invalid source pin")?;
        let value = value.trim().strip_prefix('"').and_then(|v| v.strip_suffix('"')).ok_or("invalid source pin value")?;
        if result.insert(key.trim(), value).is_some() { return Err("duplicate source pin field".into()); }
    }
    Ok(result)
}

fn valid_hash(hash: &str) -> bool {
    hash.len() == 40 && hash.bytes().all(|b| b.is_ascii_hexdigit())
}

fn main() {
    let args: Vec<_> = std::env::args_os().skip(1).collect();
    let index = match args.as_slice() { [] => false, [a] if a == "--index" => true, _ => { eprintln!("usage: bluefe-rust-upstream-check [--index]"); std::process::exit(2); } };
    let result = (|| {
        let mut pin = fields(include_str!("../upstream/rust.pin"))?;
        if pin.remove("repository") != Some("https://github.com/rust-lang/rust") || pin.len() != 7 { return Err("unexpected Rust pin".into()); }
        if pin.values().any(|hash| !valid_hash(hash)) { return Err("invalid Rust object identity".into()); }
        let root_tree = pin.remove("root_tree").ok_or("missing upstream tree")?;
        let revision = pin.remove("revision").ok_or("missing upstream revision")?;
        let scopes: Vec<_> = pin.into_iter().collect();
        if scopes.iter().map(|(path, _)| *path).collect::<Vec<_>>() != ["compiler", "library", "src/bootstrap", "src/stage0", "src/tools/bump-stage0"] { return Err("unexpected protected scopes".into()); }
        let root = Path::new(".");
        if object(root, &format!("{revision}^{{tree}}"))? != root_tree { return Err("upstream root tree mismatch".into()); }
        let mut overrides = Vec::new();
        for (path, identities) in fields(include_str!("../upstream/bluefe-fork.pin"))? {
            let parts: Vec<_> = identities.split_whitespace().collect();
            if parts.len() != 2 || !parts.iter().all(|hash| valid_hash(hash)) { return Err("invalid fork blob identities".into()); }
            overrides.push((path, parts[0], parts[1]));
        }
        check(root, revision, &scopes, &overrides, index)?;
        println!("Rust upstream {revision} retained with {} recorded fork changes", overrides.len());
        Ok::<_, String>(())
    })();
    if let Err(error) = result { eprintln!("{error}"); std::process::exit(1); }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn protects_upstream_and_fork_against_reversion_drift_and_additions() {
        let root = std::env::temp_dir().join(format!("bluefe-source-guard-{}", std::process::id()));
        std::fs::create_dir(&root).unwrap();
        git(&root, &["init", "-q"]).unwrap();
        std::fs::create_dir(root.join("compiler")).unwrap();
        std::fs::write(root.join("compiler/code.rs"), "fn original() {}\n").unwrap();
        git(&root, &["add", "compiler"]).unwrap();
        let commit = |message: &str| { git(&root, &["-c", "commit.gpgsign=false", "-c", "user.name=guard", "-c", "user.email=guard@example.invalid", "commit", "-qm", message]).unwrap(); };
        commit("upstream fixture");
        let revision = object(&root, "HEAD").unwrap();
        let tree = object(&root, "HEAD:compiler").unwrap();
        let upstream = object(&root, "HEAD:compiler/code.rs").unwrap();
        let scopes = [("compiler", tree.as_str())];
        check(&root, &revision, &scopes, &[], false).unwrap();

        std::fs::write(root.join("compiler/code.rs"), "fn restored_fork() {}\n").unwrap();
        git(&root, &["add", "compiler"]).unwrap();
        let fork = object(&root, ":compiler/code.rs").unwrap();
        let overrides = [("compiler/code.rs", upstream.as_str(), fork.as_str())];
        assert!(check(&root, &revision, &scopes, &[], true).is_err());
        check(&root, &revision, &scopes, &overrides, true).unwrap();
        commit("restore fork work");
        check(&root, &revision, &scopes, &overrides, false).unwrap();

        std::fs::write(root.join("owned.rs"), "fn independent() {}\n").unwrap();
        check(&root, &revision, &scopes, &overrides, false).unwrap();
        std::fs::write(root.join("compiler/code.rs"), "fn original() {}\n").unwrap();
        assert!(check(&root, &revision, &scopes, &overrides, false).is_err());
        git(&root, &["add", "compiler"]).unwrap();
        assert!(check(&root, &revision, &scopes, &overrides, true).is_err());
        commit("unwanted upstream reset");
        assert!(check(&root, &revision, &scopes, &overrides, false).is_err());
        std::fs::write(root.join("compiler/code.rs"), "fn restored_fork() {}\n").unwrap();
        git(&root, &["add", "compiler"]).unwrap();
        check(&root, &revision, &scopes, &overrides, true).unwrap();

        std::fs::write(root.join("compiler/extra.rs"), "fn extra() {}\n").unwrap();
        assert!(check(&root, &revision, &scopes, &overrides, true).is_err());
        git(&root, &["add", "compiler"]).unwrap();
        assert!(check(&root, &revision, &scopes, &overrides, true).is_err());
        git(&root, &["rm", "-f", "compiler/extra.rs"]).unwrap();
        let invalid = [("compiler/code.rs", fork.as_str(), upstream.as_str())];
        assert!(check(&root, &revision, &scopes, &invalid, true).is_err());
        let unscoped = [("owned.rs", upstream.as_str(), fork.as_str())];
        assert!(check(&root, &revision, &scopes, &unscoped, true).is_err());
        std::fs::remove_dir_all(root).unwrap();
    }
}
