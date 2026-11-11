fn main() {
    assert_eq!(bluefe_contract::generic(&42u64), bluefe_contract::answer());
    assert_eq!(bluefe_contract::dynamic(&42u64), bluefe_contract::answer());
    println!("bluefe-package-ok:42");
}
